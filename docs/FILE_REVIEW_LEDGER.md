# File Review Ledger

**Created:** 2026-02-05
**Reviewed:** 2026-02-05 (187 tracked files)
**Source:** `git ls-files` (post PR-2 commit `b9ed8c1`)
**Plan:** `docs/REPO_HYGIENE_PLAN_2026-02-05.md` (Section 5)
**Reviewer:** Claude Code (Opus 4.5)

Every tracked file has an explicit decision. No "maybe".

**Status values:** KEEP, MOVE, DELETE, DEPRECATE

---

## 1. `scripts/` (harvesters, preflights, agent entrypoints, validators)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `scripts/agent.py` | Agent entrypoint (orchestrator) | KEEP | none | | `tests/test_agent_*.py` |
| `scripts/scopus_harvest.py` | Scopus harvester | KEEP | none | | `tests/test_scopus_harvest.py` |
| `scripts/sciencedirect_harvest.py` | ScienceDirect harvester | KEEP | none | Added PR #203 | |
| `scripts/wos_harvest.py` | Web of Science harvester | KEEP | none | | |
| `scripts/ieee_harvest.py` | IEEE Xplore harvester | KEEP | none | Uses vendored `xploreapi/` | |
| `scripts/semanticscholar_harvest.py` | Semantic Scholar harvester | KEEP | none | | |
| `scripts/openalex_harvest.py` | OpenAlex harvester | KEEP | none | | |
| `scripts/crossref_harvest.py` | CrossRef harvester | KEEP | none | | |
| `scripts/core_harvest.py` | CORE harvester | KEEP | none | Retry-After support | |
| `scripts/google_scholar_harvest.py` | Google Scholar harvester (via Apify) | KEEP | none | | |
| `scripts/scopus_preflight.py` | Scopus API connectivity check | KEEP | none | | `tests/test_scopus_preflight.py` |
| `scripts/core_preflight.py` | CORE API connectivity check | KEEP | none | | |
| `scripts/crossref_preflight.py` | CrossRef API connectivity check | KEEP | none | | |
| `scripts/ieee_preflight.py` | IEEE API connectivity check | KEEP | none | | |
| `scripts/openalex_preflight.py` | OpenAlex API connectivity check | KEEP | none | | |
| `scripts/semanticscholar_preflight.py` | Semantic Scholar API connectivity check | KEEP | none | | |
| `scripts/wos_preflight.py` | WoS API connectivity check | KEEP | none | | |
| `scripts/validate_json.py` | JSON schema validator | KEEP | none | Core infra | `tests/test_validate_json.py` |
| `scripts/hello_bot.py` | CI smoke test (prints CI context) | KEEP | none | Used by `bot-commit.yml` | |
| `scripts/test_all_harvests.py` | Runs all 9 harvesters with testing tier | KEEP | none | Added PR #203 | |
| `scripts/test_google_scholar.py` | Google Scholar integration test | KEEP | none | Excluded from pytest | |
| `scripts/archive_old_reports.py` | Archives old validation reports (§9.1) | KEEP | none | Added PR-3 | |
| `scripts/convert_scopus_csv_to_json.py` | Converts Scopus CSV to Appendix A JSON (§7.2) | KEEP | none | Added PR-3 | |
| `scripts/elis/imports_to_appendix_a.py` | Imports converter (agent workflow) | KEEP | none | | |
| `scripts/elis/screen_mvp.py` | Screening MVP (agent step B) | KEEP | none | | `tests/test_agent_step_b.py` |
| `scripts/elis/search_mvp.py` | Search MVP (agent step A) | KEEP | none | | |

---

