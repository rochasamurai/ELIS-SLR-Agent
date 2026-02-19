# ELIS v2.0.0 Functional Qualification Report — r5
Candidate SHA: c00b3b9
Date: 2026-02-19
Executor: CODEX
Status: COMPLETED (with FAIL findings)

## Summary Verdict
FAIL

## Suite Results
| Suite | Result | Notes |
|---|---|---|
| FT-01 | PASS | CLI help and negative-path contract checks passed |
| FT-02 | PASS | Scopus preflight PASS; harvest outputs valid for openalex/crossref/scopus |
| FT-03 | PASS | explicit, from-manifest, and --inputs override modes all passed |
| FT-04 | PASS | default and fuzzy dedup runs completed |
| FT-05 | PASS | screen outputs generated (standard + policy mode) |
| FT-06 | FAIL | legacy full-mode reported `[ERR] Appendix A (Search)` |
| FT-07 | FAIL | run-manifest validations via `elis validate` returned `Expected array, got dict` |
| FT-08 | PASS | required stage folders present under `runs/ft/` |
| FT-09 | FAIL | `export-latest` crashed with `UnicodeEncodeError` (cp1252 arrow char) |
| FT-10 | FAIL | `elis agentic asta` failed: `ModuleNotFoundError: No module named 'sources'` |
| FT-11 | PASS | normalized content hashes matched for repeated merge + dedup |
| FT-12 | PASS | no legacy active workflow calls detected by grep pattern |

## Blocking Findings
1. FT-06: `elis validate` full mode reports `[ERR] Appendix A (Search)` on current dataset.
2. FT-07: run-manifest validation path fails with `Expected array, got dict` across manifests.
3. FT-09: `elis export-latest --run-id ft` crashes with `UnicodeEncodeError` before writing `LATEST_RUN_ID.txt`.
4. FT-10: ASTA CLI path fails to import adapter module (`ModuleNotFoundError: No module named 'sources'`).

## Non-Blocking Findings
1. Duplicate sidecar artifacts observed (`*_manifest_manifest.json`) in `runs/ft/*`.

## Decision
NO-GO for v2.0.0 tag at candidate SHA `c00b3b9` until blocking findings are fixed and affected suites are re-run.

## Evidence (PR #252 comments)
- Setup + preflight: `#issuecomment-3928677547`
- FT-01: `#issuecomment-3928696006`
- FT-02: `#issuecomment-3928705708`
- FT-03: `#issuecomment-3928710585`
- FT-04: `#issuecomment-3928716090`
- FT-05: `#issuecomment-3928719014`
- FT-06: `#issuecomment-3928724166`
- FT-07: `#issuecomment-3928728720`
- FT-08: `#issuecomment-3928734950`
- FT-09: `#issuecomment-3928742644`
- FT-10: `#issuecomment-3928752403`
- FT-11: `#issuecomment-3928766238`
- FT-12: `#issuecomment-3928768486`
