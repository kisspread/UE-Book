"""LangGraph pipeline for UE5 plugin documentation generation.

Uses LangGraph StateGraph for:
- State management across scan → generate → review → summary
- Checkpointing for crash recovery
- Conditional routing (retry on review failure)
"""
import os
import time
import json
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage

from . import config
from .scanner import scan_plugin, build_context, build_module_context, build_summary_context
from .generator import get_llm


# ── State ──

class PluginState(TypedDict):
    """State for a single plugin's doc generation pipeline."""
    plugin_name: str
    category: str
    src_files: int
    info: dict                  # scan result
    modules: list[dict]         # module list from scan
    module_docs: list[dict]     # generated module docs [{name, path, content}]
    index_doc: str              # final summary
    review_passed: bool
    review_feedback: str
    attempts: int
    error: str | None
    # Result fields (populated by finalize)
    result_name: str
    result_success: bool
    result_error: str | None
    result_duration: float
    result_doc_path: str
    _start_time: float


class BatchState(TypedDict):
    """Top-level state for the batch pipeline."""
    plugins: list[dict]         # input plugin list
    batch_size: int
    results: Annotated[list[dict], operator.add]
    summary: str


# ── Helpers ──

HARNESS_CACHE = None

def _get_harness() -> str:
    global HARNESS_CACHE
    if HARNESS_CACHE is None:
        with open(config.HARNESS_PATH) as f:
            HARNESS_CACHE = f.read()
    return HARNESS_CACHE


def _sanitize(doc: str) -> str:
    tags = [
        "<function",
        "</function",
        "<tool_call",
        "</tool_call",
    ]
    if not any(t in doc for t in tags):
        return doc
    lines = doc.split('\n')
    clean = []
    skip = False
    for line in lines:
        if '<function' in line or '<tool_call' in line:
            skip = True
            continue
        if skip and ('</invoke' in line or '</function' in line):
            skip = False
            continue
        if not skip:
            clean.append(line)
    return '\n'.join(clean).strip()


SYSTEM_PROMPT = """你是一个 UE5 插件文档生成专家。根据提供的插件源码信息，生成完整的中文使用文档。

{harness}

重要规则：
1. 严格按照上面模板的格式输出，不要遗漏任何章节
2. 属性表必须严格遵循格式模板
3. 用途说明必须基于源码分析，不要照抄 .uplugin 的 Description
4. 蓝图用法和 C++ 用法必须从源码中提取真实的 API
5. GitHub 链接使用对应分支格式
6. 只输出 markdown 文档内容，不要有多余的解释"""


def _call_llm(user_prompt: str) -> tuple[str, float]:
    llm = get_llm()
    harness = _get_harness().format(branch="5.7")
    start = time.time()
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT.format(harness=harness)),
        HumanMessage(content=user_prompt),
    ])
    return _sanitize(response.content), time.time() - start


# ── Graph Nodes ──

def scan_node(state: PluginState) -> PluginState:
    """Scan plugin source code."""
    info = scan_plugin(
        state["plugin_name"], state["category"],
        config.UE_SOURCE, config.GIT_MAIN_REPO,
    )
    if info.get("error"):
        state["error"] = info["error"]
        return state

    state["info"] = info
    state["modules"] = info.get("modules", [])
    state["module_docs"] = []
    state["attempts"] = 0
    return state


def generate_modules_node(state: PluginState) -> PluginState:
    """Generate per-module docs (or single doc for small plugins)."""
    if state.get("error"):
        return state

    info = state["info"]
    modules = state["modules"]
    out_dir = os.path.join(config.PROJECT_DIR, "docs", "5.7", state["category"], state["plugin_name"])
    os.makedirs(out_dir, exist_ok=True)

    if len(modules) <= 1:
        # Single module: generate one doc
        ctx = build_context(info, config.UE_SOURCE, config.GIT_MAIN_REPO)
        doc, elapsed = _call_llm(f"请为以下 UE5 插件生成完整文档：\n\n{ctx}")
        path = os.path.join(out_dir, "index.md")
        with open(path, "w") as f:
            f.write(doc)
        state["module_docs"] = [{"name": state["plugin_name"], "type": "single", "path": "index.md"}]
        print(f"    📄 index.md ({elapsed:.0f}s)")
    else:
        # Multi-module: one doc per module
        for mod in modules:
            ctx = build_module_context(info, mod, config.UE_SOURCE, config.GIT_MAIN_REPO)
            doc, elapsed = _call_llm(f"请为以下 UE5 插件模块生成详细文档：\n\n{ctx}")
            filename = f"{mod['name']}.md"
            path = os.path.join(out_dir, filename)
            with open(path, "w") as f:
                f.write(doc)
            state["module_docs"].append({
                "name": mod["name"], "type": mod["type"], "path": filename,
            })
            print(f"    📄 {filename} ({elapsed:.0f}s)")

    return state


