#!/usr/bin/env python3
"""Fix git log sections in generated docs.

For each plugin in docs/5.8/:
1. Fetch real commits from GitHub API
2. Replace fake commits or add missing section
"""
import json
import os
import re
import subprocess
import sys

REPO = "EpicGames/UnrealEngine"
BRANCH = "5.8"
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "5.8")


def get_commits(plugin_path: str, count: int = 5) -> list[dict]:
    """Get real commits from GitHub API."""
    try:
        r = subprocess.run(
            ["gh", "api", f"repos/{REPO}/commits",
             f"sha={BRANCH}", f"path={plugin_path}", f"per_page={count}"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            return []
        data = json.loads(r.stdout)
        return [
            {
                "sha": c["sha"][:8],
                "date": c["commit"]["committer"]["date"][:10],
                "message": c["commit"]["message"].split("\n")[0][:100],
            }
            for c in data
        ]
    except Exception as e:
        print(f"  ⚠️ API error: {e}")
        return []


def get_plugin_path(plugin_name: str) -> str:
    """Find plugin path from manifest."""
    manifest_path = os.path.join(os.path.dirname(DOCS_DIR), "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
        entry = manifest.get("plugins", {}).get(plugin_name, {})
        # doc_path is like "docs/5.8/small/ADM/"
        # We need the UE path like "Engine/Plugins/Runtime/ADM"
        # This isn't in manifest, so we'll use the plugin name to search
        pass
    return ""


def build_commit_section(commits: list[dict]) -> str:
    """Build the markdown commit section."""
    lines = ["### 近期更新", ""]
    for c in commits:
        lines.append(f"- {c['date']} `{c['sha']}` {c['message']}")
    lines.append("")
    return "\n".join(lines)


def fix_doc(filepath: str, commits: list[dict]) -> bool:
    """Fix git log section in a doc file. Returns True if modified."""
    if not commits:
        return False

    with open(filepath) as f:
        content = f.read()

    commit_section = build_commit_section(commits)

    # Pattern 1: Has fake commits in a code block
    # ```\n- 2026-04-14 abc1234 ...\n```
    fake_pattern = r'### 近期更新\s*\n\s*```\n(?:.*?\n)*?```'
    if re.search(fake_pattern, content):
        content = re.sub(fake_pattern, commit_section.strip(), content)
        with open(filepath, "w") as f:
            f.write(content)
        return True

    # Pattern 2: Has fake commits without code block but with abc123/def5678
    if "abc123" in content or "def5678" in content or "ghi9012" in content:
        # Find and replace the section
        pattern = r'### 近期更新\s*\n(?:.*?\n)*?(?=\n### |\n## |\Z)'
        if re.search(pattern, content):
            content = re.sub(pattern, commit_section, content)
            with open(filepath, "w") as f:
                f.write(content)
            return True

    # Pattern 3: Has real commits already — skip
    if re.search(r'### 近期更新\s*\n\s*-\s*\d{4}-\d{2}-\d{2}\s+`[a-f0-9]{7,8}`', content):
        return False

    # Pattern 4: Missing section entirely — add before "维护评价" or at end
    if "### 近期更新" not in content:
        if "### 维护评价" in content:
            content = content.replace("### 维护评价", commit_section + "\n### 维护评价")
        elif "## 相关链接" in content:
            content = content.replace("## 相关链接", commit_section + "\n## 相关链接")
        else:
            content += "\n" + commit_section
        with open(filepath, "w") as f:
            f.write(content)
        return True

    return False


def main():
    fixed = 0
    skipped = 0
    errors = 0

    # Collect all index.md files
    docs = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for f in files:
            if f.endswith(".md"):
                docs.append(os.path.join(root, f))

    docs.sort()
    print(f"Scanning {len(docs)} docs in {DOCS_DIR}")

    # Group by plugin directory
    plugins = {}
    for doc in docs:
        rel = os.path.relpath(doc, DOCS_DIR)
        parts = rel.split(os.sep)
        if len(parts) >= 2:
            plugin_dir = os.sep.join(parts[:2])  # e.g. "small/ADM"
            if plugin_dir not in plugins:
                plugins[plugin_dir] = []
            plugins[plugin_dir].append(doc)

    print(f"Found {len(plugins)} plugin directories")

    for plugin_dir, files in sorted(plugins.items()):
        size, name = plugin_dir.split(os.sep)

        # Get UE plugin path from manifest
        manifest_path = os.path.join(os.path.dirname(DOCS_DIR), "manifest.json")
        with open(manifest_path) as f:
            manifest = json.load(f)
        entry = manifest.get("plugins", {}).get(name, {})
        doc_path = entry.get("doc_path", "")

        # Try to reconstruct UE path
        # We need to search for it
        ue_path = ""
        for suffix in [f"Engine/Plugins/**/{name}", f"Engine/Plugins/**/{name}/*"]:
            try:
                r = subprocess.run(
                    ["gh", "api", f"repos/{REPO}/git/trees/{BRANCH}:Engine%2FPlugins?recursive=1",
                     "--jq", f'[.tree[].path | select(contains("{name}/{name}.uplugin") or endswith("/{name}.uplugin"))] | first'],
                    capture_output=True, text=True, timeout=30,
                )
                if r.returncode == 0 and r.stdout.strip() and r.stdout.strip() != "null":
                    uplugin_path = r.stdout.strip().strip('"')
                    ue_path = "/".join(uplugin_path.split("/")[:-1])
                    break
            except Exception:
                pass

        if not ue_path:
            # Fallback: try common patterns
            for cat in ["Runtime", "Editor", "Experimental", "Developer", "Online",
                        "Experimental/Animation", "Experimental/Toolsets", "Experimental/UAF",
                        "Experimental/MetaHuman", "Experimental/NNE", "Experimental/AVCodecs",
                        "FX", "Media", "Importers", "Interchange", "MetaHuman",
                        "MovieScene", "VirtualProduction", "Animation", "AI",
                        "Compositing", "Enterprise", "Experimental/Web",
                        "Experimental/PCGInterops", "Experimental/Microsoft",
                        "Online/Microsoft"]:
                test_path = f"Engine/Plugins/{cat}/{name}"
                try:
                    r = subprocess.run(
                        ["gh", "api", f"repos/{REPO}/contents/{test_path}", "ref=5.8", "--jq", ".type"],
                        capture_output=True, text=True, timeout=10,
                    )
                    if r.returncode == 0 and "dir" in r.stdout:
                        ue_path = test_path
                        break
                except Exception:
                    pass

        if not ue_path:
            print(f"  ⚠️ {name}: could not find UE path")
            errors += 1
            continue

        print(f"  {name} ({ue_path})...", end=" ")
        commits = get_commits(ue_path)

        if not commits:
            print("no commits")
            skipped += 1
            continue

        modified = False
        for filepath in files:
            if fix_doc(filepath, commits):
                modified = True

        if modified:
            print(f"✅ fixed ({len(commits)} commits)")
            fixed += 1
        else:
            print("already OK")
            skipped += 1

    print(f"\nDone: {fixed} fixed, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
