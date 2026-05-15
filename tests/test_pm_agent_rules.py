from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PM_AGENTS_PATH = REPO_ROOT / "openclaw" / "workspaces" / "workspace-pm" / "AGENTS.md"
PM_SKILLS_PATH = REPO_ROOT / "openclaw" / "workspaces" / "workspace-pm" / "SKILLS.md"


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


def test_pm_skills_live_in_workspace_pm() -> None:
    assert (
        PM_SKILLS_PATH.exists()
    ), f"Missing PM skills file: {PM_SKILLS_PATH}"


def test_pm_skills_defines_opening_context_guard() -> None:
    """PM SKILLS.md should reference PE opening context checks."""
    text = PM_SKILLS_PATH.read_text(encoding="utf-8")
    assert "opening context" in text.lower() or "opening" in text.lower()


def test_pm_skills_defines_dispatch_binding_guard() -> None:
    """PM SKILLS.md should reference dispatch binding preconditions."""
    text = PM_SKILLS_PATH.read_text(encoding="utf-8")
    assert "binding" in text.lower() or "bound" in text.lower()


def test_pm_skills_defines_failure_class() -> None:
    """PM SKILLS.md should reference failure class taxonomy."""
    text = PM_SKILLS_PATH.read_text(encoding="utf-8")
    assert "failure class" in text.lower() or "FAILURE" in text


def test_pm_skills_defines_pm_no_write_rule() -> None:
    """PM SKILLS.md should reference the PM no-write rule."""
    text = PM_SKILLS_PATH.read_text(encoding="utf-8")
    assert "write" in text.lower()
