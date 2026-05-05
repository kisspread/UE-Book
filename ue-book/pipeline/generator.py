"""LLM document generation."""
import os
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from . import config


def get_llm() -> ChatOpenAI:
    """Initialize MiMo LLM."""
    return ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.LLM_MODEL,
        temperature=0.3,
        max_tokens=16000,
    )


def generate_doc(harness: str, context: str) -> tuple[str, float]:
    """Generate documentation for a single plugin.
    
    Returns (markdown_content, duration_seconds).
    """
    llm = get_llm()
    
    formatted_harness = harness.format(branch="5.7")
    
    system_prompt = f"""你是一个 UE5 插件文档生成专家。根据提供的插件源码信息，生成完整的中文使用文档。

{formatted_harness}

重要规则：
1. 严格按照上面模板的格式输出，不要遗漏任何章节
2. 属性表必须严格遵循格式模板，特别是默认启用、包含内容、年龄标签的写法
3. 用途说明必须基于源码分析，不要照抄 .uplugin 的 Description
4. 蓝图用法和 C++ 用法必须从源码中提取真实的 API
5. GitHub 链接使用对应分支格式
6. 只输出 markdown 文档内容，不要有多余的解释"""

    user_prompt = f"请为以下 UE5 插件生成完整文档：\n\n{context}"

    start = time.time()
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])
    elapsed = time.time() - start
    
    return response.content, elapsed
