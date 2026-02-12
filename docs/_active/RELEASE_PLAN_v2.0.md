# ELIS SLR Agent — RELEASE PLAN v2.0

**Status:** Ready-to-implement  
**Date:** 2026-02-12  
**Applies to:** `rochasamurai/ELIS-SLR-Agent` (current repo structure, workflows, and scripts)

---

## 1. Release intent

### 1.1 Goal
Ship **v2.0.0** as a **single canonical pipeline** with:
- **reproducible, audit-ready artefacts** for every stage; and
- **optional agentic augmentation** (e.g., ASTA) as **append-only sidecars** that never overwrite canonical records.

### 1.2 Non-goals (explicitly out of scope for v2.0.0)
- Default fuzzy deduplication (OK as opt-in only).
- “Autonomous” agentic inclusion/exclusion that bypasses human review.
- Adding new databases unless required to stabilise existing adapters.

---

## 2. Canonical pipeline definition (v2.0 contract)

### 2.1 Canonical stages
1) **Harvest** (per source) → schema-valid harvester rows
2) **Merge** → single canonical Appendix A dataset
3) **Dedup** → deterministic clusters + canonical keeper policy
4) **Validate** → schema validation + reports
5) **Screen** (Appendix B) → decisions are append-only
6) **Extract** (Appendix C) → append-only, evidence-linked

Agentic augmentation (ASTA / LLM) is optional and produces sidecars that reference canonical IDs.

### 2.2 Artefact layout (standard run directory)
All runs MUST be reproducible from the artefacts below.

```
runs/<run_id>/
  run_manifest.json
  harvest/
    <source_id>.jsonl
    <source_id>_manifest.json
  merge/
    appendix_a.jsonl
    merge_report.json
  dedup/
    appendix_a_deduped.jsonl
    dedup_report.json
    collisions.jsonl
  screen/
    appendix_b_decisions.jsonl
    screening_report.json
  agentic/                 # optional
    asta/
      asta_manifest.json
      asta_outputs.jsonl
```

### 2.3 Data contract rules
- `schemas/appendix_a.schema.json` remains the authoritative canonical contract for Appendix A.
- `schemas/appendix_a_harvester.schema.json` is the contract for per-source harvest outputs.
- All schema changes must be versioned (schema_version + changelog note) and gated in CI.

---

## 3. Release strategy (branching, RCs, cut-over)

### 3.1 Branching model
- Create `release/2.0` from `main`.
- RC tags: `v2.0.0-rc.1`, `v2.0.0-rc.2`, ...
- Final tag: `v2.0.0`
- Post-release hotfixes: `v2.0.1`, `v2.0.2` (back on `main`)

### 3.2 Rollout principle
The release is delivered as a sequence of **small, reviewable PRs**, each with:
- deterministic behaviour,
- schema validation,
- a regression strategy (fixtures or equivalence checks), and
- workflow coverage.

---

## 4. Work breakdown: PR series (PE0–PE6)

> **Important:** PE6 includes *mandatory legacy removal* from all harvester scripts, executed late (RC → final) after equivalence checks.

### PE0 — Stabilise the product surface (package + CLI)
**Objective:** Stop drift from “many scripts” and standardise execution.

Deliverables:
- Introduce a single module boundary (e.g., `elis/`) and a CLI entry point:
  - `python -m elis ...` or `elis ...`
- Preserve backwards compatibility by turning existing scripts into thin wrappers.

Acceptance:
- A stable `--help` and consistent argument patterns across commands.
- Workflows can call the CLI without bespoke glue.

### PE1 — Run manifest + stage reports (auditability baseline)
**Objective:** Every stage emits a run manifest and stage reports.

Deliverables:
- `run_manifest.json` at run root
- stage-level manifests (harvest/merge/dedup/screen)
- validation report artefacts (JSON + MD)

Acceptance:
- Pipeline can be replayed from manifests.
- CI fails if required artefacts are missing.

### PE2 — Source adapter layer + shared HTTP client (highest ROI)
**Objective:** Remove duplicated request/pagination/retry logic across harvesters.

Deliverables:
- `SourceAdapter` interface (preflight, harvest, normalise, summarise)
- Shared HTTP client:
  - retry/backoff with jitter
  - 429 and transient 5xx handling
  - configurable per-source rate limits
  - structured logging without secrets
- Port sources incrementally (low friction first; high friction last).

Acceptance:
- At least 2–3 sources run through the adapter layer with fixture-based regression.

### PE3 — Canonical merge stage (Appendix A)
**Objective:** Produce one authoritative Appendix A dataset.

Deliverables:
- `merge/appendix_a.jsonl` plus `merge_report.json`
- Deterministic ordering and stable IDs (or stable keys).

Acceptance:
- Merged output validates against `schemas/appendix_a.schema.json`.
- Merge is input-manifest-driven (no “scan whatever is in json_jsonl/”).

