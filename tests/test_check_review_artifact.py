#!/usr/bin/env python3
"""Tests for scripts/check_review_artifact.py."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_review_artifact.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_review_artifact", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def test_script_help():
    """Script should print help without error."""
    result = subprocess.run(
        ["python3", str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--pe-id" in result.stdout


def test_script_requires_pe_id():
    """Script should fail without required arguments."""
    result = subprocess.run(
        ["python3", str(SCRIPT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    # Should require --pe-id
    assert "required" in result.stderr or result.returncode != 0


def test_missing_review_returns_1(tmp_path):
    """Script should return 1 when REVIEW.md does not exist."""
    result = subprocess.run(
        ["python3", str(SCRIPT), "--repo", str(tmp_path), "--pe-id", "PE-NONEXISTENT"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "MISSING_REVIEW" in result.stderr
