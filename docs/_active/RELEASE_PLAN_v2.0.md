# ELIS SLR Agent — RELEASE PLAN v2.0

**Status:** Ready-to-implement
**Date:** 2026-02-12
**Applies to:** `rochasamurai/ELIS-SLR-Agent` at commit `c81328e` on `main`

**Authored by:** Claude Opus 4.6 (Senior Architect) + ChatGPT (Architecture & Code Review)
**Reviewed and ratified by:** Carlos Rocha (Project Owner)

**Inputs synthesised:**

1. Live repo access — file tree, line counts, full source code for key files
2. ChatGPT End-to-End Architecture & Code Review (12 Feb 2026, from ZIP snapshot)
3. ChatGPT RELEASE_PLAN_v2.0.md (initial draft, committed to `docs/_active/`)
4. Claude Senior Architect Review of Refactoring Plan (5 PEs) + Definitive Refactoring Plan
5. Claude–ChatGPT cross-review: 5 adjustments agreed, 2 clarifications ratified
6. ELIS Protocol v2.0 Draft 08.1
7. Full project conversation history (Oct 2025 – Feb 2026)

---

## 1. Release intent

### 1.1 Goal

Ship **v2.0.0** as a **single canonical pipeline** with:

- one installable package (`elis/`), one CLI (`elis <command>`), one codepath;
- **reproducible, audit-ready artefacts** for every stage; and
- **optional agentic augmentation** (ASTA) as **append-only sidecars** that never overwrite canonical records.

v2.0 replaces the current dual-codepath architecture (9 standalone harvesters + 2 MVP pipeline scripts producing incompatible outputs) with a unified pipeline behind stable interfaces.

### 1.2 Non-goals (explicitly out of scope for v2.0.0)

- Default fuzzy deduplication (OK as opt-in only).
- "Autonomous" agentic inclusion/exclusion that bypasses human review.
- Adding new databases unless required to stabilise existing adapters.
- Appendix C extraction code (no implementation exists; tracked as post-v2.0 issue).

---

## 2. Canonical pipeline definition (v2.0 contract)

### 2.1 Canonical stages

```
elis harvest <source>  →  per-source output       (schema: appendix_a_harvester)
elis merge             →  canonical Appendix A     (schema: appendix_a)
elis dedup             →  deduped Appendix A       (schema: appendix_a + cluster fields)
elis screen            →  Appendix B decisions     (schema: appendix_b)
elis validate <path>   →  validation report

elis agentic asta discover  →  ASTA discovery report    (optional, sidecar)
elis agentic asta enrich    →  ASTA evidence layer      (optional, sidecar)
```

Agentic augmentation (ASTA / LLM) is optional and produces sidecars that reference canonical record IDs.

### 2.2 Artefact layout

**v2.0 canonical location:** `runs/<run_id>/`

```
runs/<run_id>/
  run_manifest.json                    # top-level manifest
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
  agentic/                             # optional
    asta/
      asta_manifest.json
      asta_outputs.jsonl
```

**Export semantics (required):**
- `runs/<run_id>/` is authoritative. `json_jsonl/` is an **export view** of the latest run.
- Export is **copy-only** (no schema/field changes during export).
- Export must be deterministic:
  - stable file naming
  - stable record ordering (if order is defined by the stage)
  - no symlinks (Windows-safe)
- Write `json_jsonl/LATEST_RUN_ID.txt` containing the exported run_id.

**Backward compatibility:** `json_jsonl/` becomes a compatibility export of the latest run:

- After each run, canonical artefacts are copied into `json_jsonl/` (no symlinks — Windows compatibility).
- `json_jsonl/LATEST_RUN_ID.txt` records which run was exported.
- Workflows may read from either `runs/<run_id>/…` or `json_jsonl/…` during v2.0.x.
- `json_jsonl/` as a write target is deprecated in v2.1.

A small `elis export-latest` command (or post-run hook) handles the copy.

### 2.3 Data contract rules

- `schemas/appendix_a.schema.json` remains the authoritative canonical contract for Appendix A.
- `schemas/appendix_a_harvester.schema.json` is the contract for per-source harvest outputs.
- All schema changes must be versioned (`schema_version` + changelog note) and gated in CI.
- The `_meta` header in canonical JSON is frozen. Run manifests are **sidecar files** alongside outputs — they extend provenance without modifying the frozen contract.

---

## 3. The central problem this release solves

The repo currently has **two independent codepaths** producing Appendix A data. They are not connected.

**Path A — 9 standalone harvesters** (`scripts/*_harvest.py`, ~4,400 lines total). Each self-contains config loading, HTTP calls, pagination, transform, per-source dedup, output writing, and summary. ~1,620 lines (~37%) are duplicated boilerplate across the nine scripts.

