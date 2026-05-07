#!/usr/bin/env python3
"""Process library submission issues — fetch GitHub repo, analyze with LLM, download images.

Flow:
  1. Parse GitHub URL from issue body
  2. Fetch repo metadata + README + file tree via gh CLI
  3. LLM judges: UE-related? Extract name / description / category
  4. If valid: download README images → insert into libraries/index.md
  5. If invalid: close issue with reason

Called from GitHub Action on issue opened with label 'library-submission'.
"""

import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent  # ue-book/scripts → root
LIBS_PATH = PROJECT_DIR / "ue-book" / "docs" / "libraries" / "index.md"
IMAGES_DIR = PROJECT_DIR / "ue-book" / "docs" / "libraries" / "images"

VALID_CATEGORIES = [
    "Editor Tools", "Animation", "Niagara", "Gameplay", "Character",
    "UI", "Material", "NetWork", "Framework", "Tools", "Plugins",
    "Engine", "Script", "Python", "Projects", "Other",
]

# ── GitHub helpers ──

def gh_api(endpoint: str) -> dict:
    """Call gh api and return parsed JSON."""
    result = subprocess.run(
        ["gh", "api", "-H", "Accept: application/vnd.github+json", endpoint],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh api {endpoint} failed: {result.stderr[:200]}")
    return json.loads(result.stdout)


def parse_github_url(url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from a GitHub URL."""
    # Handle various formats:
    #   https://github.com/owner/repo
    #   https://github.com/owner/repo.git
    #   https://github.com/owner/repo/tree/branch/...
    m = re.match(r'https?://github\.com/([^/]+)/([^/\s#?.]+)', url)
    if m:
        return m.group(1), m.group(2).removesuffix('.git')
    return None


def fetch_repo_info(owner: str, repo: str) -> dict:
    """Get repo metadata: description, topics, language, stars."""
    data = gh_api(f"repos/{owner}/{repo}")
    return {
        "full_name": data.get("full_name", f"{owner}/{repo}"),
        "description": data.get("description") or "",
        "topics": data.get("topics") or [],
        "language": data.get("language") or "",
        "stars": data.get("stargazers_count", 0),
        "html_url": data.get("html_url", ""),
    }


def fetch_readme(owner: str, repo: str) -> str:
    """Fetch and decode README.md content."""
    data = gh_api(f"repos/{owner}/{repo}/readme")
    content_b64 = data.get("content", "")
    return base64.b64decode(content_b64).decode("utf-8", errors="replace")


def fetch_file_tree(owner: str, repo: str, max_entries: int = 300) -> str:
    """Fetch recursive file tree, return as formatted string."""
    try:
        data = gh_api(f"repos/{owner}/{repo}/git/trees/HEAD?recursive=1")
        tree = data.get("tree", [])
        # Filter to files only, limit size
        files = [t["path"] for t in tree if t.get("type") == "blob"][:max_entries]
        if len(tree) > max_entries:
            files.append(f"... ({len(tree) - max_entries} more files)")
        return "\n".join(files)
    except Exception:
        return "(无法获取文件树)"


# ── Image handling ──

def extract_image_urls(readme: str, owner: str, repo: str, default_branch: str = "master") -> list[tuple[str, str]]:
    """Extract image references from markdown: [(alt_text, url), ...]"""
    images = []
    for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', readme):
        alt = m.group(1).strip() or "image"
        url = m.group(2).strip()
        # Skip YouTube thumbnails and other non-image URLs
        if any(skip in url for skip in ['youtube.com', 'youtu.be', 'img.youtube.com']):
            continue
        # Resolve relative URLs to absolute raw.githubusercontent.com URLs
        url = resolve_image_url(url, owner, repo, default_branch)
        images.append((alt, url))
    return images


def resolve_image_url(url: str, owner: str, repo: str, branch: str) -> str:
    """Resolve relative/absolute image URLs to raw.githubusercontent.com."""
    if url.startswith("http"):
        return url
    # Remove leading . or /
    path = re.sub(r'^\.?/', '', url)
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"


def download_image(url: str, save_path: Path) -> bool:
    """Download an image to a local path. Returns True on success."""
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "UE-Book/1.0"})
        if resp.status_code == 200:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(resp.content)
            return True
        else:
            print(f"  [warn] HTTP {resp.status_code} downloading {url}")
            return False
    except Exception as e:
        print(f"  [warn] Failed to download {url}: {e}")
        return False


def extract_user_description(issue_body: str) -> str:
    """Extract user's description from issue body template fields."""
    # Match "### 一句话描述（可选）" section
    m = re.search(r'###\s*一句话描述[^\n]*\n\n(.+?)(?:\n\n###|\Z)', issue_body, re.DOTALL)
    if m:
        desc = m.group(1).strip()
        # Remove "_No response_" placeholder
        desc = re.sub(r'^_No response_\s*', '', desc)
        # Strip trailing noise like "请收录", "请审核" etc
        desc = re.sub(r'\n*(?:请收录|请审核|谢谢|thanks).*$', '', desc, flags=re.IGNORECASE).strip()
        if desc and desc != '_No response_':
            return desc
    return ""


# ── LLM ──

def call_llm(prompt: str) -> str:
    """Call LLM via langchain-openai."""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage

    sys.path.insert(0, str(PROJECT_DIR / "ue-book"))
    from v2 import config

    llm = ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.LLM_MODEL,
        temperature=0.1,
        max_tokens=2000,
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def analyze_repo(repo_info: dict, readme: str, file_tree: str, user_desc: str = "") -> dict:
    """LLM analysis: is this UE-related? Extract info if yes."""
    # Truncate README for prompt
    readme_preview = readme[:4000]
    if len(readme) > 4000:
        readme_preview += "\n\n... (README 被截断)"

    user_section = ""
    if user_desc:
        user_section = f"""
## 用户提交时的描述
{user_desc}

请润色用户描述：如果太短或含糊→补充具体信息；如果冗长→精简到2-3句；如果合适→保留原意优化措辞。不要丢失用户的观点和语气。"""

    prompt = f"""分析以下 GitHub 仓库，判断是否为 Unreal Engine 相关项目。

## 仓库信息
- 名称: {repo_info['full_name']}
- GitHub 描述: {repo_info['description']}
- Topics: {', '.join(repo_info['topics'])}
- 主要语言: {repo_info['language']}
- Stars: {repo_info['stars']}

## README 内容
{readme_preview}

## 项目文件结构（前 {300 if '...' not in file_tree else '若干'} 个文件）
{file_tree[:3000]}
{user_section}
## 判断标准
UE 相关项目通常具有以下特征之一：
- README 明确提到 Unreal Engine / UE4 / UE5
- 文件结构包含 .uplugin / .uproject / Source/ / Build.cs
- C++ 项目中使用 UE 宏 (UFUNCTION, UPROPERTY, UCLASS, GENERATED_BODY)
- 是 UE 插件、工具、资产或教程

如果这是有效的 UE 开源库收录申请，提取信息并以 JSON 返回：
```json
{{
  "valid": true,
  "name": "库名（从 README 标题或仓库名提取）",
  "url": "{repo_info['html_url']}",
  "headline": "一行英文简述（从 README 提取，简洁）",
  "user_desc": "润色后的用户描述（中文，2-3句。如果用户没提交描述，此为\"\"）",
  "llm_comment": "AI 锐评（中文，1-2句。评价项目质量、亮点、适用场景。不要吹捧，客观）",
  "category": "分类（从以下选一个：{', '.join(VALID_CATEGORIES)}）"
}}
```

如果不是 UE 相关项目（如 Web 框架、Python 工具、非 UE 游戏引擎插件等），返回：
```json
{{
  "valid": false,
  "reason": "拒绝原因（中文，简洁说明）"
}}
```

只返回 JSON，不要其他内容。"""

    result = call_llm(prompt)

    # Extract JSON
    match = re.search(r"\{[\s\S]*\}", result)
    if not match:
        return {"valid": False, "reason": f"LLM 返回格式异常：{result[:200]}"}

    try:
        info = json.loads(match.group())
    except json.JSONDecodeError:
        return {"valid": False, "reason": f"LLM 返回 JSON 解析失败：{result[:200]}"}

    # Validate category
    cat = info.get("category", "")
    if cat not in VALID_CATEGORIES:
        info["category"] = "Other"

    return info


# ── Insert ──

def insert_library(info: dict, local_images: list[str]) -> str:
    """Insert library entry into libraries/index.md. Returns commit message."""
    content = LIBS_PATH.read_text(encoding="utf-8")
    category = info["category"]

    # Build entry: headline + optional images + user_desc + llm_comment
    name = info["name"]
    url = info["url"]
    headline = info.get("headline", "")
    user_desc = info.get("user_desc", "")
    llm_comment = info.get("llm_comment", "")

    entry_lines = [f"- [{name}]({url})  {headline}"]

    for img_path in local_images:
        entry_lines.append(f"  ![{name} screenshot](/libraries/images/{img_path})")

    if user_desc.strip():
        entry_lines.append(f"  - {user_desc.strip()}")
    if llm_comment.strip():
        entry_lines.append(f"  - 💬 {llm_comment.strip()}")

    entry = "\n".join(entry_lines) + "\n"

    # Find the category section header
    header = f"## {category}"
    idx = content.find(header)
    if idx == -1:
        idx = content.find("## Other")
        if idx == -1:
            return ""

    # Find insertion point before the next ## header
    next_section = content.find("\n## ", idx + len(header))
    if next_section == -1:
        next_section = len(content)

    # Try to insert before the last blank line in the section
    section_end = content.rfind("\n\n", 0, next_section)
    if section_end > idx:
        insert_pos = section_end
    else:
        insert_pos = next_section

    new_content = content[:insert_pos] + "\n" + entry + content[insert_pos:]
    LIBS_PATH.write_text(new_content, encoding="utf-8")

    return f"收录开源库: {name} ({category})"


# ── GitHub Issue actions ──

def post_comment(issue_number: str, body: str):
    subprocess.run(["gh", "issue", "comment", issue_number, "--body", body], timeout=30)


def close_issue(issue_number: str, reason: str, completed: bool = False):
    args = ["gh", "issue", "close", issue_number]
    if completed:
        args += ["--reason", "completed"]
    else:
        args += ["--reason", "not planned", "--comment", f"❌ 未通过收录审核\n\n{reason}"]
    subprocess.run(args, timeout=30)


# ── Main ──

def main():
    issue_body = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")

    if not issue_body:
        print("No issue body found.")
        return

    print(f"\n{'='*60}")
    print(f"Processing issue #{issue_number}...")

    # 1. Parse GitHub URL from issue body
    urls = re.findall(r'https?://github\.com/[\w.-]+/[\w.-]+', issue_body)
    if not urls:
        close_issue(issue_number, "未找到 GitHub 链接，请提供有效的 GitHub 仓库地址。")
        return

    gh_url = urls[0].rstrip(')').rstrip('.')
    parsed = parse_github_url(gh_url)
    if not parsed:
        close_issue(issue_number, f"无法解析 GitHub 链接：{gh_url}")
        return

    owner, repo = parsed
    print(f"  Repo: {owner}/{repo}")

    # 2. Fetch repo data
    try:
        repo_info = fetch_repo_info(owner, repo)
        print(f"  Description: {repo_info['description'][:80]}")
        print(f"  Topics: {repo_info['topics']}")
        print(f"  Language: {repo_info['language']}")
    except Exception as e:
        close_issue(issue_number, f"无法访问仓库信息：{e}")
        return

    try:
        readme = fetch_readme(owner, repo)
        print(f"  README: {len(readme)} chars")
    except Exception as e:
        print(f"  [warn] Cannot fetch README: {e}")
        readme = "(README 无法获取)"

    try:
        # Get default branch from repo info
        branch_data = gh_api(f"repos/{owner}/{repo}")
        default_branch = branch_data.get("default_branch", "master")
        
        file_tree = fetch_file_tree(owner, repo)
        print(f"  File tree: {len(file_tree.split(chr(10)))} entries")
    except Exception as e:
        print(f"  [warn] Cannot fetch file tree: {e}")
        file_tree = "(无法获取文件树)"
        default_branch = "master"

    # 3. Extract user description from issue
    user_desc = extract_user_description(issue_body)
    if user_desc:
        print(f"  User desc: {user_desc[:80]}...")

    # 4. LLM analysis
    print("  Analyzing with LLM...")
    info = analyze_repo(repo_info, readme, file_tree, user_desc)

    if not info.get("valid"):
        reason = info.get("reason", "未知原因")
        print(f"  ❌ Rejected: {reason}")
        close_issue(issue_number, reason)
        return

    print(f"  ✅ Valid: {info['name']} → {info['category']}")
    print(f"     Headline: {info.get('headline', '')[:80]}")
    if info.get('user_desc'):
        print(f"     User: {info['user_desc'][:80]}")
    if info.get('llm_comment'):
        print(f"     AI: {info['llm_comment'][:80]}")

    # 4. Download images
    images = extract_image_urls(readme, owner, repo, default_branch)
    print(f"  Images found: {len(images)}")

    local_images = []
    if images:
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', info['name'])[:40]
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        for i, (alt, img_url) in enumerate(images[:5]):  # Max 5 images
            ext = Path(urlparse(img_url).path).suffix or ".png"
            if ext.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
                ext = ".png"
            filename = f"{safe_name}_image-{i + 1}{ext}"
            save_path = IMAGES_DIR / filename
            if download_image(img_url, save_path):
                local_images.append(filename)
                print(f"    Downloaded: {filename}")
            else:
                print(f"    Failed: {filename}")

    # 5. Insert into libraries/index.md
    msg = insert_library(info, local_images)
    if not msg:
        close_issue(issue_number, "无法定位库文件中的分类位置，请手动添加。")
        return

    # 6. Post success comment
    comment = (
        f"✅ 已收录！\n\n"
        f"- **库名**: {info['name']}\n"
        f"- **地址**: {info['url']}\n"
        f"- **分类**: {info['category']}\n"
        f"- **简述**: {info.get('headline', '')}\n"
    )
    if info.get('user_desc'):
        comment += f"- **用户**: {info['user_desc']}\n"
    if info.get('llm_comment'):
        comment += f"- **锐评**: {info['llm_comment']}\n"
    if local_images:
        comment += f"- **图片**: {len(local_images)} 张已下载到本地\n"
    comment += f"\n提交: {msg}"
    post_comment(issue_number, comment)

    # 7. Close issue
    close_issue(issue_number, "", completed=True)
    print(f"  ✅ Done: {msg}")

    # 8. Output for GitHub Actions
    with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
        f.write(f"commit_msg={msg}\n")


if __name__ == "__main__":
    main()
