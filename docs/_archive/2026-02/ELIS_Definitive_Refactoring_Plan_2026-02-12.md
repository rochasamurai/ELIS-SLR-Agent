# ELIS SLR Agent — Definitive Refactoring Plan

**Date:** 12 February 2026
**Author:** Claude Opus 4.6 (Senior Architect role)
**Commit reviewed:** `c81328e` on `main` (live access via `curl` to `github.com`)
**Repository:** `github.com/rochasamurai/ELIS-SLR-Agent` (public)

**Inputs synthesised:**

1. Live repo access — file tree, line counts, full source code for key files
2. ChatGPT Updated End-to-End Architecture & Code Review (12 Feb 2026, from ZIP snapshot)
3. Claude Senior Architect Review of original ChatGPT Refactoring Plan (5 PEs)
4. Full project conversation history (Oct 2025 – Feb 2026)
5. ELIS Protocol v2.0 Draft 08.1

---

## 0. Where Both Reviews Converge — and Where This Plan Differs

ChatGPT and I independently arrived at the same diagnosis: the codebase is **functionally complete for harvest + validate** but **structurally fragmented** with duplicated logic and no merge/dedup stage. We agree on the same PE sequence. This plan goes further by:

1. Identifying the **two-codepath problem** as the central architectural issue (§1)
2. Providing **code-level evidence** for every claim (line counts, function signatures, schema fields)
3. Specifying **exact file-by-file deliverables** with acceptance criteria for each PE
4. Defining **ASTA's integration point** concretely rather than deferring it
5. Resolving the **config duality** (legacy vs new-style search configs)
6. Including **PE6: a defined v2.0 cut-over** that archives old scripts and migrates all workflows — ensuring the thin wrappers are temporary scaffolding, not permanent architecture

### What ChatGPT gets right (confirmed, adopted)

- PE0 (package + CLI) is a necessary addition — my original review underestimated this
- `tier_resolver.py` is absent from `main` — I incorrectly stated it existed
- PE sequence PE0 → PE2 → PE3 → PE1 → PE4 → PE5 is correct
- Harvester duplication is the highest-cost maintenance problem
- Fuzzy dedup must be opt-in, never default
- ASTA / agentic screening must be opt-in, deterministic default

### What ChatGPT misses or underspecifies

- The **two parallel codepaths** (standalone harvesters vs MVP pipeline scripts) are not just "duplication" — they produce **incompatible outputs** and must be converged
- The `appendix_a.schema.json` is already **sophisticated** (prefixItems meta header, run_inputs provenance, summary rollups) — PE1 scope must extend, not replace
- The `config/searches/` system (786-line electoral_integrity_search.yml with tiers, topics, per-source overrides) is a mature config framework that the adapter layer must respect
- PE0 deliverables are too ambitious for one PR — split into PE0a and PE0b
- PE5 must define ASTA's pipeline role, not just say "defer"

---

## 1. The Central Problem: Two Divergent Codepaths

This is the single most important finding from reading the actual code. The repo has two independent ways to produce Appendix A data, and **they are not connected**.

### Path A — Standalone Harvesters (9 scripts, ~4,400 lines total)

| Script | Lines | Auth | Pagination | Config |
|--------|-------|------|-----------|--------|
| `scopus_harvest.py` | 432 | API key + inst token | cursor-based | `--search-config` / legacy |
| `crossref_harvest.py` | 484 | mailto (polite pool) | cursor-based | `--search-config` / legacy |
| `semanticscholar_harvest.py` | 541 | optional API key | offset-based | `--search-config` / legacy |
| `openalex_harvest.py` | 493 | mailto | cursor-based | `--search-config` / legacy |
| `core_harvest.py` | 545 | API key | offset-based | `--search-config` / legacy |
| `ieee_harvest.py` | 477 | API key (pycurl) | offset-based | `--search-config` / legacy |
| `wos_harvest.py` | 450 | API key | offset-based | `--search-config` / legacy |
| `google_scholar_harvest.py` | 638 | Apify actor | title-based | `--search-config` / legacy |
| `sciencedirect_harvest.py` | 336 | API key + inst token | offset-based | `--search-config` / legacy |

Each script self-contains: config loading → query building → HTTP calls → pagination → transform → per-source dedup → output writing → summary. All nine follow the same dual-config pattern (new `--search-config` or legacy `elis_search_queries.yml`), the same `argparse` CLI (`--search-config`, `--tier`, `--max-results`, `--output`), and the same output format (JSON array into `json_jsonl/`).

