#!/usr/bin/env python3
"""check_validation_readiness.py — validate validator readiness.

Checks worktree scope, expected commit, clean tracked state, artefact
completeness, and forbidden runtime files. Reports runtime workspace
and Git worktree bindings.

The validator authorises the approved branch/HEAD on the fixed validator
worktree — there is no detached-head requirement. The validator worktree
is checked out to the same feature branch as the implementer.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Files that must never appear inside the fixed Git worktree.
WORKTREE_FORBIDDEN = {
    ".openclaw",
    "HEARTBEAT.md",
    "IDENTITY.md",
    "SOUL.md",
    "TOOLS.md",
    "USER.md",
}


def git(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *cmd], cwd=cwd, text=True).strip()


def _report_bindings(worktree: Path) -> list[str]:
    """Report runtime workspace and Git worktree bindings.
    Returns informational lines for display, not failure indicators."""
    lines: list[str] = []
    try:
        cwd = git(["rev-parse", "--show-toplevel"], worktree)
        branch = git(["branch", "--show-current"], worktree) or "(detached)"
        head = git(["rev-parse", "HEAD"], worktree)
        lines.append(f"Authorised Git worktree: {worktree}")
        lines.append(f"Git root: {cwd}")
        lines.append(f"Branch: {branch}")
        lines.append(f"HEAD: {head[:12]}")
        lines.append("Runtime workspace: /home/samurai/openclaw/workspace-infra-val")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        lines.append(f"WARNING: Cannot read bindings: {e}")
    return lines


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

    # Report bindings
    binding_lines = _report_bindings(worktree)
    for line in binding_lines:
        print(line)

    # Check worktree is within allowed root
    if not str(worktree).startswith(str(allowed_root)):
        print("WORKSPACE_MISMATCH", file=sys.stderr)
        return 2

    # Check expected commit
    if git(["rev-parse", "HEAD"], worktree) != args.expected_commit:
        print("MISSING_IMPLEMENTATION_COMMIT", file=sys.stderr)
        return 3

    # Check clean tracked state
    if git(["status", "--short", "--untracked-files=no"], worktree):
        print("LIVE_WORKTREE_NOT_ALLOWED", file=sys.stderr)
        return 4

    # Check for forbidden runtime/bootstrap files inside the Git worktree
    forbidden_found = []
    for f in WORKTREE_FORBIDDEN:
        candidate = worktree / f
        if candidate.exists():
            forbidden_found.append(f)
    if forbidden_found:
        print(
            f"FORBIDDEN_IN_WORKTREE:{','.join(forbidden_found)}",
            file=sys.stderr,
        )
        return 5

    # Check artifact dir exists
    if not artifact_dir.exists():
        print("MISSING_ARTIFACT_DIR", file=sys.stderr)
        return 6

    # Check for stale/unexpected artefacts
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
        return 7

    # Check for expected validation files
    for rel in [
        ".elis/pe/PE-OPS-SKILLS-01/HANDOFF.md",
        ".elis/pe/PE-OPS-SKILLS-01/REVIEW.md",
    ]:
        if not (repo / rel).exists():
            print(f"MISSING_VALIDATION_FILE:{rel}", file=sys.stderr)
            return 8

    print(f"VALIDATION_READY {args.pe_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