## 2. `schemas/` (JSON schemas + alignment with validator)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `schemas/README.md` | Schema directory overview | KEEP | none | Replaced README-old.md (PR-3) | |
| `schemas/appendix_a.schema.json` | Appendix A (Search) full schema | KEEP | none | Used by `validate_json.py` | |
| `schemas/appendix_a_harvester.schema.json` | Harvester subset schema (no meta/orchestrator fields) | KEEP | none | Added PR-3 | |
| `schemas/appendix_b.schema.json` | Appendix B (Screening) schema | KEEP | none | | |
| `schemas/appendix_c.schema.json` | Appendix C (Extraction) schema | KEEP | none | | |
| `schemas/_legacy/ELIS_Agent_LogEntry.schema.json` | Legacy log entry schema | DEPRECATE | Archive when no longer referenced | v1 schema, superseded | |
| `schemas/_legacy/ELIS_Agent_LogRotationPolicy.schema.json` | Legacy log rotation schema | DEPRECATE | Archive when no longer referenced | v1 schema, superseded | |
| `schemas/_legacy/ELIS_Agent_ValidationErrors.schema.json` | Legacy validation errors schema | DEPRECATE | Archive when no longer referenced | v1 schema, superseded | |
| `schemas/_legacy/ELIS_Appendix_A_Search.schema.json` | Legacy Appendix A schema | DEPRECATE | Archive when no longer referenced | Superseded by `appendix_a.schema.json` | |
| `schemas/_legacy/ELIS_Appendix_B_InclusionExclusion.schema.json` | Legacy Appendix B schema | DEPRECATE | Archive when no longer referenced | v1 schema | |
| `schemas/_legacy/ELIS_Appendix_B_Screening.schema.json` | Legacy Appendix B screening schema | DEPRECATE | Archive when no longer referenced | Superseded by `appendix_b.schema.json` | |
| `schemas/_legacy/ELIS_Appendix_C_Extraction.schema.json` | Legacy Appendix C schema | DEPRECATE | Archive when no longer referenced | Superseded by `appendix_c.schema.json` | |
| `schemas/_legacy/ELIS_Appendix_D_AuditLog.schema.json` | Legacy audit log schema | DEPRECATE | Archive when no longer referenced | v1 schema | |
| `schemas/_legacy/ELIS_Appendix_E_Codebook.schema.json` | Legacy codebook schema | DEPRECATE | Archive when no longer referenced | v1 schema | |
| `schemas/_legacy/ELIS_Appendix_F_RunLogPolicy.schema.json` | Legacy run log policy schema | DEPRECATE | Archive when no longer referenced | v1 schema | |
| `schemas/_legacy/ELIS_Data_Sheets_2025-08-19_v1.0.schema.json` | Legacy composite data sheet schema | DEPRECATE | Archive when no longer referenced | v1 schema | |

---

## 3. `tests/` (unit tests, fixtures)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `tests/test_agent_step_b.py` | Unit test for agent step B (screening) | KEEP | none | | |
| `tests/test_agent_toy.py` | Toy agent smoke test | KEEP | none | | |
| `tests/test_scopus_harvest.py` | Scopus harvester unit test | KEEP | none | | |
| `tests/test_scopus_preflight.py` | Scopus preflight unit test | KEEP | none | | |
| `tests/test_toy_agent_smoke.py` | Toy agent smoke test (variant) | KEEP | none | | |
| `tests/test_validate_json.py` | Validator unit test | KEEP | none | | |
| `tests/fixtures/inputs/.gitkeep` | Placeholder for test input fixtures | KEEP | none | Added PR-3 | |
| `tests/fixtures/expected/.gitkeep` | Placeholder for expected output fixtures | KEEP | none | Added PR-3 | |

---

## 4. `config/` (search configurations)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `config/elis_search_queries.yml` | Legacy search queries (multi-topic) | KEEP | none | Used by legacy mode in harvesters | |
| `config/searches/README.md` | Search config directory overview | KEEP | none | | |
| `config/searches/electoral_integrity_search.yml` | Electoral integrity search config (primary) | KEEP | none | Production search config | |
| `config/searches/tai_awasthi_2025_search.yml` | Tai & Awasthi 2025 search config (benchmark-2) | KEEP | none | Benchmark search config | |

---

## 5. `benchmarks/` (benchmark scripts, configs, queries)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `benchmarks/README.md` | Benchmark directory overview | KEEP | none | Added PR-2 | |
| `benchmarks/config/benchmark_config.yaml` | Darmawan 2021 benchmark config | KEEP | none | Moved from `configs/` in PR-2 | |
| `benchmarks/queries/benchmark_temp_queries.yml` | Benchmark temporary queries | KEEP | none | Moved from `config/` in PR-2 | |
| `benchmarks/scripts/benchmark_elis_adapter.py` | Benchmark data normalization adapter | KEEP | none | Moved from `scripts/` in PR-2 | |
| `benchmarks/scripts/run_benchmark.py` | Benchmark validation runner | KEEP | none | Moved from `scripts/` in PR-2 | |
| `benchmarks/scripts/search_benchmark.py` | Benchmark multi-database search | KEEP | none | Moved from `scripts/` in PR-2 | |

