# ELIS SLR Agent — Repo Hygiene + Full-File Review + Benchmark Reorg Plan (JSON/JSONL-only)
**File:** `docs/REPO_HYGIENE_PLAN_2026-02-05.md`
**Last updated:** 2026-02-05
**Purpose:** Codex/VS Code execution plan to:
1) review the entire project structure and every tracked file,
2) remove obsolete/temporary artifacts safely,
3) reposition benchmark docs/configs/scripts/workflows into a clean, conventional layout,
4) enforce **data files = `.json` / `.jsonl` only** (no `.csv`),
5) add guardrails (ignore rules + CI checks) so the repo stays clean.

> **Note on README updates:** `docs/README.md` and the root `README.md` **will be updated only after PR-1/PR-2/PR-3 are implemented and merged**. Until then, treat this document as the working spec.

---

## 0) Operating rules (non-negotiables)
- **Never lose information:** anything removed must be either (a) reproducible, (b) moved to `docs/archive/`, or (c) explicitly approved for deletion.
- **Tracked vs local:** `.venv/`, `.pytest_cache/`, `.ruff_cache/`, and local editor settings **must never be tracked**.
- **Benchmarks are isolated:** benchmark configs/scripts/outputs must not pollute production configs or canonical protocol appendices.
- **Data files are JSON-only:** any repo "data" must be `.json` or `.jsonl`. Raw vendor exports in `.csv` are **local-only** and ignored.
- **Current output format is JSON arrays:** all harvest scripts currently output `.json` (JSON array). JSONL migration is deferred — see §4.3.
- **Secrets never committed:** `.env`, credential files, and API keys must never be tracked.

---

## 1) Branching and PR strategy
Create a working branch:
- `chore/repo-hygiene-benchmark-reorg`

Preferred PR sequence (keeps diffs reviewable):
1) **PR-1: Hygiene & JSON/JSONL enforcement** (stop tracking junk; block CSV/TSV/XLSX)
2) **PR-2: Benchmark restructure** (move benchmark files to `benchmarks/` + update references)
3) **PR-3: Full-file review + policies + CI guardrails** (ledger, retention, workflows)

---

## 2) Baseline inventory (before touching anything)
Run from repo root.

### 2.1 Confirm clean start
```powershell
git status
git diff --stat
```

### 2.2 Capture tracked inventory
```powershell
# Full tracked-file inventory (canonical file)
git ls-files | Out-File -Encoding utf8 docs/_inventory_tracked_files.txt

# Quick view: top-level directories with tracked content
git ls-files | ForEach-Object { ($_ -split '/')[0] } | Sort-Object -Unique
```
Regenerate `docs/_inventory_tracked_files.txt` whenever the file review ledger is updated.

### 2.3 Identify accidentally tracked local folders/files
```powershell
git ls-files .venv .pytest_cache .ruff_cache .claude 2>$null
```
If output is non-empty, those items are tracked and must be removed from Git going forward (via `git rm --cached`).

---

## 3) PR-1 — Practical repo hygiene (cleanup + prevention)

### 3.1 Update `.gitignore` (minimum viable)
Ensure these patterns exist:

```gitignore
# Local environments / caches
.venv/
.pytest_cache/
.ruff_cache/
__pycache__/
*.pyc

# Secrets / credentials (never commit)
.env
.env.*
.env.local
.env.*.local
*.pem
credentials.json

# Local editor / agent settings
.claude/settings.local.json

# Data policy: only json/jsonl committed
**/*.csv
**/*.tsv
**/*.xlsx

# Local/raw exports and staging (keep out of repo)
imports/raw/
imports/staging/

# Generated benchmark outputs/reports
benchmarks/outputs/
benchmarks/reports/
benchmarks/.cache/

# Generated test outputs
tests/outputs/

# Logs (no scripts currently produce log files, but prevent future accidents)
logs/
*.log
```

> If you intentionally keep an example file in a prohibited format (not recommended), add a narrow exception with `!path/to/file.csv` and document why.

### 3.2 Untrack any mistakenly committed local folders
If any are tracked (from step 2.3), run:
```powershell
git rm -r --cached .venv .pytest_cache .ruff_cache
git rm --cached .claude/settings.local.json
```

