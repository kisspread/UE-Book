#!/usr/bin/env python3
"""Generate monthly digests from local weekly reports.

The upstream Monthly Report discussions are the primary source, but they are
not guaranteed to continue forever.  This script finds completed months that
have weekly reports but no monthly report and synthesizes a monthly summary.

It uses the configured LLM when available and falls back to a deterministic
merge of the weekly report sections if the LLM is unavailable.

Usage:
  python3 ue-book/scripts/monthly_digest.py
  python3 ue-book/scripts/monthly_digest.py --dry-run
  python3 ue-book/scripts/monthly_digest.py --month 2026-10
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
UPDATES_DIR = PROJECT_DIR / "docs" / "updates"

WEEKLY_RE = re.compile(r"^(\d{4}-\d{2})-\d{2}\.md$")
MONTHLY_RE = re.compile(r"^\d{4}-\d{2}\.md$")

SECTION_ORDER = [
    "✨ 新功能",
    "🚀 重大变更",
    "⚡ 性能优化",
    "🐛 Bug 修复",
    "🔧 API 变更",
    "⚠️ 废弃预告",
]

SECTION_MARKERS = {
    "新功能": "✨ 新功能",
    "重大变更": "🚀 重大变更",
    "性能优化": "⚡ 性能优化",
    "Bug 修复": "🐛 Bug 修复",
    "API 变更": "🔧 API 变更",
    "废弃预告": "⚠️ 废弃预告",
}


def current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def weekly_files_for_month(month: str) -> list[Path]:
    return sorted(
        p for p in UPDATES_DIR.glob(f"{month}-*.md")
        if WEEKLY_RE.match(p.name)
    )


def monthly_exists(month: str) -> bool:
    return (UPDATES_DIR / f"{month}.md").exists()


def find_missing_months(explicit_month: str | None = None) -> list[str]:
    if explicit_month:
        return [] if monthly_exists(explicit_month) else [explicit_month]

    existing = {
        p.stem for p in UPDATES_DIR.glob("????-??.md")
        if MONTHLY_RE.match(p.name)
    }
    weekly_months = {
        m.group(1) for p in UPDATES_DIR.glob("????-??-??.md")
        if (m := WEEKLY_RE.match(p.name))
    }
    this_month = current_month()
    return sorted(
        month for month in weekly_months
        if month not in existing and month < this_month and weekly_files_for_month(month)
    )


def strip_frontmatter(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)
    text = re.sub(r"^```(?:markdown)?\s*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text)
    return text.strip()


def split_sections(markdown: str) -> OrderedDict[str, list[str]]:
    """Extract H2 sections and their bullet lines from a report."""
    text = strip_frontmatter(markdown)
    # Drop the H1 title and YAML-like leftovers.
    lines = text.splitlines()
    sections: OrderedDict[str, list[str]] = OrderedDict()
    current = "其他"
    for line in lines:
        if line.startswith("## "):
            heading = line[3:].strip()
            # Normalize headings such as "## ✨ 新功能" and "## 新功能"
            matched = None
            for marker in SECTION_MARKERS:
                if marker in heading:
                    matched = SECTION_MARKERS[marker]
                    break
            current = matched or heading
            sections.setdefault(current, [])
            continue
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            # Keep the bullet, but skip the bullet prefix for deduping.
            sections.setdefault(current, []).append(stripped[2:].strip())
    return sections


def _normalized_bullet(text: str) -> str:
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def deterministic_digest(month: str, reports: list[tuple[str, str]]) -> str:
    """Merge weekly bullets by section without requiring an LLM."""
    merged: OrderedDict[str, list[str]] = OrderedDict()
    seen: dict[str, set[str]] = {}

    for _slug, content in reports:
        for heading, bullets in split_sections(content).items():
            merged.setdefault(heading, [])
            seen.setdefault(heading, set())
            for bullet in bullets:
                key = _normalized_bullet(bullet)
                if not key or key in seen[heading]:
                    continue
                seen[heading].add(key)
                merged[heading].append(bullet)

    year, month_num = month.split("-")
    lines = [
        "---",
        f"title: '{year}年{int(month_num)}月引擎更新月报'",
        f"date: '{month}-28'",
        "---",
        "",
        f"# {year}年{int(month_num)}月引擎更新月报",
        "",
        "> 上游月度报告暂未发布，本期由本月本地周报自动汇总生成。",
        "",
    ]

    ordered_headings = [h for h in SECTION_ORDER if h in merged]
    ordered_headings += [h for h in merged if h not in SECTION_ORDER and h != "其他"]
    if "其他" in merged:
        ordered_headings.append("其他")

    for heading in ordered_headings:
        bullets = merged.get(heading, [])
        if not bullets:
            continue
        lines.append(f"## {heading}")
        lines.append("")
        for bullet in bullets:
            lines.append(f"- {bullet}")
        lines.append("")

    lines.extend([
        "## 📚 周报来源",
        "",
        "本期由以下周报自动合并生成：",
        "",
    ])
    for slug, _content in reports:
        lines.append(f"- [{slug}](/updates/{slug})")
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def llm_digest(month: str, reports: list[tuple[str, str]]) -> str:
    """Use the configured LLM to synthesize a concise monthly report."""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    sys.path.insert(0, str(PROJECT_DIR))
    from v2 import config

    if not config.LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY is not configured")

    year, month_num = month.split("-")
    source = "\n\n".join(
        f"### 周报 {slug}\n\n{strip_frontmatter(content)}"
        for slug, content in reports
    )
    system = f"""你是 Unreal Engine 技术编辑。
