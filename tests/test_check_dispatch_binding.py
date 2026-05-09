#!/usr/bin/env python3
"""Tests for scripts/check_dispatch_binding.py."""

from __future__ import annotations

import importlib.util
import tempfile
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_dispatch_binding.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_dispatch_binding", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def test_is_pe_specific_runtime():
    """PE-specific runtime worktrees should be detected."""
    assert MODULE._is_pe_specific_runtime(
        "/opt/elis/agent-worktrees/PE-OPS-A2A-01-infra-impl-a"
    )
    assert not MODULE._is_pe_specific_runtime(
        "/opt/elis/agent-worktrees/infra-impl-b"
    )
    assert not MODULE._is_pe_specific_runtime("/opt/elis/repo")


def test_agent_worktree_map():
    """All canonical agents should map to fixed worktrees."""
    assert MODULE.AGENT_WORKTREE_MAP["pm"] == "/opt/elis/agent-worktrees/pm"
    assert MODULE.AGENT_WORKTREE_MAP["infra-impl-b"] == "/opt/elis/agent-worktrees/infra-impl-b"
    assert MODULE.AGENT_WORKTREE_MAP["infra-val-a"] == "/opt/elis/agent-worktrees/infra-val-a"
    assert MODULE.AGENT_WORKTREE_MAP["github-agent"] == "/opt/elis/agent-worktrees/github-agent"


def test_agent_worktree_map_legacy_aliases():
    """Legacy engine-based agent IDs should resolve to the correct worktree."""
    assert MODULE.AGENT_WORKTREE_MAP["infra-impl-claude"] == "/opt/elis/agent-worktrees/infra-impl-b"
    assert MODULE.AGENT_WORKTREE_MAP["infra-val-claude"] == "/opt/elis/agent-worktrees/infra-val-a"
    assert MODULE.AGENT_WORKTREE_MAP["infra-impl-codex"] == "/opt/elis/agent-worktrees/infra-impl-a"
    assert MODULE.AGENT_WORKTREE_MAP["infra-val-codex"] == "/opt/elis/agent-worktrees/infra-val-b"


def test_preserved_files():
    """Runtime/bootstrap files should be protected."""
    protected, _ = MODULE._is_untracked_or_dirty(".openclaw")
    assert protected
    protected, _ = MODULE._is_untracked_or_dirty("AGENTS.md")
    assert protected
    protected, _ = MODULE._is_untracked_or_dirty(".openclaw/config.yaml")
    assert protected


def test_non_preserved_files():
    """Non-runtime files should not be considered protected."""
    protected, _ = MODULE._is_untracked_or_dirty("scripts/some_new_script.py")
    assert not protected
    protected, _ = MODULE._is_untracked_or_dirty("CURRENT_PE.md")
    assert not protected


def test_script_runs_with_unknown_agent():
    """Calling with an unknown agent ID should exit 1."""
    result = subprocess.run(
        [str(SCRIPT), "--agent", "nonexistent-agent"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1
    assert "Unknown agent ID" in result.stdout


def test_script_runs_without_crash_on_real_agent():
    """Calling with a real agent ID should attempt checks."""
    result = subprocess.run(
        [str(SCRIPT), "--agent", "infra-impl-b"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # May pass or fail depending on actual worktree state, but should not crash
    assert result.returncode in (0, 1), f"Unexpected: {result.returncode}"
    assert "Agent: infra-impl-b" in result.stdout