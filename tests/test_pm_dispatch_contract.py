#!/usr/bin/env python3
"""Contract tests for the deterministic PM dispatch opening packet."""

from __future__ import annotations

from pathlib import Path


def test_current_pe_marks_the_active_pe_and_roles() -> None:
    text = Path("CURRENT_PE.md").read_text(encoding="utf-8")

    assert "PE-OPS-PM-DISPATCH-01" in text
    assert "feature/pe-ops-pm-dispatch-01-deterministic-pm-dispatch-wrapper" in text
    assert "infra-impl-b" in text
    assert "infra-val-a" in text


def test_pe_task_documents_phase_one_only_and_scope() -> None:
    text = Path(".elis/pe/PE-OPS-PM-DISPATCH-01/PE_TASK.md").read_text(encoding="utf-8")

    assert "dry-run / check / generate" in text
    assert "Phase 1 gates" in text
    assert "Do not call live dispatch APIs" in text or "live dispatch APIs" in text
    assert "scripts/pm_dispatch.py" in text


def test_handoff_contains_status_packet_and_no_live_dispatch_statement() -> None:
    text = Path(".elis/pe/PE-OPS-PM-DISPATCH-01/HANDOFF.md").read_text(encoding="utf-8")

    assert "Summary" in text
    assert "Files Changed" in text
    assert "Acceptance Criteria" in text
    assert "Validation Commands" in text
    assert (
        "Phase 1 only generates and checks dispatch contracts and does not call live dispatch APIs."
        in text
    )


def test_governance_doc_states_the_wrapper_contract() -> None:
    text = Path("docs/governance/ELIS_PM_Dispatch_Wrapper.md").read_text(
        encoding="utf-8"
    )

    assert "dry-run" in text
    assert "check" in text
    assert "generate" in text
    assert "does not call live dispatch APIs" in text
    assert "approved file scope" in text.lower() or "Approved scope" in text


def test_script_mentions_phase_one_only() -> None:
    text = Path("scripts/pm_dispatch.py").read_text(encoding="utf-8")

    assert "Phase 1 only" in text
    assert "does not call live dispatch APIs" in text
    assert "dry-run / check / generate" in text
    assert "APPROVED_FILE_SCOPE" in text