**Path B — 2 MVP pipeline scripts** (`scripts/elis/search_mvp.py` at 625 lines, `screen_mvp.py` at 426 lines). `search_mvp.py` queries only 3 of 9 sources with its own HTTP logic, field mapping, and dedup. It produces the canonical file that `screen_mvp.py` consumes. There is no step that merges Path A outputs into the format Path B expects.

v2.0 converges these into a single pipeline. Standalone harvesters become thin wrappers during migration, then are archived at cut-over (PE6).

---

## 4. Release strategy (branching, RCs, cut-over)

### 4.1 Branching model

- Create `release/2.0` from `main`.
- RC tags: `v2.0.0-rc.1`, `v2.0.0-rc.2`, …
- Final tag: `v2.0.0`
- Post-release hotfixes: `v2.0.1`, `v2.0.2` (back on `main`)

### 4.2 Migration philosophy: build → coexist → cut over

**Phase 1 — Build the new alongside the old (PE0–PE2).** The `elis/` package goes in. Both codepaths work. CI stays green. Thin wrappers bridge old scripts to new modules. No existing workflow changes.

**Phase 2 — New stages with no old equivalent (PE3–PE5).** Merge, dedup, and ASTA integration are net-new. They only exist inside the package. This naturally pulls usage toward the `elis` CLI.

**Phase 3 — Cut over and clean up (PE6).** All workflows migrate to `elis` CLI. Old scripts archived. Version bumped to 2.0.0. One codepath remains.

### 4.3 Rollout principle

The release is delivered as a sequence of **small, reviewable PRs**, each with deterministic behaviour, schema validation, a regression strategy, and workflow coverage.

---

## 5. Work breakdown: PR series (PE0–PE6)

### PE0a — Package skeleton + first subcommand

**Effort:** ~4h | **Risk:** Zero | **Branch:** `feature/elis-package`

**Goal:** Establish `elis/` as an installable Python package. Prove the pattern with one subcommand.

**Deliverables:**

```
elis/
├── __init__.py          # __version__ = "0.3.0"
├── __main__.py          # python -m elis
└── cli.py               # argparse dispatcher with subcommands
```

`pyproject.toml` additions (extend existing `[tool.*]` blocks):

```toml
[project]
name = "elis-slr-agent"
version = "0.3.0"
requires-python = ">=3.11"
dependencies = ["requests==2.31.0", "PyYAML==6.0.2", "jsonschema==4.23.0"]

[project.scripts]
elis = "elis.cli:main"
```

First subcommand: `elis validate` — wraps existing `scripts/validate_json.py`. No external API dependencies, already well-tested.

**Acceptance:**
- `pip install -e .` succeeds.
- `elis validate schemas/appendix_a.schema.json json_jsonl/ELIS_Appendix_A_Search_rows.json` produces the same output as `python scripts/validate_json.py`.
- `python -m elis validate …` works.
- CI (`ci.yml`) passes with no workflow changes.

---

### PE0b — Migrate MVP pipeline to package (including screening)

**Effort:** ~6h | **Risk:** Low | **Branch:** same or follow-up PR

**Goal:** Move `search_mvp.py`, `screen_mvp.py`, and `validate_json.py` logic into the package as importable modules. Screening migration happens here — not in a later PE.

**Deliverables:**

```
elis/
├── pipeline/
│   ├── __init__.py
│   ├── search.py        # extracted from search_mvp.py (625 lines)
│   ├── screen.py        # extracted from screen_mvp.py (426 lines)
│   └── validate.py      # extracted from validate_json.py
```

CLI additions: `elis search` and `elis screen` with identical flags to the current MVP scripts.

Existing scripts become thin wrappers:
```python
# scripts/elis/search_mvp.py (after PE0b)
"""Backward-compatible wrapper. Delegates to elis.pipeline.search."""
from elis.pipeline.search import main
if __name__ == "__main__":
    main()
```

**Acceptance:**
- `elis-agent-search.yml` workflow passes unchanged (still calls `python scripts/elis/search_mvp.py`).
- `elis search` produces byte-identical output to `python scripts/elis/search_mvp.py`.
- Same for `elis screen`.

---

### PE1a — Run manifest schema + writer utility (with PE0)

**Effort:** ~3h | **Risk:** Zero (additive) | **Branch:** `feature/run-manifest`

**Goal:** Define the manifest contract and provide a thin writer. No enforcement yet.

**Deliverables:**

```
elis/
├── manifest.py              # write_manifest() utility

schemas/
├── run_manifest.schema.json
└── validation_report.schema.json
```

