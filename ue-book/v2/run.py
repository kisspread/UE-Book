#!/usr/bin/env python3
"""v2 CLI — GitHub API-based UE5 plugin doc generator."""
import sys
import os
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v2 import config
from v2 import manifest as manifest_mod
from v2.graph import run_pipeline


def main():
    import argparse
    parser = argparse.ArgumentParser(description="UE5 Plugin Doc Generator v2")
    parser.add_argument("--version", "-v", required=True, help="UE version (e.g. 5.8)")
    parser.add_argument("--force", "-f", nargs="*", help="Force regenerate specific plugins")
    parser.add_argument("--force-all", action="store_true", help="Force regenerate all plugins")
    parser.add_argument("--batch-size", "-b", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--dry-run", action="store_true", help="Show targets without generating")
    parser.add_argument("--resume", action="store_true", help="Skip already completed plugins from last_run.json")
    args = parser.parse_args()

    # Resolve targets
    targets, manifest = manifest_mod.resolve_targets(
        version=args.version,
        force=args.force,
        force_all=args.force_all,
        manifest_path=config.MANIFEST_PATH,
    )

    if not targets:
        print("Nothing to generate.")
        return

    if args.dry_run:
        print(f"\nDry run — would generate {len(targets)} plugins:")
        for p in targets:
            print(f"  - {p['name']} ({p['path']})")
        return

    log_path = config.PROGRESS_PATH
    prev_results_raw = None

    # ── Resume detection ──
    if args.resume and os.path.exists(log_path):
        with open(log_path) as f:
            prev = json.load(f)
        if prev.get("version") == args.version and not prev.get("complete", True):
            prev_results_raw = prev.get("results", [])
            completed_names = {r["name"] for r in prev_results_raw if r.get("success")}
            remaining = [p for p in targets if p["name"] not in completed_names]
            print(f"Resume: {len(prev_results_raw)} previous results, "
                  f"{len(completed_names)} completed, {len(remaining)} remaining")
            targets = remaining
            if not targets:
                print("All plugins already completed.")
                return

    # Run pipeline
    start = time.time()
    results = run_pipeline(targets, version=args.version, batch_size=args.batch_size)
    elapsed = time.time() - start

    # ── Merge with previous results if resuming ──
    if prev_results_raw is not None:
        result_map = {r["name"]: r for r in prev_results_raw}
        for r in results:
            result_map[r["name"]] = r  # new results override old
        results = list(result_map.values())

    # Update manifest
    forced_set = set(args.force) if args.force else set()
    for r in results:
        if r["success"]:
            manifest_mod.register_plugin(
                manifest,
                name=r["name"],
                version=args.version,
                size=r["size"],
                forced=(args.force_all or r["name"] in forced_set),
            )

    manifest_mod.save(config.MANIFEST_PATH, manifest)

    # Summary
    success = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    print(f"\nDone: {success}/{len(results)} success, {failed} failed, total {elapsed:.0f}s")
    print(f"Manifest saved to {config.MANIFEST_PATH}")

    # Save final log (overwrite intermediate progress)
    with open(log_path, "w") as f:
        json.dump({"version": args.version, "results": results, "elapsed": elapsed, "complete": True}, f, indent=2)


if __name__ == "__main__":
    main()