### 3.3 Remove any tracked CSV/TSV/XLSX immediately
Check:
```powershell
git ls-files "*.csv" "*.tsv" "*.xlsx"
```
If any appear, remove from tracking and keep local copies under `imports/raw/` if needed:
```powershell
git rm --cached <path/to/file.csv>
```

### 3.4 Commit PR-1
```powershell
git add .gitignore
git commit -m "chore: enforce json/jsonl-only data and ignore local artifacts"
git push
```

**PR-1 checkpoint (must pass):**
- `git ls-files "*.csv" "*.tsv" "*.xlsx"` returns **empty**
- `git ls-files ".env*"` returns **empty**
- `git status` clean after tests
- no local artifacts are tracked

---

## 4) Canonical data format policy (what gets committed)

### 4.1 Canonical formats
- **`.json` (current)**: all harvest scripts currently output JSON arrays (e.g., `ELIS_Appendix_A_Search_rows.json`)
- **`.jsonl` (future preferred)**: row-oriented datasets — to be adopted in a future migration

### 4.2 Canonical vs generated
**Canonical (may stay tracked):**
- `docs/ELIS_2025_SLR_Protocol_*.pdf` (protocol references)
- `schemas/*.schema.json` (data contract)
- `scripts/validate_json.py` (contract enforcement)
- `json_jsonl/ELIS_Appendix_*_rows.json` (canonical reference datasets — current JSON array format)
- **Tiny fixtures** used in tests/benchmarks (see §8)

**Generated (should be ignored):**
- benchmark outputs under `benchmarks/outputs/`
- most validation logs/reports unless curated (see §9)
- test run outputs under `tests/outputs/` (generated)

### 4.3 JSON array → JSONL migration (deferred)
All 9 harvest scripts currently output **JSON arrays** (`.json`). The `validate_json.py` validator, the Appendix A schema, and all downstream workflows expect this format.

**Migration to JSONL is deferred** to avoid breaking the existing pipeline. When ready:
1. Update all harvest scripts to support `--format jsonl` flag
2. Update `validate_json.py` to accept both formats
3. Update schemas or add JSONL-specific validation
4. Update GitHub Actions workflows
5. Rename canonical files: `ELIS_Appendix_A_Search_rows.json` → `.jsonl`

Until then, the plan documents use "JSON" to mean JSON arrays and "JSONL" to mean one-record-per-line (future).

---

## 5) Full-file review plan (systematic and auditable)

### 5.1 Create a review ledger (mandatory)
Create: `docs/FILE_REVIEW_LEDGER.md` using this template:

```markdown
# File Review Ledger

| Path | Purpose (1 line) | Status (KEEP/MOVE/DELETE/DEPRECATE) | Action | Notes | Tests/Docs impacted |
|---|---|---:|---|---|---|
| scripts/scopus_harvest.py | Scopus harvester | KEEP | none |  | tests/test_scopus_harvest.py |
```

### 5.2 Review order (highest value first)
1) `scripts/` (harvesters, preflights, agent entrypoints, validators)
2) `schemas/` (Appendix A/B/C schemas + alignment with validator)
3) `tests/` (unit vs integration boundaries; fixture strategy)
4) `config/` + `configs/` (consolidate; remove duplication)
5) `docs/` (keep only active; archive old)
6) `json_jsonl/` (canonical vs generated; remove `README-old.md`)
7) `imports/`, `validation_reports/`, `presentations/`, `data/` (policies)

### 5.3 File-by-file review rule
For each tracked file:
- classify as **KEEP**, **MOVE**, **DEPRECATE**, or **DELETE**
- if MOVE/DELETE: record rationale + destination in ledger
- ensure any code move updates imports, docs links, and tests

Acceptance criteria for "full-file review done":
- `docs/FILE_REVIEW_LEDGER.md` includes **every tracked file** (from `docs/_inventory_tracked_files.txt`)
- no ambiguous "maybe"; each file has a decision

---

## 6) PR-2 — Benchmark restructure (best-practice layout)

### 6.1 Target directory structure
Create a dedicated benchmark root:

```
benchmarks/
  README.md
  config/
    benchmark_config.yaml
  queries/
    benchmark_queries.yml
    benchmark_temp_queries.yml
  scripts/
    run_benchmark.py
    search_benchmark.py
    benchmark_elis_adapter.py
  fixtures/
    inputs/
    expected/
  outputs/        # generated (ignored) -> JSON arrays (JSONL after §4.3 migration)
  reports/        # generated (ignored) -> JSON summaries / md
```

