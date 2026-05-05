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
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
UPDATES_DIR = PROJECT_DIR / "docs" / "updates"
UPSTREAM_REPO = "pafuhana1213/UnrealEngine-UpdateTrackerReport"

# Last known monthly report: #332 (2026-03), #323 (2026-04) was found manually
LAST_KNOWN = 332


def check_new_monthly() -> dict | None:
    """Scan discussion numbers > LAST_KNOWN for a new Monthly Report."""
    print(f"Checking for new Monthly Reports (starting from #{LAST_KNOWN + 1})...")

    for num in range(LAST_KNOWN + 1, LAST_KNOWN + 100):
        result = subprocess.run(
            ["gh", "api", f"repos/{UPSTREAM_REPO}/discussions/{num}"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            continue  # 404, skip

        d = json.loads(result.stdout)
        title = d.get("title", "")
        if title.startswith("Monthly Report:"):
            print(f"  Found: #{num} {title} ({d['created_at'][:10]})")
            return {
                "title": title,
                "body": d.get("body", ""),
                "date": d["created_at"][:10],
                "number": num,
            }

    print("  No new monthly report found.")
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
4. 只输出翻译后的 Markdown，不要多余解释"""

    print("  Translating via MiMo...")
    response = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=body),
    ])
    return response.content


def extract_year_month(title: str) -> str:
    """Extract YYYY-MM from title like 'Monthly Report: 2026-04'."""
    import re
    m = re.search(r"(\d{4}-\d{2})", title)
    if m:
        return m.group(1)
    return datetime.now().strftime("%Y-%m")


def main():
    parser = argparse.ArgumentParser(description="Translate monthly UE update report")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    monthly = check_new_monthly()
    if not monthly:
        return

    year_month = extract_year_month(monthly["title"])
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
