# ELIS v2.0.0 Post-Release Functional Test Plan

Status: Draft (execution-ready)  
Applies to: Release candidate after PE0-PE6 complete and validated  
Base branch: `release/2.0`

## 1. Objective
Validate that ELIS v2.0.0 is functionally correct, deterministic where required, operationally cut over, and ready for tag `v2.0.0`.

## 2. Entry Criteria
1. PE0-PE6 merged to `release/2.0`.
2. No open blocking findings in PE review files.
3. Required API secrets are configured.
4. Fresh clone / clean worktree.
5. Candidate commit SHA is fixed for test execution.

## 3. Environment Setup
```powershell
git clone https://github.com/rochasamurai/ELIS-SLR-Agent.git
cd ELIS-SLR-Agent
git checkout release/2.0
git pull --ff-only origin release/2.0

python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"
```

## 4. Required Secrets
Set as environment variables before integration runs:
- `SCOPUS_API_KEY`
- `SCOPUS_INST_TOKEN` (if required by tenant)
- `ELIS_CONTACT` (recommended for polite pools)

Not required for v2.0.0 FT commands (adapter coverage planned for v2.1):
- `WEB_OF_SCIENCE_API_KEY`
- `IEEE_EXPLORE_API_KEY`
- `CORE_API_KEY`
- `APIFY_API_TOKEN`
- `SEMANTIC_SCHOLAR_API_KEY`

## 5. Test Execution Matrix

| ID | Suite | Purpose | Pass Condition |
|---|---|---|---|
| FT-01 | CLI Contract | Command surface and argument behavior | Help, error exits, and argument parsing match contract |
| FT-02 | Harvest | Source adapters and outputs | Harvest output valid against `appendix_a_harvester` schema |
| FT-03 | Merge | Canonical Appendix A assembly | Valid Appendix A output; deterministic for same inputs |
| FT-04 | Dedup | Deterministic clustering | Stable `cluster_id`, correct keeper behavior |
| FT-05 | Screen | Appendix B decisions | Valid Appendix B output and expected filters |
| FT-06 | Validate | Validation modes | Correct outputs/exits for full + single-file modes |
| FT-07 | Manifests | Stage sidecars | `*_manifest.json` exists and matches schema |
| FT-08 | Run Layout | Canonical artefact layout | Expected files present under `runs/<run_id>/...` |
| FT-09 | Export View | Backward compatibility projection | `json_jsonl` copy view + `LATEST_RUN_ID.txt` correct |
| FT-10 | ASTA Sidecar | Optional advisory pipeline | Sidecar outputs only; canonical outputs unchanged |
| FT-11 | Determinism | Repeatability | Normalized content parity for deterministic stages |
| FT-12 | Workflow Cutover | Operational release behavior | Required workflows green; no legacy active calls |

## 6. Detailed Functional Steps

### FT-01: CLI Contract
```powershell
elis --help
elis harvest --help
elis merge --help
elis dedup --help
elis screen --help
elis validate --help
elis agentic asta discover --help
elis agentic asta enrich --help
```
Also verify invalid/missing arg behavior:
```powershell
elis merge
elis merge --from-manifest DOES_NOT_EXIST.json
elis validate DOES_NOT_EXIST.json
```

### FT-02: Harvest (testing tier)
Run per source using controlled config.
```powershell
elis harvest openalex --search-config config/searches/electoral_integrity_search.yml --tier testing --output runs/ft/harvest/openalex.json
elis harvest crossref --search-config config/searches/electoral_integrity_search.yml --tier testing --output runs/ft/harvest/crossref.json
elis harvest scopus --search-config config/searches/electoral_integrity_search.yml --tier testing --output runs/ft/harvest/scopus.json
```
Validate harvested outputs:
```powershell
python -m elis validate schemas/appendix_a_harvester.schema.json runs/ft/harvest/openalex.json
python -m elis validate schemas/appendix_a_harvester.schema.json runs/ft/harvest/crossref.json
python -m elis validate schemas/appendix_a_harvester.schema.json runs/ft/harvest/scopus.json
```