**Duplicated logic per harvester:**
- Config loading + tier resolution: ~60 lines × 9 = ~540 lines
- HTTP request + retry: ~40 lines × 9 = ~360 lines
- Response transform: ~50 lines × 9 = ~450 lines (source-specific, but pattern identical)
- Output writing + summary: ~30 lines × 9 = ~270 lines
- **Total duplication: ~1,620 lines** (~37% of harvester code)

### Path B — MVP Pipeline Scripts (2 scripts, 1,051 lines)

| Script | Lines | Purpose |
|--------|-------|---------|
| `search_mvp.py` | 625 | Queries CrossRef, Semantic Scholar, arXiv directly; writes canonical Appendix A with `_meta` header |
| `screen_mvp.py` | 426 | Reads Appendix A, applies year/language/preprint filters, writes Appendix B |

`search_mvp.py` is a **full alternative pipeline**: it has its own HTTP logic, its own field mapping, its own dedup, its own metadata header, and its own output format. It queries only 3 of 9 sources. It produces the canonical file that `screen_mvp.py` consumes.

### Why this matters

- The standalone harvesters are called by `test_database_harvest.yml` — the CI source-of-truth for individual source connectivity
- The MVP scripts are called by `elis-agent-search.yml` and `elis-agent-screen.yml` — the CI source-of-truth for the pipeline
- **There is no step that merges Path A outputs into the format Path B expects**, or vice versa
- A researcher running all 9 harvesters and then `screen_mvp.py` gets incorrect results because `screen_mvp.py` expects its own output format

### The plan must converge these paths

Target state after refactoring:

```
elis harvest <source>     →  per-source output (adapter layer, PE2)
elis merge                →  canonical Appendix A (from all per-source outputs, PE3)
elis dedup                →  deduped Appendix A (PE4)
elis screen               →  Appendix B (from canonical A, evolved from screen_mvp.py)
elis validate <path>      →  validation report
```

During the migration (PE0–PE5), standalone harvesters become thin wrappers calling the adapter layer, and the MVP scripts become thin wrappers calling the package modules. **These wrappers are temporary scaffolding** — they keep CI green while the new package is built. Once the full pipeline works end-to-end, PE6 removes the old scripts, migrates all workflows to the `elis` CLI, and tags v2.0. The final product has one codepath, not two.

---

## 2. Verified Repository State (12 Feb 2026)

### 2.1 File inventory (confirmed via live access)

```
ELIS-SLR-Agent/
├── .github/workflows/            # 19 workflows (CI, validate, search, screen,
│   │                             #   benchmarks, nightly, housekeeping, etc.)
│   ├── ci.yml                    # quality → tests → validate pipeline
│   ├── elis-agent-search.yml     # Calls search_mvp.py
│   ├── elis-agent-screen.yml     # Calls screen_mvp.py
│   ├── test_database_harvest.yml # Calls standalone harvesters
│   └── ... (15 more)
│
├── config/
│   ├── searches/
│   │   ├── electoral_integrity_search.yml  # 786 lines, tiers + topics
│   │   └── tai_awasthi_2025_search.yml     # External project config
│   ├── asta_config.yml
│   ├── asta_extracted_vocabulary.yml
│   └── elis_search_queries.yml             # Legacy global config
│
├── schemas/
│   ├── _legacy/
│   ├── appendix_a.schema.json              # Canonical, with _meta prefixItems
│   ├── appendix_a_harvester.schema.json    # Subset for standalone harvesters
│   ├── appendix_b.schema.json
│   └── appendix_c.schema.json
│
├── scripts/
│   ├── elis/                               # MVP pipeline
│   │   ├── search_mvp.py (625 lines)
│   │   ├── screen_mvp.py (426 lines)
│   │   └── imports_to_appendix_a.py
│   ├── scopus_harvest.py (432 lines)       # 9 standalone harvesters
│   ├── crossref_harvest.py (484 lines)
│   ├── ... (7 more harvesters)
│   ├── phase0_asta_scoping.py              # 3 ASTA phase scripts
│   ├── phase2_asta_screening.py
│   ├── phase3_asta_extraction.py
│   ├── agent.py                            # Toy demo
│   ├── validate_json.py
│   └── test_all_harvests.py
│
├── sources/
│   ├── asta_mcp/                           # ASTA adapter (implemented)
│   │   ├── adapter.py (394 lines)
│   │   ├── vocabulary.py
│   │   └── snippets.py
│   └── __init__.py
│
├── tests/                                  # 9 test files
├── validation_reports/                     # Timestamped MD reports + archive
├── benchmarks/                             # config, queries, scripts
├── json_jsonl/                             # Output artefacts
│
├── pyproject.toml                          # Tooling only (black, ruff, pytest)
├── requirements.txt                        # 6 pinned deps (requests, pyyaml, etc.)
└── README.md
```