### 6.2 Move mapping (from current tree)
Apply these moves:

| Current | Target |
|---|---|
| `benchmarks/config/benchmark_config.yaml` | `benchmarks/config/benchmark_config.yaml` |
| `benchmarks/queries/benchmark_temp_queries.yml` | `benchmarks/queries/benchmark_temp_queries.yml` |
| *(if benchmark queries exist/added)* | `benchmarks/queries/benchmark_queries.yml` |
| `benchmarks/scripts/run_benchmark.py` | `benchmarks/scripts/run_benchmark.py` |
| `benchmarks/scripts/search_benchmark.py` | `benchmarks/scripts/search_benchmark.py` |
| `benchmarks/scripts/benchmark_elis_adapter.py` | `benchmarks/scripts/benchmark_elis_adapter.py` |
| `benchmarks/outputs/benchmark_search_results.json` | `benchmarks/outputs/benchmark_search_results.json` (generated; ignore) |

> **Note:** `docs/HARVEST_TEST_PLAN.md` stays in `docs/` — it is a production harvest test plan, not benchmark-specific.

### 6.3 Benchmark scripts interface standard (required)
Benchmark scripts must accept explicit paths:
- `--config benchmarks/config/benchmark_config.yaml`
- `--queries benchmarks/queries/benchmark_queries.yml`
- `--out benchmarks/outputs/...json`
- `--tier testing` (mandatory for CI safety; **no `--limit` flag exists**)

No benchmark script should default to production config silently. The default tier should be `testing` or require an explicit `--tier` flag.

> **Current state (audit needed):** All 9 harvest scripts hardcode `"production"` as the fallback default when `max_results_default` is absent from config. Both search configs (`electoral_integrity_search.yml`, `tai_awasthi_2025_search.yml`) also set `production` or `benchmark` as their `max_results_default`. This means running any script without `--tier` silently uses production-level limits. PR-2 should change the hardcoded fallback from `"production"` to `"testing"` in all 9 scripts.

> **Backward compatibility:** No wrapper scripts. The move is a clean cut — update all docs, CI, and scripts in PR-2. Three scripts are internal tools with no external consumers, so wrappers add complexity without benefit.

---

## 7) Imports policy (JSON-only, no CSV in repo data paths)

### 7.1 Repo structure for imports
Adopt a JSON-only staging pattern:

```
imports/
  README.md
  samples/
    scopus_export_sample.json          # committed tiny sample (sanitized)
  raw/                                 # local only (ignored); vendor exports may be here
  staging/                             # local only (ignored); converted JSON goes here
```

### 7.2 Conversion is first-class (CSV → JSON)
If a vendor export arrives only as `.csv`, do **not** commit it. Convert it to JSON:

- Add/standardize script(s):
  - `scripts/convert_scopus_csv_to_json.py` (or similar)

Required converter characteristics:
- deterministic mapping (stable keys)
- robust parsing (quoted delimiters)
- normalization (DOI casing/format, dates)
- JSON array output matching Appendix A schema
- logs: input rows, output rows, dropped/invalid count

Example command:
```powershell
python scripts/convert_scopus_csv_to_json.py `
  --in  imports/raw/scopus_export.csv `
  --out imports/staging/scopus_export_2026-02-05.json
```

Then validate:
```powershell
python scripts/validate_json.py --schema schemas/appendix_a.schema.json --input imports/staging/scopus_export_2026-02-05.json
```

### 7.3 Conversion field mapping (document in imports/README.md)
The converter must document how vendor CSV columns map to Appendix A schema fields:

| CSV Column | JSON Field | Notes |
|---|---|---|
| `Title` | `title` | as-is |
| `Author(s)` | `authors` | split on `; ` into array |
| `Year` | `year` | parse to integer |
| `DOI` | `doi` | lowercase, normalize |
| `Source` | `venue` | journal/conference name |
| `Abstract` | `abstract` | as-is |
| `EID` | `scopus_id` | strip prefix |

---

## 8) Tests and fixtures policy (avoid committing big outputs)

### 8.1 Standardize fixtures
Create:
- `tests/fixtures/inputs/` (small, deterministic inputs)
- `tests/fixtures/expected/` (small golden JSON outputs)
- `tests/outputs/` (generated; ignored)

