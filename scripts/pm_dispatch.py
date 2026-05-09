#!/usr/bin/env python3
"""pm_dispatch.py — orchestration dispatch gate for PM.

Enforces all dispatch gates before an agent can be dispatched:

  1. Fixed worktree check (check_fixed_worktrees.py)
  2. Dispatch binding check (check_dispatch_binding.py)
  3. Reset acknowledgement check (check_reset_ack.py)
  4. Active run evidence check (check_active_run.py)

This script is the single entry point for PM to verify all dispatch
conditions before dispatching any agent to implement or validate a PE.

Required HANDOFF/evidence check before validator dispatch:
  When role is 'validator', also validates that HANDOFF.md exists,
  has all required sections, and the PE evidence directory has
  implementer evidence before allowing validator dispatch.

Usage:
  python scripts/pm_dispatch.py --pe-id PE-OPS-WORKTREE-BINDING-02 \\
      --agent infra-impl-b [--role implementer|validator] [--dry-run]

Exit codes:
  0 — all gates pass, dispatch permitted
  1 — one or more gates fail, dispatch prohibited
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Required sections in HANDOFF.md for validator dispatch.
HANDOFF_REQUIRED_SECTIONS = [
    "## Summary",
    "## Files Changed",
    "## Acceptance Criteria",
    "## Validation Commands",
]


def _run_script(script_name: str, args: list[str]) -> subprocess.CompletedProcess:
    """Run one of the gate scripts."""
    script_path = Path("scripts") / script_name
    cmd = [sys.executable, str(script_path)] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _check_handoff_for_validator(pe_id: str) -> list[str]:
    """Check HANDOFF.md completeness before validator dispatch."""
    failures: list[str] = []

    handoff_path = Path("HANDOFF.md")
    if not handoff_path.exists():
        failures.append("HANDOFF.md not found — required before validator dispatch.")
        return failures

    content = handoff_path.read_text(encoding="utf-8")
    missing = [s for s in HANDOFF_REQUIRED_SECTIONS if s not in content]
    if missing:
        failures.append(
            f"HANDOFF.md incomplete — missing sections: {', '.join(missing)}"
        )

    # Check PE evidence directory for implementer evidence
    evidence_dir = Path(f".elis/pe/{pe_id}/evidence")
    if not evidence_dir.is_dir():
        failures.append(
            f"PE evidence directory not found: .elis/pe/{pe_id}/evidence/ — "
            f"implementer evidence required before validator dispatch."
        )
    else:
        evidence_files = list(evidence_dir.iterdir())
        if not evidence_files:
            failures.append(
                f"PE evidence directory is empty: .elis/pe/{pe_id}/evidence/ — "
                f"no implementer evidence for validator review."
            )

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="PM dispatch gate orchestration.")
    parser.add_argument(
        "--pe-id",
        required=True,
        help="PE ID (e.g. PE-OPS-WORKTREE-BINDING-02).",
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent ID (e.g. infra-impl-b).",
    )
    parser.add_argument(
        "--role",
        choices=["implementer", "validator"],
        default="implementer",
        help="Agent role (default: implementer).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print gate results without dispatching.",
    )
    parser.add_argument(
        "--skip-worktree-check",
        action="store_true",
        help="Skip the fixed-worktree audit (use for focused tests).",
    )
    parser.add_argument(
        "--skip-handoff-check",
        action="store_true",
        help="Skip HANDOFF/evidence check (use for implementer dispatch).",
    )
    args = parser.parse_args()

    pe_id = args.pe_id
    agent_id = args.agent
    role = args.role

    print(f"{'=' * 60}")
    print(f"PM DISPATCH GATE — {agent_id} ({role})")
    print(f"PE: {pe_id}")
    print(f"{'=' * 60}")
    print()

    all_failures: list[str] = []
    all_passes: list[str] = []

    # === Gate 1: Fixed Worktree Check ===
    print("--- [Gate 1] Fixed Worktree Audit ---")
    if args.skip_worktree_check:
        print("  SKIPPED (--skip-worktree-check)")
        all_passes.append("Gate 1 (worktree audit, skipped)")
    else:
        result = _run_script(
            "check_fixed_worktrees.py",
            ["--worktrees"] + [f"/opt/elis/agent-worktrees/{agent_id}"],
        )
        if result.returncode == 0:
            print("  PASS")
            all_passes.append("Gate 1 (fixed worktree audit)")
        else:
            lines = [
                line
                for line in result.stdout.split("\n")
                if "FAIL" in line or "PASS" in line
            ]
            for line in lines:
                print(f"  {line}")
            all_failures.append("Gate 1 (fixed worktree audit) — see above")
    print()

    # === Gate 2: Dispatch Binding Check ===
    print("--- [Gate 2] Dispatch Binding Check ---")
    result = _run_script("check_dispatch_binding.py", ["--agent", agent_id])
    if result.returncode == 0:
        print("  PASS")
        all_passes.append("Gate 2 (dispatch binding)")
    else:
        for line in result.stdout.split("\n"):
            if "FAIL" in line or "FAILED" in line:
                print(f"  {line}")
            elif result.stderr:
                print(f"  {result.stderr}")
        all_failures.append("Gate 2 (dispatch binding) — see above")
    print()

    # === Gate 3: Reset Acknowledgement Check ===
    print("--- [Gate 3] Reset Acknowledgement (NO_RESET_ACK_NO_DISPATCH) ---")
    result = _run_script("check_reset_ack.py", ["--pe-id", pe_id, "--agent", agent_id])
    if result.returncode == 0:
        print("  PASS")
        all_passes.append("Gate 3 (reset acknowledgement)")
    else:
        for line in result.stdout.split("\n"):
            if "FAIL" in line:
                print(f"  {line}")
        all_failures.append("Gate 3 (reset acknowledgement) — see above")
    print()

    # === Gate 4: Active Run Evidence Check ===
    print("--- [Gate 4] Active Run Evidence ---")
    print("  (NO_ACTIVE_RUN_EVIDENCE_NO_IN_PROGRESS_STATUS)")
    result = _run_script("check_active_run.py", ["--pe-id", pe_id, "--agent", agent_id])
    if result.returncode == 0:
        print("  PASS")
        all_passes.append("Gate 4 (active run evidence)")
    elif result.returncode == 2:
        print("  INFO: Evidence found but invalid")
        for line in result.stdout.split("\n"):
            if "FAIL" in line:
                print(f"  {line}")
        all_passes.append("Gate 4 (active run evidence, invalid but noted)")
    else:
        print(
            "  INFO: No active run evidence — status must be NOT_STARTED/STALLED/FAILED"
        )
        all_passes.append("Gate 4 (active run, no evidence)")
    print()

    # === Gate 5: HANDOFF/Evidence check (validator only) ===
    if role == "validator" and not args.skip_handoff_check:
        print("--- [Gate 5] HANDOFF/Evidence Check (validator gate) ---")
        handoff_issues = _check_handoff_for_validator(pe_id)
        if handoff_issues:
            for issue in handoff_issues:
                print(f"  FAIL: {issue}")
            all_failures.append("Gate 5 (HANDOFF/evidence check) — see above")
        else:
            print("  PASS — HANDOFF.md and PE evidence present")
            all_passes.append("Gate 5 (HANDOFF/evidence check)")
        print()

    # === Summary ===
    print(f"{'=' * 60}")
    print("DISPATCH GATE SUMMARY")
    print(f"{'=' * 60}")
    print(f"Agent: {agent_id} | PE: {pe_id} | Role: {role}")
    print(f"Passes: {len(all_passes)}")
    print(f"Failures: {len(all_failures)}")
    print()

    for p in all_passes:
        print(f"  PASS  {p}")
    for f in all_failures:
        print(f"  FAIL  {f}")
    print()

    if args.dry_run:
        if all_failures:
            print("DRY-RUN: Would PROHIBIT dispatch due to failures above.")
            return 1
        else:
            print("DRY-RUN: Would ALLOW dispatch. All gates pass.")
            return 0

    if all_failures:
        print("DISPATCH PROHIBITED — one or more gates failed.")
        return 1
    else:
        print("DISPATCH ALLOWED — all gates pass.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
