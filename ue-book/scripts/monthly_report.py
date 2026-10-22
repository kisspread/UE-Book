#!/usr/bin/env python3
"""Monthly UE engine update report — translate from UpdateTracker.

Checks for new Monthly Highlights discussions from
pafuhana1213/UnrealEngine-UpdateTrackerReport. Translates Japanese → Chinese
via MiMo. Generates updates/YYYY-MM.md.

Usage:
  python3 ue-book/scripts/monthly_report.py              # check for new
  python3 ue-book/scripts/monthly_report.py --dry-run    # preview only
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
UPDATES_DIR = PROJECT_DIR / "docs" / "updates"
UPSTREAM_REPO = "pafuhana1213/UnrealEngine-UpdateTrackerReport"


def list_discussions() -> list[dict]:
    """List all upstream discussions, newest first.

    The old implementation scanned a fixed numeric window and returned the
    first monthly report it found. Once that report had been generated, every
    later run found the same report, skipped it because the output file already
    existed, and exited successfully. Listing the discussions instead lets us
    keep moving forward as new monthly reports are published.
    """
    discussions: list[dict] = []
    page = 1

    while page <= 20:  # safety cap: 2,000 discussions
        result = subprocess.run(
            [
                "gh", "api",
                f"repos/{UPSTREAM_REPO}/discussions"
                f"?per_page=100&page={page}",
            ],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"gh api failed while listing discussions: "
                f"{result.stderr.strip()[:500]}"
            )

        page_data = json.loads(result.stdout)
        if not isinstance(page_data, list):
            raise RuntimeError(
                "Unexpected GitHub API response while listing discussions"
            )
        discussions.extend(page_data)
        if len(page_data) < 100:
            break
        page += 1

    discussions.sort(key=lambda d: d.get("created_at", ""), reverse=True)
    return discussions


def check_new_monthly() -> dict | None:
    """Return the newest monthly report that has not been translated yet."""
    print(f"Checking {UPSTREAM_REPO} for Monthly Reports...")

    discussions = list_discussions()
    existing_months = {
        path.stem
        for path in UPDATES_DIR.glob("????-??.md")
    }

    monthly_reports = []
    for discussion in discussions:
        title = discussion.get("title", "")
        if not title.startswith("Monthly Report:"):
            continue
        year_month = extract_year_month(title)
        if not year_month:
            continue
        monthly_reports.append({
            "title": title,
            "body": discussion.get("body", ""),
            "date": discussion.get("created_at", "")[:10],
            "number": discussion.get("number"),
            "year_month": year_month,
        })

    print(f"  Found {len(monthly_reports)} monthly report(s) in discussions")

    for report in monthly_reports:
        if report["year_month"] in existing_months:
            continue
        print(
            f"  Newest unprocessed: #{report['number']} "
            f"{report['title']} ({report['date']})"
        )
        return report

    print("  No unprocessed monthly report found.")
    return None


def translate_report(body: str) -> str:
    """Translate Japanese → Chinese via MiMo."""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    sys.path.insert(0, str(PROJECT_DIR))
    from v2 import config

    llm = ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.LLM_MODEL,
        temperature=0.2,
        max_tokens=16000,
    )

    system = """你是 Unreal Engine 技术翻译专家。将以下日文引擎更新月报翻译为中文。

规则：
1. 保持原始 Markdown 格式、emoji、链接不变
2. 技术术语（API 名、类名、CVar、模块名）保持英文原文
3. 准确翻译技术概念，语气专业自然

## 标题强制规范（严格遵守）

一级标题使用：`# YYYY年M月引擎更新月报`

二级标题顺序和格式如下，不得额外添加英文括号：
- `## ✨ 新功能`
- `## 🚀 重大变更`
- `## ⚡ 性能优化`
- `## 🐛 Bug 修复`
- `## 🔧 API 变更`
- `## ⚠️ 废弃预告`
- `## 📌 重点关注模块`

只输出翻译后的 Markdown，不要多余解释。"""

    print("  Translating via MiMo...")
    response = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=body),
    ])
    return response.content


def extract_year_month(title: str) -> str:
    """Extract YYYY-MM from a title like 'Monthly Report: 2026-04'."""
    import re
    m = re.search(r"(\d{4}-\d{2})", title)
    return m.group(1) if m else ""


def main():
    parser = argparse.ArgumentParser(description="Translate monthly UE update report")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        monthly = check_new_monthly()
    except (RuntimeError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
        print(f"Failed to check monthly reports: {e}", file=sys.stderr)
        sys.exit(1)
    if not monthly:
        return

    year_month = monthly["year_month"]
    output_path = UPDATES_DIR / f"{year_month}.md"

    if output_path.exists():
        print(f"  Skipping: {output_path} already exists.")
        return

    if args.dry_run:
        print(f"\nDry run — would translate #{monthly['number']} ({len(monthly['body'])} chars)")
        print(f"Output: {output_path}")
        return

    print(f"\nTranslating {year_month}...")
    translated = translate_report(monthly["body"])

    chinese_title = f"{year_month[:4]}年{int(year_month[5:]):d}月引擎更新月报"
    content = f"---\ntitle: '{chinese_title}'\ndate: '{year_month}-28'\n---\n\n{translated}"

    UPDATES_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"  Saved: {output_path} ({len(content)} chars)")


if __name__ == "__main__":
    main()
