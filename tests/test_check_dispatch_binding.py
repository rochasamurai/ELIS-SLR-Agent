#!/usr/bin/env python3
"""Tests for scripts/check_dispatch_binding.py — PE dispatch binding guards."""

from __future__ import annotations

import importlib.util
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
    assert not MODULE._is_pe_specific_runtime("/opt/elis/agent-worktrees/infra-impl-b")
    assert not MODULE._is_pe_specific_runtime("/opt/elis/repo")


def test_agent_worktree_map():
    """All canonical agents should map to fixed worktrees."""
    assert MODULE.AGENT_WORKTREE_MAP["pm"] == "/opt/elis/agent-worktrees/pm"
    assert (
        MODULE.AGENT_WORKTREE_MAP["infra-impl-b"]
        == "/opt/elis/agent-worktrees/infra-impl-b"
    )
    assert (
        MODULE.AGENT_WORKTREE_MAP["infra-val-a"]
        == "/opt/elis/agent-worktrees/infra-val-a"
    )


def test_agent_worktree_map_new_entries():
    """New agent worktree entries should be present."""
    assert "advisor" in MODULE.AGENT_WORKTREE_MAP
    assert MODULE.AGENT_WORKTREE_MAP["advisor"] == "/opt/elis/agent-worktrees/advisor"


def test_failure_class_taxonomy():
    """Failure-class taxonomy should include all blocking scenarios."""
    assert "WRONG_BRANCH" in MODULE.FAILURE_CLASSES
    assert "WRONG_HEAD" in MODULE.FAILURE_CLASSES
    assert "DIRTY_WORKTREE" in MODULE.FAILURE_CLASSES
    assert "MISSING_ORIGIN_REMOTE" in MODULE.FAILURE_CLASSES
    assert "DETACHED_HEAD" in MODULE.FAILURE_CLASSES
    assert "MISSING_PE_TASK" in MODULE.FAILURE_CLASSES
    assert "DISPATCH_PATH_BLOCKED" in MODULE.FAILURE_CLASSES
    assert "DISPATCH_RECOVERY_BLOCKED" in MODULE.FAILURE_CLASSES
    assert "IMPLEMENTER_EXECUTION_BLOCKED" in MODULE.FAILURE_CLASSES
    assert "MISSING_RESET_ACK" in MODULE.FAILURE_CLASSES
    assert "SELF_FIX_ROUTING" in MODULE.FAILURE_CLASSES
    assert "UNCOMMITTED_MISREPORTED" in MODULE.FAILURE_CLASSES


def test_classify_failure():
    """classify_failure should return the correct label."""
    label = MODULE.classify_failure("WRONG_BRANCH")
    assert "WRONG_BRANCH" in label
    assert "Agent worktree is on an unexpected branch" in label

    label = MODULE.classify_failure("MISSING_ORIGIN_REMOTE")
    assert "MISSING_ORIGIN_REMOTE" in label

    label = MODULE.classify_failure("UNKNOWN_CODE")
    assert "UNKNOWN_FAILURE" in label


def test_untracked_or_dirty():
    """Common runtime/context files should be classified as protected."""
    is_protected, reason = MODULE._is_untracked_or_dirty("HEARTBEAT.md")
    assert is_protected
    assert "runtime/context" in reason

    is_protected, reason = MODULE._is_untracked_or_dirty("AGENTS.md")
    assert is_protected

    is_protected, reason = MODULE._is_untracked_or_dirty(".openclaw")
    assert is_protected

    is_protected, reason = MODULE._is_untracked_or_dirty("HANDOFF.md")
    assert not is_protected


def test_classify_failure_cli():
    """--classify flag should produce the correct output."""
    import subprocess
    result = subprocess.run(
        ["python3", str(SCRIPT), "--classify", "DISPATCH_PATH_BLOCKED"],
        capture_output=True, text=True,
    )
    assert "DISPATCH_PATH_BLOCKED" in result.stdout
    assert result.returncode == 1

    result = subprocess.run(
        ["python3", str(SCRIPT), "--classify", "WRONG_BRANCH"],
        capture_output=True, text=True,
    )
    assert "WRONG_BRANCH" in result.stdout
    assert result.returncode == 1