### PE4 — Deterministic dedup + clusters
**Objective:** Deduplicate before screening with explainability.

Dedup policy (default):
1) DOI exact match (normalised)
2) fallback exact key = normalised title + year + first author

Deliverables:
- `dedup/appendix_a_deduped.jsonl`
- `dedup_report.json` + `collisions.jsonl`
- Configurable “keeper precedence” (source priority) in config, not hard-coded.

Acceptance:
- Deterministic cluster IDs.
- No fuzzy matching by default (opt-in flag allowed).

### PE5 — Screening and extraction stages remain append-only
**Objective:** Canonical pipeline supports Appendix B and Appendix C without overwriting records.

Deliverables:
- `screen/appendix_b_decisions.jsonl` + report
- Optional extraction outputs under `extract/` (if included in v2.0)
- Every decision links to record IDs and evidence spans from the record text.

Acceptance:
- Deterministic by default; reviewer overrides are supported.
- Schema validation gates output.

### PE6 — Cut-over + equivalence checks + legacy removal (RC → final)
**Objective:** Ship one codepath, remove legacy modes, and eliminate pipeline divergence.

**This is a required v2.0 deliverable.**

#### PE6.1 Equivalence checks (RC period)
During RCs, for each source migrated:
- Run **legacy harvester** output and **new adapter** output on a small controlled run.
- Compare:
  - record counts (per query and total)
  - schema validity
  - key field hashes (title/year/doi/ids)
  - merge + dedup statistics where applicable

Record results as CI artefacts under `validation_reports/` (or a dedicated `runs/rc_equivalence/` folder).

#### PE6.2 Legacy removal from all harvester scripts (executed late)
Remove legacy options and codepaths from **all** harvester scripts:

Harvester scripts in this repo:
- `scripts/core_harvest.py`
- `scripts/crossref_harvest.py`
- `scripts/google_scholar_harvest.py`
- `scripts/ieee_harvest.py`
- `scripts/openalex_harvest.py`
- `scripts/sciencedirect_harvest.py`
- `scripts/scopus_harvest.py`
- `scripts/semanticscholar_harvest.py`
- `scripts/wos_harvest.py`

Rules:
- Harvester scripts must become thin wrappers invoking the canonical adapter/CLI.
- Remove alternate output formats, legacy schema emitters, and bespoke retry logic.
- Workflows must not call legacy paths.

Acceptance:
- Only one canonical pipeline is used in GitHub Actions and documented usage.
- “Legacy mode” flags and branches are deleted (not hidden).

---

## 5. Workflow mapping (what must remain green)

These workflows exist today under `.github/workflows/`:

- `agent-automerge.yml` — ELIS - Agent AutoMerge
- `agent-run.yml` — ELIS - Agent Run
- `autoformat.yml` — ELIS - Autoformat
- `benchmark_2_phase1.yml` — Benchmark 2 - Phase 1 Execution (Tai & Awasthi 2025)
- `benchmark_validation.yml` — Benchmark Validation - Darmawan 2021
- `bot-commit.yml` — ELIS - Bot Commit (direct to elis-bot via GitHub App)
- `ci.yml` — ELIS - CI
- `deep-review.yml` — ELIS - Deep Review
- `elis-agent-nightly.yml` — ELIS - Agent Nightly
- `elis-agent-screen.yml` — ELIS - Agent Screen (Appendix B)
- `elis-agent-search.yml` — ELIS - Agent Search (Appendix A)
- `elis-housekeeping.yml` — ELIS - Housekeeping
- `elis-imports-convert.yml` — ELIS - Imports Convert
- `elis-search-preflight.yml` — ELIS - Search Preflight / Self-Test
- `elis-validate.yml` — ELIS - Validate
- `export-docx.yml` — ELIS - Export Docx
- `projects-autoadd.yml` — ELIS - Projects Auto-Add
- `projects-runid.yml` — ELIS - Projects Run ID
- `test_database_harvest.yml` — Test Database Harvest Script

**v2.0 requirement:** workflows that run harvest/search/screen/validate must call the canonical CLI/module (not bespoke legacy scripts).

Minimum “must be green” set before tagging `v2.0.0`:
- `ci.yml` (ELIS - CI)
- `elis-validate.yml` (ELIS - Validate)
- `elis-search-preflight.yml` (ELIS - Search Preflight / Self-Test)
- `test_database_harvest.yml` (Test Database Harvest Script)
- `elis-agent-search.yml` (ELIS - Agent Search (Appendix A))
- `elis-agent-screen.yml` (ELIS - Agent Screen (Appendix B))
- `elis-agent-nightly.yml` (ELIS - Agent Nightly)

---

## 6. Repo-specific “contracts to freeze” (to avoid churn)