### 2.2 Schema maturity (higher than either review acknowledged)

The `appendix_a.schema.json` is already well-designed:

- Uses `prefixItems` to enforce a `_meta` header as the first array element
- The `_meta` header requires: `protocol_version`, `config_path`, `retrieved_at`, `global`, `record_count`, `summary`
- Includes `run_inputs` for provenance (year range, result caps, topic selection, preprint policies)
- Includes `summary` with `total`, `per_source`, `per_topic` rollups
- Record items require: `id`, `source`, `retrieved_at`, `query_topic`, `query_string`
- Records support: `title`, `authors`, `year`, `doi`, `venue`, `publisher`, `abstract`, `language`, `url`, `doc_type`, `source_id`, `_stable_id`
- `additionalProperties: true` throughout for forward compatibility

The `appendix_a_harvester.schema.json` is a **simpler subset** (no meta header, no orchestrator fields) for validating standalone harvester outputs.

**Implication for PE1:** The data contract is already 70% done. PE1 extends it with `run_manifest.schema.json` and `validation_report.schema.json` — it does not need to redesign the record model.

### 2.3 Config maturity

`config/searches/electoral_integrity_search.yml` (786 lines) includes:

- Search metadata (project name, research team, status, version)
- Multi-component Boolean query with protocol alignment
- Per-source configuration overrides
- Tier system (testing/pilot/benchmark/production/exhaustive) with per-tier result caps
- Topic definitions with per-topic preprint policies
- Year ranges, language filters, inclusion/exclusion criteria

Every harvester supports `--search-config <path> --tier <tier>` for this system, plus `--max-results` override and legacy fallback.

**Implication for PE2:** The adapter layer must not reinvent config loading. It must consume the same `--search-config` / `--tier` pattern.

### 2.4 ASTA integration maturity

`sources/asta_mcp/adapter.py` (394 lines) implements:

- MCP protocol client (JSON-RPC 2.0, Streamable HTTP)
- Retry-once on 429 with backoff
- Per-call audit logging to `runs/<run_id>/asta/`
- Stats tracking (requests, errors, rate_limit_hits)
- Evidence window enforcement

Three phase scripts exist, five tests cover the adapter and vocabulary.

**Implication for PE5:** ASTA is not speculative — it is implemented and tested. PE5 must define its pipeline integration point, not defer it.

---

## 3. Definitive PE Plan

### PE0a — Package Skeleton + First Subcommand

**Effort:** ~4 hours | **Risk:** Zero (additive only) | **Branch:** `feature/elis-package`

**Goal:** Establish `elis/` as an installable Python package. Prove the pattern with one subcommand.

**Deliverables:**

```
elis/
├── __init__.py          # __version__ = "0.3.0"
├── __main__.py          # python -m elis
└── cli.py               # argparse dispatcher with subcommands
```

**pyproject.toml additions** (extend existing `[tool.*]` blocks):

```toml
[project]
name = "elis-slr-agent"
version = "0.3.0"
requires-python = ">=3.11"
dependencies = ["requests==2.31.0", "PyYAML==6.0.2", "jsonschema==4.23.0"]

[project.scripts]
elis = "elis.cli:main"
```

**First subcommand:** `elis validate` — wraps existing `scripts/validate_json.py`. Lowest risk because it has no external API dependencies and is already well-tested.

```python
# elis/cli.py
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(prog="elis", description="ELIS SLR Agent CLI")
    sub = parser.add_subparsers(dest="command")

    # validate
    val = sub.add_parser("validate", help="Validate JSON against ELIS schemas")
    val.add_argument("schema", help="Path to JSON Schema file")
    val.add_argument("data", help="Path to JSON data file")
    val.add_argument("--report-dir", default="validation_reports")

    args = parser.parse_args()
    if args.command == "validate":
        from elis.pipeline.validate import run_validation
        run_validation(args.schema, args.data, args.report_dir)
    else:
        parser.print_help()
        sys.exit(1)
```

**What does NOT change:** Every existing script, workflow, and CI job keeps working. `scripts/validate_json.py` stays. Workflows keep calling `python scripts/validate_json.py`.

**Acceptance criteria:**
- `pip install -e .` succeeds
- `elis validate schemas/appendix_a.schema.json json_jsonl/ELIS_Appendix_A_Search_rows.json` produces the same output as `python scripts/validate_json.py`
- `python -m elis validate ...` works
- CI (`ci.yml`) passes with no workflow changes

---

### PE0b — Migrate MVP Pipeline to Package

**Effort:** ~6 hours | **Risk:** Low (thin wrappers preserve backward compat) | **Branch:** same or follow-up PR

**Goal:** Move `search_mvp.py` and `screen_mvp.py` logic into the package as importable modules.

