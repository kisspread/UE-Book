"""GitHub API-based plugin scanner for UE5."""
import json
import re
import base64
import subprocess
from typing import Optional


def list_plugins(branch: str) -> list[dict]:
    """List all plugins on a UE branch via GitHub API.

    Returns list of {name, path, category} where category is the
    size-independent UE category (Runtime, Editor, etc.).
    """
    from . import config
    plugins = _get_plugin_list_from_tree(branch)
    return plugins


def scan_plugin(plugin_name: str, plugin_path: str, branch: str) -> dict:
    """Scan a plugin via GitHub API and return structured info.

    Args:
        plugin_name: e.g. "ADM"
        plugin_path: e.g. "Engine/Plugins/Runtime/ADM"
        branch: e.g. "5.8"
    """
    from . import config

    # Read .uplugin
    uplugin = _read_uplugin_api(plugin_path, branch)

    # List source files and count
    tree = _get_tree(plugin_path, branch)
    src_files = sum(1 for f in tree if f.endswith((".h", ".cpp")))

    # Extract modules from Build.cs files
    modules = []
    build_cs_files = [f for f in tree if f.lower().endswith(".build.cs")]
    for cs_rel in build_cs_files:
        content = _read_file_api(f"{plugin_path}/{cs_rel}", branch, max_lines=60)
        name = cs_rel.split("/")[-1]
        if name.lower().endswith(".build.cs"):
            name = name[:-9]  # strip .Build.cs
        m = re.search(r'Type\s*=\s*ModuleType\.(\w+)', content)
        mod_type = m.group(1) if m else "Runtime"
        deps = []
        for dep_match in re.finditer(r'(?:Public|Private)DependencyModuleNames\.Add\("(\w+)"\)', content):
            deps.append(dep_match.group(1))
        modules.append({
            "name": name,
            "type": mod_type,
            "path": cs_rel,
            "deps": list(dict.fromkeys(deps))[:15],
        })

    # Get git log for recent commits
    commits = _get_commits(plugin_path, branch, count=5)
    created = commits[-1]["date"] if commits else "unknown"

    return {
        "name": plugin_name,
        "path": plugin_path,
        "src_files": src_files,
        "modules": modules,
        "created": created,
        "uplugin": uplugin,
        "commits": commits,
    }


def build_context(info: dict, branch: str) -> str:
    """Build full plugin context for single-doc generation."""
    lines = _common_header(info)

    # Key headers
    tree = _get_tree(info["path"], branch)
    headers = [f for f in tree if f.endswith(".h")]
    # Prioritize Public/ headers, then by path
    headers.sort(key=lambda h: (0 if "/Public/" in h else 1, h))
    for h in headers[:30]:
        content = _read_file_api(f"{info['path']}/{h}", branch, max_lines=80)
        lines.append(f"### {h}")
        lines.append(f"```cpp\n{content}\n```")
        lines.append("")

    # Git log
    if info.get("commits"):
        lines.append("## Recent git history")
        for c in info["commits"]:
            lines.append(f"- `{c['sha'][:8]}` {c['date'][:10]} — {c['message']}")
        lines.append("")

    return "\n".join(lines)


def build_module_context(info: dict, module: dict, branch: str) -> str:
    """Build context for a single module within a plugin."""
    lines = _common_header(info)

    lines.append(f"## 当前模块: {module['name']} ({module['type']})")
    lines.append(f"Build.cs: {module['path']}")
    if module.get("deps"):
        lines.append(f"Dependencies: {', '.join(module['deps'])}")
    lines.append("")

    # Headers from this module's directory
    mod_dir = "/".join(module["path"].split("/")[:-1])
    tree = _get_tree(f"{info['path']}/{mod_dir}", branch)
    headers = [f for f in tree if f.endswith(".h")]
    headers.sort(key=lambda h: (0 if "/Public/" in h else 1, h))
    lines.append("## 本模块头文件")
    for h in headers[:40]:
        content = _read_file_api(f"{info['path']}/{mod_dir}/{h}", branch, max_lines=100)
        lines.append(f"### {h}")
        lines.append(f"```cpp\n{content}\n```")
        lines.append("")

    return "\n".join(lines)


def build_summary_context(info: dict, module_docs: list[dict]) -> str:
    """Build context for the summary index.md after all module docs are done."""
    lines = _common_header(info)

    lines.append("## 模块文档概览")
    for md in module_docs:
        lines.append(f"- **{md['name']}** ({md.get('type', '')}): {md.get('path', '')}")
    lines.append("")

    lines.append("请基于以上模块文档，生成一个精简的 index.md 汇总文档。")
    lines.append("包含：属性表、总体用途、模块列表、各模块一句话总结、使用场景、相关链接。")
    lines.append("不需要重复各模块的详细 API，引用模块文档即可。")

    return "\n".join(lines)


