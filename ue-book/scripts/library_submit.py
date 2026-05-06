#!/usr/bin/env python3
"""Process library submission issues via LLM.

Reads issue body from env (ISSUE_BODY), validates with LLM,
extracts library info, inserts into libraries/index.md.

Called from GitHub Action on issue opened with label 'library-submission'.
"""

import json
import os
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LIBS_PATH = PROJECT_DIR / "docs" / "libraries" / "index.md"

VALID_CATEGORIES = [
    "Editor Tools", "Animation", "Niagara", "Gameplay", "Character",
    "UI", "Material", "NetWork", "Framework", "Tools", "Plugins",
    "Engine", "Script", "Python", "Projects", "Other",
]


def call_llm(prompt: str) -> str:
    """Call MiMo."""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage

    sys.path.insert(0, str(PROJECT_DIR))
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


def extract_info(issue_body: str, issue_url: str) -> dict:
    """Extract library info from issue body via LLM. Returns {'valid': bool, ...}."""
    prompt = f"""分析这个 Issue，判断是否为 UE 开源库收录申请。

Issue 内容：
{issue_body}

如果是有效的 UE 开源库收录申请，提取以下信息，以 JSON 格式返回：
```json
{{
  "valid": true,
  "name": "库名（从 GitHub URL 提取）",
  "url": "GitHub 地址",
  "description": "一句话中文描述（如果Issue没提供，根据库名推断）",
  "category": "分类（从以下选一个：{', '.join(VALID_CATEGORIES)}）"
}}
```

如果这不是有效的收录申请（不是 UE 相关、GitHub 链接无效、issue 格式错误等），返回：
```json
{{
  "valid": false,
  "reason": "拒绝原因（中文，简洁）"
}}
```

只返回 JSON，不要其他内容。"""

    result = call_llm(prompt)

    # Extract JSON from response
    match = re.search(r"\{[\s\S]*\}", result)
    if not match:
        return {"valid": False, "reason": "LLM 返回格式异常，无法解析"}

    try:
        info = json.loads(match.group())
    except json.JSONDecodeError:
        return {"valid": False, "reason": "LLM 返回 JSON 解析失败"}

    # Validate category
    cat = info.get("category", "")
    if cat not in VALID_CATEGORIES:
        info["category"] = "Other"

    return info


def insert_library(info: dict) -> str:
    """Insert library entry into the correct category section. Returns commit message."""
    content = LIBS_PATH.read_text(encoding="utf-8")
    category = info["category"]
    entry = f"- [{info['name']}]({info['url']}) {info['description']}\n"

    # Find the category section header and insert after it
    header = f"## {category}"
    idx = content.find(header)
    if idx == -1:
        # Fallback: append to Other
        idx = content.find("## Other")
        if idx == -1:
            return None

    # Find the next ## header after this section
    next_section = content.find("\n## ", idx + len(header))
    if next_section == -1:
        next_section = len(content)

    # Find the last entry in this section (before the blank line or next ##)
    insert_pos = next_section
    # Try to insert before the last blank line in the section
    section_end = content.rfind("\n\n", 0, next_section)
    if section_end > idx:
        insert_pos = section_end

    new_content = content[:insert_pos] + "\n" + entry + content[insert_pos:]
    LIBS_PATH.write_text(new_content, encoding="utf-8")

    return f"收录开源库: {info['name']} ({category})"


def post_comment(issue_number: str, body: str):
    """Post a comment on the issue via gh CLI."""
    import subprocess
    subprocess.run([
        "gh", "issue", "comment", issue_number,
        "--body", body,
    ], timeout=30)


def close_issue(issue_number: str, reason: str):
    """Close the issue with a comment."""
    import subprocess
    subprocess.run([
        "gh", "issue", "close", issue_number,
        "--reason", "not planned",
        "--comment", f"❌ 未通过收录审核\n\n{reason}",
    ], timeout=30)


def main():
    issue_body = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")
    issue_url = os.environ.get("ISSUE_URL", "")

    if not issue_body:
        print("No issue body found.")
        return

    print(f"Processing issue #{issue_number}...")
    info = extract_info(issue_body, issue_url)

    if not info.get("valid"):
        reason = info.get("reason", "未知原因")
        print(f"  Rejected: {reason}")
        close_issue(issue_number, reason)
        return

    print(f"  Valid: {info['name']} → {info['category']}")

    msg = insert_library(info)
    if not msg:
        close_issue(issue_number, "无法定位库文件中的分类位置，请手动添加。")
        return

    # Post success comment
    post_comment(issue_number,
        f"✅ 已收录！\n\n"
        f"- **库名**: {info['name']}\n"
        f"- **地址**: {info['url']}\n"
        f"- **分类**: {info['category']}\n"
        f"- **描述**: {info['description']}\n\n"
        f"提交: {msg}"
    )

    # Close issue
    import subprocess
    subprocess.run([
        "gh", "issue", "close", issue_number,
        "--reason", "completed",
    ], timeout=30)

    # Output for GitHub Actions
    with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
        f.write(f"commit_msg={msg}\n")


if __name__ == "__main__":
    main()
