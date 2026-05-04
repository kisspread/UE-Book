"""Source code scanning for UE5 plugins."""
import os
import subprocess
import json
import re


def scan_plugin(plugin_name: str, category: str, ue_source: str, git_repo: str) -> dict:
    """Scan a plugin and return structured info."""
    plugin_path = _find_plugin_path(plugin_name, ue_source)
    if not plugin_path:
        return {"error": f"Plugin {plugin_name} not found"}

    src_files = _count_src_files(plugin_path)
    modules = _extract_modules(plugin_path)
    created = _get_creation_time(plugin_path, git_repo, plugin_name)
    uplugin = _read_uplugin(plugin_path)

    return {
        "name": plugin_name,
        "category": category,
        "path": plugin_path,
        "src_files": src_files,
        "modules": modules,
        "created": created,
        "uplugin": uplugin,
    }


def build_context(info: dict, ue_source: str, git_repo: str) -> str:
    """Build full plugin context for single-doc generation."""
    lines = _common_header(info, ue_source)

    # All headers (for single-doc mode)
    for h in _get_key_headers(info["path"], max_files=30):
        rel = os.path.relpath(h, ue_source)
        content = _read_file_safe(h, max_lines=80)
        lines.append(f"### {rel}")
        lines.append(f"```cpp\n{content}\n```")
        lines.append("")

    log = _get_git_log(info["path"], git_repo, count=5)
    if log:
        lines.append("## Recent git history")
        lines.append(f"```\n{log}\n```")

    return "\n".join(lines)


def build_module_context(info: dict, module: dict, ue_source: str, git_repo: str) -> str:
    """Build context for a single module within a plugin."""
    lines = _common_header(info, ue_source)

    lines.append(f"## 当前模块: {module['name']} ({module['type']})")
    lines.append(f"Build.cs: {module['path']}")
    if module.get("deps"):
        lines.append(f"Dependencies: {', '.join(module['deps'])}")
    lines.append("")

    # Only headers from this module's directory
    mod_dir = os.path.dirname(module["path"])
    lines.append("## 本模块头文件")
    for h in _get_key_headers(mod_dir, max_files=40):
        rel = os.path.relpath(h, ue_source)
        content = _read_file_safe(h, max_lines=100)
        lines.append(f"### {rel}")
        lines.append(f"```cpp\n{content}\n```")
        lines.append("")

    log = _get_git_log(mod_dir, git_repo, count=3)
    if log:
        lines.append("## Recent git history")
        lines.append(f"```\n{log}\n```")

    return "\n".join(lines)


def build_summary_context(info: dict, module_docs: list[dict], ue_source: str) -> str:
    """Build context for the summary index.md after all module docs are done."""
    lines = _common_header(info, ue_source)

    lines.append("## 模块文档概览")
    for md in module_docs:
        lines.append(f"- **{md['name']}** ({md.get('type', '')}): {md.get('path', md.get('doc_path', ''))}")
        if md.get("summary"):
            lines.append(f"  {md['summary']}")
    lines.append("")

    lines.append("请基于以上模块文档，生成一个精简的 index.md 汇总文档。")
    lines.append("包含：属性表、总体用途、模块列表、各模块一句话总结、使用场景、相关链接。")
    lines.append("不需要重复各模块的详细 API，引用模块文档即可。")

    return "\n".join(lines)


# ── internals ──

def _common_header(info: dict, ue_source: str) -> list[str]:
    lines = []
    lines.append(f"# Plugin: {info['name']}")
    lines.append(f"Category: {info['category']}")
    lines.append(f"Path: {info['path']}")
    lines.append(f"Source files: {info['src_files']}")
    lines.append(f"Created: {info['created']}")
    lines.append("")
    if info.get("uplugin"):
        lines.append("## .uplugin metadata")
        lines.append(f"```json\n{json.dumps(info['uplugin'], indent=2, ensure_ascii=False)}\n```")
        lines.append("")
    if info.get("modules"):
        lines.append("## All Modules")
        for mod in info["modules"]:
            lines.append(f"- **{mod['name']}** ({mod['type']}): {mod['path']}")
            if mod.get("deps"):
                lines.append(f"  Dependencies: {', '.join(mod['deps'])}")
        lines.append("")
    return lines