**Deliverables:**

```
elis/
├── pipeline/
│   ├── __init__.py
│   ├── search.py        # Core logic extracted from search_mvp.py (625 lines)
│   ├── screen.py        # Core logic extracted from screen_mvp.py (426 lines)
│   └── validate.py      # Core logic extracted from validate_json.py
```

**CLI additions:** `elis search` and `elis screen` with identical flags to the current MVP scripts.

**Thin wrapper transformation:**
```python
# scripts/elis/search_mvp.py (after PE0b)
"""Backward-compatible wrapper. Delegates to elis.pipeline.search."""
from elis.pipeline.search import main

if __name__ == "__main__":
    main()
```

**Acceptance criteria:**
- `elis-agent-search.yml` workflow passes unchanged (still calls `python scripts/elis/search_mvp.py`)
- `elis search --help` shows the same flags as `search_mvp.py --help`
- `elis search` produces byte-identical output to `python scripts/elis/search_mvp.py`
- Same for `elis screen`

---

### PE2 — Source Adapter Layer + Shared HTTP Client

**Effort:** ~16 hours (2–3 PRs) | **Risk:** Medium (touches core harvest logic) | **Branch:** `feature/source-adapters`

**Goal:** Collapse duplicated harvester logic into adapters with one resilient HTTP client. This is the highest-ROI PE.

**Deliverables:**

```
elis/
├── sources/
│   ├── __init__.py       # get_adapter(name) registry
│   ├── base.py           # SourceAdapter ABC
│   ├── http_client.py    # Shared HTTP with retry/backoff/429/rate-limit
│   ├── config.py         # Config resolution (absorbs tier_resolver logic)
│   ├── openalex.py       # First adapter (simplest: no auth, cursor pagination)
│   ├── crossref.py       # Second adapter (mailto polite pool)
│   └── scopus.py         # Third adapter (inst auth, highest volume)
```

**SourceAdapter ABC:**

```python
from abc import ABC, abstractmethod
from typing import Iterator

class SourceAdapter(ABC):
    """Base class for all ELIS source adapters."""

    @abstractmethod
    def preflight(self) -> tuple[bool, str]:
        """Check API connectivity. Returns (ok, message)."""
        ...

    @abstractmethod
    def harvest(self, queries: list[dict], max_results: int) -> Iterator[dict]:
        """Yield normalised record dicts from the source API."""
        ...

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Canonical source name (e.g. 'openalex', 'scopus')."""
        ...
```

**Shared HTTP client:**

```python
class ELISHttpClient:
    """Resilient HTTP client for academic API access.

    - Retry on 429 and 5xx only (never other 4xx)
    - Exponential backoff with jitter (base 1s, max 60s, factor 2)
    - Per-source rate limits from config/sources.yml
    - Structured logging (url, status, attempt, elapsed)
    - Never logs secrets (api_key, token, inst_token)
    - Timeouts: connect 10s, read 30s (configurable)
    """

    def __init__(self, source_name: str, rate_limit_rps: float = 5.0, ...):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = f"ELIS-SLR-Agent/0.3 ({contact})"
        ...

    def get(self, url: str, params: dict = None, **kwargs) -> requests.Response:
        ...
```

**Config resolution** (absorbs the tier logic every harvester duplicates):

```python
# elis/sources/config.py
def load_harvest_config(args: argparse.Namespace) -> HarvestConfig:
    """Resolve config from --search-config/--tier or legacy fallback.

    Priority:
    1. --search-config <path> --tier <tier> (new-style)
    2. --search-config <path> (uses default tier)
    3. config/elis_search_queries.yml (legacy fallback)
    --max-results always overrides.
    """
    ...
```

**Porting order:**

1. **OpenAlex** — No auth, simple cursor pagination, well-documented API. ~60% of the 493-line script is boilerplate.
2. **CrossRef** — mailto polite pool, cursor pagination. Similar structure.
3. **Scopus** — Institutional auth, cursor pagination, complex response. Highest volume.

Remaining 6 harvesters ported in subsequent PRs. Google Scholar (Apify actor) needs an escape hatch.

**What happens to standalone scripts (after PE2):**

```python
# scripts/openalex_harvest.py (~20 lines)
"""Backward-compatible wrapper. Delegates to elis.sources.openalex."""
import sys
from elis.sources.config import load_harvest_config, build_arg_parser
from elis.sources.openalex import OpenAlexAdapter

if __name__ == "__main__":
    config = load_harvest_config(build_arg_parser("openalex").parse_args())
    adapter = OpenAlexAdapter(config)
    ok, msg = adapter.preflight()
    if not ok:
        print(f"[FAIL] Preflight: {msg}", file=sys.stderr)
        sys.exit(1)
    rows = list(adapter.harvest(config.queries, config.max_results))
    adapter.write_output(rows, config.output_path)
```

