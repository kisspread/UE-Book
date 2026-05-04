#!/usr/bin/env python3
"""Rewrite 近期更新 + 维护评价 sections using LLM with real commit data."""
import json, subprocess, os, re, time, sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "5.8")
BRANCH = "5.8"
REPO = "EpicGames/UnrealEngine"

with open("/tmp/ue58_plugin_paths.json") as f:
    uplugin_map = json.load(f)


def get_commits(path, count=5):
    url = f"repos/{REPO}/commits?sha={BRANCH}&path={quote(path, safe='')}&per_page={count}"
    r = subprocess.run(["gh", "api", url], capture_output=True, text=True, timeout=30)
    data = json.loads(r.stdout)
    if not isinstance(data, list): return []
    return [{"sha": c["sha"][:8], "date": c["commit"]["committer"]["date"][:10],
             "message": c["commit"]["message"].split("\n")[0][:120]} for c in data]


def rewrite_section(commits, plugin_name):
    """Use LLM to translate commits and write maintenance evaluation."""
    from v2.generator import get_llm
    from langchain_core.messages import SystemMessage, HumanMessage

    commit_text = "\n".join(f"- {c['date']} `{c['sha']}` {c['message']}" for c in commits)

    prompt = f"""你是一个 UE5 插件文档维护者。根据以下 git commit 记录，用中文重写"维护状态"章节。

Plugin: {plugin_name}
Branch: {BRANCH}

真实 commit 记录：
{commit_text}

请输出以下格式（不要有其他内容）：

### 近期更新

- 日期 `hash` 翻译后的中文描述
- ...（列出所有 commit）

### 维护评价

根据 commit 频率、时间跨度、内容类型，点评该插件的维护状态（活跃/稳定/停滞/实验性等）。2-3 句话即可。"""

    llm = get_llm()
    resp = llm.invoke([HumanMessage(content=prompt)])
    return resp.content.strip()


def fix_doc(filepath, commits, plugin_name):
    with open(filepath) as f:
        content = f.read()

    # Find and replace everything from "### 近期更新" to before "## 相关链接" or end
    pattern = r'(### 近期更新\s*\n)(?:.*?\n)*?(?=\n## 相关链接|\n## |\Z)'
    m = re.search(pattern, content, re.DOTALL)
    if not m:
        return False

    new_section = rewrite_section(commits, plugin_name)
    content = content[:m.start()] + new_section + "\n" + content[m.end():]

    with open(filepath, "w") as f:
        f.write(content)
    return True


def main():
    fixed = 0
    for size in ["small", "medium", "large", "xlarge"]:
        size_dir = os.path.join(DOCS_DIR, size)
        if not os.path.isdir(size_dir): continue
        for name in sorted(os.listdir(size_dir)):
            idx = os.path.join(size_dir, name, "index.md")
            if not os.path.exists(idx): continue
            with open(idx) as f:
                content = f.read()

            # Only fix docs with raw English commits
            if not re.search(r'### 近期更新\s*\n\s*-\s*\d{4}-\d{2}-\d{2}\s+`[a-f0-9]{7,8}`\s+[A-Za-z]', content):
                continue

            ue_path = uplugin_map.get(name, "")
            if not ue_path: continue

            commits = get_commits(ue_path)
            if not commits: continue

            print(f"  {name}...", end=" ", flush=True)
            try:
                if fix_doc(idx, commits, name):
                    print(f"✅")
                    fixed += 1
                else:
                    print("skipped")
            except Exception as e:
                print(f"❌ {e}")
            time.sleep(0.5)

    print(f"\nDone: {fixed} docs rewritten")


if __name__ == "__main__":
    main()
