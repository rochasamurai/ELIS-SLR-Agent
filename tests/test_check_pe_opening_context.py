#!/usr/bin/env python3
"""Tests for scripts/check_pe_opening_context.py."""

from __future__ import annotations

import importlib.util
import subprocess
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
    assert "WORKTREE_MISSING" in source


def test_check_worktree_bound_nonexistent():
    """_check_worktree_bound should return 1 with WORKTREE_MISSING for nonexistent path."""
    rc = MODULE._check_worktree_bound(
        Path("/tmp/nonexistent_worktree_pe_opening_check"),
        "feature/some-branch",
    )
    assert rc == 1


def test_check_worktree_clean_nonexistent():
    """_check_worktree_clean should return 1 with WORKTREE_MISSING for nonexistent path."""
    rc = MODULE._check_worktree_clean(
        Path("/tmp/nonexistent_worktree_pe_opening_check_clean"),
    )
    assert rc == 1


def test_check_head_matches_baseline_nonexistent():
    """_check_head_matches_baseline should return 1 with WORKTREE_MISSING for nonexistent path."""
    rc = MODULE._check_head_matches_baseline(
        Path("/tmp/nonexistent_worktree_pe_opening_check_head"),
        "abc123def456",
    )
    assert rc == 1


def test_check_worktree_bound_existing():
    """_check_worktree_bound with an existing (non-git) directory should return 1."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        rc = MODULE._check_worktree_bound(
            Path(tmpdir),
            "some-branch",
        )
    assert rc == 1


def test_cli_nonexistent_worktree_does_not_crash():
    """Running check_pe_opening_context.py with a nonexistent worktree should not crash."""
    result = subprocess.run(
        [
            "python3", str(SCRIPT),
            "--repo", str(Path(__file__).resolve().parents[1]),
            "--worktree", "/tmp/nonexistent_pe_opening_cli_test",
            "--branch", "feature/test",
            "--head", "deadbeef0123456789",
        ],
        capture_output=True, text=True,
    )
    # Should exit 1 (failure), not crash with traceback
    assert result.returncode == 1
    # Should contain WORKTREE_MISSING in stderr
    assert "WORKTREE_MISSING" in result.stderr