Run manifest schema:
```json
{
  "schema_version": "1.0",
  "run_id": "20260212_143022_scopus",
  "stage": "harvest|merge|dedup|screen|validate",
  "source": "scopus",
  "commit_sha": "c81328e",
  "config_hash": "sha256:abc123…",
  "started_at": "2026-02-12T14:30:22Z",
  "finished_at": "2026-02-12T14:31:45Z",
  "record_count": 432,
  "input_paths": ["harvest/scopus.jsonl", "harvest/crossref.jsonl"],
  "output_path": "merge/appendix_a.jsonl",
  "tool_versions": { "python": "3.11.9", "requests": "2.31.0" }
}
```

Relationship to `_meta`: the `_meta` header stays frozen in canonical JSON. Manifests are **sidecar files** (`*.manifest.json`) alongside outputs.

**Acceptance:**
- `write_manifest()` callable from any stage.
- Manifests pass `run_manifest.schema.json` validation.
- No enforcement in CI (that comes in PE1b).

---

### PE2 — Source adapter layer + shared HTTP client (highest ROI)

**Effort:** ~16h (2–3 PRs) | **Risk:** Medium | **Branch:** `feature/source-adapters`

**Goal:** Collapse duplicated harvester logic into adapters with one resilient HTTP client.

**Deliverables:**

```
elis/
├── sources/
│   ├── __init__.py       # get_adapter(name) registry
│   ├── base.py           # SourceAdapter ABC
│   ├── http_client.py    # shared HTTP with retry/backoff/429/rate-limit
│   ├── config.py         # config resolution (absorbs tier_resolver logic)
│   ├── openalex.py       # first adapter
│   ├── crossref.py       # second adapter
│   └── scopus.py         # third adapter
```

SourceAdapter ABC:
```python
from abc import ABC, abstractmethod
from typing import Iterator

class SourceAdapter(ABC):
    @abstractmethod
    def preflight(self) -> tuple[bool, str]: ...

    @abstractmethod
    def harvest(self, queries: list[dict], max_results: int) -> Iterator[dict]: ...

    @property
    @abstractmethod
    def source_name(self) -> str: ...
```

Shared HTTP client:
```python
class ELISHttpClient:
    """Retry on 429/5xx only. Exponential backoff with jitter (base 1s, max 60s).
    Per-source rate limits from config/sources.yml. Never logs secrets."""
```

Config resolution (absorbs the tier logic duplicated across 9 harvesters):
```python
# elis/sources/config.py
def load_harvest_config(args) -> HarvestConfig:
    """Priority: --search-config + --tier > --search-config (default tier) >
    config/elis_search_queries.yml (legacy). --max-results always overrides."""
```

Porting order: OpenAlex (simplest) → CrossRef → Scopus. Remaining 6 in subsequent PRs. Google Scholar (Apify actor) needs an escape hatch in the ABC.

**Acceptance:**
- `elis harvest openalex` passes `appendix_a_harvester.schema.json` validation.
- `test_database_harvest.yml` passes for ported sources with no workflow changes.
- Thin wrapper scripts produce identical output to old monolithic versions.
- HTTP client logs retry/backoff events on 429.

---

### PE3 — Canonical merge stage (Appendix A)

**Effort:** ~8h | **Risk:** Low | **Branch:** `feature/merge-pipeline`

**Goal:** Produce one authoritative Appendix A dataset from all per-source outputs.

**Deliverables:**

```
elis/
├── pipeline/
│   └── merge.py
```

**CLI:** `elis merge --inputs scopus.jsonl crossref.jsonl openalex.jsonl [--output merge/appendix_a.jsonl]`

**Critical design decision:** Merge takes **explicit `--inputs`**, not directory scanning. This keeps the run reproducible even before manifest-driven discovery is enforced (PE1b). The operator (or workflow) specifies exactly which per-source files to merge. When PE1b lands, manifests can replace explicit inputs — but `--inputs` remains as an override.

Merge algorithm:
```
1. For each input file:
   a. Load records
   b. Add provenance: source_file, merge_position
   c. Normalise:
      - doi: lowercase, strip, remove "https://doi.org/" prefix
      - title: strip, collapse internal whitespace
      - authors: strip per name
      - year: ensure int or null
2. Stable sort: (source, query_topic, title, year)
3. Write canonical JSONL + JSON array with _meta header
4. Write merge_report.json
```

merge_report.json:
```json
{
  "total_records": 4532,
  "per_source_counts": { "scopus": 1200, "crossref": 980 },
  "doi_coverage_pct": 78.3,
  "null_field_ratios": { "title": 0.02, "abstract": 0.15, "language": 0.31 },
  "input_files": ["scopus.jsonl", "crossref.jsonl", "openalex.jsonl"]
}
```

