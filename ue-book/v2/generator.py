"""LLM document generation (v2)."""
import os
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from . import config


def get_llm() -> ChatOpenAI:
    """Initialize LLM (OpenAI-compatible)."""
    return ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.LLM_MODEL,
        temperature=0.3,
        max_tokens=16000,
        max_retries=2,   # SDK-level retry for transient 429/5xx
        timeout=180,      # per-request timeout (generating long docs)
    )


def generate_doc(harness: str, context: str, branch: str = "") -> tuple[str, float]:
    """Generate documentation for a single plugin.

    Returns (markdown_content, duration_seconds).
    """
    llm = get_llm()

    branch_hint = f"GitHub 链接使用 {branch} 分支格式" if branch else "GitHub 链接使用对应分支格式"
    formatted_harness = harness.format(branch=branch) if branch else harness

    system_prompt = f"""你是一个 UE5 插件文档生成专家。根据提供的插件源码信息，生成完整的中文使用文档。

{formatted_harness}

重要规则：
1. 严格按照上面模板的格式输出，不要遗漏任何章节
2. 属性表必须严格遵循格式模板，包括新增的「中文名」字段
3. 中文名：是新增字段，不是为了替换原有的英文名（共存），而是根据插件的实际用途翻译为简洁中文名称（2-6字），
   不要直接翻译英文插件名。如 ADOSupport → "ADO数据库支持"
4. 用途说明必须基于源码分析，不要照抄 .uplugin 的 Description
5. 蓝图用法和 C++ 用法必须从源码中提取真实的 API
6. {branch_hint} 
7. 只输出 markdown 文档内容，不要有多余的解释"""

    user_prompt = f"请为以下 UE5 插件生成完整文档：\n\n{context}"

    start = time.time()
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])
    elapsed = time.time() - start

    return _sanitize(response.content), elapsed


def _sanitize(doc: str) -> str:
    """Strip LLM output tags that leak through (function calls, thinking, XML).

    Also strips unbalanced HTML tags that would cause VitePress build errors.
    """
    import re

    # ── Phase 1: strip known LLM leak tags (thinking, function calls) ──
    leak_tags = ["<function", "</function", "<tool_call", "</tool_call",
                 "</thinking", "</think", "<thinking", "<think"]
    if any(t in doc for t in leak_tags):
        lines = doc.split("\n")
        clean = []
        skip = False
        for line in lines:
            if any(t in line for t in ["<function", "<tool_call", "<thinking", "<think"]):
                skip = True
                continue
            if skip and any(t in line for t in ["</invoke", "</function", "</tool_call",
                                                  "</thinking", "</think"]):
                skip = False
                continue
            if not skip:
                clean.append(line)
        doc = "\n".join(clean)

    # ── Phase 2: strip unbalanced HTML tags that break VitePress ──
    # Only keep tags that are safe in markdown. Strip everything else.
    # Code blocks (```...```) are protected — tags inside them are literal.
    safe_tags = {"details", "summary", "br", "hr", "kbd", "sup", "sub"}
    tag_pattern = re.compile(r'</?(\w+)[^>]*>')

    # Split into code-block and non-code-block regions
    code_block = re.compile(r'```', re.MULTILINE)
    regions = []  # [(start, end, is_code)]
    pos = 0
    in_code = False
    for m in code_block.finditer(doc):
        if in_code:
            regions.append((pos, m.end(), True))
            pos = m.end()
            in_code = False
        else:
            if pos < m.start():
                regions.append((pos, m.start(), False))
            pos = m.start()
            in_code = True
    if pos < len(doc):
        regions.append((pos, len(doc), in_code))

    # Process non-code regions only
    to_strip = []
    opens = []
    for start, end, is_code in regions:
        if is_code:
            continue
        region_text = doc[start:end]
        for m in tag_pattern.finditer(region_text):
            full = m.group(0)
            tag = m.group(1).lower()
            abs_start = start + m.start()
            abs_end = start + m.end()
            if full.startswith("</"):
                found = False
                for i in range(len(opens) - 1, -1, -1):
                    if opens[i][0] == tag:
                        opens.pop(i)
                        found = True
                        break
                if not found:
                    to_strip.append((abs_start, abs_end))
            else:
                if tag in safe_tags:
                    opens.append((tag, abs_start))
                else:
                    to_strip.append((abs_start, abs_end))

    # Strip any remaining unclosed safe opening tags
    for tag, pos in opens:
        end_pos = doc.find('>', pos)
        if end_pos != -1:
            to_strip.append((pos, end_pos + 1))

    if to_strip:
        chars = list(doc)
        for s, e in sorted(to_strip, reverse=True):
            chars[s:e] = [''] * (e - s)
        doc = ''.join(chars)

    return doc.strip()