### 6.1 Folder structure contracts
- `schemas/` (authoritative schemas; `_legacy/` remains read-only or archived)
- `config/searches/*.yml` (search definitions)
- `json_jsonl/` (canonical JSON artefacts and config snapshots)
- `validation_reports/` (retention policy already documented; keep consistent)
- `sources/asta_mcp/` (agentic augmentation adapter; append-only outputs)

### 6.2 Scripts that should become wrappers (post-PE6)
- All `scripts/*_harvest.py` (listed above)
- MVP stage scripts:
- `scripts/elis/imports_to_appendix_a.py`
- `scripts/elis/screen_mvp.py`
- `scripts/elis/search_mvp.py`

These can remain as wrappers but must not contain divergent pipeline logic.

---

## 7. Release deliverables (what gets tagged)

For `v2.0.0`, publish:
- GitHub Release notes with:
  - what changed
  - migration steps (old scripts → new CLI)
  - known limitations (rate limits, provider constraints)
- `docs/MIGRATION_GUIDE_v2.0.md`
- Updated `CHANGELOG.md` (root) and/or `docs/CHANGELOG.md` if you keep both
- A short operational runbook:
  - where keys are stored (secrets)
  - how to run preflight
  - how to interpret reports/manifests

---

## 8. PR checklist (repo-tailored)

Use this checklist in **every** PR going into `release/2.0`.

### 8.1 General
- [ ] PR title is scoped (one PE step or one adapter/source at a time).
- [ ] No secrets added to logs, outputs, or reports.
- [ ] Deterministic behaviour: no random ordering; stable IDs where required.
- [ ] Updated documentation if behaviour, outputs, or flags changed.

### 8.2 Data contracts & artefacts
- [ ] Output validates against relevant schema:
  - Appendix A harvester outputs → `schemas/appendix_a_harvester.schema.json`
  - Appendix A canonical outputs → `schemas/appendix_a.schema.json`
  - Appendix B outputs → `schemas/appendix_b.schema.json`
  - Appendix C outputs → `schemas/appendix_c.schema.json`
- [ ] Run manifest/stage reports produced (or explicitly not yet part of the PE, with a tracking issue).
- [ ] If schemas changed:
  - [ ] update schema versioning note in changelog
  - [ ] update `scripts/validate_json.py` tests (`tests/test_validate_json.py`)

### 8.3 Code health (repo conventions)
- [ ] Formatting/linting: `autoformat.yml` and `ci.yml` remain green.
- [ ] Unit tests updated/added as needed:
  - ASTA: `tests/test_asta_adapter.py`, `tests/test_asta_phase_scripts.py`, `tests/test_asta_vocabulary.py`
  - Scopus: `tests/test_scopus_harvest.py`
  - Validate: `tests/test_validate_json.py`
- [ ] If you changed any harvesters (`scripts/*_harvest.py`):
  - [ ] no new bespoke retry/backoff logic introduced
  - [ ] wrapper-only direction preserved (especially after PE6)

### 8.4 Workflows (must remain green)
- [ ] `ci.yml` passes.
- [ ] `elis-validate.yml` passes and produces a validation report under `validation_reports/`.
- [ ] `elis-search-preflight.yml` passes on the smallest safe “self-test” run.
- [ ] `test_database_harvest.yml` passes (harvest smoke).
- [ ] If screening is affected: `elis-agent-screen.yml` passes.
- [ ] If search is affected: `elis-agent-search.yml` passes.
- [ ] If nightly logic changed: `elis-agent-nightly.yml` passes or is verified via workflow_dispatch.

### 8.5 PE6-specific (RC → final only)
- [ ] Equivalence check run completed for each migrated source (legacy vs canonical):
  - [ ] counts match within agreed tolerance
  - [ ] schema validity is identical
  - [ ] key field hashes comparable
- [ ] Legacy modes/options removed from all harvest scripts (final cut-over PR).
- [ ] No workflow calls legacy codepaths.
- [ ] README and migration guide updated to reflect the single canonical pipeline.

---

## Appendix A — Current repo artefacts referenced by this plan

### Config
- `config/asta_config.yml`
- `config/asta_extracted_vocabulary.yml`
- `config/elis_search_queries.yml`
- `config/searches/README.md`
- `config/searches/electoral_integrity_search.yml`
- `config/searches/tai_awasthi_2025_search.yml`

### Schemas
- `schemas/appendix_a.schema.json`
- `schemas/appendix_a_harvester.schema.json`
- `schemas/appendix_b.schema.json`
- `schemas/appendix_c.schema.json`

### Tests (for release gating)
- `tests/test_agent_step_b.py`
- `tests/test_agent_toy.py`
- `tests/test_asta_adapter.py`
- `tests/test_asta_phase_scripts.py`
- `tests/test_asta_vocabulary.py`
- `tests/test_scopus_harvest.py`
- `tests/test_scopus_preflight.py`
- `tests/test_toy_agent_smoke.py`
- `tests/test_validate_json.py`
