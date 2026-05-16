#!/usr/bin/env python3
"""Tests for scripts/check_fixed_worktrees.py."""

from __future__ import annotations

import importlib.util
import tempfile
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_fixed_worktrees.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_fixed_worktrees", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def test_is_pe_specific_runtime_matches_pattern():
    """PE-specific runtime worktrees should be detected."""
    assert MODULE._is_pe_specific_runtime(
        "/opt/elis/agent-worktrees/PE-OPS-A2A-01-infra-impl-a"
    )
    assert MODULE._is_pe_specific_runtime(
        "/opt/elis/agent-worktrees/PE-OPS-WORKTREE-01-infra-impl-b"
    )
    assert MODULE._is_pe_specific_runtime(
        "/opt/elis/agent-worktrees/PE-ARCH-02-infra-impl-b"
    )


def test_is_pe_specific_runtime_rejects_fixed():
    """Fixed canonical worktrees should not be flagged as PE-specific."""
    assert not MODULE._is_pe_specific_runtime("/opt/elis/agent-worktrees/infra-impl-b")
    assert not MODULE._is_pe_specific_runtime("/opt/elis/agent-worktrees/infra-val-a")
    assert not MODULE._is_pe_specific_runtime("/opt/elis/agent-worktrees/pm")
    assert not MODULE._is_pe_specific_runtime("/opt/elis/agent-worktrees/github-agent")


def test_is_pe_specific_runtime_rejects_other_paths():
    """Unrelated paths should not be flagged."""
    assert not MODULE._is_pe_specific_runtime("/opt/elis/repo")
    assert not MODULE._is_pe_specific_runtime("/tmp/some-other-path")
    assert not MODULE._is_pe_specific_runtime(
        "/opt/elis/agent-worktrees/something-else"
    )


def test_preserved_files_set():
    """PRESERVED_FILES should include standard runtime/bootstrap files."""
    preserved = MODULE.PRESERVED_FILES
    assert ".openclaw" in preserved
    assert "AGENTS.md" in preserved
    assert "SOUL.md" in preserved
    assert "TOOLS.md" in preserved
    assert "USER.md" in preserved
    assert "HEARTBEAT.md" in preserved
    assert "IDENTITY.md" in preserved


def test_script_runs_without_crash():
    """The script should parse arguments and attempt checks without crash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a minimal git repo so the script doesn't crash immediately
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, timeout=30)
        result = subprocess.run(
            [
                str(SCRIPT),
                "--worktrees",
                tmpdir,
                "--canonical-repo",
                tmpdir,
                "--expected-origin",
                "https://example.com/test.git",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Should run without uncaught exceptions and produce some output
        assert result.returncode in (
            0,
            1,
        ), f"Unexpected return code: {result.returncode}"
        assert result.stdout.strip(), "Script produced no output"

def test_check_worktree_rejects_forbidden_files(tmp_path):
    """check_fixed_worktrees should reject forbidden runtime files in worktree."""
    import subprocess
    import tempfile
    # Create a minimal git repo with a forbidden HEARTBEAT.md
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, timeout=30)
    (tmp_path / "README.md").write_text("root")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=tmp_path,
        capture_output=True,
        timeout=30,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=tmp_path,
        capture_output=True,
        timeout=30,
        env={"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@test.com",
             "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@test.com"},
    )
    (tmp_path / "HEARTBEAT.md").write_text("test heartbeat")
    result = subprocess.run(
        [
            str(SCRIPT),
            "--worktrees", str(tmp_path),
            "--canonical-repo", str(tmp_path),
            "--expected-origin", "https://example.com/test.git",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout + result.stderr
    assert "FORBIDDEN_IN_WORKTREE" in output
    assert "HEARTBEAT.md" in output


def test_check_worktree_passes_clean(tmp_path):
    """check_fixed_worktrees should pass on a clean worktree with no forbidden files."""
    import subprocess
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, timeout=30)
    (tmp_path / "README.md").write_text("root")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=tmp_path,
        capture_output=True,
        timeout=30,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=tmp_path,
        capture_output=True,
        timeout=30,
        env={"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@test.com",
             "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@test.com"},
    )
    result = subprocess.run(
        [
            str(SCRIPT),
            "--worktrees", str(tmp_path),
            "--canonical-repo", str(tmp_path),
            "--expected-origin", "https://example.com/test.git",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Should not have FORBIDDEN_IN_WORKTREE failures
    assert "FORBIDDEN_IN_WORKTREE" not in result.stdout
