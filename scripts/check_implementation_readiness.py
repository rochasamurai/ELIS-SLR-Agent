#!/usr/bin/env python3
"""check_implementation_readiness.py — validate dispatch readiness.

Checks branch binding, HEAD match, worktree cleanliness, and persistent
context files before declaring a worktree ready for dispatch.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PERSISTENT = [
    Path(".openclaw"),
    Path("HEARTBEAT.md"),
    Path("IDENTITY.md"),
    Path("SOUL.md"),
    Path("TOOLS.md"),
    Path("USER.md"),
]


def git(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *cmd], cwd=cwd, text=True).strip()


def required_scope_files(pe_id: str) -> list[Path]:
    return [
        Path(".elis") / "pe" / pe_id / "GOVERNANCE.md",
        Path(".elis") / "pe" / pe_id / "SKILLS_PM.md",
        Path(".elis") / "pe" / pe_id / "SKILLS_IMPLEMENTERS.md",
        Path(".elis") / "pe" / pe_id / "SKILLS_VALIDATORS.md",
    ]


def main() -> int:
    p = argparse.ArgumentParser(description="Check implementation readiness")
    p.add_argument("--repo", default=".")
    p.add_argument("--branch")
    p.add_argument("--head", required=True)
    p.add_argument("--worktree", required=True)
    p.add_argument("--pe-id", required=True)
    p.add_argument(
        "--mode", choices=["implementer", "validator"], default="implementer"
    )
    p.add_argument("--require-persistent-context", action="store_true")
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    worktree = Path(args.worktree).resolve()

    # Check worktree path exists
    if not worktree.exists():
        print("MISSING_WORKTREE", file=sys.stderr)
        return 1

    # Check branch binding
    current_branch = git(["branch", "--show-current"], worktree)
    if args.mode == "implementer":
        if not args.branch:
            print("MISSING_BRANCH", file=sys.stderr)
            return 2
        if current_branch != args.branch:
            print(
                f"WRONG_BRANCH expected={args.branch} actual={current_branch}",
                file=sys.stderr,
            )
            return 2
    else:
        if current_branch:
            print(f"EXPECTED_DETACHED_HEAD actual={current_branch}", file=sys.stderr)
            return 2

    # Check HEAD matches
    current_head = git(["rev-parse", "HEAD"], worktree)
    if current_head != args.head:
        print(
            f"WRONG_HEAD expected={args.head[:12]} actual={current_head[:12]}",
            file=sys.stderr,
        )
        return 3

    # Check no dirty tracked files
    dirty = git(["status", "--short", "--untracked-files=no"], worktree)
    if dirty:
        print("DIRTY_WORKTREE", file=sys.stderr)
        return 4

    # Check persistent context files if required
    if args.require_persistent_context:
        for rel in PERSISTENT:
            if not (worktree / rel).exists():
                print(f"MISSING_PERSISTENT_CONTEXT:{rel}", file=sys.stderr)
                return 5

    # Check PE task packet exists only for implementer mode.
    if args.mode == "implementer":
        pe_task = repo / ".elis" / "pe" / args.pe_id / "PE_TASK.md"
        if not pe_task.exists():
            print("MISSING_PE_TASK", file=sys.stderr)
            return 6

    for rel in required_scope_files(args.pe_id):
        if not (repo / rel).exists():
            print(f"MISSING_SCOPE_FILE:{rel}", file=sys.stderr)
            return 7

    print(f"READY {args.pe_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
