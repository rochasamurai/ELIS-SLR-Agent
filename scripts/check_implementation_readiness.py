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
    p.add_argument("--branch", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--worktree", required=True)
    p.add_argument("--pe-id", required=True)
    args = p.parse_args()
    repo = Path(args.repo).resolve()
    worktree = Path(args.worktree).resolve()
    if git(["branch", "--show-current"], worktree) != args.branch:
        print("WRONG_BRANCH", file=sys.stderr)
        return 2
    if git(["rev-parse", "HEAD"], worktree) != args.head:
        print("WRONG_HEAD", file=sys.stderr)
        return 3
    if git(["status", "--short", "--untracked-files=no"], worktree):
        print("DIRTY_WORKTREE", file=sys.stderr)
        return 4
    for rel in PERSISTENT:
        if not (repo / rel).exists():
            print(f"MISSING_PERSISTENT_CONTEXT:{rel}", file=sys.stderr)
            return 5
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
