"""GitHub API-based plugin scanner for UE5 (v2.1 — annotation-density aware)."""

import json
import re
import base64
import subprocess
from typing import Optional


def list_plugins(branch: str) -> list[dict]:
    """List all plugins on a UE branch via GitHub API."""
    from . import config
    return _get_plugin_list_from_tree(branch)


def scan_plugin(plugin_name: str, plugin_path: str, branch: str) -> dict:
    """Scan a plugin via GitHub API and return structured info."""
    from . import config

    uplugin = _read_uplugin_api(plugin_path, branch)
    tree = _get_tree(plugin_path, branch)
    src_files = sum(1 for p, _ in tree if p.endswith((".h", ".cpp")))

    modules = []
    build_cs_files = [p for p, _ in tree if p.lower().endswith(".build.cs")]
    for cs_rel in build_cs_files:
        content = _read_file_api(f"{plugin_path}/{cs_rel}", branch, max_lines=60)
        name = cs_rel.split("/")[-1]
        if name.lower().endswith(".build.cs"):
            name = name[:-9]
        m = re.search(r'Type\s*=\s*ModuleType\.(\w+)', content)
        mod_type = m.group(1) if m else "Runtime"
        deps = []
        for dep_match in re.finditer(r'(?:Public|Private)DependencyModuleNames\.Add\("(\w+)"\)', content):
            deps.append(dep_match.group(1))
        modules.append({
            "name": name, "type": mod_type, "path": cs_rel,
            "deps": list(dict.fromkeys(deps))[:15],
        })
    # Get creation date (from .uplugin first commit) and recent commits
    created = _get_creation_date(plugin_path, branch)
    commits = _get_commits(plugin_path, branch, count=5)

    return {
        "name": plugin_name, "path": plugin_path, "src_files": src_files,
        "modules": modules, "created": created, "uplugin": uplugin, "commits": commits,
    }


# ── Annotation-density context builder ──

# UE annotations that signal "important API surface"
ANNOTATIONS = [
    'UFUNCTION', 'UPROPERTY', 'UCLASS', 'USTRUCT', 'UENUM', 'UINTERFACE',
    'GENERATED_BODY', 'DECLARE_DYNAMIC', 'DECLARE_DELEGATE',
    'BlueprintCallable', 'BlueprintReadOnly', 'BlueprintReadWrite',
    'BlueprintAssignable', 'EditAnywhere', 'EditDefaultsOnly',
    'Category', 'meta', 'UMETA',
]


def _score_header(path: str, size_bytes: int) -> float:
    """Score a header file by path heuristics + size. Higher = more important."""
    score = 0.0
    lower = path.lower()

    # Directory signals
    if '/public/' in lower:
        score += 100
    if '/private/' in lower:
        score -= 30
    if any(d in lower for d in ['/tests/', '/test/', '/debug/']):
        score -= 200
    if any(d in lower for d in ['/utils/', '/helpers/']):
        score -= 50

    # Filename signals
    basename = path.split('/')[-1].lower()
    if any(k in basename for k in ['interface', 'core', 'api', 'base', 'module',
                                     'registry', 'manager', 'library', 'subsystem']):
        score += 50

    # Size bonus (bigger files tend to have more API)
    if size_bytes > 0:
        score += min(size_bytes / 100.0, 80)  # cap at 80 pts

    return score


def _read_file_anchored(path: str, branch: str, budget_lines: int) -> str:
    """Read a header file starting from the UCLASS/USTRUCT comment block, within budget."""
    full = _read_file_api(path, branch, max_lines=5000)
    if not full or full.startswith("(file"):
        return full

    lines = full.split('\n')
    total = len(lines)

    # Find UCLASS / USTRUCT / UENUM / UINTERFACE anchor
    anchor = None
    for i, line in enumerate(lines):
        if re.match(r'\s*(UCLASS|USTRUCT|UENUM|UINTERFACE)\s*\(', line):
            anchor = i
            break

    if anchor is None:
        # No anchor found: skip top boilerplate (copyright+includes+pragma)
        start = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('//') and not stripped.startswith('#') \
               and not stripped.startswith('/*') and not stripped.startswith('*'):
                start = i
                break
    else:
        # Scan backwards from anchor to find /// comment block start
        start = anchor
        while start > 0 and (lines[start - 1].strip().startswith('///')
                             or lines[start - 1].strip().startswith('/**')
                             or lines[start - 1].strip().startswith('*')
                             or lines[start - 1].strip() == ''):
            start -= 1
        # Skip leading blank lines
        while start < anchor and lines[start].strip() == '':
            start += 1

    # Apply budget
    end = min(total, start + budget_lines)

    # Also check tail for missed annotations if file extends beyond budget
    tail_lines = []
    if total > end + 20:
        tail_start = max(end, total - 100)
        tail_text = '\n'.join(lines[tail_start:total])
        if any(anno in tail_text for anno in ['UFUNCTION', 'UPROPERTY', 'UCLASS']):
            tail_lines = [f"\n... (tail {tail_start+1}-{total}) ...",
                          "```cpp", tail_text, "```", ""]

    body = '\n'.join(lines[start:end])
    result = f"```cpp\n{body}\n```\n"
    if tail_lines:
        result += '\n'.join(tail_lines)
    return result


