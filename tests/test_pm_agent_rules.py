from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PM_AGENTS_PATH = REPO_ROOT / "openclaw" / "workspaces" / "workspace-pm" / "AGENTS.md"


def test_pm_rules_live_in_workspace_pm_agents() -> None:
    assert (
        PM_AGENTS_PATH.exists()
    ), f"Missing PM rules source of truth: {PM_AGENTS_PATH}"


def test_pm_rules_source_defines_prompt_source_order() -> None:
    text = PM_AGENTS_PATH.read_text(encoding="utf-8")
    assert "Prompt Source Order" in text
    assert "AGENTS.md" in text
    assert "MEMORY.md" in text


def test_pm_rules_source_defines_status_transition_guard() -> None:
    text = PM_AGENTS_PATH.read_text(encoding="utf-8")
    assert "Status Transition Guard" in text
    assert "implementing → validating" in text
    assert "validating → gate-2-pending" in text
    assert "gate-2-pending → merged" in text
