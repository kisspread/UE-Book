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
    )


def generate_doc(harness: str, context: str, branch: str = "") -> tuple[str, float]:
    """Generate documentation for a single plugin.

    Returns (markdown_content, duration_seconds).
    """
    llm = get_llm()

    branch_hint = f"GitHub 链接使用 {branch} 分支格式" if branch else "GitHub 链接使用对应分支格式"

    system_prompt = f"""你是一个 UE5 插件文档生成专家。根据提供的插件源码信息，生成完整的中文使用文档。

{harness}

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
    """Strip LLM output tags that leak through."""
    tags = ["<function", "</function", "<tool_call", "</tool_call"]
    if not any(t in doc for t in tags):
        return doc
    lines = doc.split("\n")
    clean = []
    skip = False
    for line in lines:
        if "<function" in line or "<tool_call" in line:
            skip = True
            continue
        if skip and ("</invoke" in line or "</function" in line):
            skip = False
            continue
        if not skip:
            clean.append(line)
    return "\n".join(clean).strip()