---

## 6. `docs/` (documentation)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `docs/README.md` | Docs directory overview | KEEP | none | Update after PR-3 merge | |
| `docs/CHANGELOG.md` | Protocol changelog (v1.7, v1.8) | KEEP | none | Different from root CHANGELOG.md | |
| `docs/CONTRIBUTING.md` | Contribution guidelines | KEEP | none | | |
| `docs/ELIS_2025_SLR_Protocol_Electoral_Integrity_Strategies_2026-01-28_v2.0_draft-08.1.pdf` | SLR protocol v2.0 draft | KEEP | none | Canonical protocol reference | |
| `docs/ELIS_2025_SLR_Protocol_v1.8.pdf` | SLR protocol v1.8 | KEEP | none | Historical protocol reference | |
| `docs/FILE_REVIEW_LEDGER.md` | This file (file review decisions) | KEEP | none | Added PR-1 | |
| `docs/HARVEST_TEST_PLAN.md` | Production harvest test plan | KEEP | none | Not benchmark-specific | |
| `docs/INTEGRATION_PLAN_V2.md` | Integration plan (benchmark → production) | KEEP | none | | |
| `docs/REPO_HYGIENE_PLAN_2026-02-05.md` | Repo hygiene master plan | KEEP | none | Added PR-1 | |
| `docs/VALIDATION_REPORTS_RETENTION.md` | Validation report retention policy (§9) | KEEP | none | Added PR-3 | |
| `docs/_inventory_tracked_files.txt` | Tracked files inventory baseline | KEEP | Regenerate after ledger | Added PR-1 | |

### `docs/benchmark-1/` (Darmawan 2021 benchmark documentation)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `docs/benchmark-1/README.md` | Benchmark-1 overview | KEEP | none | Historical record | |
| `docs/benchmark-1/docs/BENCHMARK_DARMAWAN_2021.md` | Darmawan benchmark setup | KEEP | none | Paths updated in PR-2 | |
| `docs/benchmark-1/docs/BENCHMARK_DOCUMENTATION_REGISTRY.md` | Benchmark docs registry | KEEP | none | | |
| `docs/benchmark-1/docs/BENCHMARK_EXECUTIVE_SUMMARY.md` | Benchmark executive summary | KEEP | none | | |
| `docs/benchmark-1/docs/BENCHMARK_FINAL_RESULTS.md` | Benchmark final results (42.3%) | KEEP | none | Paths updated in PR-2 | |
| `docs/benchmark-1/docs/BENCHMARK_OBJECTIVE_SUMMARY.md` | Benchmark objective summary | KEEP | none | Paths updated in PR-2 | |
| `docs/benchmark-1/docs/BENCHMARK_WORKFLOW_RUNS_SUMMARY.md` | Benchmark workflow runs summary | KEEP | none | Paths updated in PR-2 | |
| `docs/benchmark-1/docs/archive/BENCHMARK_VALIDATION_REPORT_v1_RUN01.md` | Benchmark validation run 01 | KEEP | none | Archived; paths updated in PR-2 | |