**The convergence point:** After PE2, `elis/pipeline/search.py` imports adapters:

```python
# elis/pipeline/search.py (after PE2 convergence)
from elis.sources import get_adapter

def run_search(config):
    all_rows = []
    for source_name in config.enabled_sources:
        adapter = get_adapter(source_name, config)
        rows = list(adapter.harvest(config.queries_for(source_name), config.max_results))
        all_rows.extend(rows)
    # ... dedup, write canonical output with _meta header
```

**Acceptance criteria:**
- `elis harvest openalex` passes `appendix_a_harvester.schema.json` validation
- `test_database_harvest.yml` passes for ported sources with no workflow changes
- `scripts/openalex_harvest.py` (thin wrapper) produces identical output to old version
- HTTP client logs retry/backoff events on 429

---

### PE3 — Canonical Merge + Normalise

**Effort:** ~8 hours | **Risk:** Low (new stage) | **Branch:** `feature/merge-pipeline`

**Goal:** One authoritative Appendix A dataset from all per-source outputs.

**Deliverables:**

```
elis/
├── pipeline/
│   └── merge.py
```

**CLI:** `elis merge [--input-dir json_jsonl/] [--output json_jsonl/ELIS_Appendix_A_Search_rows.json]`

**Merge algorithm:**

```
1. Scan input directory for *_harvest.json / *_rows.json files
2. Per file:
   a. Load records
   b. Add provenance: source_file, merge_position
   c. Normalise:
      - doi: lowercase, strip, remove "https://doi.org/" prefix
      - title: strip, collapse internal whitespace
      - authors: strip per name
      - year: ensure int or null
3. Stable sort: (source, query_topic, title, year)
4. Write canonical JSON array with _meta header (appendix_a.schema.json)
5. Write JSONL sidecar (append-friendly)
6. Write merge_report.json
```

**merge_report.json:**
```json
{
  "total_records": 4532,
  "per_source_counts": { "scopus": 1200, "crossref": 980, ... },
  "doi_coverage_pct": 78.3,
  "null_field_ratios": { "title": 0.02, "abstract": 0.15, "language": 0.31 },
  "source_files_processed": ["scopus_rows.json", "crossref_rows.json", ...]
}
```

**Acceptance criteria:**
- Same inputs → byte-identical output (deterministic)
- Output passes `appendix_a.schema.json` validation
- `elis screen` accepts the merged output
- Merge report includes counts and coverage metrics

---

### PE1 — Data Contract + Run Manifest

**Effort:** ~8 hours | **Risk:** Low (additive) | **Branch:** `feature/run-manifest`

**Goal:** Every pipeline stage produces a run manifest sidecar.

**Why after PE3:** The manifest must cover merge, which doesn't exist until PE3. The existing `_meta` header provides partial provenance — PE1 formalises and extends.

**Deliverables:**

```
elis/
├── manifest.py

schemas/
├── run_manifest.schema.json
└── validation_report.schema.json
```

**Run manifest:**
```json
{
  "schema_version": "1.0",
  "run_id": "20260212_143022_scopus",
  "stage": "harvest",
  "source": "scopus",
  "commit_sha": "c81328e",
  "config_hash": "sha256:abc123...",
  "started_at": "2026-02-12T14:30:22Z",
  "finished_at": "2026-02-12T14:31:45Z",
  "record_count": 432,
  "input_path": null,
  "output_path": "json_jsonl/scopus_rows.json",
  "tool_versions": { "python": "3.11.9", "requests": "2.31.0" }
}
```

**Relationship to `_meta`:** The `_meta` header stays frozen in canonical JSON. Manifests are **sidecar files**: `*.manifest.json` alongside outputs.

**Acceptance criteria:**
- `elis search`, `elis merge`, `elis screen`, `elis validate` all emit `*.manifest.json`
- Manifests pass `run_manifest.schema.json` validation
- `_meta` header untouched

---

### PE4 — Cross-Source Dedup + Cluster IDs

**Effort:** ~8 hours | **Risk:** Low (new stage) | **Branch:** `feature/dedup`

**Goal:** Deterministic dedup with transparent clusters.

**Deliverables:**

```
elis/
├── pipeline/
│   └── dedup.py
```

**CLI:** `elis dedup [--input <merged A>] [--output <deduped A>] [--fuzzy] [--threshold 0.85]`

**Dedup policy (exact-match default):**

