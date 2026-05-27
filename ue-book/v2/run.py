#!/usr/bin/env python3
"""v2 CLI — GitHub API-based UE5 plugin doc generator.

Each GA run processes as many plugins as possible within max_duration
(~2h47m default).  The next GA run auto-resumes from the manifest and
last_run.json.  When there are still plugins remaining, the run
self-triggers the next GA workflow via the GitHub Actions API.
"""
import sys
import os
import json
import time
import subprocess

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v2 import config
from v2 import manifest as manifest_mod
from v2.graph import run_pipeline, MAX_RUN_DURATION


def main():
    import argparse
    parser = argparse.ArgumentParser(description="UE5 Plugin Doc Generator v2")
    parser.add_argument("--version", "-v", required=True, help="UE version (e.g. 5.8)")
    parser.add_argument("--force", "-f", nargs="*", help="Force regenerate specific plugins")
    parser.add_argument("--force-all", action="store_true", help="Force regenerate all plugins")
    parser.add_argument("--batch-size", "-b", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--dry-run", action="store_true", help="Show targets without generating")
    parser.add_argument("--max-duration", type=int, default=MAX_RUN_DURATION,
                        help="Max duration per GA run in seconds")
    args = parser.parse_args()

    log_path = config.PROGRESS_PATH
    manifest_path = config.MANIFEST_PATH
    project_dir = config.PROJECT_DIR

    # ── Load previous state (auto-resume) ──
    prev = None
    if os.path.exists(log_path):
        with open(log_path) as f:
            prev = json.load(f)
        if prev.get("version") != args.version or prev.get("complete", True):
            prev = None  # Different version or already complete — start fresh
        else:
            print(f"[auto-resume] {prev['last_result']['success']} completed "
                  f"in previous run, continuing...")

    # ── Resolve targets ──
    targets, manifest = manifest_mod.resolve_targets(
        version=args.version,
        force=args.force,
        force_all=args.force_all,
        manifest_path=manifest_path,
    )

    if not targets:
        print("All plugins already generated. ✓")
        _mark_complete(log_path)
        return

    if args.dry_run:
        print(f"\nDry run — would generate {len(targets)} plugins:")
        for p in targets:
            print(f"  - {p['name']} ({p['path']})")
        return

    # ── Run single timeboxed round ──
    start = time.time()
    results = run_pipeline(
        targets, version=args.version,
        batch_size=args.batch_size,
        max_duration=args.max_duration,
    )
    elapsed = time.time() - start

    # ── Merge with previous results ──
    if prev:
        result_map = {r["name"]: r for r in prev.get("results", [])}
        for r in results:
            result_map[r["name"]] = r
        all_results = list(result_map.values())
    else:
        all_results = results

    # ── Update manifest for completed (non-skipped, successful) plugins ──
    forced_set = set(args.force) if args.force else set()
    n_registered = 0
    for r in all_results:
        if r.get("success") and not r.get("skipped"):
            manifest_mod.register_plugin(
                manifest,
                name=r["name"],
                version=args.version,
                size=r.get("size", "small"),
                forced=(args.force_all or r["name"] in forced_set),
            )
            n_registered += 1
    manifest_mod.save(manifest_path, manifest)
    print(f"Manifest updated: {n_registered} newly registered")

    # ── Counters ──
    n_done = sum(1 for r in results if r.get("success"))
    n_skip = sum(1 for r in results if r.get("skipped"))

    # ── Check status & decide: complete or chain? ──
    if n_skip == 0:
        print("\n🎉 All plugins generated!")
        _mark_complete(log_path, results=all_results, elapsed=elapsed)
    else:
        # Save intermediate state for debugging / resume (MUST come before commit)
        _save_progress(log_path, args, results=all_results,
                       elapsed=elapsed, skipped=n_skip)

    # ── Commit and push (after save, so last_run.json is up to date) ──
    _git_commit_push(project_dir, version=args.version,
                     done=n_done, skipped=n_skip)

    # ── Self-trigger next run (only if work remains) ──
    if n_skip > 0:
        _trigger_next_workflow(project_dir, args)


# ═══════════════════════════════════════════════════════════════════
# ── Helpers ──
# ═══════════════════════════════════════════════════════════════════

def _git_commit_push(project_dir: str, version: str,
                     done: int, skipped: int):
    """Commit generated docs + manifest and push to remote."""
    try:
        subprocess.run(
            ["git", "config", "user.name", "github-actions[bot]"],
            cwd=project_dir, capture_output=True, text=True, timeout=10,
        )
        subprocess.run(
            ["git", "config", "user.email",
             "github-actions[bot]@users.noreply.github.com"],
            cwd=project_dir, capture_output=True, text=True, timeout=10,
        )
        subprocess.run(
            ["git", "add", "ue-book/docs/", "ue-book/manifest.json",
             "ue-book/v2/last_run.json"],
            cwd=project_dir, capture_output=True, text=True, timeout=30,
        )
        # Check if there's anything to commit
        r = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=project_dir, capture_output=True, timeout=15,
        )
        if r.returncode == 0:
            print("(no changes to commit)")
            return
        msg = f"docs: update UE {version} plugin docs ({done} done, {skipped} remaining)"
        r = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=project_dir, capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            print(f"⚠️  git commit failed: {r.stderr.strip()[:200]}")
            return
        # Pull rebase + push
        subprocess.run(
            ["git", "pull", "--rebase", "origin", "master"],
            cwd=project_dir, capture_output=True, text=True, timeout=60,
        )
        subprocess.run(
            ["git", "push"],
            cwd=project_dir, capture_output=True, text=True, timeout=60,
        )
        print(f"📤 Committed: {msg}")
    except subprocess.TimeoutExpired:
        print("⚠️  git operation timed out")
    except Exception as e:
        print(f"⚠️  git error: {e}")


