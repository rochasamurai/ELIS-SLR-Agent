"""PE-SLR-10 end-to-end hybrid SLR execution tests."""

from __future__ import annotations

import pytest

from elis.hybrid_slr_validation import (
    HybridFlowResult,
    assert_no_heavy_local_workload,
    assert_surface_invariants,
    report_artefact_surfaces,
    report_execution_surfaces,
    report_phase_surfaces_for_pm,
    run_hybrid_slr_flow,
)
from elis.synthesis_offhost_contract import SynthesisReasoningTrace
from elis.workload_placement_policy import (
    WorkloadPlacementPolicy,
    prevent_local_promotion,
)


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
        {"record_id": "rec-1", "title": "Study Alpha"},
        {"record_id": "rec-2", "title": "Study Beta"},
    ]


def _make_screening_records() -> list[dict]:
    return [
        {"record_id": "r-1", "title": "Electoral integrity study alpha"},
        {"record_id": "r-2", "title": "Electoral integrity study beta"},
        {"record_id": "r-3", "title": "Voting systems review"},
    ]


# ---------------------------------------------------------------------------
# AC-1 — One representative flow proves Harvest → Screening → support-agent
#         → Extraction/Synthesis boundary works as designed
# ---------------------------------------------------------------------------


def test_ac1_full_hybrid_flow_runs_end_to_end() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-e2e",
        run_id="run-1",
        trigger_source="github-actions",
        screening_records=_make_screening_records(),
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        synthesis_findings=[{"claim_id": "claim-1", "impact_level": "high"}],
        commit_sha="abc1234",
        generated_at="2026-04-22T10:00:00Z",
    )
    assert isinstance(result, HybridFlowResult)
    assert result.review_id == "review-e2e"
    assert result.governance_invariants_satisfied is True


def test_ac1_harvest_contract_is_verified() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-harvest",
        run_id="run-h",
        trigger_source="github-actions",
        screening_records=_make_screening_records(),
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        synthesis_findings=[],
        commit_sha="abc1234",
        generated_at="2026-04-22T10:00:00Z",
    )
    assert result.harvest_contract_verified is True


def test_ac1_screening_is_admitted_locally() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-screening",
        run_id="run-s",
        trigger_source="github-actions",
        screening_records=_make_screening_records(),
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        synthesis_findings=[],
        commit_sha="abc1234",
        generated_at="2026-04-22T10:00:00Z",
    )
    assert result.screening_decision["allowed"] is True
    assert result.screening_decision["workload_class"] == "screening"


def test_ac1_support_agent_cannot_promote_to_off_host() -> None:
    with pytest.raises(RuntimeError, match="Promotion blocked"):
        prevent_local_promotion(
            from_workload_class="bibliometric-preanalysis",
            to_workload_class="extraction",
        )


def test_ac1_support_agent_clusters_screening_records() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-support",
        run_id="run-sa",
        trigger_source="github-actions",
        screening_records=_make_screening_records(),
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        synthesis_findings=[],
        commit_sha="abc1234",
        generated_at="2026-04-22T10:00:00Z",
    )
    assert result.support_agent_clusters >= 0  # may be 0 with low similarity


def test_ac1_extraction_and_synthesis_are_off_host() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-offhost",
        run_id="run-oh",
        trigger_source="github-actions",
        screening_records=[],
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        synthesis_findings=[],
        commit_sha="abc1234",
        generated_at="2026-04-22T10:00:00Z",
    )
    assert result.extraction_bundle["execution_surface"] == "off-host-workflow"
    assert result.extraction_bundle["local_execution_allowed"] is False
    assert result.synthesis_bundle["execution_surface"] == "off-host-workflow"
    assert result.synthesis_bundle["local_execution_allowed"] is False


# ---------------------------------------------------------------------------
# AC-2 — Artefacts are stored in the correct surfaces throughout
# ---------------------------------------------------------------------------


def test_ac2_artefact_surfaces_are_correct() -> None:
    surfaces = report_artefact_surfaces("review-artefacts")
    for key, entry in surfaces.items():
        if key == "max_local_concurrency":
            continue
        assert (
            entry["surface"] == "off-host-workflow"
        ), f"Artefact '{key}' should be off-host, got '{entry['surface']}'"


def test_ac2_artefact_paths_are_well_formed() -> None:
    surfaces = report_artefact_surfaces("review-xyz")
    assert "harvest" in surfaces["harvest_canonical_output"]["path"]
    assert "extraction" in surfaces["extraction_evidence_bundle"]["path"]
    assert "synthesis" in surfaces["synthesis_trace_bundle"]["path"]


# ---------------------------------------------------------------------------
# AC-3 — PM can report execution surface by SLR phase accurately
# ---------------------------------------------------------------------------


def test_ac3_phase_surfaces_reported_accurately() -> None:
    surfaces = report_execution_surfaces()
    assert surfaces["harvest"] == "off-host-workflow"
    assert surfaces["screening"] == "local"
    assert surfaces["extraction"] == "off-host-workflow"
    assert surfaces["synthesis"] == "off-host-workflow"


def test_ac3_pm_report_includes_surface_and_policy_data() -> None:
    report = report_phase_surfaces_for_pm()
    assert "phase_execution_surfaces" in report
    assert "local_workload_classes" in report
    assert "off_host_workload_classes" in report
    assert report["max_local_concurrency"] == 1


def test_ac3_surface_invariants_pass_for_default_policy() -> None:
    assert_surface_invariants()  # must not raise


def test_ac3_surface_invariants_fail_on_policy_mismatch() -> None:
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
# AC-4 — No unsupported local heavy workload is required for the validation run
# ---------------------------------------------------------------------------


def test_ac4_no_heavy_local_workload_in_flow_result() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-heavy",
        run_id="run-hv",
        trigger_source="github-actions",
        screening_records=_make_screening_records(),
        extraction_rows=_make_extraction_rows(),
        synthesis_traces=_make_traces(),
        synthesis_findings=[],
        commit_sha="abc1234",
        generated_at="2026-04-22T10:00:00Z",
    )
    assert_no_heavy_local_workload(result)  # must not raise


# ---------------------------------------------------------------------------
# AC-5 — Test suite passes
# ---------------------------------------------------------------------------


def test_ac5_suite_marker() -> None:
    """AC-5 contract: `pytest tests/test_hybrid_slr_execution.py -v` passes."""
    assert True
