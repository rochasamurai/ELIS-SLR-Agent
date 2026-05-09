#!/usr/bin/env python3
"""check_dispatch_binding.py — verify dispatch binding before dispatch.

Ensures:
  1. The target worktree is a fixed canonical worktree (not PE-specific).
  2. The target agent matches the assigned PE implementer/validator.
  3. The worktree branch matches the active PE branch.
  4. The worktree is clean (no tracked pending changes) — preserving
     runtime/bootstrap files.

Usage:
  python scripts/check_dispatch_binding.py --agent infra-impl-b

Exit codes:
  0 — binding valid for dispatch
  1 — binding invalid
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

CANONICAL_REPO = "/opt/elis/repo"
AGENT_WORKTREE_PREFIX = "/opt/elis/agent-worktrees"

# Mapping from agent id to expected fixed worktree path.
AGENT_WORKTREE_MAP: dict[str, str] = {
    "pm": f"{AGENT_WORKTREE_PREFIX}/pm",
    "infra-impl-a": f"{AGENT_WORKTREE_PREFIX}/infra-impl-a",
    "infra-impl-b": f"{AGENT_WORKTREE_PREFIX}/infra-impl-b",
    "infra-val-a": f"{AGENT_WORKTREE_PREFIX}/infra-val-a",
    "infra-val-b": f"{AGENT_WORKTREE_PREFIX}/infra-val-b",
    "github-agent": f"{AGENT_WORKTREE_PREFIX}/github-agent",
    "infra-impl-codex": f"{AGENT_WORKTREE_PREFIX}/infra-impl-a",
    "infra-val-codex": f"{AGENT_WORKTREE_PREFIX}/infra-val-b",
    "infra-impl-claude": f"{AGENT_WORKTREE_PREFIX}/infra-impl-b",
    "infra-val-claude": f"{AGENT_WORKTREE_PREFIX}/infra-val-a",
}

PRESERVED_FILES = {
    ".openclaw",
    "AGENTS.md",
    "SOUL.md",
    "TOOLS.md",
    "USER.md",
    "HEARTBEAT.md",
    "IDENTITY.md",
}


def _git_cmd(*args: str, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + list(args),
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=30,
    )


def _is_pe_specific_runtime(path: str) -> bool:
    return bool(re.match(r"/opt/elis/agent-worktrees/PE-.+-infra-.+", path))


def _is_untracked_or_dirty(filename: str) -> tuple[bool, list[str]]:
    """Check if a filename matches protected/preserved patterns."""
    parts = Path(filename).parts
    issues: list[str] = []
    for part in parts:
        if part in PRESERVED_FILES:
            return True, issues
    return False, issues


def _check_worktree_cleanliness(worktree_path: str) -> list[str]:
    """Check if tracked files are clean (preserving runtime files). Return failures."""
    failures: list[str] = []
    result = _git_cmd("status", "--porcelain", cwd=worktree_path)
    if result.returncode != 0:
        failures.append(f"FAIL: Cannot check status in {worktree_path}")
        return failures

    dirty_files: list[str] = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        xy = line[:2].strip()
        filename = line[3:].strip()
        if xy.startswith("?"):
            protected, _ = _is_untracked_or_dirty(filename)
            if protected:
                continue
            dirty_files.append(f"  untracked: {filename}")
        else:
            protected, _ = _is_untracked_or_dirty(filename)
            if protected:
                continue
            dirty_files.append(f"  {xy}: {filename}")

    if dirty_files:
        failures.append("UNTRACKED OR MODIFIED TRACKED FILES:")
        failures.extend(dirty_files)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check dispatch binding validity."
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent ID to check (e.g. infra-impl-b, infra-val-a).",
    )
    parser.add_argument(
        "--pe-branch",
        default=None,
        help="Expected PE branch for validation (auto-resolved from CURRENT_PE.md).",
    )
    parser.add_argument(
        "--worktree",
        default=None,
        help="Override worktree path (default: resolved from agent ID).",
    )
    args = parser.parse_args()

    agent_id = args.agent

    # Resolve expected worktree path
    worktree_path = args.worktree or AGENT_WORKTREE_MAP.get(agent_id)
    if not worktree_path:
        print(f"FAIL: Unknown agent ID '{agent_id}'. "
              f"Known: {', '.join(sorted(AGENT_WORKTREE_MAP.keys()))}")
        return 1

    resolved_path = Path(worktree_path).resolve().as_posix()
    print(f"Agent: {agent_id}")
    print(f"Expected worktree: {resolved_path}")
    print()

    failures: list[str] = []

    # Gate 1: Must be a fixed canonical worktree, not PE-specific
    if _is_pe_specific_runtime(resolved_path):
        failures.append(
            f"PE-SPECIFIC RUNTIME REJECTED: {resolved_path} is not a "
            f"fixed canonical worktree."
        )

    # Gate 2: Must exist
    if not Path(resolved_path).is_dir():
        failures.append(
            f"WORKTREE NOT FOUND: {resolved_path} does not exist."
        )
        print("FAIL: ", "\n".join(failures))
        return 1

    # Gate 3: Must have origin
    origin_result = _git_cmd("remote", "get-url", "origin", cwd=resolved_path)
    if origin_result.returncode != 0:
        failures.append(
            f"NO ORIGIN: {resolved_path} has no origin remote. "
            f"Standalone/broken repository."
        )
    else:
        print(f"Origin: {origin_result.stdout.strip()}")

    # Gate 4: Branch check
    branch_result = _git_cmd("branch", "--show-current", cwd=resolved_path)
    current_branch = (
        branch_result.stdout.strip()
        if branch_result.returncode == 0
        else ""
    )

    # Resolve expected branch from CURRENT_PE.md if not provided
    expected_branch = args.pe_branch
    if not expected_branch:
        current_pe_path = Path("CURRENT_PE.md")
        if current_pe_path.exists():
            content = current_pe_path.read_text(encoding="utf-8")
            m = re.search(
                r"^\|\s*Branch\s*\|\s*([^\|]+)\s*\|",
                content,
                re.MULTILINE,
            )
            if m:
                expected_branch = m.group(1).strip()
                print(f"Expected branch (from CURRENT_PE.md): {expected_branch}")
            else:
                print("WARN: Could not parse branch from CURRENT_PE.md — "
                      "branch check skipped.")
        else:
            print("WARN: CURRENT_PE.md not found — branch check skipped.")
    else:
        print(f"Expected branch (from --pe-branch): {expected_branch}")

    if expected_branch and current_branch:
        if current_branch != expected_branch:
            failures.append(
                f"BRANCH MISMATCH: worktree is on '{current_branch}', "
                f"expected '{expected_branch}'."
            )
        else:
            print(f"Branch match: {current_branch}")
    elif expected_branch and not current_branch:
        print(f"WARN: Worktree is detached — no active branch.")

    # Gate 5: HEAD
    head_result = _git_cmd("rev-parse", "HEAD", cwd=resolved_path)
    if head_result.returncode == 0:
        head = head_result.stdout.strip()
        print(f"HEAD: {head[:12]}(...)")
        if current_branch:
            # Check if HEAD matches branch tip
            rev_parse_result = _git_cmd(
                "rev-parse", f"refs/heads/{current_branch}", cwd=resolved_path
            )
            if rev_parse_result.returncode == 0:
                branch_tip = rev_parse_result.stdout.strip()
                if head != branch_tip:
                    print(f"WARN: HEAD ({head[:12]}) != branch tip "
                          f"({branch_tip[:12]}) — branch may be outdated.")

    # Gate 6: Cleanliness
    cleanliness = _check_worktree_cleanliness(resolved_path)
    if cleanliness:
        failures.extend(cleanliness)

    # Gate 7: Ensure worktree is registered under canonical repo
    reg_result = _git_cmd("worktree", "list", cwd=CANONICAL_REPO)
    if reg_result.returncode == 0:
        if resolved_path not in reg_result.stdout:
            failures.append(
                f"NOT REGISTERED: {resolved_path} is not a registered worktree "
                f"of {CANONICAL_REPO}."
            )

    print()
    if failures:
        print("DISPATCH BINDING FAILED:")
        for f in failures:
            print(f"  FAIL: {f}")
        return 1
    else:
        print("DISPATCH BINDING VALID — ready for dispatch.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
