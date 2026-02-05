# Full Validation Report — PR #204 (Combined PR-1/2/3)

**Date:** 2026-02-05
**Validated by:** Claude Code
**PR:** #204 — `chore: repo hygiene + benchmark restructure + full-file review (combined PR-1/2/3)`
**Branch:** `chore/repo-hygiene-benchmark-reorg`
**Plan reference:** `docs/REPO_HYGIENE_PLAN_2026-02-05.md`

---

## Summary

| Section | Description | Status |
|---|---|---|
| §3 | .gitignore and tracked artifacts | PASS |
| §5 | File review ledger | PASS |
| §6 | Benchmark restructure (§6.1-6.3) | PASS |
| §7 | CSV removal and import policy | PASS |
| §8 | Test fixture structure | PASS |
| §9 | Validation report retention | PASS |
| §10 | Config consolidation | PASS |
| §11 | README-old.md cleanup | PASS |
| §13 | CI workflows | PASS |
| Linting | ruff check | PASS |
| Tests | pytest | PASS (25/25) |

**Overall Result:** ALL CHECKS PASS

---

## §3 — .gitignore and Tracked Artifacts

| Check | Expected | Actual | Status |
|---|---|---|---|
| Tracked CSV files | 0 | 0 | PASS |
| Tracked TSV files | 0 | 0 | PASS |
| Tracked XLSX files | 0 | 0 | PASS |
| Tracked .env files | 0 | 0 | PASS |
| Tracked .venv/ | Not tracked | Not tracked | PASS |
| Tracked .pytest_cache/ | Not tracked | Not tracked | PASS |
| Tracked .ruff_cache/ | Not tracked | Not tracked | PASS |
| Tracked .claude/settings.local.json | Not tracked | Not tracked | PASS |
| .gitignore contains all §3.1 patterns | 17 patterns | All present | PASS |

---

## §5 — File Review Ledger

| Check | Expected | Actual | Status |
|---|---|---|---|
| Tracked files in inventory | 187 | 187 | PASS |
| Files with decisions in ledger | >= 187 | 191 | PASS |
| Ambiguous entries (maybe/TBD) | 0 | 0 | PASS |
| Missing files from ledger | 0 | 0 | PASS |

---

## §6 — Benchmark Restructure

### §6.1 Directory Structure

| Path | Expected | Status |
|---|---|---|
| `benchmarks/` | Directory exists | PASS |
| `benchmarks/README.md` | File exists | PASS |
| `benchmarks/config/` | Directory exists | PASS |
| `benchmarks/queries/` | Directory exists | PASS |
| `benchmarks/scripts/` | Directory exists | PASS |
| `benchmarks/fixtures/` | Directory exists | PASS |
| `benchmarks/outputs/` | Directory exists (ignored) | PASS |
| `benchmarks/reports/` | Directory exists (ignored) | PASS |

### §6.2 File Moves

| File | Expected Location | Status |
|---|---|---|
| benchmark_config.yaml | `benchmarks/config/` | PASS |
| benchmark_temp_queries.yml | `benchmarks/queries/` | PASS |
| run_benchmark.py | `benchmarks/scripts/` | PASS |
| search_benchmark.py | `benchmarks/scripts/` | PASS |
| benchmark_elis_adapter.py | `benchmarks/scripts/` | PASS |
| benchmark_search_results.json | Removed from `json_jsonl/` | PASS |
| HARVEST_TEST_PLAN.md | Stayed in `docs/` | PASS |
| `configs/` directory | Deleted | PASS |

### §6.3 Default Tier Safety

| Check | Expected | Actual | Status |
|---|---|---|---|
| Scripts with `"production"` fallback | 0 | 0 | PASS |
| Scripts with `"testing"` fallback | 18 (2×9) | 18 | PASS |

All 9 harvest scripts changed from `"production"` to `"testing"` as default tier.

---

## §7 — CSV Removal and Import Policy

| Check | Status |
|---|---|
| No tracked CSV files | PASS |
| `imports/README.md` exists | PASS |
| JSON-only policy documented | PASS |
| `scripts/convert_scopus_csv_to_json.py` exists | PASS |
| Column documentation in README | PASS (list format) |

---

## §8 — Test Fixture Structure

| Check | Status |
|---|---|
| `tests/fixtures/inputs/.gitkeep` exists | PASS |
| `tests/fixtures/expected/.gitkeep` exists | PASS |
| `tests/outputs/` in .gitignore | PASS |

---

## §9 — Validation Report Retention

| Check | Expected | Actual | Status |
|---|---|---|---|
| `docs/VALIDATION_REPORTS_RETENTION.md` exists | Yes | Yes | PASS |
| `scripts/archive_old_reports.py` exists | Yes | Yes | PASS |
| `validation_reports/archive/2025/` exists | Yes | Yes | PASS |
| Reports archived | >0 | 17 | PASS |
| Reports remaining | <= 10 + new | 12 | PASS |

---

## §10 — Config Consolidation

| Check | Status |
|---|---|
| `configs/` directory deleted | PASS |
| Benchmark configs under `benchmarks/config/` | PASS |

---

## §11 — README-old.md Cleanup

| Check | Status |
|---|---|
| `json_jsonl/README-old.md` removed | PASS |
| `schemas/README-old.md` removed | PASS |
| No `README-old.md` tracked anywhere | PASS |

---

## §13 — CI Workflows

| Check | Status |
|---|---|
| `benchmark_validation.yml` exists | PASS |
| Uses `workflow_dispatch` | PASS |
| Correct benchmark script paths | PASS |
| Uploads artifacts | PASS |

---

## Linting and Tests

### Ruff

```
All checks passed!
```

### Pytest

```
25 passed in 0.73s
```

### validate_json.py

| Appendix | Rows | Status | Notes |
|---|---|---|---|
| A (Search) | 1918 | ERR | Pre-existing schema alignment gap (§12.5) |
| B (Screening) | 155 | OK | |
| C (Extraction) | 78 | OK | |

**Note:** Appendix A errors are pre-existing and documented in §12.5. Harvester outputs lack `id`, `retrieved_at`, `query_topic`, `query_string` — these are added by the orchestrator layer. The `schemas/appendix_a_harvester.schema.json` subset schema was added for standalone harvester testing.

---

## Conclusion

All plan sections (§3, §5, §6, §7, §8, §9, §10, §11, §13) have been validated and pass. The codebase is clean:

- No prohibited file types tracked (CSV/TSV/XLSX/.env)
- All 187 tracked files have explicit decisions in the ledger
- Benchmark assets consolidated under `benchmarks/`
- Default tier safety implemented (all 9 scripts default to "testing")
- Report retention policy implemented and archived 17 old reports
- README-old.md files removed
- Ruff linting passes
- All 25 tests pass

**PR #204 is ready for merge.**