def _trigger_next_workflow(project_dir: str, args):
    """Use the GitHub CLI to trigger the next generate.yml run."""
    repo = os.environ.get("GITHUB_REPOSITORY", "kisspread/UE-Book")
    token = os.environ.get("GH_PAT") or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    if not token:
        print("⚠️  No GITHUB_TOKEN available — cannot self-trigger next run.")
        print("    Next run must be triggered manually.")
        return

    try:
        env = os.environ.copy()
        env["GH_TOKEN"] = token
        r = subprocess.run(
            ["gh", "workflow", "run", "generate.yml",
             "--repo", repo,
             "--ref", "master",
             "-F", f"version={args.version}",
             "-F", f"max_duration={args.max_duration}"]
            + (["-F", "force=all"] if args.force_all else [])
            + (["-F", f"force={','.join(args.force)}"] if args.force and not args.force_all else []),
            cwd=project_dir,
            capture_output=True, text=True,
            timeout=30,
            env=env,
        )
        if r.returncode == 0:
            print("🔗 Next workflow triggered successfully")
        else:
            print(f"⚠️  Self-trigger failed: {r.stderr.strip()[:200]}")
            print("    Next run must be triggered manually.")
    except subprocess.TimeoutExpired:
        print("⚠️  Self-trigger timed out — next run must be triggered manually.")
    except Exception as e:
        print(f"⚠️  Self-trigger error: {e}")


def _save_progress(log_path: str, args,
                   results: list[dict], elapsed: float,
                   skipped: int):
    """Save intermediate state to last_run.json."""
    n_ok = sum(1 for r in results if r.get("success") and not r.get("skipped"))
    data = {
        "version": args.version,
        "complete": False,
        "params": {
            "force_all": args.force_all,
            "force": args.force,
            "batch_size": args.batch_size,
            "max_duration": args.max_duration,
        },
        "results": results,
        "last_result": {
            "success": n_ok,
            "skipped": skipped,
            "elapsed": elapsed,
        },
    }
    with open(log_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _mark_complete(log_path: str, results: list[dict] | None = None,
                   elapsed: float = 0):
    """Mark the run as fully complete."""
    data: dict = {
        "complete": True,
        "last_result": {
            "success": sum(1 for r in (results or []) if r.get("success")),
            "elapsed": elapsed,
        },
    }
    if results:
        data["results"] = results
    with open(log_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