### FT-03: Merge
1) Explicit input mode:
```powershell
elis merge --inputs runs/ft/harvest/openalex.json runs/ft/harvest/crossref.json runs/ft/harvest/scopus.json --output runs/ft/merge/appendix_a.json --report runs/ft/merge/merge_report.json
```
2) Manifest mode:
```powershell
elis merge --from-manifest runs/ft/harvest/openalex_manifest.json --output runs/ft/merge/from_manifest_appendix_a.json --report runs/ft/merge/from_manifest_report.json
```
3) Override behavior:
```powershell
elis merge --inputs runs/ft/harvest/crossref.json --from-manifest runs/ft/harvest/openalex_manifest.json --output runs/ft/merge/override_appendix_a.json --report runs/ft/merge/override_report.json
```
Expected result: `--inputs` takes precedence over `--from-manifest` and command exits `0`.

### FT-04: Dedup
```powershell
elis dedup --input runs/ft/merge/appendix_a.json --output runs/ft/dedup/appendix_a_deduped.json --report runs/ft/dedup/dedup_report.json --duplicates runs/ft/dedup/collisions.jsonl
```
Check default non-fuzzy and optional fuzzy:
```powershell
elis dedup --input runs/ft/merge/appendix_a.json --output runs/ft/dedup/appendix_a_deduped_fuzzy.json --report runs/ft/dedup/dedup_report_fuzzy.json --duplicates runs/ft/dedup/collisions_fuzzy.jsonl --fuzzy --threshold 0.85
```

### FT-05: Screen
```powershell
elis screen --input runs/ft/dedup/appendix_a_deduped.json --output runs/ft/screen/appendix_b_decisions.json
```
Optional policy checks:
```powershell
elis screen --input runs/ft/dedup/appendix_a_deduped.json --output runs/ft/screen/appendix_b_decisions_policy.json --enforce-preprint-policy --allow-unknown-language
```

### FT-06: Validate
Single-file:
```powershell
elis validate schemas/appendix_a.schema.json runs/ft/merge/appendix_a.json
elis validate schemas/appendix_b.schema.json runs/ft/screen/appendix_b_decisions.json
```
Legacy full mode:
```powershell
elis validate
```
Note: legacy full-mode currently exits `0` even when it finds validation errors. Mark FT-06 pass/fail from reported validation status (`[OK]` / `[ERR]` lines and error details), not exit code alone.

### FT-07: Manifest Presence and Schema
Required stage sidecars:
- `runs/ft/harvest/*_manifest.json`
- `runs/ft/merge/*_manifest.json`
- `runs/ft/dedup/*_manifest.json`
- `runs/ft/screen/*_manifest.json`
- `validation_reports/*_manifest.json` (from full validate mode, if generated)

Validate all manifests:
```powershell
Get-ChildItem -Recurse runs\ft -Filter *_manifest.json | ForEach-Object { python -m elis validate schemas/run_manifest.schema.json $_.FullName }
```
`runs/` is gitignored. Capture execution evidence separately (zip `runs/ft` as build artefact or attach to release evidence packet).

### FT-08: Canonical Run Layout
Confirm expected stage folders and files exist for the run under test:
- `harvest/`
- `merge/`
- `dedup/`
- `screen/`
- `agentic/asta/` (if FT-10 executed)

### FT-09: Export Compatibility
Run export command, then verify:
```powershell
elis export-latest --run-id ft
```
1. `json_jsonl/` contains latest copies.
2. `json_jsonl/LATEST_RUN_ID.txt` matches exported run.
3. Export is copy-only (no schema mutation).

### FT-10: ASTA Sidecar
Capture canonical baseline hashes before ASTA:
```powershell
Get-FileHash runs/ft/merge/appendix_a.json
Get-FileHash runs/ft/dedup/appendix_a_deduped.json
Get-FileHash runs/ft/screen/appendix_b_decisions.json
```

