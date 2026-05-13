#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def git(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *cmd], cwd=cwd, text=True).strip()


def main() -> int:
    p = argparse.ArgumentParser(description="Check PE dispatch binding")
    p.add_argument("--repo", default=".")
    p.add_argument("--pe-id", required=True)
    p.add_argument("--branch")
    p.add_argument("--head", required=True)
    p.add_argument("--worktree", required=True)
    p.add_argument("--mode", choices=["implementer", "validator"], default="implementer")
    args = p.parse_args()
    repo = Path(args.repo).resolve()
    worktree = Path(args.worktree).resolve()
    if git(["rev-parse", "--show-toplevel"], repo) != str(repo):
        print("WORKTREE_MISMATCH: repo root mismatch", file=sys.stderr)
        return 2
    current_branch = git(["branch", "--show-current"], worktree)
    if args.mode == "implementer":
        if not args.branch:
            print("MISSING_BRANCH", file=sys.stderr)
            return 3
        if current_branch != args.branch:
            print("WRONG_BRANCH", file=sys.stderr)
            return 3
    else:
        if current_branch:
            print("EXPECTED_DETACHED_HEAD", file=sys.stderr)
            return 3
    if git(["rev-parse", "HEAD"], worktree) != args.head:
        print("WRONG_HEAD", file=sys.stderr)
        return 4
    if git(["status", "--short", "--untracked-files=no"], worktree):
        print("DIRTY_WORKTREE", file=sys.stderr)
        return 5
    pe_task = repo / ".elis" / "pe" / args.pe_id / "PE_TASK.md"
    if not pe_task.exists():
        print("MISSING_PE_TASK", file=sys.stderr)
        return 6
    print(f"OK {args.pe_id} {args.branch} {args.head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