def review_node(state: PluginState) -> PluginState:
    """Review generated docs for completeness."""
    if state.get("error"):
        state["review_passed"] = True  # skip review on error
        return state

    state["attempts"] = state.get("attempts", 0) + 1
    out_dir = os.path.join(config.PROJECT_DIR, "docs", "5.7", state["category"], state["plugin_name"])

    # Collect doc summaries for review
    doc_summaries = []
    for md in state["module_docs"]:
        path = os.path.join(out_dir, md["path"])
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            # Check basic completeness
            has_table = "| 属性 |" in content or "|---|" in content
            has_usage = "## 用途" in content
            has_modules = "## 模块" in content or "## 依赖" in content
            line_count = len(content.split("\n"))
            doc_summaries.append({
                "name": md["name"],
                "lines": line_count,
                "has_table": has_table,
                "has_usage": has_usage,
                "has_modules": has_modules,
            })

    # Simple rule-based review
    issues = []
    for ds in doc_summaries:
        if ds["lines"] < 50:
            issues.append(f"{ds['name']}: 文档太短 ({ds['lines']} lines)")
        if not ds["has_table"]:
            issues.append(f"{ds['name']}: 缺少属性表")
        if not ds["has_usage"]:
            issues.append(f"{ds['name']}: 缺少用途章节")

    # Multi-module: check all modules covered (skip if too many modules)
    if len(state["modules"]) > 1 and len(state["modules"]) <= 15:
        expected = {m["name"] for m in state["modules"]}
        actual = {md["name"] for md in state["module_docs"]}
        missing = expected - actual
        if missing:
            issues.append(f"缺少模块文档: {', '.join(missing)}")

    if issues:
        state["review_passed"] = False
        state["review_feedback"] = "; ".join(issues)
        print(f"    ⚠️  Review failed: {state['review_feedback'][:100]}")
    else:
        state["review_passed"] = True
        state["review_feedback"] = ""

    return state


def generate_index_node(state: PluginState) -> PluginState:
    """Generate summary index.md for multi-module plugins."""
    if state.get("error") or len(state["modules"]) <= 1:
        return state

    info = state["info"]
    ctx = build_summary_context(info, state["module_docs"], config.UE_SOURCE)
    doc, elapsed = _call_llm(f"请为以下 UE5 插件生成汇总 index.md：\n\n{ctx}")

    out_dir = os.path.join(config.PROJECT_DIR, "docs", "5.7", state["category"], state["plugin_name"])
    path = os.path.join(out_dir, "index.md")
    with open(path, "w") as f:
        f.write(doc)
    print(f"    📋 index.md ({elapsed:.0f}s)")
    return state


def finalize_node(state: PluginState) -> dict:
    """Collect result."""
    start = state.get("_start_time", time.time())
    return {
        "result_name": state["plugin_name"],
        "result_success": not bool(state.get("error")),
        "result_error": state.get("error"),
        "result_duration": time.time() - start,
        "result_doc_path": os.path.join("docs", "5.7", state["category"], state["plugin_name"]),
    }


# ── Routing ──

def route_after_scan(state: PluginState) -> str:
    if state.get("error"):
        return "finalize"
    return "generate_modules"


def route_after_review(state: PluginState) -> str:
    if state.get("error"):
        return "finalize"
    if state["review_passed"]:
        return "generate_index" if len(state["modules"]) > 1 else "finalize"
    if state["attempts"] < 2:
        return "generate_modules"  # retry
    return "generate_index" if len(state["modules"]) > 1 else "finalize"  # give up


# ── Build Single-Plugin Graph ──

def build_plugin_graph():
    """Build the LangGraph for a single plugin's lifecycle."""
    g = StateGraph(PluginState)

    g.add_node("scan", scan_node)
    g.add_node("generate_modules", generate_modules_node)
    g.add_node("review", review_node)
    g.add_node("generate_index", generate_index_node)
    g.add_node("finalize", finalize_node)

    g.add_edge(START, "scan")
    g.add_conditional_edges("scan", route_after_scan, {
        "generate_modules": "generate_modules",
        "finalize": "finalize",
    })
    g.add_edge("generate_modules", "review")
    g.add_conditional_edges("review", route_after_review, {
        "generate_index": "generate_index",
        "generate_modules": "generate_modules",  # retry
        "finalize": "finalize",
    })
    g.add_edge("generate_index", "finalize")
    g.add_edge("finalize", END)

    return g.compile()


plugin_graph = build_plugin_graph()


# ── Batch Runner ──

def run_pipeline(plugins: list[dict], batch_size: int = 3) -> dict:
    """Run the doc generation pipeline with batching and LangGraph state."""
    import asyncio

    async def _run():
        sem = asyncio.Semaphore(batch_size)
        results = []

        async def _process_one(plugin):
            async with sem:
                loop = asyncio.get_event_loop()
                initial_state = {
                    "plugin_name": plugin["name"],
                    "category": plugin.get("_output_category", plugin["category"]),
                    "src_files": plugin.get("src_files", 0),
                    "info": {},
                    "modules": [],
                    "module_docs": [],
                    "index_doc": "",
                    "review_passed": False,
                    "review_feedback": "",
                    "attempts": 0,
                    "error": None,
                    "_start_time": time.time(),
                }
                result = await loop.run_in_executor(
                    None, lambda: plugin_graph.invoke(initial_state)
                )
                # Extract result from state
                out = {
                    "name": result.get("result_name", result.get("plugin_name")),
                    "success": result.get("result_success", not bool(result.get("error"))),
                    "error": result.get("result_error", result.get("error")),
                    "duration_seconds": result.get("result_duration", 0),
                    "doc_path": result.get("result_doc_path", ""),
                }
                status = "✅" if out["success"] else "❌"
                dur = f"{out['duration_seconds']:.0f}s"
                print(f"  {status} {out['name']} ({dur})")
                if out.get("error"):
                    print(f"     Error: {out['error'][:120]}")
                return out

        tasks = [_process_one(p) for p in plugins]
        results = await asyncio.gather(*tasks)
        return list(results)

    print(f"\nGenerating docs for {len(plugins)} plugins (batch_size={batch_size})...\n")
    results = asyncio.run(_run())

    success = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    total_time = sum(r["duration_seconds"] for r in results)

    summary = f"Done: {success}/{len(plugins)} success, {failed} failed, total {total_time:.0f}s"
    print(f"\n{summary}")

    return {"results": results, "summary": summary}