Reconcile current:
- `tests/fixtures/` → canonical test fixtures (inputs/expected)
- `tests/outputs/` → generated only; ignored

### 8.2 Integration tests vs unit tests
- Unit tests: run without network/secrets by default (`pytest`)
- Integration tests: explicitly marked (e.g., `@pytest.mark.integration`) and run only when secrets exist

---

## 9) Validation reports retention policy (reduce noise)
Current `validation_reports/` is large.

Adopt **Policy A**:
- Keep:
  - `validation_reports/validation-report.md` (canonical/latest)
  - last **N** timestamped reports (suggest N=10)
- Archive older reports into:
  - `validation_reports/archive/2025/`
  - `validation_reports/archive/2026/`

Add a short policy doc:
- `docs/VALIDATION_REPORTS_RETENTION.md`

### 9.1 Archive helper script (optional but recommended)
Add `scripts/archive_old_reports.py` that:
- reads `validation_reports/` for timestamped report files
- keeps the N most recent
- moves older files to `validation_reports/archive/YYYY/`
- prints a summary of moved files
- can be run manually or from CI

---

## 10) Consolidate config directories (`config/` vs `configs/`)
You currently have both `config/` and `configs/`.

Best practice:
- Keep **only `config/`** for production.
- Benchmarks live under `benchmarks/config/`.

Actions:
- Move `benchmarks/config/benchmark_config.yaml` → `benchmarks/config/benchmark_config.yaml`
- Delete `configs/` if empty.

Acceptance criteria:
- `configs/` folder removed (or contains only legacy wrapper with deprecation note)

---

## 11) Obsolete README cleanup (`README-old.md`)
Current:
- `json_jsonl/README-old.md`
- `schemas/README-old.md`

Best practice:
- If content is still relevant: merge into the current README in that folder, then delete old file.
- If not relevant: move to `docs/archive/` (with a note) or delete.

Acceptance criteria:
- No `README-old.md` remains in active directories.

---

## 12) Harvest + JSON contract verification (aligns with this sprint)
Goal: confirm each harvester/preflight generates correct JSON output per schema.

### 12.1 Source list (all 9 production harvesters)
| # | Script | Preflight | ID Field | API Key Env Var |
|---|---|---|---|---|
| 1 | `scripts/scopus_harvest.py` | `scripts/scopus_preflight.py` | `scopus_id` | `SCOPUS_API_KEY` + `SCOPUS_INST_TOKEN` |
| 2 | `scripts/sciencedirect_harvest.py` | *(none)* | `sciencedirect_id` | `SCIENCEDIRECT_API_KEY` + `SCIENCEDIRECT_INST_TOKEN` |
| 3 | `scripts/wos_harvest.py` | `scripts/wos_preflight.py` | `wos_id` | `WEB_OF_SCIENCE_API_KEY` |
| 4 | `scripts/ieee_harvest.py` | `scripts/ieee_preflight.py` | `ieee_id` | `IEEE_EXPLORE_API_KEY` |
| 5 | `scripts/semanticscholar_harvest.py` | `scripts/semanticscholar_preflight.py` | `s2_id` | *(none — public API)* |
| 6 | `scripts/openalex_harvest.py` | `scripts/openalex_preflight.py` | `openalex_id` | *(none — public API)* |
| 7 | `scripts/crossref_harvest.py` | `scripts/crossref_preflight.py` | `doi` | *(none — public API)* |
| 8 | `scripts/core_harvest.py` | `scripts/core_preflight.py` | `core_id` | `CORE_API_KEY` |
| 9 | `scripts/google_scholar_harvest.py` | *(none)* | `google_scholar_id` | `APIFY_API_TOKEN` |

### 12.2 Required checks per source
For each source:
1) run preflight (if exists) with `--tier testing` (limits results to ~25)
2) run harvest with `--tier testing --output tests/outputs/<name>_smoke.json`
3) validate output against schema:
   - Appendix A: `schemas/appendix_a.schema.json`
   - Appendix B: `schemas/appendix_b.schema.json`
   - Appendix C: `schemas/appendix_c.schema.json`
4) record results in a report:
   - `validation_reports/validation-report.md` (latest summary)
   - optionally store timestamped reports in `validation_reports/`