```
1. Compute dedup_key per record:
   a. DOI present → normalise_doi(doi)
   b. No DOI    → normalise(title) + "|" + str(year) + "|" + normalise(first_author)

2. Group by dedup_key → clusters

3. Per cluster:
   a. cluster_id = sha256(dedup_key)[:12]
   b. Keeper = record with most non-null fields
      Tie-break: Scopus > WoS > S2 > CrossRef > OpenAlex > IEEE > CORE > SD > GS
   c. Others: duplicate_of = keeper.id

4. Output: keepers with cluster_id, cluster_size, cluster_sources
```

**Normalisation:**
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

**Fuzzy:** Opt-in only (`--fuzzy --threshold 0.85`). Never default. Logs a warning when enabled.

**dedup_report.json:**
```json
{
  "input_records": 4532,
  "unique_clusters": 3187,
  "duplicates_removed": 1345,
  "doi_based_dedup": 892,
  "title_year_author_dedup": 453,
  "fuzzy_dedup": 0,
  "top_10_collisions": [
    { "cluster_id": "a3f2c1d4e5f6", "size": 7, "sources": ["scopus","wos","crossref"] }
  ]
}
```

**Acceptance criteria:**
- Same input → same cluster IDs (deterministic)
- No data loss (all records traceable via cluster_id)
- Fuzzy off by default

---

### PE5 — ASTA Pipeline Integration

**Effort:** ~6 hours | **Risk:** Low (leverages existing code) | **Branch:** `feature/asta-integration`

**Goal:** Define ASTA's exact role as an advisory, append-only sidecar. Not "defer" — specify.

ASTA is already implemented: adapter (394 lines), vocabulary, snippets, 3 phase scripts, 5 tests, 2 configs. PE5 wires it into the package with a defined interface.

**Pipeline position:**

```
elis harvest → merge → dedup → screen      ← canonical (deterministic)
                                  ↓
elis asta discover                          ← advisory (AI-augmented)
elis asta enrich                            ← append-only sidecar
```

**Key rule:** ASTA outputs live in `runs/asta/<run_id>/`, never in `json_jsonl/`. Canonical pipeline works identically with or without ASTA.

**Deliverables:**

```
elis/
├── agentic/
│   ├── __init__.py
│   ├── asta.py           # Wraps sources/asta_mcp/adapter.py
│   └── evidence.py       # Evidence span validation
```

**Evidence span validation:**
```python
def validate_evidence_spans(record: dict, spans: list[str]) -> list[dict]:
    """Verify each ASTA-cited span actually exists in the record text."""
    text = (record.get("title") or "") + " " + (record.get("abstract") or "")
    return [{"span": s, "valid": s.lower() in text.lower()} for s in spans]
```

**ASTA output schema (per suggestion):**
```json
{
  "record_id": "...",
  "suggestion": "include|exclude|review",
  "confidence": 0.87,
  "evidence_spans": [{ "text": "...", "valid": true }],
  "model_id": "asta-mcp-v1",
  "prompt_hash": "sha256:...",
  "run_id": "20260212_143022",
  "timestamp": "2026-02-12T14:30:22Z"
}
```

**Acceptance criteria:**
- ASTA outputs go to `runs/asta/`, not `json_jsonl/`
- Evidence spans validated; invalid flagged, not suppressed
- Canonical pipeline produces identical output with or without ASTA
- Existing ASTA tests keep passing

---

### PE6 — Migration + Cleanup (v2.0 Release)

**Effort:** ~4 hours | **Risk:** Low (package battle-tested by this point) | **Branch:** `release/v2.0`

**Goal:** Remove the old codepath entirely. The `elis` CLI becomes the only interface. Tag v2.0.

**Why this PE exists:** Without it, the thin wrappers introduced in PE0–PE2 become permanent — and the codebase has two ways to do everything forever. PE6 is the demolition of the old house after you've moved into the new one.

**Prerequisite:** PE0–PE5 all merged. Full pipeline (`elis harvest → merge → dedup → screen → validate`) working in CI for at least one full cycle.

**Deliverables:**

**1. Migrate all 19 workflows to `elis` CLI**

Before (current):
```yaml
# elis-agent-search.yml
- run: python scripts/elis/search_mvp.py --year-from 1990 ...
```

After:
```yaml
# elis-agent-search.yml
- run: pip install -e .
- run: elis search --year-from 1990 ...
```

Before (current):
```yaml
# test_database_harvest.yml
- run: python scripts/scopus_harvest.py --search-config config/searches/...
```

After:
```yaml
# test_database_harvest.yml
- run: pip install -e .
- run: elis harvest scopus --search-config config/searches/...
```

**2. Archive old scripts**

