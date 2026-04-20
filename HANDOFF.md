# HANDOFF — PE-SLR-03 · ASReview Screening Pilot

**Date:** 2026-04-20  
**PE:** `PE-SLR-03`  
**Branch:** `feature/pe-slr-03-asreview-screening-pilot`  
**Implementer:** `slr-impl-a` (CODEX @ `elis-server`)  
**Validator:** `slr-val-b` (Claude Code)

---

## 1) Summary

This PE adds the local screening pilot contract and tooling for Phase 2:

- review-scoped screening workspace contract
- schema-bound input/output paths for Appendix A/B
- bounded pilot runner with auditable report + manifest artefacts
- PE-specific test suite for contract behaviour

`elis-server` deployment and runtime pilot execution are deferred by PO decision until after PR merge.

---

## 2) Deliverables

| File | Change |
|------|--------|
| `elis/screening_local_contract.py` | Added screening contract, ASReview detection, bounded pilot execution, and runtime-state storage guard |
| `scripts/run_screening_local_pilot.py` | Added CLI runner for bounded local pilot |
| `tests/test_screening_local_contract.py` | Added PE-SLR-03 contract tests |
| `docs/slr/SCREENING_LOCAL_CONTRACT.md` | Added local screening contract and runbook |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | ASReview installed and runnable on `elis-server` | **DEFERRED TO POST-MERGE DEPLOYMENT** |
| AC-2 | Review-specific screening workspace contract defined | PASS |
| AC-3 | Screening inputs and outputs are schema-bound and auditable | PASS |
| AC-4 | Bounded pilot run completes locally on `elis-server` | **DEFERRED TO POST-MERGE DEPLOYMENT** |
| AC-5 | Screening artefacts are stored outside runtime state directories | PASS |
| AC-6 | `python -m pytest tests/test_screening_local_contract.py -v` passes | PENDING CI |

---

## 4) Validator Findings Addressed

`REVIEW_PE_SLR_03.md` requested:

- F1: Replace incorrect HANDOFF content from prior PE — **fixed** (this file now targets PE-SLR-03).
- F2: Resolve black/test issues — **partially fixed in-code**:
  - normalised path serialisation in report/manifests to `.as_posix()` for cross-platform consistency;
  - Windows-local Python tooling is unavailable in this shell, so black/pytest were not executed locally and must be confirmed by CI.

---

## 5) Scope Gate

```text
git diff --name-status origin/main..HEAD
A	HANDOFF.md
A	docs/slr/SCREENING_LOCAL_CONTRACT.md
A	elis/screening_local_contract.py
A	scripts/run_screening_local_pilot.py
A	tests/test_screening_local_contract.py
```

---

## 6) Validation Commands

```bash
python -m black --check elis/screening_local_contract.py tests/test_screening_local_contract.py
python -m ruff check .
python -m pytest tests/test_screening_local_contract.py -v
git diff --name-status origin/main..HEAD
```

Note: local shell here does not provide `python`, so command execution evidence must come from CI/validator environment.
