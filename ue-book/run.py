#!/usr/bin/env python3
"""CLI entry point for UE5 doc generation pipeline."""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import config
from pipeline.graph import run_pipeline


def load_plugins(category: str = None, limit: int = None, specific: list[str] = None) -> list[dict]:
    """Load plugin list."""
    with open(config.PLUGINS_INDEX) as f:
        all_plugins = json.load(f)

    if specific:
        plugins = [p for p in all_plugins if p["name"] in specific]
    elif category:
        # Map xlarge to src_files >= 100
        if category == "xlarge":
            plugins = [p for p in all_plugins if p.get("src_files", 0) >= 100]
        else:
            plugins = [p for p in all_plugins if p["category"] == category]
    else:
        plugins = []
        for p in all_plugins:
            cat = p.get("category", "")
            # Determine output dir
            if p.get("src_files", 0) >= 100:
                cat = "xlarge"
            doc_path = os.path.join(config.PROJECT_DIR, "docs", cat, p["name"], "index.md")
            if not os.path.exists(doc_path):
                plugins.append(p)

    if limit:
        plugins = plugins[:limit]
    
    # Set output category based on size
    for p in plugins:
        p["_output_category"] = p.get("size", "small")
    
    return plugins


def main():
    import argparse
    parser = argparse.ArgumentParser(description="UE5 Plugin Doc Generator")
    parser.add_argument("--category", "-c", help="small/medium/large/xlarge")
    parser.add_argument("--limit", "-n", type=int)
    parser.add_argument("--batch-size", "-b", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--plugins", "-p", nargs="+", help="Specific plugin names")
    args = parser.parse_args()

    plugins = load_plugins(category=args.category, limit=args.limit, specific=args.plugins)
    if not plugins:
        print("No plugins to process.")
        return

    result = run_pipeline(plugins, batch_size=args.batch_size)

    log_path = os.path.join(config.PROJECT_DIR, "pipeline", "last_run.json")
    with open(log_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {log_path}")


if __name__ == "__main__":
    main()
