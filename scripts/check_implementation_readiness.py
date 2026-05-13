#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PERSISTENT = [Path('.openclaw'), Path('HEARTBEAT.md'), Path('IDENTITY.md'), Path('SOUL.md'), Path('TOOLS.md'), Path('USER.md')]


def git(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *cmd], cwd=cwd, text=True).strip()


def main() -> int:
    p = argparse.ArgumentParser(description="Check implementation readiness")
    p.add_argument("--repo", default=".")
    p.add_argument("--branch")
    p.add_argument("--head", required=True)
    p.add_argument("--worktree", required=True)
    p.add_argument("--pe-id", required=True)
    p.add_argument("--mode", choices=["implementer", "validator"], default="implementer")
    p.add_argument("--require-persistent-context", action="store_true")
    args = p.parse_args()
    repo = Path(args.repo).resolve()
    worktree = Path(args.worktree).resolve()
    current_branch = git(["branch", "--show-current"], worktree)
    if args.mode == "implementer":
        if not args.branch:
            print("MISSING_BRANCH", file=sys.stderr)
            return 3
        if current_branch != args.branch:
            print("WRONG_BRANCH", file=sys.stderr)
            return 2
    else:
        if current_branch:
            print("EXPECTED_DETACHED_HEAD", file=sys.stderr)
            return 2
    if git(["rev-parse", "HEAD"], worktree) != args.head:
        print("WRONG_HEAD", file=sys.stderr)
        return 3
    if git(["status", "--short", "--untracked-files=no"], worktree):
        print("DIRTY_WORKTREE", file=sys.stderr)
        return 4
    if args.require_persistent_context:
        for rel in PERSISTENT:
            if not (repo / rel).exists():
                print(f"MISSING_PERSISTENT_CONTEXT:{rel}", file=sys.stderr)
                return 5
    elif args.mode == "validator":
        print("PERSISTENT_CONTEXT_OPTIONAL", file=sys.stderr)
    for rel in [
        ".elis/pe/PE-OPS-SKILLS-01/GOVERNANCE.md",
        ".elis/pe/PE-OPS-SKILLS-01/SKILLS_PM.md",
        ".elis/pe/PE-OPS-SKILLS-01/SKILLS_IMPLEMENTERS.md",
        ".elis/pe/PE-OPS-SKILLS-01/SKILLS_VALIDATORS.md",
    ]:
        if not (repo / rel).exists():
            print(f"MISSING_SCOPE_FILE:{rel}", file=sys.stderr)
            return 6
    print(f"READY {args.pe_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