### 12.3 Command pattern (example)
```powershell
# Run preflight (if exists)
python scripts/scopus_preflight.py --search-config config/searches/electoral_integrity_search.yml --tier testing

# Run harvest with testing tier (limits to ~25 results)
python scripts/scopus_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier testing --output tests/outputs/scopus_smoke.json

# Validate against schema
python scripts/validate_json.py --schema schemas/appendix_a.schema.json --input tests/outputs/scopus_smoke.json
```

### 12.4 Batch test runner
Use `scripts/test_all_harvests.py` to run all 9 harvesters with the `testing` tier:
```powershell
python scripts/test_all_harvests.py
```
This script runs each harvester sequentially, validates output structure (ID field presence, type correctness for `authors` and `year`), and prints a pass/fail summary.

### 12.5 Schema alignment gap (known issue)
The Appendix A schema (`schemas/appendix_a.schema.json`) requires these fields on each record:
- `id`, `source`, `retrieved_at`, `query_topic`, `query_string`

The individual harvest scripts currently output:
- `source`, `title`, `authors`, `year`, `doi`, `abstract`, `url`, `<source>_id`

**Missing from harvester output:** `id`, `retrieved_at`, `query_topic`, `query_string`

These fields are added by the orchestrator/agent layer (e.g., `scripts/run_all_harvests.py` or the GitHub Actions workflow), not by individual harvesters. This is **by design** — harvesters are source-specific; the orchestrator adds cross-cutting metadata.

For standalone harvester testing, validation should use a **relaxed schema** or validate only the harvester-specific fields. Add `schemas/appendix_a_harvester.schema.json` as a subset schema for standalone testing.

### 12.6 Rate-limit and transient-error handling (implemented)
CORE is intermittently unavailable (500/503) and aggressively rate-limits (429). All harvest scripts already implement retry with exponential backoff, but CORE required special attention:

- **Retries on 429, 500, 503** with exponential backoff (5s, 10s, 15s, ...), max 5 retries
- **Honors `Retry-After` header** on 429 responses (uses `X-RateLimit-Retry-After`)
- **Logs rate-limit headers** once per run (`X-RateLimit-Remaining`, `X-RateLimit-Limit`, `X-RateLimit-Retry-After`)
- **Warns on low remaining quota** when `X-RateLimit-Remaining` drops below threshold

When testing CORE, expect occasional retries in output — this is normal. If all 5 retries are exhausted, the script stops gracefully with partial results rather than crashing.

Acceptance criteria:
- each source produces well-formed JSON with correct types for the intended appendix contract
- all errors are either fixed or documented with explicit reasons
- schema alignment gap documented (orchestrator vs harvester responsibility)
- transient failures handled gracefully (retry + partial results, no crashes)

---

## 13) PR-3 — Workflows (CI guardrails)
Keep workflows in `.github/workflows/` and add two benchmark workflows:

1) `benchmark_selftest.yml` (manual `workflow_dispatch`)
- Runs each source in **testing tier** (`--tier testing`)
- Validates JSON with `scripts/validate_json.py`
- Uploads artifacts (reports) as workflow artifacts

2) `benchmark_run.yml` (manual + optional schedule weekly)
- Runs deeper benchmark (still rate-limited, `--tier benchmark`)
- Uploads reports/artifacts
- Does not commit generated outputs to repo

Naming convention:
- `benchmark_*` for benchmark workflows
- `harvest_*` for production harvest validations (if introduced later)

> **Existing workflow:** `.github/workflows/test_database_harvest.yml` already tests individual databases via `workflow_dispatch` with `--tier testing`. The benchmark workflows complement this with multi-source batch runs.

---

## 14) Implementation checklist (Codex-ready)

### PR-1: Hygiene + JSON/JSONL enforcement
- [ ] Update `.gitignore` (local caches, venv, benchmark outputs, **block csv/tsv/xlsx**, imports raw/staging, `.env`/secrets, `tests/outputs/`)
- [ ] `git rm --cached` any tracked local artifacts (`.venv`, caches, `.claude/settings.local.json`)
- [ ] `git rm --cached` any tracked `.csv` exports (move local copies to `imports/raw/`)
- [ ] Add `docs/_inventory_tracked_files.txt`
- [ ] Add `docs/FILE_REVIEW_LEDGER.md` skeleton

