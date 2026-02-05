# PR-2 Benchmark Restructure — Validation Report

**Date:** 2026-02-05
**Branch:** `chore/repo-hygiene-benchmark-reorg`
**Plan reference:** `docs/REPO_HYGIENE_PLAN_2026-02-05.md` sections 6.1–6.3, 11.1
**Validator:** Claude Code (Opus 4.5)

---

## Summary

| Category | Checks | Passed | Failed |
|---|---|---|---|
| Directory structure (§6.1) | 1 | 1 | 0 |
| File moves (§6.2) | 6 | 6 | 0 |
| Doc reference updates | 8 | 8 | 0 |
| Workflow updates | 1 | 1 | 0 |
| .gitignore coverage | 3 | 3 | 0 |
| configs/ deletion (§11.1) | 1 | 1 | 0 |
| Default tier audit (§6.3) | 1 | 0 | 1 (fixed) |
| **Total** | **21** | **20** | **1 (fixed)** |

**Verdict:** ALL PASS after fix applied.

---

## 1. Directory Structure (§6.1)

Target layout from plan vs actual:

| Plan §6.1 | Present | Status |
|---|---|---|
| `benchmarks/README.md` | Yes | PASS |
| `benchmarks/config/benchmark_config.yaml` | Yes | PASS |
| `benchmarks/queries/benchmark_temp_queries.yml` | Yes | PASS |
| `benchmarks/queries/benchmark_queries.yml` | No | OK (plan: "if benchmark queries exist/added") |
| `benchmarks/scripts/run_benchmark.py` | Yes | PASS |
| `benchmarks/scripts/search_benchmark.py` | Yes | PASS |
| `benchmarks/scripts/benchmark_elis_adapter.py` | Yes | PASS |
| `benchmarks/fixtures/` | Empty | OK (no fixtures yet) |
| `benchmarks/outputs/` | Yes (generated) | PASS |
| `benchmarks/reports/` | Yes (empty) | PASS |

---

## 2. File Moves (§6.2)

Content comparison of each moved file against its last committed version (via `git show HEAD:<old-path>`):

| Old Location | New Location | Content | Status |
|---|---|---|---|
| `config/benchmark_temp_queries.yml` | `benchmarks/queries/benchmark_temp_queries.yml` | Identical | PASS |
| `configs/benchmark_config.yaml` | `benchmarks/config/benchmark_config.yaml` | Identical | PASS |
| `scripts/benchmark_elis_adapter.py` | `benchmarks/scripts/benchmark_elis_adapter.py` | Identical | PASS |
| `scripts/search_benchmark.py` | `benchmarks/scripts/search_benchmark.py` | Identical | PASS |
| `scripts/run_benchmark.py` | `benchmarks/scripts/run_benchmark.py` | 3 path refs updated (intentional) | PASS |
| `json_jsonl/benchmark_search_results.json` | `benchmarks/outputs/benchmark_search_results.json` | Identical (line endings only) | PASS |

`run_benchmark.py` path updates (3 lines):
- Line 31: default config path `configs/benchmark_config.yaml` -> `benchmarks/config/benchmark_config.yaml`
- Lines 387-388: docstring script/config references updated

---

## 3. Doc Reference Updates

All old paths (`scripts/run_benchmark.py`, `configs/benchmark_config.yaml`, etc.) updated to new `benchmarks/` locations:

| File | Changes | Status |
|---|---|---|
| `docs/benchmark-1/docs/BENCHMARK_DARMAWAN_2021.md` | 2 path refs | PASS |
| `docs/benchmark-1/docs/BENCHMARK_FINAL_RESULTS.md` | 4 path refs | PASS |
| `docs/benchmark-1/docs/BENCHMARK_OBJECTIVE_SUMMARY.md` | 7 path refs | PASS |
| `docs/benchmark-1/docs/BENCHMARK_WORKFLOW_RUNS_SUMMARY.md` | 2 path refs | PASS |
| `docs/benchmark-1/docs/archive/BENCHMARK_VALIDATION_REPORT_v1_RUN01.md` | 2 path refs | PASS |
| `docs/benchmark-2/SESSION_SUMMARY_INTEGRATION_AND_PHASE1.md` | 5 path refs | PASS |
| `docs/INTEGRATION_PLAN_V2.md` | 7 path refs | PASS |
| `docs/_inventory_tracked_files.txt` | 5 path entries | PASS |

---

## 4. Workflow Updates

| File | Changes | Status |
|---|---|---|
| `.github/workflows/benchmark_validation.yml` | 3 path refs updated (`search_benchmark.py`, `run_benchmark.py`, `benchmark_search_results.json`) | PASS |

---

## 5. .gitignore Coverage

| Pattern | Present | Status |
|---|---|---|
| `benchmarks/outputs/` | Line 63 | PASS |
| `benchmarks/reports/` | Line 64 | PASS |
| `benchmarks/.cache/` | Line 65 | PASS |

---

## 6. configs/ Directory (§11.1)

`git ls-files configs/` returns only `configs/benchmark_config.yaml`. After deletion from tracking, `configs/` will be completely empty and removed. **PASS**

---

## 7. Default Tier Audit (§6.3)

**Initial state:** All 9 harvest scripts hardcoded `"production"` as fallback default tier (18 occurrences total, 2 per script).

**Plan requirement:** Change fallback from `"production"` to `"testing"` to prevent accidental production-level API usage.

**Fix applied:** Replaced all 18 occurrences of `get("max_results_default", "production")` with `get("max_results_default", "testing")`.

**Verification:** `grep` confirms 0 remaining `"production"` fallbacks, 18 `"testing"` fallbacks across 9 files.

| Script | Occurrences Fixed | Status |
|---|---|---|
| `scripts/scopus_harvest.py` | 2 | FIXED |
| `scripts/sciencedirect_harvest.py` | 2 | FIXED |
| `scripts/wos_harvest.py` | 2 | FIXED |
| `scripts/ieee_harvest.py` | 2 | FIXED |
| `scripts/semanticscholar_harvest.py` | 2 | FIXED |
| `scripts/openalex_harvest.py` | 2 | FIXED |
| `scripts/crossref_harvest.py` | 2 | FIXED |
| `scripts/core_harvest.py` | 2 | FIXED |
| `scripts/google_scholar_harvest.py` | 2 | FIXED |

---

## Plan Doc Update

`docs/REPO_HYGIENE_PLAN_2026-02-05.md` §6.2 move mapping table updated to reflect completed moves (current = target).