# ── Internal API helpers ──

def _gh_api(endpoint: str, **kwargs) -> dict:
    """Call GitHub REST API via gh CLI.

    kwargs are appended as query parameters (?key=value).
    """
    if kwargs:
        params = "&".join(f"{k}={v}" for k, v in kwargs.items())
        if "?" in endpoint:
            endpoint = f"{endpoint}&{params}"
        else:
            endpoint = f"{endpoint}?{params}"
    r = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"GitHub API error: {r.stderr.strip()}")
    return json.loads(r.stdout)


def _gh_graphql(query: str, **kwargs) -> dict:
    """Call GitHub GraphQL API via gh CLI."""
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in kwargs.items():
        cmd.extend(["-f", f"{k}={v}"])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"GraphQL error: {r.stderr.strip()}")
    return json.loads(r.stdout)


def _get_plugin_list_from_tree(branch: str) -> list[dict]:
    """Get all plugins by scanning .uplugin files via Git Trees API."""
    from . import config
    repo = config.GH_REPO

    # Get recursive tree for Engine/Plugins
    tree_ref = f"{branch}:Engine%2FPlugins"
    data = _gh_api(f"repos/{repo}/git/trees/{tree_ref}", recursive=1)
    plugins = {}  # name -> {path, category}

    for entry in data.get("tree", []):
        if entry["path"].endswith(".uplugin") and entry["type"] == "blob":
            # path like "Runtime/ADM/ADM.uplugin" or "Experimental/Foo/Foo.uplugin"
            parts = entry["path"].split("/")
            if len(parts) >= 2:
                plugin_dir = "/".join(parts[:-1])
                plugin_name = parts[-1].replace(".uplugin", "")
                # Determine category from top-level dir
                category = parts[0]
                full_path = f"Engine/Plugins/{plugin_dir}"
                if plugin_name not in plugins:
                    plugins[plugin_name] = {
                        "name": plugin_name,
                        "path": full_path,
                        "category": category,
                    }

    return list(plugins.values())


def _get_tree(path: str, branch: str) -> list[str]:
    """Get file list under a path (relative paths)."""
    from . import config
    repo = config.GH_REPO
    try:
        encoded_path = path.replace("/", "%2F")
        tree_ref = f"{branch}:{encoded_path}"
        data = _gh_api(f"repos/{repo}/git/trees/{tree_ref}", recursive=1)
        return [e["path"] for e in data.get("tree", []) if e["type"] == "blob"]
    except RuntimeError:
        return []


def _read_file_api(path: str, branch: str, max_lines: int = 100) -> str:
    """Read a file from GitHub repo via API."""
    from . import config
    repo = config.GH_REPO
    try:
        data = _gh_api(f"repos/{repo}/contents/{path}", ref=branch)
        if data.get("encoding") == "base64":
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        else:
            content = data.get("content", "")
        lines = content.split("\n")
        if len(lines) > max_lines:
            return "\n".join(lines[:max_lines]) + f"\n... (truncated, {max_lines} lines)"
        return content
    except (RuntimeError, Exception):
        return "(file not readable)"


def _read_uplugin_api(plugin_path: str, branch: str) -> Optional[dict]:
    """Read .uplugin file via GitHub API."""
    from . import config
    repo = config.GH_REPO
    try:
        tree = _gh_api(f"repos/{repo}/git/trees/{branch}:{plugin_path}")
        for entry in tree.get("tree", []):
            if entry["path"].endswith(".uplugin"):
                content = _read_file_api(
                    f"{plugin_path}/{entry['path']}", branch, max_lines=50
                )
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"raw": content[:500]}
    except RuntimeError:
        pass
    return None


def _get_commits(path: str, branch: str, count: int = 5) -> list[dict]:
    """Get recent commits for a path."""
    from . import config
    repo = config.GH_REPO
    try:
        data = _gh_api(
            f"repos/{repo}/commits",
            sha=branch, path=path, per_page=count,
        )
        commits = []
        for c in data:
            commits.append({
                "sha": c["sha"],
                "date": c["commit"]["committer"]["date"],
                "message": c["commit"]["message"].split("\n")[0][:100],
            })
        return commits
    except RuntimeError:
        return []


def _common_header(info: dict) -> list[str]:
    """Build common header lines for context."""
    lines = []
    lines.append(f"# Plugin: {info['name']}")
    lines.append(f"Path: {info['path']}")
    lines.append(f"Source files: {info['src_files']}")
    lines.append(f"Created: {info.get('created', 'unknown')}")
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