def _build_header_context(headers_with_sizes: list[tuple[str, int]],
                          plugin_path: str, branch: str,
                          max_files: int = 30,
                          budget_per_file: dict = None) -> list[str]:
    """Build context lines for scored headers. Returns list of lines."""
    if budget_per_file is None:
        budget_per_file = {0: 500, 6: 300, 16: 150}

    scored = [(_score_header(p, s), p, s) for p, s in headers_with_sizes
              if p.endswith('.h')]
    scored.sort(key=lambda x: -x[0])

    lines = []
    lines.append(f"## File analysis ({len(scored)} headers, showing top {max_files} by annotation density)")
    lines.append(f"Score formula: Public/+100, Interface/API/Core/+50, Tests/-200, size/100")
    lines.append("")

    count = 0
    for rank, (score, path, size) in enumerate(scored[:max_files]):
        # Determine budget based on rank
        budget = 150  # default
        for threshold, b in sorted(budget_per_file.items(), reverse=True):
            if rank >= threshold:
                budget = b
                break

        content = _read_file_anchored(f"{plugin_path}/{path}", branch, budget)
        lines.append(f"### {path}  (density={score:.0f}, {size}B, budget={budget}L)")
        lines.append(content)
        lines.append("")
        count += 1

    return lines


def build_context(info: dict, branch: str) -> str:
    """Build full plugin context using annotation-density-aware reading."""
    lines = _common_header(info)

    tree = _get_tree(info["path"], branch)
    lines += _build_header_context(tree, info["path"], branch)

    if info.get("commits"):
        lines.append("## Recent git history")
        for c in info["commits"]:
            lines.append(f"- `{c['sha'][:8]}` {c['date'][:10]} — {c['message']}")
        lines.append("")

    return "\n".join(lines)


def build_module_context(info: dict, module: dict, branch: str) -> str:
    """Build context for a single module using annotation-density-aware reading."""
    lines = _common_header(info)
    lines.append(f"## Current module: {module['name']} ({module['type']})")
    lines.append(f"Build.cs: {module['path']}")
    if module.get("deps"):
        lines.append(f"Dependencies: {', '.join(module['deps'])}")
    lines.append("")

    mod_dir = "/".join(module["path"].split("/")[:-1])
    tree = _get_tree(f"{info['path']}/{mod_dir}", branch)
    lines += _build_header_context(tree, f"{info['path']}/{mod_dir}", branch,
                                    max_files=40,
                                    budget_per_file={0: 500, 6: 300, 16: 200})

    if info.get("commits"):
        lines.append("## Recent git history")
        for c in info["commits"]:
            lines.append(f"- `{c['sha'][:8]}` {c['date'][:10]} — {c['message']}")
        lines.append("")

    return "\n".join(lines)


def build_summary_context(info: dict, module_docs: list[dict]) -> str:
    """Build context for the summary index.md after all module docs are done."""
    lines = _common_header(info)
    lines.append("## Module doc overview")
    for md in module_docs:
        lines.append(f"- **{md['name']}** ({md.get('type', '')}): {md.get('path', '')}")
    lines.append("")
    lines.append("Based on the module docs above, generate a compact index.md summary.")
    lines.append("Include: property table, overall purpose, module list with one-liners, "
                 "use cases, related links. Don't repeat detailed API.")
    if info.get("commits"):
        lines.append("## Recent git history")
        for c in info["commits"]:
            lines.append(f"- `{c['sha'][:8]}` {c['date'][:10]} — {c['message']}")
        lines.append("")
    return "\n".join(lines)


