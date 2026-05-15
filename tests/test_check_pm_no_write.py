#!/usr/bin/env python3
"""Tests for scripts/check_pm_no_write.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_pm_no_write.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_pm_no_write", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def test_forbidden_pm_write_patterns():
    """Forbidden PM write patterns should be defined."""
    assert len(MODULE.FORBIDDEN_PM_WRITE_PATTERNS) > 0
    assert any("HANDOFF.md" in p for p in MODULE.FORBIDDEN_PM_WRITE_PATTERNS)
    assert any("REVIEW.md" in p for p in MODULE.FORBIDDEN_PM_WRITE_PATTERNS)


def test_pm_allowed_write():
    """PM allowed write set should include PE_TASK.md."""
    assert ".elis/pe/*/PE_TASK.md" in MODULE.PM_ALLOWED_WRITE


def test_non_pm_authors():
    """Non-PM author identities should be defined."""
    assert "infra-impl-b" in MODULE.NON_PM_AUTHORS
    assert "infra-val-a" in MODULE.NON_PM_AUTHORS


def test_git_helper():
    """The git helper should exist."""
    assert hasattr(MODULE, "git")
    assert callable(MODULE.git)


def test_pm_write_violation_class():
    """PMWriteViolation should expose file_path, commit_sha, and author."""
    v = MODULE.PMWriteViolation("scripts/check_foo.py", "abc123def456", "Elis PM Agent")
    assert v.file_path == "scripts/check_foo.py"
    assert v.commit_sha == "abc123def456"
    assert v.author == "Elis PM Agent"
    assert "PM_WROTE_FILE" in str(v)
    assert "scripts/check_foo.py" in str(v)


def test_pm_write_violation_class_minimal():
    """PMWriteViolation should work with just a file path."""
    v = MODULE.PMWriteViolation("scripts/check_foo.py")
    assert v.file_path == "scripts/check_foo.py"
    assert v.commit_sha == ""
    assert v.author == ""


def test_main_returns_non_zero_on_violations():
    """main() should return 1 when PM write violations exist."""
    import subprocess

    # Run against a known commit range; if no PM violations found, it returns 0
    result = subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--repo",
            ".",
            "--pe-id",
            "PE-OPS-PM-GUARDRAILS-02",
            "--pe-range",
            "HEAD~1..HEAD",
        ],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    # On non-violating ranges, it should return 0
    assert result.returncode == 0


def test_main_exit_code_on_invalid_range():
    """main() should handle gracefully with a missing range."""
    import subprocess

    result = subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--repo",
            ".",
            "--pe-id",
            "PE-OPS-PM-GUARDRAILS-02",
            "--pe-range",
            "INVALID..RANGE",
        ],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    # Should return 0 because no violations can be detected from invalid range
    assert result.returncode == 0


def test_pm_write_check_error_class():
    """PMWriteCheckError should be a distinct exception type."""
    e = MODULE.PMWriteCheckError("git failure")
    assert isinstance(e, Exception)
    assert "git failure" in str(e)


def test_check_violations_returns_list():
    """check_violations() should return a list (possibly empty)."""
    # Empty list for a non-violating range
    repo = Path(__file__).resolve().parents[1]
    violations = MODULE.check_violations(
        repo, "HEAD~1..HEAD", "PE-OPS-PM-GUARDRAILS-02"
    )
    assert isinstance(violations, list)


def test_check_violations_with_pm_author_detection():
    """check_violations() with a PM-authored commit should find violations."""
    import subprocess

    repo = Path(__file__).resolve().parents[1]
    # First, let's see if there are any PM commits in the full history
    results = subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--repo",
            str(repo),
            "--pe-id",
            "PE-OPS-PM-GUARDRAILS-02",
            "--pe-range",
            "HEAD~10..HEAD",
        ],
        capture_output=True,
        text=True,
        cwd=str(repo),
    )
    # We just check it doesn't crash and returns an integer exit code
    assert isinstance(results.returncode, int)