### PR-2: Benchmarks
- [ ] Create `benchmarks/` structure
- [ ] Move benchmark config/query/script files per §6.2 mapping
- [ ] Move benchmark outputs to `benchmarks/outputs/` (ignored)
- [ ] Delete `configs/` directory after move (§10)
- [ ] Update all docs references to new benchmark paths
- [ ] Confirm `docs/HARVEST_TEST_PLAN.md` stays in `docs/` (not moved)
- [ ] Audit all 9 harvest scripts: change hardcoded fallback tier from `"production"` to `"testing"` (§6.3)

### PR-3: Full-file review + policies + CI
- [ ] Populate `docs/FILE_REVIEW_LEDGER.md` for all tracked files
- [ ] Implement retention policy for `validation_reports/` (§9)
- [ ] Add `scripts/archive_old_reports.py` helper (§9.1)
- [ ] Remove/merge `README-old.md` files (§11)
- [ ] Standardize test fixtures vs outputs (JSON only) (§8)
- [ ] Add/update workflows: `benchmark_selftest.yml`, `benchmark_run.yml` (§13)
- [ ] Add converter script(s) if needed (CSV → JSON), and document field mapping in `imports/README.md` (§7.3)
- [ ] Add `schemas/appendix_a_harvester.schema.json` subset schema for standalone testing (§12.5)

### Final step (after merge): update READMEs
- [ ] Update `docs/README.md` to link to this plan
- [ ] Update root `README.md` to link to this plan (and/or to `docs/README.md`)
- [ ] Verify links render correctly in GitHub

---

## 15) Done criteria (repo-level)
Repo is considered "clean + reorganized" when:
- No local artifacts tracked (`.venv/`, caches, `.claude/settings.local.json`)
- No secrets tracked (`.env`, credential files)
- Data files in repo are **`.json` / `.jsonl` only**
- Any vendor exports in `.csv` are local-only in `imports/raw/` (ignored) and converted to `.json` in `imports/staging/` (ignored)
- All benchmark assets live under `benchmarks/` (configs/queries/scripts/docs references updated)
- `configs/` directory removed
- Generated outputs are ignored; only canonical references + tiny fixtures are tracked
- `docs/FILE_REVIEW_LEDGER.md` covers all tracked files with explicit decisions
- All 9 harvesters tested with `--tier testing` and validated
- Schema alignment gap documented (orchestrator vs harvester responsibility)
- Benchmarks and harvest selftests can run locally and via workflow using testing tier + schema validation
- `docs/README.md` and root `README.md` updated **after** the plan is implemented

---

## Appendix: Changes from previous version

This updated plan incorporates the following corrections and improvements:

1. **Source list expanded to 9** (§12.1): Added `sciencedirect_harvest.py` and `google_scholar_harvest.py` with full details (ID fields, API keys, preflight availability).

2. **CLI flags corrected** (§12.2, §12.3): Replaced non-existent `--limit 5` with actual CLI: `--tier testing` and `--search-config`. All 9 harvesters use `--search-config`, `--tier`, `--max-results`, `--output`.

3. **JSON array format acknowledged** (§4.1, §4.3): Added explicit note that all harvesters currently output JSON arrays (`.json`), not JSONL. JSONL migration deferred with documented migration steps.

4. **HARVEST_TEST_PLAN.md stays in docs/** (§6.2): Removed incorrect proposal to move it to `docs/benchmarks/`. It is a production harvest test plan, not benchmark-specific.

5. **Wrapper scripts removed** (§6.3): Eliminated backward-compatibility wrapper recommendation. Clean cut is simpler for internal tooling with no external consumers.

6. **Secrets added to .gitignore** (§3.1): Added `.env`, `.env.*`, `*.pem`, `credentials.json` patterns.

7. **tests/outputs/ added to .gitignore** (§3.1): Generated test outputs are ignored.

8. **Schema alignment gap documented** (§12.5): Documented that individual harvesters don't produce `id`, `retrieved_at`, `query_topic`, `query_string` — these are added by the orchestrator. Proposed subset schema for standalone testing.

9. **Batch test runner documented** (§12.4): Referenced `scripts/test_all_harvests.py` for running all 9 harvesters.

10. **Benchmark default safety** (§6.3): Added requirement that benchmark scripts must default to `testing` tier or require explicit `--tier` flag.

11. **Archive helper script** (§9.1): Added recommendation for `scripts/archive_old_reports.py` to automate report retention policy.

12. **Import field mapping** (§7.3): Added requirement to document CSV-to-JSON column mapping in `imports/README.md`.