```
scripts/
├── _archive/                         # NEW: superseded by elis/ package
│   ├── README.md                     # Explains: "These scripts are archived.
│   │                                 #   Use `elis <command>` instead."
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
├── phase0_asta_scoping.py            # KEEP: ASTA phase scripts (PE5 wraps these)
├── phase2_asta_screening.py
├── phase3_asta_extraction.py
├── imports_to_appendix_a.py          # KEEP: standalone utility
├── agent.py                          # KEEP or archive: toy demo
├── convert_scopus_csv_to_json.py     # KEEP: one-off utility
├── archive_old_reports.py            # KEEP: housekeeping utility
└── test_all_harvests.py              # UPDATE: call `elis harvest` instead
```

**Decision: archive, not delete.** Git history preserves everything, but archiving keeps the files visible for reference during the transition. After v2.1 or v3.0, the `_archive/` directory can be deleted entirely.

**3. Update pyproject.toml**

```toml
[project]
version = "2.0.0"
```

**4. Update README.md**

Replace current "Usage Guide" section (which references `python scripts/scopus_harvest.py ...`) with:

```markdown
## Quick Start

# Install
pip install -e .

# Harvest from a single source
elis harvest scopus --search-config config/searches/electoral_integrity_search.yml --tier pilot

# Merge all per-source outputs into canonical Appendix A
elis merge

# Deduplicate
elis dedup

# Screen (apply protocol filters)
elis screen

# Validate any output
elis validate schemas/appendix_a.schema.json json_jsonl/ELIS_Appendix_A_Search_rows.json
```

**5. Update CHANGELOG.md**

