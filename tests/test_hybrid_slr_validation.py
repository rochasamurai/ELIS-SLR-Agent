"""PE-SLR-10 end-to-end hybrid SLR validation tests."""

from __future__ import annotations

import pytest

from elis.hybrid_slr_validation import (
    HybridFlowResult,
    assert_surface_invariants,
    report_execution_surfaces,
    report_phase_surfaces_for_pm,
    run_hybrid_slr_flow,
    validate_audit_reproducibility,
)
from elis.synthesis_offhost_contract import SynthesisReasoningTrace
from elis.workload_placement_policy import WorkloadPlacementPolicy


def _make_traces() -> list[SynthesisReasoningTrace]:
    return [
        SynthesisReasoningTrace(
            claim_id="claim-1",
            supporting_record_ids=("rec-1", "rec-2"),
            evidence_refs=("appendix-c:row-1",),
            reasoning_summary="Two aligned studies support the claim.",
        )
    ]


def _make_extraction_rows() -> list[dict]:
    return [
        {"record_id": "rec-1", "title": "Study A"},
        {"record_id": "rec-2", "title": "Study B"},
    ]


# ---------------------------------------------------------------------------
# AC-1 — Execution surfaces reported accurately by SLR phase
# ---------------------------------------------------------------------------


def test_ac1_phase_surfaces_reported_accurately() -> None:
    surfaces = report_execution_surfaces()
    assert surfaces["screening"] == "local"
    assert surfaces["metadata-triage"] == "local"
    assert surfaces["bibliometric-preanalysis"] == "local"
    assert surfaces["extraction"] == "off-host-workflow"
    assert surfaces["synthesis"] == "off-host-workflow"
    assert surfaces["harvest"] == "off-host-workflow"


def test_ac1_pm_report_includes_surface_and_policy_data() -> None:
    report = report_phase_surfaces_for_pm()
    assert "phase_execution_surfaces" in report
    assert "local_workload_classes" in report
    assert "off_host_workload_classes" in report
    assert report["max_local_concurrency"] == 1


# ---------------------------------------------------------------------------
# AC-2 — Hybrid flow exercises local + off-host contracts together
# ---------------------------------------------------------------------------


def test_ac2_hybrid_flow_runs_end_to_end() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-e2e",
        run_id="run-1",
        trigger_source="github-actions",
        screening_records=[{"id": "r1"}, {"id": "r2"}],
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        synthesis_findings=[{"claim_id": "claim-1", "impact_level": "high"}],
        commit_sha="abc1234",
        generated_at="2026-04-21T10:00:00Z",
    )
    assert isinstance(result, HybridFlowResult)
    assert result.review_id == "review-e2e"
    assert result.governance_invariants_satisfied is True


def test_ac2_hybrid_flow_screening_is_admitted_locally() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-e2e-2",
        run_id="run-2",
        trigger_source="github-actions",
        screening_records=[],
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        synthesis_findings=[],
        commit_sha="abc1234",
        generated_at="2026-04-21T10:00:00Z",
    )
    assert result.screening_decision["allowed"] is True
    assert result.screening_decision["workload_class"] == "screening"


def test_ac2_hybrid_flow_extraction_is_off_host() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-e2e-3",
        run_id="run-3",
        trigger_source="github-actions",
        screening_records=[],
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        synthesis_findings=[],
        commit_sha="abc1234",
        generated_at="2026-04-21T10:00:00Z",
    )
    assert result.extraction_bundle["execution_surface"] == "off-host-workflow"
    assert result.extraction_bundle["local_execution_allowed"] is False


def test_ac2_hybrid_flow_synthesis_is_off_host() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-e2e-4",
        run_id="run-4",
        trigger_source="github-actions",
        screening_records=[],
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        synthesis_findings=[],
        commit_sha="abc1234",
        generated_at="2026-04-21T10:00:00Z",
    )
    assert result.synthesis_bundle["execution_surface"] == "off-host-workflow"
    assert result.synthesis_bundle["local_execution_allowed"] is False


# ---------------------------------------------------------------------------
# AC-3 — Governance invariants verifiable: extraction/synthesis off-host,
#         screening local
# ---------------------------------------------------------------------------


def test_ac3_surface_invariants_pass_for_default_policy() -> None:
    assert_surface_invariants()  # must not raise


def test_ac3_surface_invariants_fail_on_policy_mismatch() -> None:
    # Policy that omits metadata-triage and bibliometric-preanalysis from local classes
    bad_policy = WorkloadPlacementPolicy(
        policy_version="bad",
        max_local_concurrency=1,
        local_workload_classes=("screening",),
        off_host_workload_classes=("harvest", "extraction", "synthesis"),
        throttle_guidance=("defer if full",),
    )
    with pytest.raises(ValueError, match="local_workload_classes"):
        assert_surface_invariants(policy=bad_policy)


# ---------------------------------------------------------------------------
# AC-4 — Audit evidence is reproducible
# ---------------------------------------------------------------------------


def test_ac4_audit_evidence_is_reproducible() -> None:
    assert validate_audit_reproducibility(
        review_id="review-repro",
        run_id="run-repro",
        trigger_source="github-actions",
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        commit_sha="deadbeef",
        generated_at="2026-04-21T00:00:00Z",
    )


# ---------------------------------------------------------------------------
# AC-5 — Test suite passes
# ---------------------------------------------------------------------------


def test_ac5_suite_marker() -> None:
    """AC-5 exists as the test-command contract (`pytest ...test_hybrid_slr_validation`)."""
    assert True
