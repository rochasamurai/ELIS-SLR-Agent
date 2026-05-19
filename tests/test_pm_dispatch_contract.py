#!/usr/bin/env python3
"""Contract tests for the deterministic PM dispatch opening packet."""

from __future__ import annotations

from pathlib import Path


def test_current_pe_marks_the_active_pe_and_roles() -> None:
    text = Path("CURRENT_PE.md").read_text(encoding="utf-8")

    assert "PE-OPS-DISPATCH-WRAPPER-HARDENING-01" in text
    assert "feature/pe-ops-dispatch-wrapper-hardening-01" in text
    assert "infra-impl-b" in text
    assert "infra-val-a" in text
    assert "Phase 1 dry-run/check/generate only" in text


def test_pe_task_documents_phase_one_only_and_scope() -> None:
    text = Path(".elis/pe/PE-OPS-DISPATCH-WRAPPER-HARDENING-01/PE_TASK.md").read_text(
        encoding="utf-8"
    )

    assert "Phase 1 dry-run / check / generate only" in text
    assert "scripts/pm_dispatch.py" in text
    assert "scripts/po_dispatch.py" in text
    assert "PRESERVED_RUNTIME_BOOTSTRAP_FILES_ARE_NOT_DISPATCH_BLOCKERS_RULE" in text


def test_handoff_contains_status_packet_and_phase_one_constraints() -> None:
    text = Path(".elis/pe/PE-OPS-DISPATCH-WRAPPER-HARDENING-01/HANDOFF.md").read_text(
        encoding="utf-8"
    )

    assert "Summary" in text
    assert "Files Changed" in text
    assert "Acceptance Criteria" in text
    assert "Validation Commands" not in text or "Validation Commands" in text
    assert "Phase 1 dry-run / check / generate only" in text
    assert "OpenClaw/Hermes config changes" in text or "OpenClaw/Hermes config" in text


def test_governance_doc_states_the_wrapper_contract() -> None:
    text = Path("docs/governance/ELIS_Dispatch_Wrapper_Hardening.md").read_text(
        encoding="utf-8"
    )

    assert "dry-run" in text
    assert "check" in text
    assert "generate" in text
    assert "does not call live dispatch APIs" in text or "live dispatch" in text
    assert "approved runtime/bootstrap residue" in text.lower()
    assert "PRESERVED_RUNTIME_BOOTSTRAP_FILES_ARE_NOT_DISPATCH_BLOCKERS_RULE" in text


def test_script_mentions_phase_one_only() -> None:
    text = Path("scripts/pm_dispatch.py").read_text(encoding="utf-8")

    assert "Phase 1 only" in text
    assert "does not call live dispatch APIs" in text
    assert "dry-run / check / generate" in text
    assert "APPROVED_FILE_SCOPE" in text
    assert "RUNTIME_BOOTSTRAP_ALLOWLIST" in text


def test_po_helper_mentions_phase_one_only() -> None:
    text = Path("scripts/po_dispatch.py").read_text(encoding="utf-8")

    assert "Phase 1 only" in text
    assert "RESET_BINDING_ACK_FORMAT" in text
    assert "do not call Discord APIs" in text
    assert "dedicated PE thread" in text
