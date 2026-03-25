"""Tests for scripts/check_workspace_completeness.py"""

from __future__ import annotations


from scripts import check_workspace_completeness as cwc


def _make_agent(agent_id: str, workspace: str, model: str = "test/model") -> dict:
    return {"id": agent_id, "workspace": workspace, "model": model}


def _make_config(agents: list[dict]) -> dict:
    return {"agents": {"list": agents}}


# ---------------------------------------------------------------------------
# check_workspace_presence
# ---------------------------------------------------------------------------


def test_presence_passes_when_workspace_exists(tmp_path):
    ws = tmp_path / "workspace-infra-impl"
    ws.mkdir()
    agent = _make_agent(
        "infra-impl-codex", "/home/samurai/openclaw/workspace-infra-impl"
    )
    # patch WORKSPACES_DIR
    original = cwc.WORKSPACES_DIR
    cwc.WORKSPACES_DIR = tmp_path
    try:
        errors = cwc.check_workspace_presence([agent])
    finally:
        cwc.WORKSPACES_DIR = original
    assert errors == []


def test_presence_fails_when_workspace_missing(tmp_path):
    agent = _make_agent(
        "infra-impl-codex", "/home/samurai/openclaw/workspace-infra-impl"
    )
    original = cwc.WORKSPACES_DIR
    cwc.WORKSPACES_DIR = tmp_path
    try:
        errors = cwc.check_workspace_presence([agent])
    finally:
        cwc.WORKSPACES_DIR = original
    assert any("does not exist" in e for e in errors)


def test_presence_shared_workspace_checked_once(tmp_path):
    ws = tmp_path / "workspace-infra-impl"
    ws.mkdir()
    agents = [
        _make_agent("infra-impl-codex", "/home/samurai/openclaw/workspace-infra-impl"),
        _make_agent("infra-impl-claude", "/home/samurai/openclaw/workspace-infra-impl"),
    ]
    original = cwc.WORKSPACES_DIR
    cwc.WORKSPACES_DIR = tmp_path
    try:
        errors = cwc.check_workspace_presence(agents)
    finally:
        cwc.WORKSPACES_DIR = original
    assert errors == []


# ---------------------------------------------------------------------------
# check_required_files
# ---------------------------------------------------------------------------


def test_required_files_passes_when_agents_md_present(tmp_path):
    ws = tmp_path / "workspace-prog-impl"
    ws.mkdir()
    (ws / "AGENTS.md").write_text("# agents", encoding="utf-8")
    agent = _make_agent("prog-impl-codex", "/home/samurai/openclaw/workspace-prog-impl")
    original = cwc.WORKSPACES_DIR
    cwc.WORKSPACES_DIR = tmp_path
    try:
        errors = cwc.check_required_files([agent])
    finally:
        cwc.WORKSPACES_DIR = original
    assert errors == []


def test_required_files_fails_when_agents_md_missing(tmp_path):
    ws = tmp_path / "workspace-prog-impl"
    ws.mkdir()
    agent = _make_agent("prog-impl-codex", "/home/samurai/openclaw/workspace-prog-impl")
    original = cwc.WORKSPACES_DIR
    cwc.WORKSPACES_DIR = tmp_path
    try:
        errors = cwc.check_required_files([agent])
    finally:
        cwc.WORKSPACES_DIR = original
    assert any("AGENTS.md" in e for e in errors)


# ---------------------------------------------------------------------------
# check_segmentation
# ---------------------------------------------------------------------------


def test_segmentation_passes_separate_workspaces():
    agents = [
        _make_agent("infra-impl-codex", "/home/samurai/openclaw/workspace-infra-impl"),
        _make_agent("infra-impl-claude", "/home/samurai/openclaw/workspace-infra-impl"),
        _make_agent("infra-val-codex", "/home/samurai/openclaw/workspace-infra-val"),
        _make_agent("infra-val-claude", "/home/samurai/openclaw/workspace-infra-val"),
    ]
    errors = cwc.check_segmentation(agents)
    assert errors == []


def test_segmentation_fails_shared_impl_val_workspace():
    agents = [
        _make_agent("infra-impl-codex", "/home/samurai/openclaw/workspace-infra"),
        _make_agent("infra-val-codex", "/home/samurai/openclaw/workspace-infra"),
    ]
    errors = cwc.check_segmentation(agents)
    assert any("share workspace" in e for e in errors)


def test_segmentation_pm_agent_ignored():
    """pm agent has no impl/val role in the ID — must not cause false positives."""
    agents = [
        _make_agent("pm", "/home/samurai/openclaw/workspace-pm"),
    ]
    errors = cwc.check_segmentation(agents)
    assert errors == []