**Acceptance:**
- Same inputs in same order → byte-identical output (deterministic).
- Output passes `appendix_a.schema.json` validation.
- `elis screen` accepts the merged output.

---

### PE1b — Wire manifests into all stages + CI enforcement

**Effort:** ~5h | **Risk:** Low | **Branch:** `feature/run-manifest` (continued)

**Goal:** Every pipeline stage emits a manifest sidecar. CI fails if a required manifest is missing.

**Deliverables:**
- `elis harvest`, `elis merge`, `elis dedup`, `elis screen`, `elis validate` all emit `*_manifest.json` alongside outputs.
- `elis merge` gains `--from-manifest <run_manifest.json>` as an alternative to `--inputs` — reads input paths from the manifest.
- CI validation step checks for manifest presence.

**Acceptance:**
- All stage outputs have a companion manifest that passes schema validation.
- `--inputs` still works as an override (no regression).

---

### PE4 — Deterministic dedup + clusters

**Effort:** ~8h | **Risk:** Low | **Branch:** `feature/dedup`

**Goal:** Deduplicate before screening with transparent, explainable clusters.

**Deliverables:**

```
elis/
├── pipeline/
│   └── dedup.py
```

**CLI:** `elis dedup [--input <merged A>] [--output <deduped A>] [--fuzzy] [--threshold 0.85]`

Dedup policy (exact-match default):
```
1. Compute dedup_key per record:
   a. DOI present → normalise_doi(doi)
   b. No DOI    → normalise(title) + "|" + str(year) + "|" + normalise(first_author)

2. Group by dedup_key → clusters

3. Per cluster:
   a. cluster_id = sha256(dedup_key)[:12]
   b. Keeper = record with most non-null fields
      Tie-break: source priority from config/sources.yml (keeper_priority list)
      Default if config absent: Scopus > WoS > S2 > CrossRef > OpenAlex > IEEE > CORE > SD > GS
   c. Others: duplicate_of = keeper.id

4. Output: keepers with cluster_id, cluster_size, cluster_sources
```

Normalisation:
```python
def normalise_doi(doi: str) -> str:
    doi = doi.lower().strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi

def normalise_text(text: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', text.lower())).strip()
```

Fuzzy matching: opt-in only (`--fuzzy --threshold 0.85`). Never default. Logs a warning when enabled.

dedup_report.json:
```json
{
  "input_records": 4532,
  "unique_clusters": 3187,
  "duplicates_removed": 1345,
  "doi_based_dedup": 892,
  "title_year_author_dedup": 453,
  "fuzzy_dedup": 0,
  "keeper_priority_source": "config/sources.yml",
  "top_10_collisions": [
    { "cluster_id": "a3f2c1d4e5f6", "size": 7, "sources": ["scopus","wos","crossref"] }
  ]
}
```

**Acceptance:**
- Same input → same cluster IDs (deterministic).
- No data loss (all records traceable via cluster_id).
- Fuzzy off by default.
- Keeper precedence read from config; code default used only if config absent.

---

### PE5 — ASTA pipeline integration

**Effort:** ~6h | **Risk:** Low | **Branch:** `feature/asta-integration`

**Goal:** Wire the existing ASTA adapter (`sources/asta_mcp/`, 394-line adapter, vocabulary, snippets, 3 phase scripts, 5 tests, 2 configs) into the `elis/` package with defined CLI subcommands and sidecar-only output.

This is not "defer." ASTA is already implemented and tested. Without a defined integration point, the code is orphaned.

**Pipeline position:**

```
elis harvest → merge → dedup → screen → validate    ← canonical (deterministic)
                                  ↓
elis agentic asta discover                           ← advisory (AI-augmented)
elis agentic asta enrich                             ← append-only sidecar
```

**Key rule:** ASTA outputs live in `runs/<run_id>/agentic/asta/`, never in `json_jsonl/` or the canonical merge/dedup/screen paths. Canonical pipeline works identically with or without ASTA.

**Deliverables:**

```
elis/
├── agentic/
│   ├── __init__.py
│   ├── asta.py           # wraps sources/asta_mcp/adapter.py
│   └── evidence.py       # evidence span validation
```

Evidence span validation — when ASTA proposes inclusion/exclusion, cited spans must be verified as actual substrings of the record text:

```python
def validate_evidence_spans(record: dict, spans: list[str]) -> list[dict]:
    text = (record.get("title") or "") + " " + (record.get("abstract") or "")
    return [{"span": s, "valid": s.lower() in text.lower()} for s in spans]
```