# ── Internal API helpers ──

def _gh_api(endpoint: str, **kwargs) -> dict:
    if kwargs:
        params = "&".join(f"{k}={v}" for k, v in kwargs.items())
        endpoint = f"{endpoint}?{params}" if "?" not in endpoint else f"{endpoint}&{params}"
    r = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"GitHub API error: {r.stderr.strip()}")
    return json.loads(r.stdout)


def _gh_graphql(query: str, **kwargs) -> dict:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in kwargs.items():
        cmd.extend(["-f", f"{k}={v}"])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"GraphQL error: {r.stderr.strip()}")
    return json.loads(r.stdout)


def _get_plugin_list_from_tree(branch: str) -> list[dict]:
    from . import config
    repo = config.GH_REPO
    tree_ref = f"{branch}:Engine%2FPlugins"
    data = _gh_api(f"repos/{repo}/git/trees/{tree_ref}", recursive=1)
    plugins = {}
    for entry in data.get("tree", []):
        if entry["path"].endswith(".uplugin") and entry["type"] == "blob":
            parts = entry["path"].split("/")
            if len(parts) >= 2:
                plugin_dir = "/".join(parts[:-1])
                plugin_name = parts[-1].replace(".uplugin", "")
                category = parts[0]
                full_path = f"Engine/Plugins/{plugin_dir}"
                if plugin_name not in plugins:
                    plugins[plugin_name] = {
                        "name": plugin_name, "path": full_path, "category": category,
                    }
    return list(plugins.values())


def _get_tree(path: str, branch: str) -> list[tuple[str, int]]:
    """Get file list under a path. Returns [(relative_path, size_bytes), ...]."""
    from . import config
    repo = config.GH_REPO
    try:
        encoded_path = path.replace("/", "%2F")
        tree_ref = f"{branch}:{encoded_path}"
        data = _gh_api(f"repos/{repo}/git/trees/{tree_ref}", recursive=1)
        return [(e["path"], e.get("size", 0)) for e in data.get("tree", []) if e["type"] == "blob"]
    except RuntimeError:
        return []


def _read_file_api(path: str, branch: str, max_lines: int = 100) -> str:
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
    from . import config
    repo = config.GH_REPO
    try:
        tree = _gh_api(f"repos/{repo}/git/trees/{branch}:{plugin_path}")
        for entry in tree.get("tree", []):
            if entry["path"].endswith(".uplugin"):
                content = _read_file_api(f"{plugin_path}/{entry['path']}", branch, max_lines=50)
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"raw": content[:500]}
    except RuntimeError:
        pass
    return None


def _get_creation_date(plugin_path: str, branch: str) -> str:
    """Get the earliest commit date for a plugin's .uplugin file."""
    from . import config
    repo = config.GH_REPO
    try:
        # Get total commit count for the .uplugin file, then fetch the last page (first commit)
        # First API call: get count from the first page
        uplugin_path = f"{plugin_path}/{plugin_path.split('/')[-1]}.uplugin"
        data = _gh_api(f"repos/{repo}/commits", sha=branch, path=uplugin_path, per_page=1)
        if not data:
            return "unknown"
        
        # Get total count from Link header not easily accessible via gh CLI.
        # Fallback: fetch many commits and take oldest
        all_data = _gh_api(f"repos/{repo}/commits", sha=branch, path=uplugin_path, per_page=100)
        if all_data and len(all_data) > 0:
            return all_data[-1]["commit"]["committer"]["date"]
        return data[0]["commit"]["committer"]["date"]
    except RuntimeError:
        pass
    # Fallback: try path without .uplugin
    try:
        data = _gh_api(f"repos/{repo}/commits", sha=branch, path=plugin_path, per_page=100)
        if data and len(data) > 0:
            return data[-1]["commit"]["committer"]["date"]
    except RuntimeError:
        pass
    return "unknown"


def _get_commits(path: str, branch: str, count: int = 5) -> list[dict]:
    from . import config
    repo = config.GH_REPO
    try:
        data = _gh_api(f"repos/{repo}/commits", sha=branch, path=path, per_page=count)
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
    lines = [
        f"# Plugin: {info['name']}",
        f"Path: {info['path']}",
        f"Source files: {info['src_files']}",
        f"Created: {info.get('created', 'unknown')}",
        "",
    ]
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