def _find_plugin_path(name: str, ue_source: str) -> str | None:
    for root in [
        os.path.join(ue_source, "Engine", "Plugins"),
        os.path.join(ue_source, "Engine", "Plugins", "Experimental"),
    ]:
        candidate = os.path.join(root, name)
        if os.path.exists(os.path.join(candidate, f"{name}.uplugin")):
            return candidate

    from . import config as _cfg
    git_main = _cfg.GIT_MAIN_REPO
    r = subprocess.run(
        ["git", "-C", git_main, "ls-files", f"*/{name}/{name}.uplugin", f"*/{name}.uplugin"],
        capture_output=True, text=True, timeout=20,
    )
    for line in r.stdout.strip().split("\n"):
        if line and "Intermediate" not in line and name in line:
            abs_path = os.path.join(ue_source, line)
            if os.path.exists(abs_path):
                return os.path.dirname(abs_path)
    return None


def _count_src_files(path: str) -> int:
    count = 0
    for _, _, files in os.walk(path):
        for f in files:
            if f.endswith((".h", ".cpp")):
                count += 1
    return count


def _extract_modules(plugin_path: str) -> list[dict]:
    modules = []
    for root, dirs, files in os.walk(plugin_path):
        dirs[:] = [d for d in dirs if d not in ("Intermediate", "Binaries")]
        for f in files:
            if f.lower().endswith(".build.cs"):
                cs_path = os.path.join(root, f)
                name = os.path.splitext(f)[0]  # e.g. "GeometryCache.Build"
                # Strip trailing ".Build" — the real module name is just "GeometryCache"
                if name.endswith(".Build"):
                    name = name[:-6]
                content = _read_file_safe(cs_path, max_lines=60)

                m = re.search(r'Type\s*=\s*ModuleType\.(\w+)', content)
                mod_type = m.group(1) if m else "Runtime"

                deps = []
                for dep_match in re.finditer(r'(?:Public|Private)DependencyModuleNames\.Add\("(\w+)"\)', content):
                    deps.append(dep_match.group(1))

                modules.append({
                    "name": name,
                    "type": mod_type,
                    "path": cs_path,
                    "deps": list(dict.fromkeys(deps))[:15],
                })
    return modules


def _get_creation_time(plugin_path: str, git_repo: str, plugin_name: str) -> str:
    for pattern in [
        f"Engine/Plugins/**/{plugin_name}/*.uplugin",
        f"Engine/Plugins/**/{plugin_name}.uplugin",
    ]:
        try:
            r = subprocess.run(
                ["git", "-C", git_repo, "log", "--diff-filter=A", "--format=%ai", "--", pattern],
                capture_output=True, text=True, timeout=15,
            )
            if r.stdout.strip():
                return r.stdout.strip().split("\n")[-1]
        except Exception:
            pass
    return "unknown"


def _read_uplugin(plugin_path: str) -> dict | None:
    for f in os.listdir(plugin_path):
        if f.endswith(".uplugin"):
            content = _read_file_safe(os.path.join(plugin_path, f), max_lines=50)
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw": content[:500]}
    return None


def _get_key_headers(plugin_path: str, max_files: int = 30) -> list[str]:
    headers = []
    for root, dirs, files in os.walk(plugin_path):
        dirs[:] = [d for d in dirs if d not in ("Private", "Generated", "Intermediate", "Binaries")]
        for f in files:
            if f.endswith(".h"):
                headers.append(os.path.join(root, f))

    def sort_key(h):
        is_public = "/Public/" in h
        try:
            size = os.path.getsize(h)
        except OSError:
            size = 999999
        return (0 if is_public else 1, size)

    headers.sort(key=sort_key)
    return headers[:max_files]


def _read_file_safe(path: str, max_lines: int = 100) -> str:
    try:
        with open(path, "r", errors="replace") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"... (truncated, {max_lines} lines)")
                    break
                lines.append(line)
            return "".join(lines)
    except (OSError, IOError):
        return "(file not readable)"


def _get_git_log(plugin_path: str, git_repo: str, count: int = 5) -> str:
    from . import config as _cfg
    rel = os.path.relpath(plugin_path, _cfg.UE_SOURCE)
    try:
        r = subprocess.run(
            ["git", "-C", git_repo, "log", f"-{count}", "--oneline", "--", rel],
            capture_output=True, text=True, timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return ""
