#!/usr/bin/env python3
"""Weekly UE plugin update report.

Fetches commits from EpicGames/UnrealEngine 5.8 branch touching Engine/Plugins/,
filters noise, feeds to MiMo for analysis, generates updates/YYYY-Www.md.

Usage:
  python3 ue-book/scripts/weekly_report.py                     # past 7 days
  python3 ue-book/scripts/weekly_report.py --days 14           # past 14 days
  python3 ue-book/scripts/weekly_report.py --dry-run           # show only
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = PROJECT_DIR / "prompts" / "report_prompt.md"
UPDATES_DIR = PROJECT_DIR / "docs" / "updates"

NOISE_AUTHORS = {"buildmachine", "UnrealBot"}
NOISE_PATTERNS = [
    "Localization Automation", "LocalizationData", "loc automation",
    "[Backout]", "Fix non-unity build", "PR #", "Localization Fixes",
    "fix typo", "fix build", "Fix compile error",
]


def fetch_commits(branch: str, since: str) -> list[dict]:
    """Fetch commits touching Engine/Plugins/ via commits API. Parse JSON in Python."""
    print(f"Fetching commits from {branch}, path=Engine/Plugins, since={since}...")

    url = (
        f"repos/EpicGames/UnrealEngine/commits"
        f"?sha={branch}&path=Engine/Plugins&since={since}T00:00:00Z&per_page=100"
    )
    result = subprocess.run(
        ["gh", "api", url],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        print(f"gh api error: {result.stderr}")
        return []

    try:
        raw = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to parse API response")
        return []

    commits = []
    for c in raw:
        msg = c["commit"]["message"].split("\n")[0]
        commits.append({
            "sha": c["sha"][:7],
            "date": c["commit"]["author"]["date"][:10],
            "author": c["commit"]["author"]["name"],
            "message": msg,
        })

    print(f"  Raw: {len(commits)} commits")
    return commits


def filter_commits(commits: list[dict]) -> list[dict]:
    """Filter out noise."""
    filtered = []
    for c in commits:
        author = c.get("author", "").lower()
        msg = c.get("message", "")

        if author in NOISE_AUTHORS:
            continue
        if any(p.lower() in msg.lower() for p in NOISE_PATTERNS):
            continue
        if msg.lower().startswith("merge"):
            continue

        filtered.append(c)

    print(f"  Meaningful: {len(filtered)} commits")
    return filtered


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call MiMo via langchain."""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    sys.path.insert(0, str(PROJECT_DIR))
    from v2 import config

    llm = ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.LLM_MODEL,
        temperature=0.3,
        max_tokens=16000,
    )
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])
    return response.content


def build_commit_data(commits: list[dict]) -> str:
    """Build commit list text for the prompt."""
    lines = []
    for c in commits:
        lines.append(
            f"---\n"
            f"Commit: {c['sha']}\n"
            f"Author: {c['author']}\n"
            f"Date: {c['date']}\n"
            f"Message: {c['message']}\n"
        )
    return "\n".join(lines)


def get_week_label() -> str:
    """Get ISO week label like '2026-W19'."""
    now = datetime.now()
    iso = now.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def main():
    parser = argparse.ArgumentParser(description="Generate weekly UE plugin update report")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%Y-%m-%d")
    commits = fetch_commits("5.8", since)
    commits = filter_commits(commits)

    if not commits:
        print("No meaningful commits this week.")
        return

    week_label = get_week_label()
    output_path = UPDATES_DIR / f"{week_label}.md"

    if args.dry_run:
        print(f"\nDry run — {len(commits)} commits for {week_label}:")
        for c in commits:
            print(f"  {c['date']} {c['sha']} {c['author'][:20]}: {c['message'][:80]}")
        print(f"Output: {output_path}")
        return

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    commit_data = build_commit_data(commits)

    system_prompt = f"""你是 Unreal Engine 技术文档专家。根据提供的提交信息，生成中文周报。

{prompt_template}

## 🔥 最大亮点
从所有提交中挑选 2-3 个最重要的变更，放在报告最前面，用一段话解释为什么重要。

## 剩余内容
按分类输出（新功能、重大变更、性能优化、Bug 修复、API 变更、废弃预告）。
给报告加上 YAML frontmatter: title '{week_label} 引擎插件周报', date '{datetime.now().date()}'"""

    print(f"\nGenerating {week_label} report ({len(commits)} commits)...")
    report = call_llm(system_prompt, commit_data)

    UPDATES_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Saved: {output_path} ({len(report)} chars)")


if __name__ == "__main__":
    main()