### `docs/benchmark-2/` (Tai & Awasthi 2025 benchmark session)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `docs/benchmark-2/README.md` | Benchmark-2 overview | KEEP | none | | |
| `docs/benchmark-2/GOOGLE_SCHOLAR_NOTES.md` | Google Scholar integration notes | KEEP | none | | |
| `docs/benchmark-2/SESSION_SUMMARY_INTEGRATION_AND_PHASE1.md` | Session summary | KEEP | none | Paths updated in PR-2 | |
| `docs/benchmark-2/TESTING_SESSION_2026-01-30.md` | Testing session notes | KEEP | none | | |
| `docs/benchmark-2/docs/BENCHMARK_2_PHASE1_RESULTS.md` | Phase 1 results | KEEP | none | | |
| `docs/benchmark-2/docs/BENCHMARK_TAI_AWASTHI_2025.md` | Tai & Awasthi benchmark setup | KEEP | none | | |
| `docs/benchmark-2/docs/INTEGRATION_TEST_RESULTS.md` | Integration test results | KEEP | none | | |
| `docs/benchmark-2/docs/Tai_Awasthi_2025_Agile_Government_Systematic_Review_GIQ.pdf` | Reference paper PDF | KEEP | none | Benchmark gold standard source | |
| `docs/benchmark-2/benchmark_2_integration.py` | Benchmark-2 integration script | KEEP | none | Historical; lives in docs as session artifact | |
| `docs/benchmark-2/benchmark_2_runner.py` | Benchmark-2 runner script | KEEP | none | Historical; lives in docs as session artifact | |
| `docs/benchmark-2/configs/benchmark_2_config.yaml` | Benchmark-2 config | KEEP | none | Self-contained benchmark session config | |
| `docs/benchmark-2/data/tai_awasthi_2025_references_FINAL.json` | Gold standard references (Tai & Awasthi) | KEEP | none | Benchmark gold standard | |
| `docs/benchmark-2/full_integration.py` | Full integration script | KEEP | none | Historical session artifact | |
| `docs/benchmark-2/minimal_integration.py` | Minimal integration script | KEEP | none | Historical session artifact | |
| `docs/benchmark-2/rematch_results.py` | Rematch results script | KEEP | none | Historical session artifact | |
| `docs/benchmark-2/results/phase1_full_results.json` | Phase 1 full results | KEEP | none | Benchmark reference data | |
| `docs/benchmark-2/results/test_openalex_results.json` | OpenAlex test results | KEEP | none | Benchmark reference data | |
| `docs/benchmark-2/run_phase1_benchmark.py` | Phase 1 benchmark runner | KEEP | none | Historical session artifact | |
| `docs/benchmark-2/simple_test.py` | Simple test script | KEEP | none | Historical session artifact | |
| `docs/benchmark-2/test_integration.py` | Integration test script | KEEP | none | Historical session artifact | |

---

## 7. `json_jsonl/` (canonical data artefacts)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `json_jsonl/README.md` | Directory overview (canonical vs generated) | KEEP | none | Replaced README-old.md (PR-3) | |
| `json_jsonl/ELIS_Appendix_A_Search_rows.json` | Canonical search results (Appendix A) | KEEP | none | Primary output of harvesters | |
| `json_jsonl/ELIS_Appendix_B_Screening_rows.json` | Canonical screening results (Appendix B) | KEEP | none | | |
| `json_jsonl/ELIS_Appendix_C_DataExtraction_rows.json` | Canonical data extraction (Appendix C, new schema) | KEEP | none | 22 lines; uses `timestamp`/`record_id`/`reviewer_id` | |
| `json_jsonl/ELIS_Appendix_C_Extraction_rows.json` | Canonical extraction (Appendix C, original schema) | KEEP | none | 548 lines; uses `id`/`screening_id`/`key_findings` | |
| `json_jsonl/config/ELIS_Agent_LogRotationPolicy.json` | Log rotation policy config | KEEP | none | Agent governance | |
| `json_jsonl/config/ELIS_Appendix_A_Search_config.json` | Appendix A authoring config | KEEP | none | | |
| `json_jsonl/config/ELIS_Appendix_B_InclusionExclusion_config.json` | Appendix B I/E authoring config | KEEP | none | | |
| `json_jsonl/config/ELIS_Appendix_B_Screening_config.json` | Appendix B screening authoring config | KEEP | none | | |
| `json_jsonl/config/ELIS_Appendix_C_DataExtraction_config.json` | Appendix C authoring config | KEEP | none | | |
| `json_jsonl/config/ELIS_Appendix_E_Codebook_2025-08-19.json` | Codebook config | KEEP | none | | |
| `json_jsonl/config/ELIS_Appendix_F_RunLogPolicy_2025-08-19.json` | Run log policy config | KEEP | none | | |
| `json_jsonl/logs/ELIS_Agent_ValidationErrors.jsonl` | Validation errors log (latest) | KEEP | none | | |
| `json_jsonl/logs/ELIS_Agent_ValidationErrors_2025-08-16.jsonl` | Validation errors log (2025-08-16) | KEEP | none | Historical log | |
| `json_jsonl/logs/ELIS_Appendix_D_AuditLog_2025-08-19.jsonl` | Audit log | KEEP | none | Governance requirement | |

