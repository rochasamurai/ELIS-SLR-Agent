# Hybrid SLR Validation — PE-SLR-10

## Overview

`elis/hybrid_slr_validation.py` validates one representative hybrid SLR flow
end-to-end, demonstrating that all governance invariants hold across local and
off-host execution surfaces.

## Execution Surface Registry

Each SLR phase is assigned a canonical execution surface:

| Phase | Surface | Workload class |
|-------|---------|----------------|
| Harvest | `off-host-workflow` | off-host |
| Screening | `local` | local |
| Metadata triage | `local` | local |
| Bibliometric pre-analysis | `local` | local |
| Extraction | `off-host-workflow` | off-host |
| Synthesis | `off-host-workflow` | off-host |

`report_execution_surfaces()` returns this map. `assert_surface_invariants()`
verifies every entry is consistent with the active `WorkloadPlacementPolicy`.

## Hybrid Flow

`run_hybrid_slr_flow()` exercises all phase boundaries in sequence:

1. **Screening** — admitted as a local workload via `enforce_local_workload_request`.
2. **Extraction** — governed by `ExtractionWorkflowEnvelope` (off-host only).
3. **Synthesis** — governed by `SynthesisWorkflowEnvelope` (off-host only).
4. **Surface report** — `report_execution_surfaces()` captures the surface map.
5. **Invariant check** — `assert_surface_invariants()` confirms no surface drift.

The function returns a `HybridFlowResult` with the screening decision, extraction
evidence bundle, synthesis trace bundle, and a `governance_invariants_satisfied`
flag.

## Audit Reproducibility

`validate_audit_reproducibility()` confirms that extraction and synthesis bundles
produce identical output (including SHA-256 digests) for identical inputs.

## PM Reporting

`report_phase_surfaces_for_pm()` returns a combined report including:

- `phase_execution_surfaces` — surface map by SLR phase
- `local_workload_classes` — classes allowed to run locally
- `off_host_workload_classes` — classes pinned to off-host workflows
- `max_local_concurrency` — local concurrency cap from the active policy

## Invariants Validated

1. Extraction and synthesis cannot be admitted as local workloads (enforced by
   `ExtractionWorkflowEnvelope` and `SynthesisWorkflowEnvelope`).
2. Screening cannot be promoted to an off-host class (enforced by
   `prevent_local_promotion` in `workload_placement_policy`).
3. Audit evidence is deterministic: identical inputs produce identical digests.
4. Surface registry is consistent with the workload placement policy.