根据同一月份的多篇中文周报，合并生成一篇中文月度总结。

规则：
1. 合并重复或高度相近的内容，保留重要技术细节，不虚构事实。
2. 技术术语（API 名、类名、CVar、模块名）保持英文原文。
3. 第一行必须是：`# {year}年{int(month_num)}月引擎更新月报`
4. 按以下二级标题顺序输出，无内容的章节可以省略：
   `## ✨ 新功能`
   `## 🚀 重大变更`
   `## ⚡ 性能优化`
   `## 🐛 Bug 修复`
   `## 🔧 API 变更`
   `## ⚠️ 废弃预告`
5. 最后可以增加 `## 📚 周报来源`，列出用于汇总的周报日期。
6. 只输出 Markdown，不要 YAML frontmatter，不要额外解释。"""

    llm = ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.LLM_MODEL,
        temperature=0.2,
        max_tokens=16000,
    )
    response = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=source),
    ])
    content = strip_frontmatter(str(response.content))

    expected_h1 = f"# {year}年{int(month_num)}月引擎更新月报"
    if expected_h1 not in content:
        content = f"{expected_h1}\n\n{content}"
    return content.strip() + "\n"


def build_monthly(month: str, reports: list[tuple[str, str]]) -> str:
    try:
        body = llm_digest(month, reports)
        print(f"  LLM digest generated for {month}")
    except Exception as e:
        print(f"  LLM unavailable for {month}: {e}", file=sys.stderr)
        print(f"  Falling back to deterministic weekly merge for {month}", file=sys.stderr)
        return deterministic_digest(month, reports)

    year, month_num = month.split("-")
    return (
        "---\n"
        f"title: '{year}年{int(month_num)}月引擎更新月报'\n"
        f"date: '{month}-28'\n"
        "---\n\n"
        f"{body}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate monthly reports from weekly reports")
    parser.add_argument("--dry-run", action="store_true", help="List missing months without writing files")
    parser.add_argument("--month", help="Only process one YYYY-MM month")
    args = parser.parse_args()

    months = find_missing_months(args.month)
    if not months:
        print("No missing monthly reports to generate from weekly reports.")
        return

    print("Missing monthly reports: " + ", ".join(months))
    if args.dry_run:
        for month in months:
            files = weekly_files_for_month(month)
            print(f"  {month}: {len(files)} weekly report(s): {', '.join(p.stem for p in files)}")
        return

    for month in months:
        reports = []
        for path in weekly_files_for_month(month):
            reports.append((path.stem, path.read_text(encoding="utf-8")))
        if not reports:
            continue
        print(f"Generating {month} from {len(reports)} weekly report(s)...")
        content = build_monthly(month, reports)
        output = UPDATES_DIR / f"{month}.md"
        output.write_text(content, encoding="utf-8")
        print(f"  Saved: {output} ({len(content)} chars)")


if __name__ == "__main__":
    main()
