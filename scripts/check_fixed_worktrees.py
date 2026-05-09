#!/usr/bin/env python3
"""check_fixed_worktrees.py — audit fixed canonical worktrees.

Verifies each fixed agent worktree:
  1. Is a Git worktree registered under /opt/elis/repo (via git worktree list).
  2. Has origin pointing to the ELIS GitHub repository.
  3. Has a valid branch, accessible HEAD, and clean tracked state.
  4. Rejects PE-specific runtime worktrees matching /opt/elis/agent-worktrees/PE-*-infra-*.
  5. Detects standalone/broken repos (no origin) like the old pm worktree.
  6. Preserves runtime/bootstrap files — does not flag .openclaw, AGENTS.md,
     SOUL.md, TOOLS.md, USER.md, HEARTBEAT.md as contamination.

Required environment variables:
  CANONICAL_REPO  — path to the canonical Git repository (default: /opt/elis/repo)
  ELIS_GITHUB_REMOTE — expected origin URL (default: https://github.com/rochasamurai/ELIS-Multi-AI-Agent-Platform.git)

Usage:
  python scripts/check_fixed_worktrees.py [--worktrees PM INFRA_IMPL_A INFRA_IMPL_B INFRA_VAL_A INFRA_VAL_B GITHUB_AGENT]

Exit codes:
  0 — all worktrees pass
  1 — one or more failures
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

CANONICAL_REPO_DEFAULT = "/opt/elis/repo"
ELIS_GITHUB_REMOTE_DEFAULT = (
    "https://github.com/rochasamurai/ELIS-Multi-AI-Agent-Platform.git"
)

# Runtime/bootstrap files that must be preserved, not flagged.
PRESERVED_FILES = {
    ".openclaw",
    "AGENTS.md",
    "SOUL.md",
    "TOOLS.md",
    "USER.md",
    "HEARTBEAT.md",
    "IDENTITY.md",
}

# Fixed canonical worktrees for agent roles.
DEFAULT_FIXED_WORKTREES = [
    "/opt/elis/agent-worktrees/pm",
    "/opt/elis/agent-worktrees/infra-impl-a",
    "/opt/elis/agent-worktrees/infra-impl-b",
    "/opt/elis/agent-worktrees/infra-val-a",
    "/opt/elis/agent-worktrees/infra-val-b",
    "/opt/elis/agent-worktrees/github-agent",
]


def _git_cmd(*args: str, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + list(args),
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=30,
    )


def _get_registered_worktrees(canonical_repo: str) -> list[dict]:
    """Return list of worktree dicts registered under canonical_repo."""
    result = _git_cmd("worktree", "list", cwd=canonical_repo)
    if result.returncode != 0:
        print(f"FAIL: Cannot list worktrees in {canonical_repo}: {result.stderr}")
        sys.exit(1)

    worktrees = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split()
        if len(parts) < 3:
            continue
        path = Path(parts[0]).resolve().as_posix()
        head = parts[1]
        branch_raw = " ".join(parts[2:]) if len(parts) > 2 else "(detached HEAD)"
        branch = branch_raw.strip("[]")
        worktrees.append({"path": path, "head": head, "branch": branch})

    return worktrees


def _is_pe_specific_runtime(path: str) -> bool:
    """Return True if path matches a PE-specific runtime worktree pattern."""
    return bool(re.match(r"/opt/elis/agent-worktrees/PE-.+-infra-.+", path))


def _check_worktree(
    path: str,
    registered_paths: set[str],
    expected_origin: str,
) -> list[str]:
    """Check a single worktree path. Return list of failure messages."""
    failures: list[str] = []

    # Check 0: path exists
    p = Path(path)
    if not p.is_dir():
        failures.append(f"Worktree path does not exist: {path}")
        return failures

    resolved = p.resolve().as_posix()

    # Check 1: registered under canonical repo
    if resolved not in registered_paths:
        failures.append(
            f"NOT REGISTERED: {resolved} is not a registered worktree of "
            f"{CANONICAL_REPO_DEFAULT}. It may be a standalone/broken repo."
        )

    # Check 2: reject PE-specific runtime worktrees
    if _is_pe_specific_runtime(resolved):
        failures.append(
            f"PE-SPECIFIC RUNTIME REJECTED: {resolved} matches "
            f"PE-*-infra-* pattern. Use fixed canonical worktrees only."
        )

    # Check 3: has origin remote
    result = _git_cmd("remote", "get-url", "origin", cwd=resolved)
    if result.returncode != 0:
        failures.append(
            f"NO ORIGIN: {resolved} has no 'origin' remote. "
            f"This is a standalone/broken Git repo."
        )
    else:
        actual_origin = result.stdout.strip()
        if actual_origin != expected_origin:
            failures.append(
                f"WRONG ORIGIN: {resolved} origin is '{actual_origin}', "
                f"expected '{expected_origin}'."
            )

    # Check 4: can get a branch/HEAD
    branch_result = _git_cmd("branch", "--show-current", cwd=resolved)
    head_result = _git_cmd("rev-parse", "HEAD", cwd=resolved)
    if head_result.returncode != 0:
        failures.append(f"BROKEN HEAD: {resolved} cannot resolve HEAD.")
    else:
        head = head_result.stdout.strip()
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else ""
        status = f"branch={branch or '(detached)'}" if branch else "branch=(detached)"
        failures.append(f"STATUS OK: {resolved} — HEAD={head[:12]}(...) {status}")

    # Check 5: tracked file cleanliness (ignoring preserved runtime files)
    status_result = _git_cmd("status", "--porcelain", cwd=resolved)
    if status_result.returncode == 0:
        dirty_tracked = []
        for line in status_result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            # Porcelain format: XY filename
            xy = line[:2].strip()
            filename = line[3:].strip()
            # Ignore untracked (? prefixed) and preserved files
            if xy.startswith("?"):
                basename = os.path.basename(filename)
                if basename in PRESERVED_FILES:
                    continue
                # Check if it's a path containing preserved files
                parts = Path(filename).parts
                if any(part in PRESERVED_FILES for part in parts):
                    continue
                dirty_tracked.append(f"  untracked: {filename}")
            elif xy != "  ":
                basename = os.path.basename(filename)
                if basename in PRESERVED_FILES:
                    continue
                parts = Path(filename).parts
                if any(part in PRESERVED_FILES for part in parts):
                    continue
                dirty_tracked.append(f"  {xy}: {filename}")

        if dirty_tracked:
            failures.append("UNTRACKED OR MODIFIED FILES:")
            failures.extend(dirty_tracked)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit fixed canonical worktrees for ELIS dispatch gating."
    )
    parser.add_argument(
        "--worktrees",
        nargs="*",
        default=DEFAULT_FIXED_WORKTREES,
        help="Fixed worktree paths to audit (default: all agent worktrees).",
    )
    parser.add_argument(
        "--canonical-repo",
        default=os.environ.get("CANONICAL_REPO", CANONICAL_REPO_DEFAULT),
        help="Canonical Git repository path.",
    )
    parser.add_argument(
        "--expected-origin",
        default=os.environ.get("ELIS_GITHUB_REMOTE", ELIS_GITHUB_REMOTE_DEFAULT),
        help="Expected origin URL for worktrees.",
    )
    args = parser.parse_args()

    canonical_repo = args.canonical_repo
    expected_origin = args.expected_origin

    # Ensure canonical_repo exists
    if not Path(canonical_repo).is_dir():
        print(f"FAIL: Canonical repo not found: {canonical_repo}")
        return 1

    # Get registered worktree paths
    registered = _get_registered_worktrees(canonical_repo)
    registered_paths = {w["path"] for w in registered}

    all_failures: list[str] = []
    all_pass: list[str] = []

    print(f"Auditing fixed worktrees against canonical repo: {canonical_repo}")
    print(f"Expected remote: {expected_origin}")
    print()

    for wt_path in args.worktrees:
        print(f"--- Checking: {wt_path} ---")
        failures = _check_worktree(wt_path, registered_paths, expected_origin)
        if failures:
            # Separate informational STATUS lines from actual failures
            status_lines = [f for f in failures if f.startswith("STATUS OK:")]
            actual_failures = [f for f in failures if not f.startswith("STATUS OK:")]
            if status_lines:
                for line in status_lines:
                    print(f"  {line}")
            if actual_failures:
                all_failures.append(f"FAILURES for {wt_path}:")
                for f in actual_failures:
                    print(f"  FAIL: {f}")
                    all_failures.append(f"  {f}")
            else:
                print("  PASS")
                all_pass.append(wt_path)
        else:
            print("  PASS")
            all_pass.append(wt_path)
        print()

    # Summary
    print("=" * 60)
    print(f"Worktrees audited: {len(args.worktrees)}")
    print(f"Passed: {len(all_pass)}")
    print(f"Failed: {len(all_failures)}")

    if all_pass:
        for p in all_pass:
            print(f"  PASS  {p}")
    if all_failures:
        for f in all_failures:
            print(f"  FAIL  {f}")

    return 0 if not all_failures else 1


if __name__ == "__main__":
    sys.exit(main())
