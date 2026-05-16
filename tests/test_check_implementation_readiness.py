#!/usr/bin/env python3
"""Tests for scripts/check_implementation_readiness.py."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_implementation_readiness.py"
)


def _load():
    spec = importlib.util.spec_from_file_location(
        "check_implementation_readiness", SCRIPT
    )
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


def test_required_scope_files_are_pe_specific():
    """Required scope files should be derived from the PE id."""
    paths = MODULE.required_scope_files("PE-OPS-SKILLS-01")
    assert [p.name for p in paths] == [
        "GOVERNANCE.md",
        "SKILLS_PM.md",
        "SKILLS_IMPLEMENTERS.md",
        "SKILLS_VALIDATORS.md",
    ]
    assert all("PE-OPS-SKILLS-01" in str(p) for p in paths)


def test_script_help():
    """Script should print help without error."""
    result = subprocess.run(
        ["python3", str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--pe-id" in result.stdout
    assert "--head" in result.stdout
    assert "--worktree" in result.stdout


def test_script_requires_pe_id():
    """Script should fail without required arguments."""
    result = subprocess.run(
        ["python3", str(SCRIPT), "--repo", "."],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0

def test_worktree_forbidden_set():
    """WORKTREE_FORBIDDEN should include runtime/bootstrap files that must not be in worktree."""
    assert MODULE.WORKTREE_FORBIDDEN is not None
    assert "HEARTBEAT.md" in MODULE.WORKTREE_FORBIDDEN
    assert "IDENTITY.md" in MODULE.WORKTREE_FORBIDDEN
    assert "SOUL.md" in MODULE.WORKTREE_FORBIDDEN
    assert "TOOLS.md" in MODULE.WORKTREE_FORBIDDEN
    assert "USER.md" in MODULE.WORKTREE_FORBIDDEN


def test_implementation_readiness_rejects_forbidden_in_worktree(tmp_path):
    """Implementation readiness should fail if forbidden runtime files are in worktree."""
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    (tmp_path / "README.md").write_text("root")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@test.com",
             "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@test.com"},
    )
    branch = "feature/test"
    subprocess.run(
        ["git", "checkout", "-b", branch],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    # Create a forbidden SOUL.md in the worktree
    (tmp_path / "SOUL.md").write_text("test soul")
    head_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    head = head_result.stdout.strip()
    proc = subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--repo", str(tmp_path),
            "--pe-id", "PE-OPS-SKILLS-01",
            "--branch", branch,
            "--head", head,
            "--worktree", str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "FORBIDDEN_IN_WORKTREE" in proc.stderr
    assert "SOUL.md" in proc.stderr
