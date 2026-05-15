#!/usr/bin/env python3
"""Tests for scripts/check_implementation_readiness.py."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_implementation_readiness.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_implementation_readiness", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def test_persistent_files_list():
    """Persistent context files list should be defined."""
    assert MODULE.PERSISTENT is not None
    names = {p.name for p in MODULE.PERSISTENT}
    assert "HEARTBEAT.md" in names
    assert "IDENTITY.md" in names
    assert "SOUL.md" in names
    assert "TOOLS.md" in names
    assert "USER.md" in names


def test_script_help():
    """Script should print help without error."""
    result = subprocess.run(
        ["python3", str(SCRIPT), "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "--pe-id" in result.stdout
    assert "--head" in result.stdout
    assert "--worktree" in result.stdout


def test_script_requires_pe_id():
    """Script should fail without required arguments."""
    result = subprocess.run(
        ["python3", str(SCRIPT), "--repo", "."],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
