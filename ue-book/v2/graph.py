"""LangGraph pipeline for v2 (GitHub API-based)."""
import os
import time
import json
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage

from . import config
from . import scanner
from . import manifest as manifest_mod
from .generator import get_llm, _sanitize


# ── State ──

class PluginState(TypedDict):
    plugin_name: str
    plugin_path: str          # Engine/Plugins/...
    branch: str               # e.g. "5.8"
    version: str              # e.g. "5.8"
    info: dict                # scan result
    modules: list[dict]
    module_docs: list[dict]   # [{name, path, content}]
    index_doc: str
    review_passed: bool
    review_feedback: str
    attempts: int
    error: str | None
    # Result
    result_name: str
    result_success: bool
    result_error: str | None
    result_duration: float
    result_doc_path: str
    result_size: str
    _start_time: float


# ── Helpers ──

HARNESS_CACHE = None

def _get_harness() -> str:
    global HARNESS_CACHE
    if HARNESS_CACHE is None:
        with open(config.HARNESS_PATH) as f:
            HARNESS_CACHE = f.read()
    return HARNESS_CACHE


SYSTEM_PROMPT = """你是一个 UE5 插件文档生成专家。根据提供的插件源码信息，生成完整的中文使用文档。

{harness}

重要规则：
1. 严格按照上面模板的格式输出，不要遗漏任何章节
2. 属性表必须严格遵循格式模板
3. 用途说明必须基于源码分析，不要照抄 .uplugin 的 Description
4. 蓝图用法和 C++ 用法必须从源码中提取真实的 API
5. GitHub 链接使用 {branch} 分支格式
6. 只输出 markdown 文档内容，不要有多余的解释"""


def _call_llm(user_prompt: str, branch: str, max_retries: int = 2) -> tuple[str, float]:
    llm = get_llm()
    harness = _get_harness().replace('{branch}', branch)
    system = SYSTEM_PROMPT.format(harness=harness, branch=branch)

    last_exc = None
    for attempt in range(1 + max_retries):
        try:
            start = time.time()
            response = llm.invoke([
                SystemMessage(content=system),
                HumanMessage(content=user_prompt),
            ])
            return _sanitize(response.content), time.time() - start
        except Exception as e:
            last_exc = e
            if attempt < max_retries:
                wait = 10 * (2 ** attempt)  # 10s → 20s
                print(f"    ⚠️ LLM error, retry {attempt+1}/{max_retries} in {wait}s: {e}")
                time.sleep(wait)
    # last_exc is always set here — the loop reaches this line only after
    # all attempts exhausted, which means at least one exception was caught
    raise last_exc  # type: ignore


# ── Graph Nodes ──

def scan_node(state: PluginState) -> PluginState:
    """Scan plugin source code via GitHub API."""
    try:
        info = scanner.scan_plugin(
            state["plugin_name"], state["plugin_path"], state["branch"],
        )
        if info.get("error"):
            state["error"] = info["error"]
            return state
        state["info"] = info
        state["modules"] = info.get("modules", [])
        state["module_docs"] = []
        state["attempts"] = 0
    except Exception as e:
        state["error"] = str(e)
    return state


def generate_modules_node(state: PluginState) -> PluginState:
    """Generate per-module docs (or single doc for small plugins)."""
    if state.get("error"):
        return state

    info = state["info"]
    branch = state["branch"]
    version = state["version"]
    out_dir = os.path.join(config.PROJECT_DIR, "docs", version, "small", state["plugin_name"])
    os.makedirs(out_dir, exist_ok=True)

    if len(state["modules"]) <= 1:
        ctx = scanner.build_context(info, branch)
        doc, elapsed = _call_llm(f"请为以下 UE5 插件生成完整文档：\n\n{ctx}", branch)
        path = os.path.join(out_dir, "index.md")
        with open(path, "w") as f:
            f.write(doc)
        state["module_docs"] = [{"name": state["plugin_name"], "type": "single", "path": "index.md"}]
        print(f"    📄 index.md ({elapsed:.0f}s)")
    else:
        for mod in state["modules"]:
            ctx = scanner.build_module_context(info, mod, branch)
            doc, elapsed = _call_llm(f"请为以下 UE5 插件模块生成详细文档：\n\n{ctx}", branch)
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
        state["review_passed"] = True
        return state

    state["attempts"] = state.get("attempts", 0) + 1
    version = state["version"]
    out_dir = os.path.join(config.PROJECT_DIR, "docs", version, "small", state["plugin_name"])

    issues = []
    for md in state["module_docs"]:
        path = os.path.join(out_dir, md["path"])
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            has_table = "| 属性 |" in content or "|---|" in content
            has_usage = "## 用途" in content
            line_count = len(content.split("\n"))
            if line_count < 50:
                issues.append(f"{md['name']}: 文档太短 ({line_count} lines)")
            if not has_table:
                issues.append(f"{md['name']}: 缺少属性表")
            if not has_usage:
                issues.append(f"{md['name']}: 缺少用途章节")

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
    branch = state["branch"]
    version = state["version"]
    ctx = scanner.build_summary_context(info, state["module_docs"])
    doc, elapsed = _call_llm(f"请为以下 UE5 插件生成汇总 index.md：\n\n{ctx}", branch)

    out_dir = os.path.join(config.PROJECT_DIR, "docs", version, "small", state["plugin_name"])
    path = os.path.join(out_dir, "index.md")
    with open(path, "w") as f:
        f.write(doc)
    print(f"    📋 index.md ({elapsed:.0f}s)")
    return state


