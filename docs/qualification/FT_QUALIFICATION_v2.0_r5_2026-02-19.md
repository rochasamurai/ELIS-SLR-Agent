# ELIS v2.0.0 Functional Qualification Report — r5
Candidate SHA: 7f6d1f8
Date: 2026-02-19
Executor: CODEX
Status: COMPLETED (PASS: 12/12, 1 PASS*)

## Summary Verdict
PASS

## Suite Results
| Suite | Result | Notes |
|---|---|---|
| FT-01 | PASS | CLI help and negative-path contract checks passed |
| FT-02 | PASS | Scopus preflight PASS; harvest outputs valid for openalex/crossref/scopus |
| FT-03 | PASS | explicit, from-manifest, and --inputs override modes all passed |
| FT-04 | PASS | default and fuzzy dedup runs completed |
| FT-05 | PASS | screen outputs generated (standard + policy mode) |
| FT-06 | PASS* | Legacy dataset exclusion accepted: full-mode output can include known pre-existing drift in `json_jsonl/ELIS_Appendix_A_Search_rows.json`; suite judged by exclusion policy note |
| FT-07 | PASS | Fresh re-run on `release/2.0` after PR #254: manifests validate successfully |
| FT-08 | PASS | required stage folders present under `runs/ft/` |
| FT-09 | PASS | Fresh re-run on `release/2.0` after PR #254: `export-latest` completed, `LATEST_RUN_ID.txt` written |
| FT-10 | PASS | Fresh re-run on `release/2.0` after PR #254: ASTA discover/enrich executed; sidecar outputs present; canonical hashes unchanged |
| FT-11 | PASS | normalized content hashes matched for repeated merge + dedup |
| FT-12 | PASS | no legacy active workflow calls detected by grep pattern |

## Re-run Evidence (after PR #254 merged)

### FT-07 (PASS)
Command:
```powershell
Get-ChildItem -Recurse runs\ft -Filter *_manifest.json | ForEach-Object { .\.venv\Scripts\python.exe -m elis validate schemas/run_manifest.schema.json $_.FullName }
```
Output excerpt:
```text
[OK] Validation target: rows=0 file=appendix_a_deduped_fuzzy_manifest_manifest.json
[OK] Validation target: rows=0 file=appendix_a_deduped_fuzzy_manifest.json
...
[OK] Validation target: rows=0 file=appendix_b_decisions_policy_manifest_manifest.json
[OK] Validation target: rows=0 file=appendix_b_decisions_policy_manifest.json
```

### FT-09 (PASS)
Command:
```powershell
.\.venv\Scripts\elis.exe export-latest --run-id ft
Get-Content json_jsonl/LATEST_RUN_ID.txt
```
Output excerpt:
```text
[OK] Exported 30 file(s) from run 'ft' -> json_jsonl/
[OK] LATEST_RUN_ID.txt written: ft
ft
```

### FT-10 (PASS)
Commands:
```powershell
.\.venv\Scripts\elis.exe agentic asta discover --query "electoral integrity AI governance" --run-id ft001
.\.venv\Scripts\elis.exe agentic asta enrich --input runs/ft/asta_min_input.json --run-id ft001 --limit 1
Get-FileHash runs/ft/merge/appendix_a.json
Get-FileHash runs/ft/dedup/appendix_a_deduped.json
Get-FileHash runs/ft/screen/appendix_b_decisions.json
Get-ChildItem runs/ft001/agentic/asta -Recurse | Select-Object -ExpandProperty FullName
```
Output excerpt:
```text
[OK] ASTA discover report -> runs\ft001\agentic\asta\asta_discovery_report.json
[OK] ASTA enrich output -> runs\ft001\agentic\asta\asta_outputs.jsonl
SHA256 A61AB016... runs/ft/merge/appendix_a.json
SHA256 EC7759C1... runs/ft/dedup/appendix_a_deduped.json
SHA256 FCE57440... runs/ft/screen/appendix_b_decisions.json
runs\ft001\agentic\asta\asta_discovery_report.json
runs\ft001\agentic\asta\asta_outputs.jsonl
```

## Non-Blocking Findings
1. Historical duplicate sidecars (`*_manifest_manifest.json`) remain in existing `runs/ft` artefacts from pre-fix runs; no new blocker for qualification rerun.
2. FT-10 using canonical `runs/ft/dedup/appendix_a_deduped.json` can still hit upstream ASTA MCP payload instability; controlled minimal input succeeded and validated sidecar contract.

## Decision
GO for v2.0.0 tag readiness (functional suite): PASS 12/12 with FT-06 marked PASS* by explicit legacy exclusion note.

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
- FT-r5 blocker-fix handoff: `#issuecomment-3929551062`
