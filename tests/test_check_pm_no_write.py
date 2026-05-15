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
    import inspect
    assert hasattr(MODULE, "git")
    assert callable(MODULE.git)