```markdown
## v2.0.0 — 2026-XX-XX

### Breaking Changes
- All standalone harvest scripts archived to `scripts/_archive/`
- All workflows now use `elis` CLI instead of `python scripts/*.py`
- Requires `pip install -e .` before running any pipeline command

### Added
- `elis` CLI with subcommands: harvest, merge, dedup, screen, validate, asta
- Source adapter layer with shared HTTP client
- Cross-source merge stage producing canonical Appendix A
- Cross-source dedup with deterministic cluster IDs
- Run manifest sidecars for all pipeline stages
- ASTA integration as advisory sidecar

### Removed
- Direct invocation of `scripts/*_harvest.py` (use `elis harvest <source>`)
- Direct invocation of `scripts/elis/search_mvp.py` (use `elis search`)
- Direct invocation of `scripts/elis/screen_mvp.py` (use `elis screen`)
```

**6. Tag `v2.0.0`**

```bash
git tag -a v2.0.0 -m "ELIS SLR Agent v2.0 — unified pipeline"
git push origin v2.0.0
```

**Acceptance criteria:**
- All 19 workflows pass using `elis` CLI commands (no `python scripts/*.py` calls remain outside `_archive/`)
- `scripts/_archive/README.md` explains the migration
- `pip install -e . && elis harvest scopus --search-config config/searches/electoral_integrity_search.yml --tier testing` works from a clean clone
- CHANGELOG documents all breaking changes
- Git tag `v2.0.0` exists

---

## 4. Implementation Order and Effort

### Migration philosophy: build → coexist → cut over

The refactoring follows three phases, not a big-bang rewrite:

**Phase 1 — Build the new alongside the old (PE0a–PE2)**
The `elis/` package goes in. Both codepaths work. CI stays green. Thin wrappers bridge old scripts to new modules. No existing workflow changes.

**Phase 2 — New stages with no old equivalent (PE3–PE5)**
Merge, dedup, and ASTA integration are net-new. They only exist inside the package. This naturally pulls usage toward the `elis` CLI.

**Phase 3 — Cut over and clean up (PE6)**
All workflows migrate to `elis` CLI. Old scripts archived. Version bumped to 2.0.0. One codepath remains.

### Effort table

| PE | Description | Effort | Dependencies | Risk |
|----|------------|--------|-------------|------|
| **PE0a** | Package skeleton + `elis validate` | 4h | None | Zero |
| **PE0b** | Migrate MVP search/screen to package | 6h | PE0a | Low |
| **PE2** | Adapter layer + HTTP client + 3 sources | 16h | PE0a | Medium |
| **PE3** | Canonical merge + normalise | 8h | PE2 (≥1 adapter) | Low |
| **PE1** | Run manifest + extended schemas | 8h | PE0a | Low |
| **PE4** | Cross-source dedup + cluster IDs | 8h | PE3 | Low |
| **PE5** | ASTA pipeline integration | 6h | PE0a + existing ASTA | Low |
| **PE6** | Migration + cleanup → **v2.0 release** | 4h | PE0–PE5 all merged | Low |

**Total:** ~60 hours (~8 working days)

**Critical path:** PE0a → PE2 → PE3 → PE4 → PE6

**Parallel tracks:** PE1 and PE5 can both start after PE0a, in parallel with PE2.

```
Phase 1 (build):
  Week 1:  PE0a ──► PE0b ──► PE2 (OpenAlex, CrossRef, Scopus adapters)
                      ├──► PE1 (parallel)
                      └──► PE5 (parallel)

Phase 2 (new stages):
  Week 2:  PE2 (remaining adapters) ──► PE3 (merge) ──► PE4 (dedup)

Phase 3 (cut over):
  Week 3:  PE6 (migrate workflows, archive scripts, tag v2.0.0)
```

---

## 5. Config Strategy

| File | Purpose | Used by | Status |
|------|---------|---------|--------|
| `config/elis_search_queries.yml` | Legacy global config | All harvesters (fallback) | Keep through v2.0; deprecate in v2.1 |
| `config/searches/*.yml` | Per-project search configs with tiers | All harvesters (preferred) | Keep |
| `config/asta_config.yml` | ASTA-specific | ASTA adapter | Keep |
| **`config/sources.yml`** (NEW) | Per-source rate limits, endpoints, auth env var names | Adapter layer | Create in PE2 |

**`config/sources.yml` example:**
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
```

---

## 6. Interfaces to Freeze

### Freeze (breaking change = schema version bump)
- `schemas/appendix_a.schema.json` field names, types, `_meta` structure
- `schemas/appendix_b.schema.json`, `appendix_c.schema.json`
- Output paths: `json_jsonl/ELIS_Appendix_A_Search_rows.json`, `ELIS_Appendix_B_Screening_rows.json`
- CLI flags: `--search-config`, `--tier`, `--max-results`, `--output`

### Freeze after PE6 (v2.0 release)
- CLI subcommand names: `elis harvest`, `elis merge`, `elis dedup`, `elis screen`, `elis validate`, `elis asta`
- Workflow names and dispatch inputs (updated once in PE6, then frozen)

### Flexible (internal, may change between PEs)
- Internal module layout within `elis/`
- Adapter implementation details
- Retry/backoff parameters
- Validation report Markdown format
- Run manifest schema (until v1.0)
- Benchmark harness internals

---

## 7. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PE2 adapter changes harvest output | Medium | High | Golden snapshots: diff before/after |
| PE0 pyproject.toml changes break CI | Low | High | Test `pip install -e .` in CI first |
| Schema migration breaks downstream | Low | High | Additive only; `additionalProperties: true` |
| Merge ordering drift | Low | Medium | Deterministic sort key; golden snapshot |
| Solo researcher bandwidth | High | Medium | PE0a + PE2 first — max ROI, min effort |
| Google Scholar too different for ABC | Medium | Low | Apify escape hatch; defer GS adapter |
| PE6 workflow migration breaks CI | Low | High | Migrate one workflow at a time; keep old script as immediate rollback; run full CI after each migration |
| PE6 delayed indefinitely (wrappers become permanent) | Medium | Medium | Set calendar deadline: PE6 ships within 1 week of PE5 merge, no exceptions |

---

## 8. Conclusion

The codebase is more mature than either review initially credited. The schemas, CI surface, ASTA integration, and MVP pipeline scripts demonstrate real engineering. The structural problem is **convergence**: two codepaths producing incompatible outputs, ~1,600 lines of duplicated boilerplate, and no merge/dedup stage connecting harvester outputs to the screening pipeline.

The refactoring is not a big-bang rewrite. It follows three phases: **build** the new package alongside the old scripts (PE0–PE2), **extend** with net-new stages that only exist in the package (PE3–PE5), then **cut over** by migrating all workflows and archiving old scripts (PE6). The thin wrappers introduced in Phase 1 are temporary scaffolding — PE6 removes them.

**v2.0 is the deliverable.** Not a cleaned-up MVP. A unified product with one CLI, one pipeline, one data contract, and every stage producing a run manifest. The old scripts are archived, not deleted — Git history preserves everything, but the working tree is clean.

**Start with PE0a.** Four hours, zero risk, every subsequent PE depends on it. Then PE2 — the adapter layer eliminates duplication and creates the foundation for merge and dedup. PE6 closes the loop.

**Target end-state (v2.0):**
```
elis harvest → merge → dedup → screen → validate
     ↓           ↓       ↓        ↓         ↓
  manifest    manifest manifest manifest  manifest
                                   ↓
                              asta (advisory)
```

One pipeline. One data contract. One CLI. Every stage auditable. No legacy scripts in the active path.

---

*Generated 12 February 2026 by Claude Opus 4.6 — updated with PE6 (v2.0 migration strategy)*
*Repository verified via live access at commit `c81328e`*