ASTA output schema (per suggestion):
```json
{
  "record_id": "…",
  "suggestion": "include|exclude|review",
  "confidence": 0.87,
  "evidence_spans": [{ "text": "…", "valid": true }],
  "model_id": "asta-mcp-v1",
  "prompt_hash": "sha256:…",
  "run_id": "20260212_143022",
  "timestamp": "2026-02-12T14:30:22Z"
}
```

**Acceptance:**
- ASTA outputs go to `runs/<run_id>/agentic/asta/`, not canonical paths.
- Evidence spans validated; invalid flagged, not suppressed.
- Canonical pipeline produces identical output with or without ASTA.
- Existing ASTA tests keep passing.

---

### PE6 — Cut-over + equivalence checks + legacy removal (RC → final)

**Effort:** ~4h | **Risk:** Low (package battle-tested by this point) | **Branch:** `release/2.0`

**Goal:** Ship one codepath. Remove legacy modes. Archive old scripts. Tag v2.0.0.

**This is a required v2.0 deliverable.** Without it, thin wrappers become permanent and the codebase retains two ways to do everything.

**Prerequisite:** PE0–PE5 all merged. Full pipeline working in CI for at least one full cycle.

**Deadline rule:** PE6 ships within 1 week of PE5 merge, no exceptions.

#### PE6.1 Equivalence checks (RC period)

During RCs, for each source migrated:

- Run **legacy harvester** and **new adapter** on a small controlled run.
- Compare: record counts (per query and total), schema validity, key field hashes (title/year/doi/ids), merge + dedup statistics.
- Record results as CI artefacts under `runs/rc_equivalence/`.

**Comparison method (required):**
- Compute a stable hash over the **normalised tuple set** per run.
- **Identifier rule:** prefer `stable_id` if present; otherwise use `source_record_id`. Do not mix both within a single run.
- Default tuple fields (in order) = `{id, doi_norm, title_norm, year, first_author_norm}`
- Canonical serialisation for hashing:
  - normalise each field: UTF-8, trim, collapse internal whitespace, lowercase
  - build one tuple string per record: fields joined by a single TAB (`\t`)
  - sort tuple strings lexicographically
  - hash payload = tuple strings joined by `\n`
  - hash algorithm = `SHA-256`
- Compare:
  - **count parity** (exact) per source and per `query_id`
  - **tuple-hash parity** (exact) for deterministic sources
- If a provider is known to be non-deterministic (e.g., ranked endpoints), allow an explicit tolerance:
  - tolerance must be declared in the run manifest (e.g., `equivalence_tolerance_pct`)
  - default tolerance = `0%` (no drift allowed)

#### PE6.2 Workflow migration

All 19 workflows that call harvest/search/screen/validate must switch to the canonical CLI.

Before:
```yaml
# elis-agent-search.yml
- run: python scripts/elis/search_mvp.py --year-from 1990 …
```

After:
```yaml
# elis-agent-search.yml
- run: pip install -e .
- run: elis search --year-from 1990 …
```

Before:
```yaml
# test_database_harvest.yml
- run: python scripts/scopus_harvest.py --search-config config/searches/…
```

After:
```yaml
# test_database_harvest.yml
- run: pip install -e .
- run: elis harvest scopus --search-config config/searches/…
```

#### PE6.3 Legacy removal + archive

```
scripts/
├── _archive/                         # superseded by elis/ package
│   ├── README.md                     # "Wrappers preserved for transition.
│   │                                 #  Not used by CI. May be removed in v2.1."
│   ├── scopus_harvest.py             # 9 standalone harvesters
│   ├── crossref_harvest.py
│   ├── semanticscholar_harvest.py
│   ├── openalex_harvest.py
│   ├── core_harvest.py
│   ├── ieee_harvest.py
│   ├── wos_harvest.py
│   ├── google_scholar_harvest.py
│   ├── sciencedirect_harvest.py
│   ├── search_mvp.py                 # MVP pipeline scripts
│   ├── screen_mvp.py
│   └── validate_json.py
│
├── __init__.py                      # KEEP: allow `import scripts.*` in tests
├── core_preflight.py                # KEEP: CI/dev utility
├── crossref_preflight.py            # KEEP: CI/dev utility
├── ieee_preflight.py                # KEEP: CI/dev utility
├── openalex_preflight.py            # KEEP: CI/dev utility
├── scopus_preflight.py              # KEEP: CI/dev utility
├── semanticscholar_preflight.py     # KEEP: CI/dev utility
├── wos_preflight.py                 # KEEP: CI/dev utility
│
├── phase0_asta_scoping.py            # KEEP: ASTA phase scripts
├── phase2_asta_screening.py
├── phase3_asta_extraction.py
├── imports_to_appendix_a.py          # KEEP: standalone utility
├── convert_scopus_csv_to_json.py     # KEEP: one-off utility
├── archive_old_reports.py            # KEEP: housekeeping utility
└── test_all_harvests.py              # UPDATE: call elis harvest
```

