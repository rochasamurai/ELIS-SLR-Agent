# HANDOFF — PE-SLR-04 · Local Screening Governance and Evidence

**Date:** 2026-04-21
**PE:** `PE-SLR-04`
**Branch:** `feature/pe-slr-04-local-screening-governance-and-evidence`
**Implementer:** `slr-impl-b` (Claude Code)
**Validator:** `slr-val-a` (CODEX @ `elis-server`)

---

## 1) Summary

Implements local screening governance for `elis-server`: provenance/rationale field
enforcement, borderline-case detection and surfacing, reproducible audit bundles, and
capacity/throttling policy for local screening runs.

All four acceptance criteria are delivered in a single self-contained module
`elis/screening_governance.py` that requires no cross-PE imports. The module is fully
documented in `docs/slr/SCREENING_GOVERNANCE.md` and covered by 19 acceptance tests.

---

## 2) Deliverables

| File | Change |
|------|--------|
| `elis/screening_governance.py` | New module — `ScreeningDecision`, borderline detection, audit bundle, `CapacityPolicy`, `enforce_capacity` |
| `tests/test_screening_governance.py` | New file — 19 acceptance tests covering all ACs |
| `docs/slr/SCREENING_GOVERNANCE.md` | New documentation — field tables, borderline markers, audit bundle schema, capacity policy rationale and usage |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | `ScreeningDecision` dataclass enforces provenance and rationale fields at construction time | PASS |
| AC-2 | `is_borderline()` / `surface_borderline_cases()` detect borderline decisions by decision field or rationale markers | PASS |
| AC-3 | `generate_audit_bundle()` returns reproducible, schema-stable dict with sorted `borderline_ids` | PASS |
| AC-4 | `CapacityPolicy` dataclass + `enforce_capacity()` enforce resource limits on local screening runs | PASS |

---

## 4) Validation Commands

```bash
# PE-specific tests
python -m pytest tests/test_screening_governance.py -v

# Quality gates
python -m black --check .
python -m ruff check .

# Full suite
python -m pytest -q

# Scope gate
git diff --name-status origin/main..HEAD
```

---

## 5) Scope Gate

```
git diff --name-status origin/main..HEAD

A	docs/slr/SCREENING_GOVERNANCE.md
A	elis/screening_governance.py
A	tests/test_screening_governance.py
M	HANDOFF.md
```

No files outside PE-SLR-04 scope are modified.

---

## 6) Design Notes

### Self-contained module

`elis/screening_governance.py` does not import from `elis.screening_local_contract`
(PE-SLR-03, not yet merged to main at implementation time). The UTC timestamp helper
`_now_utc_iso()` is defined locally and is only used in `generate_audit_bundle()` for
the `generated_at` field.

### `ScreeningDecision` as frozen dataclass

Using `@dataclass(frozen=True)` ensures decisions are immutable after construction.
Validation in `__post_init__` enforces non-empty `record_id`, `source_id`, `rationale`,
and `decided_at`, and rejects any `decision` value outside `VALID_DECISIONS`.

### Borderline detection

`is_borderline()` checks two conditions independently:
1. `decision == "borderline"` (explicit decision field)
2. Any uncertainty marker present in `rationale.lower()` (catches cases where the agent
   used `decision="included"` but noted uncertainty in the rationale text)

The `_BORDERLINE_MARKERS` frozenset includes: `uncertain`, `borderline`, `ambiguous`,
`unclear`, `inconclusive`, `marginal`, `review required`, `needs review`.

### Reproducible audit bundle

`generate_audit_bundle()` is deterministic given the same inputs: `decision_counts` is
computed via `Counter`, `borderline_ids` is always `sorted()`, and `capacity_policy` is
a snapshot of the policy fields. Only `generated_at` varies (wall-clock UTC timestamp).

### `CapacityPolicy` defaults

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| `max_records_per_run` | `100` | Keeps pilot runs fast and auditable on elis-server hardware |
| `max_records_per_batch` | `500` | Prevents single bulk imports from exhausting RAM |
| `max_concurrent_runs` | `1` | Avoids I/O contention on shared `artifacts/screening/` |
| `min_seconds_between_runs` | `0` | No mandatory cooldown by default |

---

## 7) Notes for Validator

**Key things to verify:**

1. **AC-1**: Construct a `ScreeningDecision` with empty `rationale` → expect `ValueError`.
   Construct with `decision="maybe"` → expect `ValueError`. Confirm all provenance fields
   (`record_id`, `source_id`, `title`, `decided_at`, `reviewer`) are preserved.

2. **AC-2**: Call `is_borderline()` with `decision="borderline"` → `True`. Call with
   `decision="included"` and `rationale="uncertain methodology"` → `True`. Call with
   `decision="included"` and `rationale="directly relevant"` → `False`.

3. **AC-3**: Call `generate_audit_bundle("r", decisions)` → verify all required keys are
   present, `borderline_ids` is sorted, `decision_counts` is correct.

4. **AC-4**: `DEFAULT_CAPACITY_POLICY.max_records_per_run == 100`. `enforce_capacity` on
   200 records with `max_records_per_run=10` returns exactly 10 records.

5. **Self-contained**: Confirm `elis/screening_governance.py` has no import from
   `elis.screening_local_contract` or any other PE-SLR-03 module.

6. **Quality gates**: `black --check`, `ruff check`, and `pytest -q` must all pass.
