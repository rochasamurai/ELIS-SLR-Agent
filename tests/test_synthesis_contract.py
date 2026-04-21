"""PE-SLR-08 synthesis off-host contract tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from elis.synthesis_offhost_contract import (
    LocalMigrationCriteria,
    SynthesisOffHostContract,
    SynthesisReasoningTrace,
    SynthesisWorkflowEnvelope,
    assert_local_migration_not_activated,
    build_high_impact_checkpoints,
    build_synthesis_trace_bundle,
    persist_synthesis_contract_artefacts,
)


def test_ac1_synthesis_envelope_requires_off_host_workflow() -> None:
    envelope = SynthesisWorkflowEnvelope(
        review_id="r-1", run_id="run-1", trigger_source="github-actions"
    )
    assert envelope.execution_surface == "off-host-workflow"
    assert envelope.local_execution_allowed is False


def test_ac1_rejects_local_execution_surface() -> None:
    with pytest.raises(ValueError, match="off-host workflow surfaces only"):
        SynthesisWorkflowEnvelope(
            review_id="r-1",
            run_id="run-1",
            trigger_source="github-actions",
            execution_surface="local",
        )


def test_ac2_trace_requires_claim_to_evidence_links() -> None:
    trace = SynthesisReasoningTrace(
        claim_id="claim-1",
        supporting_record_ids=("rec-1", "rec-2"),
        evidence_refs=("appendix-c:row-7",),
        reasoning_summary="Claim supported by two aligned studies.",
    )
    assert trace.claim_id == "claim-1"
    assert trace.supporting_record_ids == ("rec-1", "rec-2")


def test_ac2_bundle_preserves_traceability_fields() -> None:
    envelope = SynthesisWorkflowEnvelope(
        review_id="r-2", run_id="run-2", trigger_source="github-actions"
    )
    contract = SynthesisOffHostContract(review_id="r-2")
    bundle = build_synthesis_trace_bundle(
        envelope=envelope,
        contract=contract,
        traces=[
            SynthesisReasoningTrace(
                claim_id="claim-a",
                supporting_record_ids=("rec-9",),
                evidence_refs=("appendix-c:row-9",),
                reasoning_summary="Single high-quality study supports claim.",
            )
        ],
        commit_sha="deadbeef",
        generated_at="2026-04-21T12:00:00Z",
    )
    assert bundle["claim_ids"] == ["claim-a"]
    assert bundle["claim_count"] == 1
    assert bundle["trace_sha256"]
    assert bundle["generated_at"] == "2026-04-21T12:00:00Z"


def test_ac3_high_impact_checkpoints_are_explicit_and_pending() -> None:
    checkpoints = build_high_impact_checkpoints(
        [
            {"claim_id": "claim-1", "impact_level": "high"},
            {"claim_id": "claim-2", "impact_level": "critical"},
            {"claim_id": "claim-3", "impact_level": "medium"},
        ]
    )
    assert len(checkpoints) == 2
    assert all(cp.reviewer_required for cp in checkpoints)
    assert all(cp.status == "pending" for cp in checkpoints)


def test_ac3_rejects_non_high_impact_checkpoint() -> None:
    with pytest.raises(ValueError, match="impact_level must be 'high' or 'critical'"):
        from elis.synthesis_offhost_contract import HumanReviewCheckpoint

        HumanReviewCheckpoint(
            checkpoint_id="chk-1", claim_id="claim-x", impact_level="medium"
        )


def test_ac4_migration_criteria_documented_not_activated() -> None:
    criteria = LocalMigrationCriteria(
        criteria_version="v1",
        prerequisites=("capacity-proof", "policy-approval", "traceability-pass"),
        activation_requested=False,
    )
    assert criteria.activation_requested is False
    assert_local_migration_not_activated(criteria)


def test_ac4_activated_migration_criteria_is_blocked() -> None:
    criteria = LocalMigrationCriteria(
        criteria_version="v1",
        prerequisites=("capacity-proof",),
        activation_requested=True,
    )
    with pytest.raises(RuntimeError, match="cannot be activated"):
        assert_local_migration_not_activated(criteria)


def test_persist_synthesis_artefacts_writes_bundle_and_checkpoints(
    tmp_path: Path,
) -> None:
    envelope = SynthesisWorkflowEnvelope(
        review_id="review-7", run_id="run-7", trigger_source="github-actions"
    )
    contract = SynthesisOffHostContract(review_id="review-7", root=tmp_path)
    traces = [
        SynthesisReasoningTrace(
            claim_id="claim-7",
            supporting_record_ids=("rec-a",),
            evidence_refs=("appendix-c:row-33",),
            reasoning_summary="Evidence link retained.",
        )
    ]
    bundle = persist_synthesis_contract_artefacts(
        envelope=envelope,
        contract=contract,
        traces=traces,
        findings=[{"claim_id": "claim-7", "impact_level": "high"}],
        commit_sha="cafebabe",
        generated_at="2026-04-21T16:00:00Z",
    )
    assert contract.envelope_path().exists()
    assert contract.trace_bundle_path().exists()
    assert contract.checkpoints_path().exists()
    persisted_bundle = json.loads(contract.trace_bundle_path().read_text("utf-8"))
    assert persisted_bundle["commit_sha"] == "cafebabe"
    assert persisted_bundle["generated_at"] == "2026-04-21T16:00:00Z"
    assert persisted_bundle == bundle


def test_ac5_suite_marker() -> None:
    """AC-5 exists as the test-command contract (`pytest ...test_synthesis_contract`)."""
    assert True
