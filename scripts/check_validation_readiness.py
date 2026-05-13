#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def git(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *cmd], cwd=cwd, text=True).strip()


def main() -> int:
    p = argparse.ArgumentParser(description="Check validation readiness")
    p.add_argument("--repo", default=".")
    p.add_argument("--worktree", required=True)
    p.add_argument("--expected-commit", required=True)
    p.add_argument("--allowed-root", required=True)
    p.add_argument("--artifact-dir", required=True)
    p.add_argument("--pe-id", required=True)
    args = p.parse_args()
    repo = Path(args.repo).resolve()
    worktree = Path(args.worktree).resolve()
    allowed_root = Path(args.allowed_root).resolve()
    artifact_dir = Path(args.artifact_dir).resolve()
    if not str(worktree).startswith(str(allowed_root)):
        print("WORKSPACE_MISMATCH", file=sys.stderr)
        return 2
    if git(["rev-parse", "HEAD"], worktree) != args.expected_commit:
        print("MISSING_IMPLEMENTATION_COMMIT", file=sys.stderr)
        return 3
    if git(["status", "--short", "--untracked-files=no"], worktree):
        print("LIVE_WORKTREE_NOT_ALLOWED", file=sys.stderr)
        return 4
    if not artifact_dir.exists():
        print("MISSING_ARTIFACT_DIR", file=sys.stderr)
        return 5
    allowed = {
        "PE_TASK.md",
        "GOVERNANCE.md",
        "SKILLS_PM.md",
        "SKILLS_IMPLEMENTERS.md",
        "SKILLS_VALIDATORS.md",
        "SKILLS_GITHUB_GATEWAY.md",
        "HANDOFF.md",
        "REVIEW.md",
    }
    seen = {p.name for p in artifact_dir.iterdir() if p.is_file()}
    unexpected = sorted(seen - allowed)
    if unexpected:
        print(f"STALE_PE_ARTIFACTS:{','.join(unexpected)}", file=sys.stderr)
        return 6
    for rel in [
        ".elis/pe/PE-OPS-SKILLS-01/HANDOFF.md",
        ".elis/pe/PE-OPS-SKILLS-01/REVIEW.md",
    ]:
        if not (repo / rel).exists():
            print(f"MISSING_VALIDATION_FILE:{rel}", file=sys.stderr)
            return 7
    print(f"VALIDATION_READY {args.pe_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