Rules:
- Archived scripts must not be called by any workflow.
- Legacy mode flags and branches are deleted from all active code (not hidden).
- `_archive/README.md` explains the migration.

#### PE6.4 Release artefacts

- `pyproject.toml` version → `2.0.0`
- Updated `README.md` with `elis` CLI usage (replaces `python scripts/*.py` examples)
- Updated `CHANGELOG.md` with breaking changes, additions, removals
- `docs/MIGRATION_GUIDE_v2.0.md` — old scripts → new CLI mapping
- Operational runbook: where keys are stored, how to run preflight, how to interpret manifests
- Backward-compatibility export: `elis export-latest` copies canonical artefacts to `json_jsonl/`
- Git tag: `v2.0.0`

**Acceptance:**
- All 19 workflows pass using `elis` CLI commands (no `python scripts/*.py` calls remain outside `_archive/`).
- `pip install -e . && elis harvest scopus --search-config config/searches/electoral_integrity_search.yml --tier testing` works from a clean clone.
- CHANGELOG documents all breaking changes.
- Equivalence check results recorded.
- Git tag `v2.0.0` exists.

---

## 6. Effort summary and timeline

| PE | Description | Effort | Dependencies | Risk |
|----|------------|--------|-------------|------|
| **PE0a** | Package skeleton + `elis validate` | 4h | None | Zero |
| **PE0b** | Migrate search/screen/validate to package | 6h | PE0a | Low |
| **PE1a** | Manifest schema + writer utility | 3h | PE0a | Zero |
| **PE2** | Adapter layer + HTTP client + 3 sources | 16h | PE0a | Medium |
| **PE3** | Canonical merge (explicit `--inputs`) | 8h | PE2 (≥1 adapter) | Low |
| **PE1b** | Wire manifests into all stages + CI enforcement | 5h | PE3 | Low |
| **PE4** | Deterministic dedup + clusters | 8h | PE3 | Low |
| **PE5** | ASTA pipeline integration | 6h | PE0a + existing ASTA | Low |
| **PE6** | Cut-over + equivalence + archive → **v2.0.0** | 4h | PE0–PE5 all merged | Low |

**Total:** ~60 hours (~8 working days)

**Critical path:** PE0a → PE2 → PE3 → PE4 → PE6

**Parallel tracks:** PE1a, PE0b, and PE5 can all start after PE0a, in parallel with PE2.

```
Phase 1 (build):
  Week 1:  PE0a ──► PE0b ──► PE2 (OpenAlex, CrossRef, Scopus)
                      ├──► PE1a (parallel)
                      └──► PE5 (parallel)

Phase 2 (new stages):
  Week 2:  PE2 (remaining adapters) ──► PE3 (merge) ──► PE1b ──► PE4 (dedup)

Phase 3 (cut over):
  Week 3:  PE6 (RC → equivalence checks → workflow migration → archive → v2.0.0 tag)
```

---

## 7. Config strategy

| File | Purpose | Used by | v2.0 status |
|------|---------|---------|-------------|
| `config/elis_search_queries.yml` | Legacy global config | Harvesters (fallback) | Keep through v2.0; deprecate in v2.1 |
| `config/searches/*.yml` | Per-project search configs with tiers | Harvesters (preferred) | Keep |
| `config/asta_config.yml` | ASTA-specific | ASTA adapter | Keep |
| `config/asta_extracted_vocabulary.yml` | ASTA vocabulary | ASTA adapter | Keep |
| **`config/sources.yml`** (NEW) | Per-source rate limits, endpoints, auth env vars, keeper priority | Adapter layer + dedup | Create in PE2 |

`config/sources.yml` example:
```yaml
sources:
  openalex:
    base_url: "https://api.openalex.org"
    rate_limit_rps: 10
    auth_env_var: null
    pagination: cursor

  scopus:
    base_url: "https://api.elsevier.com/content/search/scopus"
    rate_limit_rps: 3
    auth_env_var: "SCOPUS_API_KEY"
    auth_token_env_var: "SCOPUS_INST_TOKEN"
    pagination: cursor

# Dedup keeper precedence (first = highest priority)
keeper_priority:
  - scopus
  - wos
  - semanticscholar
  - crossref
  - openalex
  - ieee
  - core
  - sciencedirect
  - google_scholar
```

---

## 8. Workflow mapping (what must remain green)

These workflows exist today under `.github/workflows/`:

