"""Manifest management — track generated plugins across versions."""
import json
import os
from typing import Optional


def load(path: str) -> dict:
    """Load manifest.json, return empty structure if missing."""
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"versions": {}, "plugins": {}}


def save(path: str, manifest: dict):
    """Save manifest.json."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_generated_names(manifest: dict) -> set[str]:
    """Get all plugin names that have been generated (any version)."""
    return set(manifest.get("plugins", {}).keys())


def get_version_plugins(manifest: dict, version: str) -> set[str]:
    """Get plugin names generated for a specific version."""
    return {
        name for name, info in manifest.get("plugins", {}).items()
        if info.get("generated_in") == version
    }


def compute_diff(ue_plugins: list[dict], manifest: dict,
                 version: str = "") -> list[dict]:
    """Compute which plugins need generation for a specific version.

    Args:
        ue_plugins: list of {name, path, category} from GitHub API
        manifest: current manifest
        version: UE version — plugins generated for OTHER versions don't count

    Returns:
        list of plugins NOT yet generated for this version
    """
    if version:
        generated = get_version_plugins(manifest, version)
    else:
        generated = get_generated_names(manifest)
    return [p for p in ue_plugins if p["name"] not in generated]


def register_plugin(
    manifest: dict,
    name: str,
    version: str,
    size: str,
    forced: bool = False,
) -> dict:
    """Register a plugin as generated (or re-generated).

    Updates the manifest in-place and returns the updated manifest.
    """
    if "plugins" not in manifest:
        manifest["plugins"] = {}

    doc_path = f"docs/{version}/{size}/{name}/"
    manifest["plugins"][name] = {
        "generated_in": version,
        "size": size,
        "doc_path": doc_path,
    }
    if forced:
        manifest["plugins"][name]["forced"] = True

    return manifest


def resolve_targets(
    version: str,
    force: Optional[list[str]] = None,
    force_all: bool = False,
    manifest_path: str = "",
) -> tuple[list[dict], dict]:
    """Determine which plugins to generate.

    Returns (plugins_to_generate, manifest).
    """
    from . import scanner

    manifest = load(manifest_path) if manifest_path else {"plugins": {}}

    # Get all plugins from UE branch
    print(f"Fetching plugin list from EpicGames/UnrealEngine @ {version}...")
    all_plugins = scanner.list_plugins(version)
    print(f"  Found {len(all_plugins)} plugins on {version}")

    if force_all:
        # "Generate all" = ensure every plugin is in the manifest.
        # Skip already-registered plugins — manifest is the resume checkpoint.
        targets = compute_diff(all_plugins, manifest, version=version)
        print(f"  Force-all: {len(targets)} plugins to generate "
              f"(skipping {len(all_plugins) - len(targets)} already in manifest)")
    elif force:
        # Re-generate specific plugins
        force_set = set(force)
        targets = [p for p in all_plugins if p["name"] in force_set]
        found = {p["name"] for p in targets}
        missing = force_set - found
        if missing:
            print(f"  ⚠️ Not found on {version}: {', '.join(missing)}")
        print(f"  Force: will regenerate {len(targets)} plugins")
    else:
        # Incremental: only new plugins
        targets = compute_diff(all_plugins, manifest, version=version)
        print(f"  Incremental: {len(targets)} new plugins to generate")

    return targets, manifest


def categorize(src_files: int) -> str:
    """Determine size category from source file count."""
    if src_files >= 100:
        return "xlarge"
    elif src_files >= 51:
        return "large"
    elif src_files >= 21:
        return "medium"
    else:
        return "small"
