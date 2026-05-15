#!/usr/bin/env python3
"""Tests for scripts/check_pe_opening_context.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_pe_opening_context.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_pe_opening_context", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def test_required_checks_list():
    """All required checks should be defined."""
    assert len(MODULE.REQUIRED_CHECKS) == 6
    assert "origin_remote" in MODULE.REQUIRED_CHECKS
    assert "origin_main_fetched" in MODULE.REQUIRED_CHECKS
    assert "current_pe_reconciled" in MODULE.REQUIRED_CHECKS
    assert "worktree_bound" in MODULE.REQUIRED_CHECKS
    assert "worktree_clean" in MODULE.REQUIRED_CHECKS
    assert "head_matches_baseline" in MODULE.REQUIRED_CHECKS


def test_failure_classification_patterns():
    """Check that common failure classifications are present in the module logic."""
    import inspect
    source = inspect.getsource(MODULE)

    assert "MISSING_ORIGIN_REMOTE" in source
    assert "STALE_FETCH" in source
    assert "DIRTY_CURRENT_PE_MD" in source
    assert "WRONG_BRANCH" in source
    assert "DETACHED_HEAD" in source
    assert "DIRTY_WORKTREE" in source
    assert "HEAD_MISMATCH" in source