```powershell
elis agentic asta discover --query "electoral integrity AI governance" --run-id ft001
elis agentic asta enrich --input runs/ft/dedup/appendix_a_deduped.json --run-id ft001
```
Verify outputs under:
- `runs/ft001/agentic/asta/`

Recompute the same hashes after ASTA; all canonical hashes must match baseline.

### FT-11: Determinism
Re-run merge and dedup with identical inputs and compare normalized content hashes.
Do not use raw byte-level `Get-FileHash` for this check because volatile fields differ between runs.
```powershell
elis merge --inputs runs/ft/harvest/openalex.json runs/ft/harvest/crossref.json runs/ft/harvest/scopus.json --output runs/ft/determinism/merge_1.json --report runs/ft/determinism/merge_1_report.json
elis merge --inputs runs/ft/harvest/openalex.json runs/ft/harvest/crossref.json runs/ft/harvest/scopus.json --output runs/ft/determinism/merge_2.json --report runs/ft/determinism/merge_2_report.json

python - <<'PY'
import hashlib, json
from pathlib import Path

def digest(path: str) -> str:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    for row in payload:
        if isinstance(row, dict):
            row.pop("started_at", None)
            row.pop("finished_at", None)
            row.pop("run_id", None)
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

print("merge_1:", digest("runs/ft/determinism/merge_1.json"))
print("merge_2:", digest("runs/ft/determinism/merge_2.json"))
PY
```
Repeat for dedup outputs. Determinism guarantee excludes volatile fields (`started_at`, `finished_at`, `run_id`).

### FT-12: Workflow Cutover
Confirm required workflows are green on the candidate SHA and no active workflow still depends on legacy `scripts/*.py` pipeline commands, except explicitly retained utilities/preflight per release plan.

Required migrated workflows:
- `ci.yml`
- `elis-validate.yml`
- `elis-agent-screen.yml`
- `elis-agent-nightly.yml`
- `elis-agent-search.yml`
- `elis-search-preflight.yml`
- `test_database_harvest.yml`

Executable check:
```powershell
rg -n "python scripts/(.*harvest|elis/search_mvp|elis/screen_mvp|validate_json)\.py" .github/workflows
```
Expected result: no hits for active pipeline calls in the seven workflows above.

## 7. Failure/Negative Tests
1. Missing required source API key should fail fast with clear message.
2. Invalid/missing `--from-manifest` should fail cleanly.
3. Malformed manifest should fail schema validation.
4. Invalid schema/data path in validate mode should return non-zero and clear error.
5. Empty input files should produce valid empty-stage outputs where contract allows.
6. Unknown source should fail clearly:
```powershell
elis harvest wos --search-config config/searches/electoral_integrity_search.yml --tier testing
```
Expected: non-zero exit and clear `Unknown source` message.

## 8. Exit Criteria
1. FT-01..FT-12 pass.
2. No Sev-1/Sev-2 functional defects open.
3. Determinism checks pass.
4. Required workflows green on candidate SHA.
5. Sign-off packet completed.

## 9. Result Template

```markdown
# ELIS v2.0.0 Functional Qualification Report

Candidate SHA: <sha>
Date: <yyyy-mm-dd>
Executor: <name>

## Summary Verdict
PASS / FAIL

## Suite Results
| Suite | Result | Notes |
|---|---|---|
| FT-01 | PASS/FAIL | |
| FT-02 | PASS/FAIL | |
| FT-03 | PASS/FAIL | |
| FT-04 | PASS/FAIL | |
| FT-05 | PASS/FAIL | |
| FT-06 | PASS/FAIL | |
| FT-07 | PASS/FAIL | |
| FT-08 | PASS/FAIL | |
| FT-09 | PASS/FAIL | |
| FT-10 | PASS/FAIL | |
| FT-11 | PASS/FAIL | |
| FT-12 | PASS/FAIL | |

## Blocking Findings
1. <finding>

## Non-Blocking Findings
1. <finding>

## Decision
GO / NO-GO for v2.0.0 tag
```
