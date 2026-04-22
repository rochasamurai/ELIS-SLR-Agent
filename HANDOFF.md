# HANDOFF — PE-SLR-10 · End-to-End Hybrid SLR Validation

**Date:** 2026-04-22
**PE:** `PE-SLR-10`
**Branch:** `feature/pe-slr-10-end-to-end-hybrid-slr-validation`
**Implementer:** `slr-impl-b` (Claude Code)
**Validator:** `slr-val-a` (CODEX @ `elis-server`)

---

## 1) Summary

Validates one representative hybrid SLR flow end-to-end by composing the contracts
built in PE-SLR-07, PE-SLR-08, and PE-SLR-09:

- execution surface registry mapping each SLR phase to local or off-host
- `run_hybrid_slr_flow` exercises local screening + off-host extraction + off-host synthesis
- `assert_surface_invariants` verifies the registry is consistent with the active placement policy
- `validate_audit_reproducibility` confirms SHA-256 digests are deterministic for identical inputs
- `report_phase_surfaces_for_pm` provides a combined PM-facing surface and policy report

---

## 2) Deliverables

| File | Change |
|------|--------|
| `elis/hybrid_slr_validation.py` | New module implementing hybrid flow runner, surface registry, invariant checks, reproducibility validation, and PM reporting |
| `tests/test_hybrid_slr_validation.py` | New test suite with 10 tests covering AC-1 to AC-5 |
| `docs/slr/HYBRID_SLR_VALIDATION.md` | New documentation for hybrid flow, surface registry, and invariants |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | PM can report execution surface by SLR phase accurately | PASS |
| AC-2 | One representative hybrid SLR flow exercises local + off-host contracts together | PASS |
| AC-3 | Governance invariants are verifiable: extraction/synthesis off-host, screening local | PASS |
| AC-4 | Hybrid flow audit evidence is reproducible | PASS |
| AC-5 | `python -m pytest tests/test_hybrid_slr_validation.py -v` passes | PASS |

---

## 4) Validation Commands

```bash
python -m black --check elis/hybrid_slr_validation.py tests/test_hybrid_slr_validation.py
python -m ruff check elis/hybrid_slr_validation.py tests/test_hybrid_slr_validation.py
python -m pytest tests/test_hybrid_slr_validation.py -v
```

---

## 5) Scope Gate

```bash
git diff --name-status origin/main..HEAD

M  HANDOFF.md
A  docs/slr/HYBRID_SLR_VALIDATION.md
A  elis/hybrid_slr_validation.py
A  tests/test_hybrid_slr_validation.py
```

---

## 6) Design Notes

### Composition over re-implementation

`hybrid_slr_validation.py` imports and composes the contracts from PE-SLR-07
(`ExtractionWorkflowEnvelope`, `build_extraction_evidence_bundle`), PE-SLR-08
(`SynthesisWorkflowEnvelope`, `build_synthesis_trace_bundle`), and PE-SLR-09
(`enforce_local_workload_request`, `WorkloadPlacementPolicy`). No governance
logic is duplicated.

### Surface registry as the single source of truth

`_PHASE_SURFACES` maps every SLR phase to its canonical execution surface.
`assert_surface_invariants` cross-checks this map against the active placement
policy, so any future policy change that contradicts the registry is caught
immediately.

### Reproducibility by construction

Both extraction and synthesis bundles use canonical JSON + SHA-256, so
`validate_audit_reproducibility` simply calls each builder twice and compares
the results.

---

## 7) Notes for Validator

1. Confirm `report_execution_surfaces()` returns correct surface for each phase.
2. Confirm `run_hybrid_slr_flow` completes without error and returns
   `governance_invariants_satisfied=True`.
3. Confirm extraction and synthesis bundles in the flow result have
   `execution_surface="off-host-workflow"` and `local_execution_allowed=False`.
4. Confirm `validate_audit_reproducibility` returns `True`.
5. Confirm `assert_surface_invariants` raises on a mismatched policy.
6. Run `python -m pytest tests/test_hybrid_slr_validation.py -v` and verify all pass.
