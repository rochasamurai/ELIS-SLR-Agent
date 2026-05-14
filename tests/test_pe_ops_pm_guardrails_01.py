from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE = REPO_ROOT / "docs" / "governance" / "ELIS_Agent_Roles_and_Boundaries.md"
PE_TASK = REPO_ROOT / ".elis" / "pe" / "PE-OPS-PM-GUARDRAILS-01" / "PE_TASK.md"


def test_pm_guardrails_governance_mentions_coordination_only() -> None:
    text = GOVERNANCE.read_text(encoding="utf-8")
    assert "PM" in text
    assert "coordination-only" in text
    assert "edit implementation files or validation artefacts" in text
    assert "broad read-only visibility" in text


def test_pm_guardrails_governance_mentions_future_containerisation_boundary() -> None:
    text = GOVERNANCE.read_text(encoding="utf-8")
    assert "Future containerisation" in text
    assert "filesystem permissions and mount design" in text


def test_pe_task_requires_validator_checklist_language() -> None:
    text = PE_TASK.read_text(encoding="utf-8")
    assert "did not author implementation artefacts" in text
    assert "did not author validation artefacts" in text
    assert "PM coordinates only" in text