def finalize_node(state: PluginState) -> dict:
    """Collect result."""
    start = state.get("_start_time", time.time())
    size = manifest_mod.categorize(state.get("info", {}).get("src_files", 0))

    # Move docs to correct size directory if needed
    version = state["version"]
    src_dir = os.path.join(config.PROJECT_DIR, "docs", version, "small", state["plugin_name"])
    dst_dir = os.path.join(config.PROJECT_DIR, "docs", version, size, state["plugin_name"])
    if size != "small" and os.path.exists(src_dir) and not os.path.exists(dst_dir):
        os.makedirs(os.path.dirname(dst_dir), exist_ok=True)
        os.rename(src_dir, dst_dir)

    return {
        "result_name": state["plugin_name"],
        "result_success": not bool(state.get("error")),
        "result_error": state.get("error"),
        "result_duration": time.time() - start,
        "result_doc_path": f"docs/{version}/{size}/{state['plugin_name']}",
        "result_size": size,
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
        return "generate_modules"
    return "generate_index" if len(state["modules"]) > 1 else "finalize"


# ── Build Graph ──

def build_plugin_graph():
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
        "generate_modules": "generate_modules",
        "finalize": "finalize",
    })
    g.add_edge("generate_index", "finalize")
    g.add_edge("finalize", END)
    return g.compile()


plugin_graph = build_plugin_graph()


# ── Runner ──

def run_pipeline(plugins: list[dict], version: str, batch_size: int = 3) -> list[dict]:
    """Run doc generation for a list of plugins."""
    import asyncio

    progress_path = config.PROGRESS_PATH

    async def _run():
        sem = asyncio.Semaphore(batch_size)

        async def _process_one(plugin):
            async with sem:
                loop = asyncio.get_event_loop()
                initial_state = {
                    "plugin_name": plugin["name"],
                    "plugin_path": plugin["path"],
                    "branch": version,
                    "version": version,
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
                try:
                    result = await loop.run_in_executor(
                        None, lambda: plugin_graph.invoke(initial_state)
                    )
                    out = {
                        "name": result.get("result_name", result.get("plugin_name")),
                        "success": result.get("result_success", not bool(result.get("error"))),
                        "error": result.get("result_error", result.get("error")),
                        "duration_seconds": result.get("result_duration", 0),
                        "doc_path": result.get("result_doc_path", ""),
                        "size": result.get("result_size", "small"),
                    }
                except Exception as e:
                    out = {
                        "name": plugin["name"],
                        "success": False,
                        "error": str(e),
                        "duration_seconds": time.time() - initial_state["_start_time"],
                        "doc_path": "",
                        "size": "small",
                    }
                status = "✅" if out["success"] else "❌"
                dur = f"{out['duration_seconds']:.0f}s"
                print(f"  {status} {out['name']} ({dur})")
                if out.get("error"):
                    print(f"     Error: {out['error'][:120]}")
                return out

        tasks = [_process_one(p) for p in plugins]
        results = []
        start_t = time.time()

        for coro in asyncio.as_completed(tasks):
            out = await coro
            results.append(out)
            # Incremental progress save — atomic via rename
            progress = {
                "version": version,
                "results": results,
                "elapsed": time.time() - start_t,
                "complete": False,
            }
            tmp = progress_path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
            os.replace(tmp, progress_path)

        return results

    print(f"\nGenerating docs for {len(plugins)} plugins (batch_size={batch_size})...\n")
    results = asyncio.run(_run())

    # Mark complete
    _mark_progress_complete(progress_path)
    return results


def _mark_progress_complete(progress_path: str):
    """Set complete=True on the progress file after successful finish."""
    if os.path.exists(progress_path):
        with open(progress_path) as f:
            data = json.load(f)
        data["complete"] = True
        tmp = progress_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, progress_path)
