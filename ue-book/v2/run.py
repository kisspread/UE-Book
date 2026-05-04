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

    # Run pipeline
    start = time.time()
    results = run_pipeline(targets, version=args.version, batch_size=args.batch_size)
    elapsed = time.time() - start

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

    # Save run log
    log_path = os.path.join(config.PROJECT_DIR, "v2", "last_run.json")
    with open(log_path, "w") as f:
        json.dump({"version": args.version, "results": results, "elapsed": elapsed}, f, indent=2)


if __name__ == "__main__":
    main()
