# ELIS v2.0.0 Functional Qualification Report (r3)

Candidate SHA: 05860fb9ff8b59a95dce593840b657346214b1b1
Date: 2026-02-18
Executor: CODEX

## Summary Verdict
FAIL

## Suite Results
| Suite | Result | Notes |
|---|---|---|
| FT-01 | PASS (precondition) | Prior FT-01 blocker fixed by merged hotfix PR #238 (hotfix/pe3-merge-manifest-notfound). |
| FT-02 | PASS | OpenAlex and CrossRef harvested/validated (25 rows each); Scopus harvested 0 rows and still validated. |
| FT-03 | FAIL | Step 2 (--from-manifest) exits 1 with no controlled message after FT-02 validation sidecar overwrite of harvest manifest. |
| FT-04 | NOT RUN | Stopped after FT-03 failure per ordered execution rule. |
| FT-05 | NOT RUN | Stopped after FT-03 failure per ordered execution rule. |
| FT-06 | NOT RUN | Stopped after FT-03 failure per ordered execution rule. |
| FT-07 | NOT RUN | Stopped after FT-03 failure per ordered execution rule. |
| FT-08 | NOT RUN | Stopped after FT-03 failure per ordered execution rule. |
| FT-09 | NOT RUN | Stopped after FT-03 failure per ordered execution rule. |
| FT-10 | NOT RUN | Stopped after FT-03 failure per ordered execution rule. |
| FT-11 | NOT RUN | Stopped after FT-03 failure per ordered execution rule. |
| FT-12 | NOT RUN | Stopped after FT-03 failure per ordered execution rule. |

## Blocking Findings
1. FT-03 manifest mode regression: lis merge --from-manifest reports/ft/r2/FT-02/harvest/openalex_manifest.json fails (exit 1, empty output).
2. Root cause evidence: openalex_manifest.json in FT-02 harvest path was overwritten by validate-stage sidecar (stage: validate, source: system) and includes schema path in input_paths, so merge manifest-mode no longer points to pure harvest inputs.

## Non-Blocking Findings
1. FT-02 results are deterministic and schema-valid for harvested outputs in this run.

## Decision
NO-GO for v2.0.0 tag

## Execution Evidence

### Preflight Pin Check
`	ext
$ git rev-parse HEAD
05860fb9ff8b59a95dce593840b657346214b1b1
`

### FT-02: Harvest
Artefacts:
- eports/ft/r2/FT-02/harvest/openalex.json
- eports/ft/r2/FT-02/harvest/crossref.json
- eports/ft/r2/FT-02/harvest/scopus.json
- eports/ft/r2/FT-02/harvest/openalex_manifest.json
- eports/ft/r2/FT-02/harvest/crossref_manifest.json
- eports/ft/r2/FT-02/harvest/scopus_manifest.json

### 01_openalex_harvest.log.txt
`	ext
$ .\.venv\Scripts\elis harvest openalex --search-config config/searches/electoral_integrity_search.yml --tier testing --output reports/ft/r2/FT-02/harvest/openalex.json
ExitCode: 0
Output:

================================================================================
OPENALEX HARVEST � NEW CONFIG
================================================================================
Queries: 1
Max results per query: 25
Output: reports/ft/r2/FT-02/harvest/openalex.json
================================================================================


================================================================================
[OK] OpenAlex harvest complete
================================================================================
New results added: 25
Total records in dataset: 25
Saved to: reports/ft/r2/FT-02/harvest/openalex.json
================================================================================



` 

### 02_crossref_harvest.log.txt
`	ext
$ .\.venv\Scripts\elis harvest crossref --search-config config/searches/electoral_integrity_search.yml --tier testing --output reports/ft/r2/FT-02/harvest/crossref.json
ExitCode: 0
Output:

================================================================================
CROSSREF HARVEST � NEW CONFIG
================================================================================
Queries: 1
Max results per query: 25
Output: reports/ft/r2/FT-02/harvest/crossref.json
================================================================================


================================================================================
[OK] CrossRef harvest complete
================================================================================
New results added: 25
Total records in dataset: 25
Saved to: reports/ft/r2/FT-02/harvest/crossref.json
================================================================================



` 

### 03_scopus_harvest.log.txt
`	ext
$ .\.venv\Scripts\elis harvest scopus --search-config config/searches/electoral_integrity_search.yml --tier testing --output reports/ft/r2/FT-02/harvest/scopus.json
ExitCode: 0
Output:

================================================================================
SCOPUS HARVEST � NEW CONFIG
================================================================================
Queries: 1
Max results per query: 25
Output: reports/ft/r2/FT-02/harvest/scopus.json
================================================================================


================================================================================
[OK] Scopus harvest complete
================================================================================
New results added: 0
Total records in dataset: 0
Saved to: reports/ft/r2/FT-02/harvest/scopus.json
================================================================================



` 

### 04_validate_openalex.log.txt
`	ext
$ .\.venv\Scripts\python -m elis validate schemas/appendix_a_harvester.schema.json reports/ft/r2/FT-02/harvest/openalex.json
ExitCode: 0
Output:
[OK] Validation target: rows=25 file=openalex.json


` 

### 05_validate_crossref.log.txt
`	ext
$ .\.venv\Scripts\python -m elis validate schemas/appendix_a_harvester.schema.json reports/ft/r2/FT-02/harvest/crossref.json
ExitCode: 0
Output:
[OK] Validation target: rows=25 file=crossref.json


` 

### 06_validate_scopus.log.txt
`	ext
$ .\.venv\Scripts\python -m elis validate schemas/appendix_a_harvester.schema.json reports/ft/r2/FT-02/harvest/scopus.json
ExitCode: 0
Output:
[OK] Validation target: rows=0 file=scopus.json


` 



### FT-03: Merge
Artefacts:
- eports/ft/r2/FT-03/out/appendix_a.json
- eports/ft/r2/FT-03/out/merge_report.json
- eports/ft/r2/FT-03/logs/01_merge_inputs.log.txt
- eports/ft/r2/FT-03/logs/02_merge_manifest.log.txt

### 01_merge_inputs.log.txt
`	ext
$ .\.venv\Scripts\elis merge --inputs reports/ft/r2/FT-02/harvest/openalex.json reports/ft/r2/FT-02/harvest/crossref.json reports/ft/r2/FT-02/harvest/scopus.json --output reports/ft/r2/FT-03/out/appendix_a.json --report reports/ft/r2/FT-03/out/merge_report.json
ExitCode: 0
Output:
[OK] Merged 3 input file(s) -> reports/ft/r2/FT-03/out/appendix_a.json
[OK] Merge report -> reports/ft/r2/FT-03/out/merge_report.json


` 

### 02_merge_manifest.log.txt
`	ext
$ .\.venv\Scripts\elis merge --from-manifest reports/ft/r2/FT-02/harvest/openalex_manifest.json --output reports/ft/r2/FT-03/out/from_manifest_appendix_a.json --report reports/ft/r2/FT-03/out/from_manifest_report.json
ExitCode: 1
Output:


` 



### Stop Condition
FT-03 failed at step 2 (--from-manifest), so FT-04 through FT-12 were not run.