| Workflow | Name | v2.0 action |
|----------|------|-------------|
| `ci.yml` | ELIS - CI | **Must be green** for every PR and release |
| `elis-validate.yml` | ELIS - Validate | **Must be green** |
| `elis-search-preflight.yml` | ELIS - Search Preflight / Self-Test | **Must be green** |
| `test_database_harvest.yml` | Test Database Harvest Script | **Must be green** |
| `elis-agent-search.yml` | ELIS - Agent Search (Appendix A) | **Must be green** |
| `elis-agent-screen.yml` | ELIS - Agent Screen (Appendix B) | **Must be green** |
| `elis-agent-nightly.yml` | ELIS - Agent Nightly | **Must be green** |
| `agent-automerge.yml` | ELIS - Agent AutoMerge | Verify not broken |
| `agent-run.yml` | ELIS - Agent Run | Verify not broken |
| `autoformat.yml` | ELIS - Autoformat | Unchanged |
| `benchmark_2_phase1.yml` | Benchmark 2 - Phase 1 Execution | Verify not broken |
| `benchmark_validation.yml` | Benchmark Validation - Darmawan 2021 | Verify not broken |
| `bot-commit.yml` | ELIS - Bot Commit | Unchanged |
| `deep-review.yml` | ELIS - Deep Review | Unchanged |
| `elis-housekeeping.yml` | ELIS - Housekeeping | Verify not broken |
| `elis-imports-convert.yml` | ELIS - Imports Convert | Verify not broken |
| `export-docx.yml` | ELIS - Export Docx | Unchanged |
| `projects-autoadd.yml` | ELIS - Projects Auto-Add | Unchanged |
| `projects-runid.yml` | ELIS - Projects Run ID | Unchanged |

**v2.0 requirement:** All "must be green" workflows must call the canonical `elis` CLI (not legacy scripts) before tagging `v2.0.0`.
**Preflight scripts (must remain in v2.0):**

- Keep database preflight utilities under `scripts/*_preflight.py` (importable by tests and callable by CI/self-test workflows).
- These are **not** “legacy harvesters”. They are **CI/dev utilities** and are exempt from PE6 wrapper-archiving.
- If/when a canonical `elis preflight <source>` subcommand is added, workflows may switch to it, but the scripts remain until explicitly retired in a later release.


---

## 9. Contracts to freeze

### 9.1 Freeze now (breaking change = schema version bump)

- `schemas/appendix_a.schema.json` — field names, types, `_meta` structure
- `schemas/appendix_a_harvester.schema.json` — field names, types
- `schemas/appendix_b.schema.json`
- `schemas/appendix_c.schema.json`
- CLI flags: `--search-config`, `--tier`, `--max-results`, `--output`

### 9.2 Freeze at v2.0.0 tag

- CLI subcommand names: `elis harvest`, `elis merge`, `elis dedup`, `elis screen`, `elis validate`, `elis agentic asta`
- Output paths within `runs/<run_id>/` (artefact layout in §2.2)
- Workflow names and dispatch inputs (updated once in PE6, then frozen)

### 9.3 Keep flexible (internal, may change between PEs)

- Internal module layout within `elis/`
- Adapter implementation details per source
- Retry/backoff parameters
- Validation report Markdown format
- Run manifest schema (until PE1b enforces it)
- Benchmark harness internals
- `json_jsonl/` compatibility export mechanism

---

## 10. Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PE2 adapter changes harvest output | Medium | High | Golden snapshots: diff before/after |
| PE0 pyproject.toml changes break CI | Low | High | Test `pip install -e .` in CI first |
| Schema migration breaks downstream | Low | High | Additive only; `additionalProperties: true` |
| Merge ordering drift | Low | Medium | Deterministic sort key; golden snapshot |
| Solo researcher bandwidth | High | Medium | PE0a + PE2 first — max ROI, min effort |
| Google Scholar too different for ABC | Medium | Low | Apify escape hatch; defer GS adapter |
| PE6 workflow migration breaks CI | Low | High | Migrate one workflow at a time; rollback = revert PR |
| PE6 delayed indefinitely | Medium | Medium | Hard deadline: ships within 1 week of PE5 merge |
| `runs/` vs `json_jsonl/` confusion | Medium | Low | `LATEST_RUN_ID.txt` + `elis export-latest` |

---

## 11. PR checklist (repo-tailored)

Use this checklist in **every** PR going into `release/2.0`.

### 11.1 General

- [ ] PR title is scoped (one PE step or one adapter/source at a time).
- [ ] No secrets added to logs, outputs, or reports.
- [ ] Deterministic behaviour: no random ordering; stable IDs where required.
- [ ] Updated documentation if behaviour, outputs, or flags changed.

### 11.2 Data contracts and artefacts