---

## 8. `imports/` (raw database exports)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `imports/README.md` | Imports policy and converter usage | KEEP | none | Updated PR-3 (JSON-only policy) | |

---

## 9. `data/benchmark/` (benchmark gold standard data)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `data/benchmark/benchmark_results.json` | Benchmark-1 aggregated results | KEEP | none | | |
| `data/benchmark/darmawan_2021_references.json` | Darmawan 2021 gold standard (78 studies) | KEEP | none | Referenced by `run_benchmark.py` | |
| `data/benchmark/matched_studies.json` | Matched studies (33 of 78) | KEEP | none | Benchmark output | |
| `data/benchmark/missed_studies.json` | Missed studies (45 of 78) | KEEP | none | Benchmark output | |

---

## 10. `presentations/`

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `presentations/ELIS_Protocol_Summary_2026-02-03.html` | Protocol summary presentation (latest) | KEEP | none | | |
| `presentations/elis_presentation_slides_2025-11-17.html` | Presentation slides (Nov 2025) | KEEP | none | | |

---

## 11. `validation_reports/` (per §9 retention policy: keep 10 most recent)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `validation_reports/.gitkeep` | Placeholder | KEEP | none | | |
| `validation_reports/validation-report.md` | Canonical latest report | KEEP | none | Always kept | |
| `validation_reports/2026-02-05_PR-2_benchmark_restructure_validation.md` | PR-2 validation report | KEEP | none | 1 of 10 most recent | |
| `validation_reports/2025-11-14_121922_validation_report.md` | Timestamped report | KEEP | none | 2 of 10 most recent | |
| `validation_reports/2025-09-30_2025-09-30_103844_validation_report.md` | Timestamped report | KEEP | none | 3 of 10 most recent | |
| `validation_reports/2025-09-29_2025-09-29_161231_validation_report.md` | Timestamped report | KEEP | none | 4 of 10 most recent | |
| `validation_reports/2025-09-29_2025-09-29_154030_validation_report.md` | Timestamped report | KEEP | none | 5 of 10 most recent | |
| `validation_reports/2025-09-29_2025-09-29_145302_validation_report.md` | Timestamped report | KEEP | none | 6 of 10 most recent | |
| `validation_reports/2025-09-29_2025-09-29_130705_validation_report.md` | Timestamped report | KEEP | none | 7 of 10 most recent | |
| `validation_reports/2025-09-29_2025-09-29_103854_validation_report.md` | Timestamped report | KEEP | none | 8 of 10 most recent | |
| `validation_reports/2025-09-29_2025-09-29_103746_validation_report.md` | Timestamped report | KEEP | none | 9 of 10 most recent | |
| `validation_reports/2025-09-23_2025-09-23_124137_validation_report.md` | Timestamped report | KEEP | none | 10 of 10 most recent | |
| `validation_reports/2025-09-23_2025-09-23_124105_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | Run `scripts/archive_old_reports.py --keep 10` | |
| `validation_reports/2025-09-23_2025-09-23_005950_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-23_2025-09-23_005919_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-23_2025-09-23_000053_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-23_2025-09-23_000024_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-22_2025-09-22_235427_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-22_2025-09-22_235259_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-22_2025-09-22_235233_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-22_2025-09-22_235148_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-22_2025-09-22_220046_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-22_2025-09-22_011239_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-21_2025-09-21_033933_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-21_2025-09-21_023310_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-21_2025-09-21_013126_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-20_2025-09-20_205447_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-20_2025-09-20_204714_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | | |
| `validation_reports/2025-09-16_validation_report.md` | Timestamped report | MOVE | `archive/2025/` | Oldest tracked report | |

---

## 12. `xploreapi/` (vendored third-party)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `xploreapi/__init__.py` | IEEE Xplore Python SDK (vendored) | KEEP | none | Excluded from ruff/black | |
| `xploreapi/xploreapi.py` | IEEE Xplore API client (vendored) | KEEP | none | Do not modify | |

---

