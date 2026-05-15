#!/usr/bin/env python3
"""check_pe_opening_context.py — validate PE opening preconditions.

Exits 0 on success. Exits non-zero with a classification code on failure.
Used by the PM Agent before announcing a PE as open.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REQUIRED_CHECKS = [
    "origin_remote",
    "origin_main_fetched",
    "current_pe_reconciled",
    "worktree_bound",
    "worktree_clean",
    "head_matches_baseline",
]


def git(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(["git", *cmd], cwd=cwd, text=True).strip()


def _check_origin_remote(repo: Path) -> int:
    """Verify the repo has an origin remote."""
    try:
        remote = git(["remote", "get-url", "origin"], cwd=repo)
    except subprocess.CalledProcessError:
        print("CLASSIFY: MISSING_ORIGIN_REMOTE", file=sys.stderr)
        return 1
    if not remote:
        print("CLASSIFY: MISSING_ORIGIN_REMOTE", file=sys.stderr)
        return 1
    return 0


def _check_origin_main_fetched(repo: Path) -> int:
    """Verify origin/main is reachable."""
    try:
        git(["rev-parse", "origin/main"], cwd=repo)
    except subprocess.CalledProcessError:
        print("CLASSIFY: STALE_FETCH", file=sys.stderr)
        return 1
    return 0


def _check_current_pe_reconciled(repo: Path) -> int:
    """Verify CURRENT_PE.md is either clean or properly acknowledged as dirty."""
    try:
        git(["diff-index", "--quiet", "HEAD", "--", "CURRENT_PE.md"], cwd=repo)
    except subprocess.CalledProcessError:
        print("CLASSIFY: DIRTY_CURRENT_PE_MD", file=sys.stderr)
        return 1
    short = git(["status", "--short", "--", "CURRENT_PE.md"], cwd=repo)
    if short:
        print("CLASSIFY: DIRTY_CURRENT_PE_MD", file=sys.stderr)
        return 1
    return 0


def _check_worktree_bound(worktree: Path, expected_branch: str) -> int:
    """Verify the worktree is on the expected branch."""
    try:
        branch = git(["branch", "--show-current"], cwd=worktree)
    except subprocess.CalledProcessError:
        print("CLASSIFY: WORKTREE_MISSING", file=sys.stderr)
        return 1
    if not branch:
        print("CLASSIFY: DETACHED_HEAD", file=sys.stderr)
        return 1
    if branch != expected_branch:
        print(f"CLASSIFY: WRONG_BRANCH expected={expected_branch} actual={branch}",
              file=sys.stderr)
        return 1
    return 0


def _check_worktree_clean(worktree: Path) -> int:
    """Verify the worktree has no dirty tracked files."""
    try:
        dirty = git(["status", "--short", "--untracked-files=no"], cwd=worktree)
    except subprocess.CalledProcessError:
        print("CLASSIFY: WORKTREE_MISSING", file=sys.stderr)
        return 1
    if dirty:
        print("CLASSIFY: DIRTY_WORKTREE", file=sys.stderr)
        return 1
    return 0


def _check_head_matches_baseline(worktree: Path, expected_head: str) -> int:
    """Verify the worktree HEAD matches the expected baseline."""
    try:
        head = git(["rev-parse", "HEAD"], cwd=worktree)
    except subprocess.CalledProcessError:
        print("CLASSIFY: WORKTREE_MISSING", file=sys.stderr)
        return 1
    if head != expected_head:
        print(f"CLASSIFY: HEAD_MISMATCH expected={expected_head[:12]} actual={head[:12]}",
              file=sys.stderr)
        return 1
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Check PE opening context")
    p.add_argument("--repo", required=True, help="Path to the repo checkout")
    p.add_argument("--worktree", required=True, help="Path to the agent worktree")
    p.add_argument("--branch", required=True, help="Expected PE branch name")
    p.add_argument("--head", required=True, help="Expected HEAD SHA")
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    worktree = Path(args.worktree).resolve()

    failures: list[str] = []

    if _check_origin_remote(repo):
        failures.append("origin_remote")
    if _check_origin_main_fetched(repo):
        failures.append("origin_main_fetched")
    if _check_current_pe_reconciled(repo):
        failures.append("current_pe_reconciled")
    if _check_worktree_bound(worktree, args.branch):
        failures.append("worktree_bound")
    if _check_worktree_clean(worktree):
        failures.append("worktree_clean")
    if _check_head_matches_baseline(worktree, args.head):
        failures.append("head_matches_baseline")

    if failures:
        print(f"FAIL: {', '.join(failures)}", file=sys.stderr)
        return 1

    print(f"OPENING_READY branch={args.branch} head={args.head[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