- [ ] Output validates against relevant schema:
  - Harvester outputs → `schemas/appendix_a_harvester.schema.json`
  - Canonical Appendix A → `schemas/appendix_a.schema.json`
  - Appendix B → `schemas/appendix_b.schema.json`
  - Appendix C → `schemas/appendix_c.schema.json`
- [ ] Run manifest/stage reports produced (or explicitly not yet part of the PE, with a tracking issue).
- [ ] If schemas changed: update schema versioning note in changelog; update validation tests.

### 11.3 Code health (repo conventions)

- [ ] Formatting/linting: `autoformat.yml` and `ci.yml` remain green.
- [ ] Unit tests updated/added as needed.
- [ ] If you changed any harvesters: no new bespoke retry/backoff logic; wrapper-only direction preserved.

### 11.4 Workflows (must remain green)

- [ ] `ci.yml` passes.
- [ ] `elis-validate.yml` passes and produces a validation report.
- [ ] `elis-search-preflight.yml` passes on smallest safe self-test run.
- [ ] `test_database_harvest.yml` passes (harvest smoke).
- [ ] If screening affected: `elis-agent-screen.yml` passes.
- [ ] If search affected: `elis-agent-search.yml` passes.
- [ ] If nightly logic changed: `elis-agent-nightly.yml` verified via workflow_dispatch.

### 11.5 PE6-specific (RC → final only)

- [ ] Equivalence check completed for each migrated source (legacy vs canonical): counts match, schema validity identical, key field hashes comparable.
- [ ] Legacy modes/options removed from all active code.
- [ ] No workflow calls legacy codepaths.
- [ ] Wrapper harvest scripts moved to `scripts/_archive/` (preflight utilities remain in `scripts/`).
- [ ] README and migration guide updated.
- [ ] `elis export-latest` produces correct `json_jsonl/` output.

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
### Preflight scripts (CI/dev utilities)

- `scripts/__init__.py`
- `scripts/core_preflight.py`
- `scripts/scopus_preflight.py`
- `scripts/wos_preflight.py`
- `scripts/openalex_preflight.py`
- `scripts/crossref_preflight.py`
- `scripts/semanticscholar_preflight.py`
- `scripts/ieee_preflight.py`


### Harvester scripts (all 9, to be archived at PE6)

- `scripts/core_harvest.py` (545 lines)
- `scripts/crossref_harvest.py` (484 lines)
- `scripts/google_scholar_harvest.py` (638 lines)
- `scripts/ieee_harvest.py` (477 lines)
- `scripts/openalex_harvest.py` (493 lines)
- `scripts/sciencedirect_harvest.py` (336 lines)
- `scripts/scopus_harvest.py` (432 lines)
- `scripts/semanticscholar_harvest.py` (541 lines)
- `scripts/wos_harvest.py` (450 lines)

### MVP pipeline scripts (to be archived at PE6)

- `scripts/elis/search_mvp.py` (625 lines)
- `scripts/elis/screen_mvp.py` (426 lines)
- `scripts/elis/imports_to_appendix_a.py`

---

## Appendix B — Agreed adjustments (Claude–ChatGPT cross-review)

This plan incorporates five adjustments identified by Claude and ratified by ChatGPT, plus two clarifications:

1. **PE1 split into PE1a/PE1b.** Manifest schema defined early (PE1a with PE0), enforcement wired after PE3 (PE1b). Avoids designing the manifest in a vacuum.

2. **PE5 redefined as ASTA integration.** Screening migration moved to PE0b (where it belongs — it already exists). Extraction (Appendix C) deferred to post-v2.0. ASTA gets a defined PE so `sources/asta_mcp/` is not orphaned.

3. **Wrapper scripts archived at PE6, not kept permanently.** Wrappers exist during migration (Phase 1–2) but are moved to `scripts/_archive/` at cut-over. No workflow calls them after v2.0.0.

4. **`runs/<run_id>/` is canonical; `json_jsonl/` is compatibility export.** Resolved the contradiction between the new artefact layout and the frozen output path. `elis export-latest` copies to `json_jsonl/` with `LATEST_RUN_ID.txt`. No symlinks (Windows).

5. **Dedup keeper precedence configurable.** Moved from hard-coded to `config/sources.yml` (`keeper_priority` list). Code default used only if config absent.

**Clarification 1 (ChatGPT):** PE3 merge uses explicit `--inputs`, not directory scanning. Reproducible by construction even before manifests are enforced.

**Clarification 2 (ChatGPT):** Wrapper scripts can exist during transition but must not be used by workflows and must move out of the main scripts surface at PE6.

---

*Final release — 12 February 2026*
*Claude Opus 4.6 + ChatGPT (cross-reviewed) — ratified by Carlos Rocha*