## 13. `.github/` (workflows, templates)

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `.github/CODEOWNERS` | Code ownership rules | KEEP | none | | |
| `.github/pull_request_template.md` | PR template | KEEP | none | | |
| `.github/workflows/agent-automerge.yml` | Auto-merge workflow | KEEP | none | | |
| `.github/workflows/agent-run.yml` | Agent run workflow | KEEP | none | | |
| `.github/workflows/autoformat.yml` | Black autoformat workflow | KEEP | none | | |
| `.github/workflows/benchmark_2_phase1.yml` | Benchmark-2 phase 1 workflow | KEEP | none | References benchmark-2 | |
| `.github/workflows/benchmark_validation.yml` | Benchmark validation workflow | KEEP | none | Paths updated PR-2 | |
| `.github/workflows/bot-commit.yml` | Bot commit workflow | KEEP | none | Uses `hello_bot.py` | |
| `.github/workflows/ci.yml` | CI (ruff + black + pytest) | KEEP | none | Core CI | |
| `.github/workflows/deep-review.yml` | Deep review workflow | KEEP | none | | |
| `.github/workflows/elis-agent-nightly.yml` | Nightly agent run | KEEP | none | | |
| `.github/workflows/elis-agent-screen.yml` | Screening agent workflow | KEEP | none | | |
| `.github/workflows/elis-agent-search.yml` | Search agent workflow | KEEP | none | | |
| `.github/workflows/elis-api-preflight.yml` | API preflight (all sources) | KEEP | none | | |
| `.github/workflows/elis-housekeeping.yml` | Housekeeping (cleanup old runs) | KEEP | none | | |
| `.github/workflows/elis-ieee-preflight.yml` | IEEE preflight workflow | KEEP | none | | |
| `.github/workflows/elis-imports-convert.yml` | Imports conversion workflow | KEEP | none | | |
| `.github/workflows/elis-scopus-preflight.yml` | Scopus preflight workflow | KEEP | none | | |
| `.github/workflows/elis-search-preflight.yml` | Search preflight workflow | KEEP | none | | |
| `.github/workflows/elis-semanticscholar-preflight.yml` | Semantic Scholar preflight | KEEP | none | | |
| `.github/workflows/elis-validate.yml` | Validation workflow | KEEP | none | | |
| `.github/workflows/elis-wos-preflight.yml` | WoS preflight workflow | KEEP | none | | |
| `.github/workflows/export-docx.yml` | Export to DOCX workflow | KEEP | none | | |
| `.github/workflows/projects-autoadd.yml` | Auto-add to projects | KEEP | none | | |
| `.github/workflows/projects-runid.yml` | Projects run ID workflow | KEEP | none | | |
| `.github/workflows/test_database_harvest.yml` | Database harvest test workflow | KEEP | none | | |
| `.github/workflows/test_google_scholar.yml` | Google Scholar test workflow | KEEP | none | | |
| `.github/workflows/test_scopus_new_config.yml` | Scopus new config test workflow | KEEP | none | | |

---

## 14. Root files

| Path | Purpose | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| `.claudeignore` | Claude Code ignore patterns | KEEP | none | | |
| `.gitattributes` | Git line-ending normalization | KEEP | none | | |
| `.gitignore` | Git ignore patterns | KEEP | none | Updated PR-1 | |
| `CHANGELOG.md` | Software release changelog | KEEP | none | Different from `docs/CHANGELOG.md` (protocol) | |
| `README.md` | Project README | KEEP | none | Update after all PRs merge | |
| `pyproject.toml` | Tooling config (black, ruff, pytest) | KEEP | none | | |
| `requirements.txt` | Python dependencies | KEEP | none | | |

---

## Summary

| Decision | Count | Action needed |
|---|---|---|
| KEEP | 153 | none |
| MOVE | 16 | Run `scripts/archive_old_reports.py --keep 10` |
| DELETE | 0 | — |
| DEPRECATE | 11 | `schemas/_legacy/` — archive when no longer referenced |
| **Total** | **180** | |

**Note:** 187 tracked files, but 7 validation report entries share a MOVE action (one archive command handles all 16).

**Pending actions:**
1. Run `python scripts/archive_old_reports.py --keep 10` to archive 16 old validation reports
2. Regenerate `docs/_inventory_tracked_files.txt` after archive
