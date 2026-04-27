"""PE-SLR-15 end-to-end validation and housekeeping checks.

These tests validate the final v1.9 hybrid SLR release properties:
- the PE-SLR-15 plan section is present and precise;
- the state machine and control-plane wiring still allow the implementer →
  validator → merge flow;
- the hybrid flow remains local-first for screening/support and off-host for
  extraction/synthesis;
- review artefacts stay archived and the repo remains in a clean documented
  state.
"""

from __future__ import annotations

from pathlib import Path

from elis.hybrid_slr_validation import (
    assert_no_heavy_local_workload,
    assert_surface_invariants,
    report_artefact_surfaces,
    report_execution_surfaces,
    report_phase_surfaces_for_pm,
    run_hybrid_slr_flow,
)
from elis.synthesis_offhost_contract import SynthesisReasoningTrace
from elis.workflow_state_machine import (
    CANONICAL_STATES,
    can_transition,
    implementer_dispatch_allowed,
    validator_dispatch_allowed_after_evidence,
)
from elis.workload_placement_policy import DEFAULT_WORKLOAD_PLACEMENT_POLICY
from scripts.check_control_plane_wiring import validate_control_plane_wiring

REPO = Path(__file__).resolve().parents[1]
PLAN = REPO / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"


def _screening_records() -> list[dict[str, str]]:
    return [
        {"record_id": "r-1", "title": "Electoral integrity study alpha"},
        {"record_id": "r-2", "title": "Electoral integrity study beta"},
        {"record_id": "r-3", "title": "Voting systems review"},
    ]


def _extraction_rows() -> list[dict[str, str]]:
    return [
        {"record_id": "rec-1", "title": "Study Alpha"},
        {"record_id": "rec-2", "title": "Study Beta"},
    ]


def _synthesis_traces() -> list[SynthesisReasoningTrace]:
    return [
        SynthesisReasoningTrace(
            claim_id="claim-1",
            supporting_record_ids=("rec-1", "rec-2"),
            evidence_refs=("appendix-c:row-1",),
            reasoning_summary="Two aligned studies support the claim.",
        )
    ]


def test_pe_slr15_plan_section_and_acceptance_criteria_are_present() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "#### PE-SLR-15 · Hybrid SLR End-to-End Validation and Housekeeping" in text
    assert "| Domain | SLR |" in text
    assert "| Track | End-to-end validation |" in text
    assert "| Implementer | `prog-impl-claude` |" in text
    assert "| Validator | `prog-val-codex` |" in text
    assert "| Depends On | PE-SLR-14 |" in text
    assert "| Status | Planned |" in text
    assert (
        "Prove the full hybrid workflow end to end, including the state machine, "
        "archive layout, gate sequencing, and release housekeeping." in text
    )
    assert (
        "| AC-1 | The implementer → validator → merge flow succeeds under the v1.9 state machine. |"
        in text
    )
    assert (
        "| AC-2 | Review artefacts are written to the archive path and discoverable by the review tooling. |"
        in text
    )
    assert (
        "| AC-3 | GitHub Actions remain bounded to CI and control-plane duties. |"
        in text
    )
    assert "| AC-4 | The hybrid placement rules hold across the full run. |" in text
    assert (
        "| AC-5 | The final housekeeping step leaves the repo in a clean, documented state. |"
        in text
    )


def test_state_machine_and_control_plane_wiring_support_the_full_release_flow() -> None:
    assert list(CANONICAL_STATES) == [
        "planning",
        "implementing",
        "gate-1-pending",
        "validating",
        "gate-2-pending",
        "merged",
        "blocked",
        "superseded",
    ]
    assert implementer_dispatch_allowed("implementing") is True
    assert validator_dispatch_allowed_after_evidence("implementing") is True
    assert can_transition("planning", "implementing") is True
    assert can_transition("implementing", "gate-1-pending") is True
    assert can_transition("gate-1-pending", "validating") is True
    assert can_transition("validating", "gate-2-pending") is True
    assert can_transition("gate-2-pending", "merged") is True
    assert validate_control_plane_wiring() == []


def test_hybrid_flow_remains_local_first_and_off_host_only_where_required() -> None:
    result = run_hybrid_slr_flow(
        review_id="review-pe-slr-15",
        run_id="run-pe-slr-15",
        trigger_source="github-actions",
        screening_records=_screening_records(),
        extraction_rows=_extraction_rows(),
        synthesis_traces=_synthesis_traces(),
        synthesis_findings=[{"claim_id": "claim-1", "impact_level": "high"}],
        commit_sha="abc1234",
        generated_at="2026-04-26T10:00:00Z",
        policy=DEFAULT_WORKLOAD_PLACEMENT_POLICY,
    )

    assert result.harvest_contract_verified is True
    assert result.screening_decision["allowed"] is True
    assert result.screening_decision["workload_class"] == "screening"
    assert result.support_agent_clusters >= 0
    assert result.surface_report == report_execution_surfaces()
    assert result.artefact_surfaces == report_artefact_surfaces(
        "review-pe-slr-15", policy=DEFAULT_WORKLOAD_PLACEMENT_POLICY
    )
    assert result.extraction_bundle["local_execution_allowed"] is False
    assert result.synthesis_bundle["local_execution_allowed"] is False
    assert result.extraction_bundle["execution_surface"] == "off-host-workflow"
    assert result.synthesis_bundle["execution_surface"] == "off-host-workflow"
    assert result.governance_invariants_satisfied is True
    assert_no_heavy_local_workload(result)
    assert_surface_invariants(policy=DEFAULT_WORKLOAD_PLACEMENT_POLICY)


def test_phase_surface_and_workload_reports_remain_consistent() -> None:
    report = report_phase_surfaces_for_pm()

    assert report["phase_execution_surfaces"] == report_execution_surfaces()
    assert report["local_workload_classes"] == [
        "screening",
        "lightweight-support",
        "metadata-triage",
        "bibliometric-preanalysis",
    ]
    assert report["off_host_workload_classes"] == [
        "harvest",
        "extraction",
        "synthesis",
    ]
    assert report["max_local_concurrency"] == 1


def test_final_housekeeping_leaves_a_clean_documented_repo_state() -> None:
    assert (REPO / "CURRENT_PE.md").exists()
    assert (REPO / "HANDOFF.md").exists()
    assert (REPO / "docs" / "reviews" / "README.md").exists()
    assert (REPO / "docs" / "reviews" / "archive").is_dir()
    assert (REPO / "docs" / "workflow" / "PE_STATE_MACHINE.md").exists()
    assert (REPO / "docs" / "slr" / "HYBRID_SLR_VALIDATION.md").exists()
    assert (REPO / "docs" / "slr" / "WORKLOAD_PLACEMENT_POLICY.md").exists()
    assert (REPO / "docs" / "slr" / "SCREENING_LOCAL_CONTRACT.md").exists()
    assert (REPO / "docs" / "slr" / "EXTRACTION_OFF_HOST_CONTRACT.md").exists()
    assert (REPO / "docs" / "slr" / "SYNTHESIS_OFF_HOST_CONTRACT.md").exists()
    assert not (REPO / "REVIEW.md").exists()
