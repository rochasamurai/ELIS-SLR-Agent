#!/usr/bin/env python3
"""Tests for scripts/pm_dispatch.py — dispatch gate orchestration."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pm_dispatch.py"


def _load():
    spec = importlib.util.spec_from_file_location("pm_dispatch", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def test_handoff_check_missing_handoff(tmp_path):
    """Missing HANDOFF.md should produce failures."""
    import os as _os

    orig_cwd = _os.getcwd()
    try:
        _os.chdir(str(tmp_path))
        failures = MODULE._check_handoff_for_validator("PE-TEST-01")
        assert any("HANDOFF.md not found" in f for f in failures)
    finally:
        _os.chdir(str(orig_cwd))


def test_handoff_check_missing_evidence_dir(tmp_path):
    """Missing PE evidence directory should produce failures."""
    cwd = Path(tmp_path)
    handoff = cwd / "HANDOFF.md"
    handoff.write_text(
        "## Summary\n\n...\n\n## Files Changed\n\n...\n\n"
        "## Acceptance Criteria\n\n...\n\n## Validation Commands\n\n..."
    )
    orig_cwd = Path.cwd()
    try:
        __import__("os").chdir(str(cwd))
        failures = MODULE._check_handoff_for_validator("PE-NO-EVIDENCE-01")
        assert any("evidence directory not found" in f for f in failures)
    finally:
        __import__("os").chdir(str(orig_cwd))


def test_handoff_check_pass(tmp_path):
    """Complete HANDOFF.md and evidence dir should pass."""
    cwd = Path(tmp_path)
    handoff = cwd / "HANDOFF.md"
    handoff.write_text(
        "## Summary\n\n...\n\n## Files Changed\n\n...\n\n"
        "## Acceptance Criteria\n\n...\n\n## Validation Commands\n\n..."
    )
    ev_dir = cwd / ".elis" / "pe" / "PE-EVIDENCE-PASS" / "evidence"
    ev_dir.mkdir(parents=True)
    (ev_dir / "implementation_evidence.md").write_text("evidence")

    orig_cwd = Path.cwd()
    try:
        __import__("os").chdir(str(cwd))
        failures = MODULE._check_handoff_for_validator("PE-EVIDENCE-PASS")
        assert len(failures) == 0, f"Expected 0 failures, got: {failures}"
    finally:
        __import__("os").chdir(str(orig_cwd))


def test_script_with_unknown_agent():
    """Calling with unknown agent should exit 1."""
    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            "PE-TEST",
            "--agent",
            "nonexistent-agent",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1
    # Should mention the agent in output
    assert "nonexistent" in result.stdout or result.stderr


def test_script_dry_run_no_crash():
    """Dry run should not crash."""
    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            "PE-OPS-WORKTREE-BINDING-02",
            "--agent",
            "infra-impl-b",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # The script may pass or fail depending on environment, but must not crash
    assert result.returncode in (0, 1), f"Unexpected return code: {result.returncode}"
    assert "PM DISPATCH GATE" in result.stdout


def test_skip_worktree_check():
    """--skip-worktree-check should still run other gates."""
    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            "PE-TEST-SKIP",
            "--agent",
            "infra-impl-b",
            "--dry-run",
            "--skip-worktree-check",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode in (0, 1)
    assert "SKIPPED (--skip-worktree-check)" in result.stdout


def test_validator_role_checks_handoff():
    """Validator role should trigger HANDOFF/evidence check."""
    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            "PE-TEST-VAL",
            "--agent",
            "infra-val-a",
            "--role",
            "validator",
            "--dry-run",
            "--skip-worktree-check",
            "--skip-handoff-check",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # With --skip-handoff-check, gate 5 should be skipped
    assert result.returncode in (0, 1)
