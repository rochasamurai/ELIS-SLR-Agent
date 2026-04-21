# HANDOFF — PE-SLR-06 · Bibliometric Clustering and Discrepancy Pre-analysis

**Date:** 2026-04-21
**PE:** `PE-SLR-06`
**Branch:** `feature/pe-slr-06-bibliometric-clustering-and-discrepancy-pre-analysis`
**Implementer:** `slr-impl-b` (Claude Code)
**Validator:** `slr-val-a` (CODEX @ `elis-server`)

---

## 1) Summary

Implements bounded local support capabilities for bibliometric clustering and
discrepancy pre-analysis on review datasets running on `elis-server`.

All functionality is delivered in `elis/local_support_analysis.py` — a
self-contained module with no cross-PE imports. Advisory-only enforcement is
structural: `BibliometricCluster` and `DiscrepancyReport` reject construction
with `advisory_only=False`, and `DiscrepancyReport.as_final_decision()` raises
unconditionally. Capacity impact is measurable via `measure_capacity_impact()`.
21 acceptance tests pass.

---

## 2) Deliverables

| File | Change |
|------|--------|
| `elis/local_support_analysis.py` | New module — `BibliometricCluster`, `cluster_by_title_similarity` (AC-1), `DiscrepancyReport`, `detect_discrepancies` (AC-2/AC-3), `CapacityReport`, `measure_capacity_impact` (AC-4) |
| `tests/test_local_support_analysis.py` | New file — 21 acceptance tests covering all ACs |
| `docs/slr/LOCAL_SUPPORT_ANALYSIS.md` | New documentation — API reference, capacity rationale, usage examples |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | Bibliometric clustering can run on bounded local datasets | PASS |
| AC-2 | Discrepancy pre-analysis outputs are stored as advisory artefacts only | PASS |
| AC-3 | Runtime safeguards prevent these helpers from being treated as final review decisions | PASS |
| AC-4 | Capacity impact is measured and documented | PASS |
| AC-5 | `python -m pytest tests/test_local_support_analysis.py -v` passes | PASS (21/21) |

---

## 4) Validation Commands

```bash
# PE-specific tests
python -m pytest tests/test_local_support_analysis.py -v

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

A	docs/slr/LOCAL_SUPPORT_ANALYSIS.md
A	elis/local_support_analysis.py
A	tests/test_local_support_analysis.py
M	HANDOFF.md
```

No files outside PE-SLR-06 scope are modified.

---

## 6) Design Notes

### Advisory-only enforcement (AC-2, AC-3)

Both `BibliometricCluster` and `DiscrepancyReport` are frozen dataclasses.
`advisory_only=True` is the default and is validated in `__post_init__` —
passing `advisory_only=False` raises `ValueError` at construction time.
`DiscrepancyReport.as_final_decision()` is a no-return method that raises
`TypeError` unconditionally, making it structurally impossible to use the
report as a decision without an explicit crash.

### Clustering algorithm (AC-1)

Union-find over Jaccard similarity of title word-token sets. Stop words and
short tokens (≤ 2 chars) are excluded. This is intentionally lightweight — no
ML dependencies, O(n²) pair comparison, bounded by `max_records`. Output is
deterministic for stable input (sorted `record_ids` per cluster, clusters
ordered by root index).

### Capacity bound and O(n²) behaviour (AC-4)

Both `cluster_by_title_similarity` and `detect_discrepancies` compare all
pairs: O(n²) iterations. At `max_records=500` (~125,000 iterations), runtime
is < 1 second on elis-server hardware for typical title lengths. The
`DEFAULT_MAX_RECORDS=500` constant matches PE-SLR-04's `max_records_per_batch`
for consistency. Operators must use `measure_capacity_impact()` to confirm
actual timing on their hardware before increasing the cap.

### Self-contained module

`elis/local_support_analysis.py` has no imports from other PE modules
(`elis.screening_governance`, `elis.screening_local_contract`, etc.).

---

## 7) Notes for Validator

**Key things to verify:**

1. **AC-1**: Call `cluster_by_title_similarity` with two near-identical titles
   → expect them in the same cluster. Call with `max_records=10` on a 200-record
   list → expect no record with index ≥ 10 in any cluster.

2. **AC-2**: Confirm `detect_discrepancies` returns `DiscrepancyReport` with
   `advisory_only=True` and non-empty `disclaimer`. Confirm `BibliometricCluster`
   also carries `advisory_only=True`.

3. **AC-3**: Construct `DiscrepancyReport(..., advisory_only=False)` → expect
   `ValueError`. Call `report.as_final_decision()` → expect `TypeError`.

4. **AC-4**: Call `measure_capacity_impact(cluster_by_title_similarity, records,
   max_records=10)` → confirm `CapacityReport.record_count == 10` and
   `elapsed_seconds >= 0`.

5. **Self-contained**: Confirm no import from `elis.screening_governance` or
   `elis.screening_local_contract`.

6. **Quality gates**: `black --check`, `ruff check`, and `pytest -q` must all
   pass (2 pre-existing failures in `test_verify_claude_auth.py` are not
   introduced by this PE).
