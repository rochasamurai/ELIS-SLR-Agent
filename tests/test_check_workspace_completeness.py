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
    (ws / "CLAUDE.md").write_text("# claude", encoding="utf-8")
    (ws / "CODEX.md").write_text("# codex", encoding="utf-8")
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
    (ws / "CLAUDE.md").write_text("# claude", encoding="utf-8")
    (ws / "CODEX.md").write_text("# codex", encoding="utf-8")
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


def test_segmentation_passes_for_phase_workspace_shared_by_impl_and_val():
    agents = [
        _make_agent(
            "harvest-impl-codex", "/home/samurai/openclaw/workspace-slr-harvest"
        ),
        _make_agent(
            "harvest-val-claude", "/home/samurai/openclaw/workspace-slr-harvest"
        ),
    ]
    errors = cwc.check_segmentation(agents)
    assert errors == []


def test_segmentation_fails_for_phase_workspace_split_across_two_dirs():
    agents = [
        _make_agent(
            "harvest-impl-codex", "/home/samurai/openclaw/workspace-slr-harvest"
        ),
        _make_agent(
            "harvest-val-claude",
            "/home/samurai/openclaw/workspace-slr-harvest-validator",
        ),
    ]
    errors = cwc.check_segmentation(agents)
    assert any("must share one phase workspace" in e for e in errors)


def test_required_files_pm_workspace_uses_pm_file_set(tmp_path):
    ws = tmp_path / "workspace-pm"
    ws.mkdir()
    (ws / "AGENTS.md").write_text("# agents", encoding="utf-8")
    (ws / "MEMORY.md").write_text("# memory", encoding="utf-8")
    (ws / "SOUL.md").write_text("# soul", encoding="utf-8")
    agent = _make_agent("pm", "/home/samurai/openclaw/workspace-pm")
    original = cwc.WORKSPACES_DIR
    cwc.WORKSPACES_DIR = tmp_path
    try:
        errors = cwc.check_required_files([agent])
    finally:
        cwc.WORKSPACES_DIR = original
    assert errors == []


def test_slr_phase_cutover_passes_for_full_phase_agent_roster():
    agents = [
        _make_agent("pm", "/home/samurai/openclaw/workspace-pm"),
        _make_agent(
            "harvest-impl-codex", "/home/samurai/openclaw/workspace-slr-harvest"
        ),
        _make_agent(
            "harvest-val-claude", "/home/samurai/openclaw/workspace-slr-harvest"
        ),
        _make_agent(
            "screen-impl-claude", "/home/samurai/openclaw/workspace-slr-screen"
        ),
        _make_agent("screen-val-codex", "/home/samurai/openclaw/workspace-slr-screen"),
        _make_agent(
            "extract-impl-codex", "/home/samurai/openclaw/workspace-slr-extract"
        ),
        _make_agent(
            "extract-val-claude", "/home/samurai/openclaw/workspace-slr-extract"
        ),
        _make_agent("synth-impl-claude", "/home/samurai/openclaw/workspace-slr-synth"),
        _make_agent("synth-val-codex", "/home/samurai/openclaw/workspace-slr-synth"),
        _make_agent(
            "prisma-impl-claude", "/home/samurai/openclaw/workspace-slr-prisma"
        ),
        _make_agent("prisma-val-codex", "/home/samurai/openclaw/workspace-slr-prisma"),
    ]
    errors = cwc.check_slr_phase_cutover(agents)
    assert errors == []


def test_slr_phase_cutover_requires_all_phase_agents():
    agents = [
        _make_agent("pm", "/home/samurai/openclaw/workspace-pm"),
        _make_agent(
            "harvest-impl-codex", "/home/samurai/openclaw/workspace-slr-harvest"
        ),
    ]
    errors = cwc.check_slr_phase_cutover(agents)
    assert any("missing phase-specialized SLR agent IDs" in err for err in errors)


def test_slr_phase_cutover_rejects_legacy_generic_ids():
    agents = [
        _make_agent("slr-impl-codex", "/home/samurai/openclaw/workspace-slr-impl"),
        _make_agent("slr-val-claude", "/home/samurai/openclaw/workspace-slr-val"),
    ]
    errors = cwc.check_slr_phase_cutover(agents)
    assert any("legacy generic SLR agent IDs still present" in err for err in errors)
