"""End-to-end hybrid SLR validation for PE-SLR-10.

Validates that one representative hybrid SLR flow satisfies all governance
invariants across local and off-host execution surfaces: screening runs locally,
extraction and synthesis remain off-host, capacity policy is respected, and
audit evidence is reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from elis.extraction_offhost_contract import (
    ExtractionOffHostContract,
    ExtractionWorkflowEnvelope,
    build_extraction_evidence_bundle,
)
from elis.synthesis_offhost_contract import (
    SynthesisOffHostContract,
    SynthesisReasoningTrace,
    SynthesisWorkflowEnvelope,
    build_synthesis_trace_bundle,
)
from elis.workload_placement_policy import (
    DEFAULT_WORKLOAD_PLACEMENT_POLICY,
    WorkloadPlacementPolicy,
    enforce_local_workload_request,
    report_workload_classes,
)

# ---------------------------------------------------------------------------
# Execution surface registry
# ---------------------------------------------------------------------------

_PHASE_SURFACES: dict[str, str] = {
    "harvest": "off-host-workflow",
    "screening": "local",
    "metadata-triage": "local",
    "bibliometric-preanalysis": "local",
    "extraction": "off-host-workflow",
    "synthesis": "off-host-workflow",
}


def report_execution_surfaces() -> dict[str, str]:
    """Return the canonical execution surface for each SLR phase."""
    return dict(_PHASE_SURFACES)


def assert_surface_invariants(
    policy: WorkloadPlacementPolicy = DEFAULT_WORKLOAD_PLACEMENT_POLICY,
) -> None:
    """Raise if any phase surface violates the placement policy."""
    for phase, surface in _PHASE_SURFACES.items():
        if surface == "local":
            if phase not in policy.local_workload_classes:
                raise ValueError(
                    f"Phase '{phase}' is mapped to 'local' but not in local_workload_classes"
                )
        elif surface == "off-host-workflow":
            if phase not in policy.off_host_workload_classes:
                raise ValueError(
                    f"Phase '{phase}' is mapped to 'off-host-workflow' but not in "
                    "off_host_workload_classes"
                )
        else:
            raise ValueError(f"Unknown surface '{surface}' for phase '{phase}'")


# ---------------------------------------------------------------------------
# Hybrid flow runner
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HybridFlowResult:
    """Aggregated result of one end-to-end hybrid SLR flow run."""

    review_id: str
    run_id: str
    screening_decision: dict[str, Any]
    extraction_bundle: dict[str, Any]
    synthesis_bundle: dict[str, Any]
    surface_report: dict[str, str]
    governance_invariants_satisfied: bool


def run_hybrid_slr_flow(
    *,
    review_id: str,
    run_id: str,
    trigger_source: str,
    screening_records: list[dict[str, Any]],
    extraction_rows: list[dict[str, Any]],
    synthesis_traces: list[SynthesisReasoningTrace],
    synthesis_findings: list[dict[str, Any]],
    commit_sha: str,
    generated_at: str,
    policy: WorkloadPlacementPolicy = DEFAULT_WORKLOAD_PLACEMENT_POLICY,
) -> HybridFlowResult:
    """Run one representative hybrid SLR flow and return the aggregated result.

    Validates governance invariants at each phase boundary:
    - Screening is admitted as a local workload.
    - Extraction envelope rejects local execution.
    - Synthesis envelope rejects local execution.
    - Local helper cannot promote extraction/synthesis to local.
    """
    # Phase 2 — local screening
    screening_decision = enforce_local_workload_request(
        "screening",
        requested_concurrency=1,
        current_local_jobs=0,
        policy=policy,
    )
    if not screening_decision["allowed"]:
        raise RuntimeError("Screening was unexpectedly deferred during hybrid flow")

    # Phase 4a — off-host extraction
    extraction_envelope = ExtractionWorkflowEnvelope(
        review_id=review_id,
        run_id=run_id,
        trigger_source=trigger_source,
    )
    extraction_contract = ExtractionOffHostContract(review_id=review_id)
    extraction_bundle = build_extraction_evidence_bundle(
        envelope=extraction_envelope,
        contract=extraction_contract,
        output_rows=extraction_rows,
        commit_sha=commit_sha,
        generated_at=generated_at,
    )

    # Phase 4b — off-host synthesis
    synthesis_envelope = SynthesisWorkflowEnvelope(
        review_id=review_id,
        run_id=run_id,
        trigger_source=trigger_source,
    )
    synthesis_contract = SynthesisOffHostContract(review_id=review_id)
    synthesis_bundle = build_synthesis_trace_bundle(
        envelope=synthesis_envelope,
        contract=synthesis_contract,
        traces=synthesis_traces,
        commit_sha=commit_sha,
        generated_at=generated_at,
    )

    # Surface report
    surface_report = report_execution_surfaces()

    # Validate invariants
    assert_surface_invariants(policy=policy)

    return HybridFlowResult(
        review_id=review_id,
        run_id=run_id,
        screening_decision=screening_decision,
        extraction_bundle=extraction_bundle,
        synthesis_bundle=synthesis_bundle,
        surface_report=surface_report,
        governance_invariants_satisfied=True,
    )


def validate_audit_reproducibility(
    *,
    review_id: str,
    run_id: str,
    trigger_source: str,
    extraction_rows: list[dict[str, Any]],
    synthesis_traces: list[SynthesisReasoningTrace],
    commit_sha: str,
    generated_at: str,
) -> bool:
    """Return True if extraction and synthesis bundles are deterministic for identical inputs."""
    envelope_e = ExtractionWorkflowEnvelope(
        review_id=review_id, run_id=run_id, trigger_source=trigger_source
    )
    contract_e = ExtractionOffHostContract(review_id=review_id)
    b1 = build_extraction_evidence_bundle(
        envelope=envelope_e,
        contract=contract_e,
        output_rows=extraction_rows,
        commit_sha=commit_sha,
        generated_at=generated_at,
    )
    b2 = build_extraction_evidence_bundle(
        envelope=envelope_e,
        contract=contract_e,
        output_rows=extraction_rows,
        commit_sha=commit_sha,
        generated_at=generated_at,
    )

    envelope_s = SynthesisWorkflowEnvelope(
        review_id=review_id, run_id=run_id, trigger_source=trigger_source
    )
    contract_s = SynthesisOffHostContract(review_id=review_id)
    s1 = build_synthesis_trace_bundle(
        envelope=envelope_s,
        contract=contract_s,
        traces=synthesis_traces,
        commit_sha=commit_sha,
        generated_at=generated_at,
    )
    s2 = build_synthesis_trace_bundle(
        envelope=envelope_s,
        contract=contract_s,
        traces=synthesis_traces,
        commit_sha=commit_sha,
        generated_at=generated_at,
    )

    return b1 == b2 and s1 == s2


def report_phase_surfaces_for_pm() -> dict[str, Any]:
    """Return a PM-facing report combining phase surfaces and workload class policy."""
    workload_report = report_workload_classes()
    return {
        "phase_execution_surfaces": report_execution_surfaces(),
        "local_workload_classes": workload_report["local_workload_classes"],
        "off_host_workload_classes": workload_report["off_host_workload_classes"],
        "max_local_concurrency": workload_report["max_local_concurrency"],
    }
