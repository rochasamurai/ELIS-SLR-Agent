# ELIS SLR Agent — Updated End-to-End Architecture & Code Review (UK English)

**Date:** 2026-02-12  
**Inputs used:**  
1) Repository snapshot provided as ZIP (`ELIS-SLR-Agent-main.zip`)  
2) Claude “Senior Architect Review of ChatGPT Refactoring Plan” (`ELIS_Refactoring_Review_Senior_Architect_by_Claude.md`)  

---

## 0. Executive Summary

This ZIP snapshot shows a **more mature repo** than the “as-is” structure assumed in the Claude review (which was based on indirect access and conversation history). In particular, the repo now includes:

- A **tooling-oriented `pyproject.toml`** (Black/Ruff/Pytest defaults), but **no installable package metadata yet**.
- A large **GitHub Actions suite** (search/screen/validate/benchmark/nightly/housekeeping/etc.), well beyond a single harvest test workflow.
- A **validation-report pipeline** producing timestamped Markdown artefacts into `validation_reports/`.
- **MVP pipeline scripts** under `scripts/elis/` for search and screening.
- An **ASTA MCP source adapter** under `sources/asta_mcp/`.

At the same time, several structural gaps remain (and match the direction of the prior refactor plan):

- The codebase is still **scripts-first** with duplicated HTTP/pagination/normalisation logic across harvesters.
- There is still **no single canonical merged dataset** across sources and no cross-source **dedup clustering layer** as a first-class stage.
- There is no **stable, importable package boundary** (e.g., `elis/`) with a single CLI entrypoint; instead, the project is driven by many scripts and workflows.
- “Run provenance” exists informally (logs + validation reports), but not yet as a **standard run manifest schema** carried by all pipeline steps.

Claude’s main recommendation—**prioritise consolidation via an adapter layer and shared client, then implement merge/dedup, and defer agentic work**—is still directionally correct, but the PE plan must be updated to reflect what is already in the repo and what is missing in this ZIP snapshot.

---

## 1. What Claude Review Concluded (and What We Must Preserve)

Claude’s review (12 Feb 2026) argues that:
- the refactoring direction is strong, but should **build on existing progress** rather than invent parallel structures;
- **PE2 (adapter + shared HTTP client)** is the highest ROI, unblocking merge/dedup;
- **LLM/agentic screening should be opt-in**, and deterministic screening should remain the default.

These are the right guardrails to keep. (See the review’s “Key characteristics”, “PE-by-PE assessment”, and “Conclusion”.)

---

## 2. Repository Snapshot — Observed Structure (from ZIP)

### 2.1 Top-level directories (high signal)
- `.github/workflows/` — **19** workflows
- `scripts/` — harvester scripts + MVP pipeline scripts (`scripts/elis/`)
- `schemas/` — Appendix schemas plus `_legacy/`
- `json_jsonl/` — canonical JSON artefacts + configs + logs
- `validation_reports/` — generated Markdown validation reports (timestamped + latest)
- `sources/asta_mcp/` — ASTA MCP adapter module
- `benchmarks/` and `docs/benchmark-*` — benchmarking harnesses
- `imports/` — import conversion staging (consistent with earlier workflow defaults)

### 2.2 Key counts
- Python files: **48**
- Harvesters: **9** (`scripts/*_harvest.py`)
- Workflows: **19**
- `tier_resolver.py` present? **False**
- ASTA adapter present? **True**
- Validation reports present? **True**

### 2.3 Harvesters found in this snapshot
- `core_harvest.py`
- `crossref_harvest.py`
- `google_scholar_harvest.py`
- `ieee_harvest.py`
- `openalex_harvest.py`
- `sciencedirect_harvest.py`
- `scopus_harvest.py`
- `semanticscholar_harvest.py`
- `wos_harvest.py`

### 2.4 MVP pipeline scripts found
- `scripts/elis/imports_to_appendix_a.py`
- `scripts/elis/screen_mvp.py`
- `scripts/elis/search_mvp.py`

### 2.5 Non-legacy schemas found
- `schemas/appendix_a.schema.json`
- `schemas/appendix_a_harvester.schema.json`
- `schemas/appendix_b.schema.json`
- `schemas/appendix_c.schema.json`

### 2.6 README protocol reference check
The README references protocol PDFs: ELIS_2025_SLR_Protocol_v1.8.pdf.

**Action:** reconcile README references with the protocol version you consider canonical now (the repo contains v2.x draft artefacts under `docs/`).

---

## 3. Key Deltas vs Claude’s “As-Is” Picture

Claude’s review describes a repo that (a) is not publicly accessible to this chat session and (b) contains a `tier_resolver.py` and a single main harvest test workflow. In the ZIP snapshot:

1) **`tier_resolver.py` is not present** (either removed, renamed, or it lives in another branch/tag).  
2) There is a **much richer GitHub Actions surface** (`elis-agent-search`, `elis-agent-screen`, `elis-validate`, benchmarks, nightly jobs, housekeeping, etc.).  
3) There is already a **validation-report subsystem** writing into `validation_reports/`.  
4) There is an embryonic staged pipeline under `scripts/elis/`, suggesting you started separating *pipeline stages* from *source harvesters*.  
5) There is a **single “sources” package**, but it currently only contains the ASTA MCP adapter, not a general adapter layer for all sources.

Net: the repo has progressed towards the right direction, but the consolidation is **partial and inconsistent** (pipeline logic exists, but harvesters remain monolithic; a `sources/` package exists, but only for ASTA).

---

## 4. End-to-End Architecture Assessment (Best Practices Lens)

### 4.1 What’s strong (keep and extend)
1) **CI/Automation depth**  
   You have moved well beyond “run a script”; workflows appear to cover staged execution, validation, benchmarks, nightly runs, housekeeping, and formatting.

2) **Contract-first direction is visible**  
   Appendix schemas exist (plus a `_legacy/` folder), and validation produces artefacts.

3) **Evidence of reproducibility thinking**  
   Generated validation reports with timestamping are a practical start for “auditability”.

4) **Benchmark harness exists**  
   This is a meaningful differentiator (most SLR automation repos never get here).

### 4.2 Key gaps and risks (highest impact)
1) **No unified, importable application boundary**  
   You have `pyproject.toml` tooling, but not an installable package with a stable CLI (e.g., `python -m elis ...`). This makes local dev and CI scripting harder than necessary and increases drift between scripts.

2) **Harvester duplication remains the biggest maintenance cost**  
   Each harvester is still a monolith combining:
   - request building
   - pagination
   - error/backoff
   - normalisation
   - local dedup
   - output writing
   - summary/report writing

   This is exactly where you will bleed time as sources change APIs, quotas, parameters, and response shapes.

3) **No canonical merged dataset + cross-source dedup stage**  
   You have per-source outputs and config artefacts, but no single authoritative merged + deduped “Appendix A canonical dataset” step.

4) **Provenance is present but not standardised across stages**  
   You generate validation reports and logs, but you still need a run manifest schema and consistent provenance fields carried through search → screen → extract.

5) **Tooling vs package mismatch**  
   `pyproject.toml` config exists, but without package metadata you cannot easily ship reusable modules, and CI cannot enforce “imports” vs “scripts” hygiene.

---

## 5. Updated Refactoring Plan (5 PEs) — Tailored to This ZIP Snapshot

> This preserves the spirit of the earlier plan and Claude’s guidance, but updates sequencing and scope to match what is already in the repo.

### PE0 — “Stabilise the Product Surface” (1 PR)
**Goal:** stop the project being a collection of scripts; establish a stable CLI + module layout.

Deliverables:
- Create top-level package `elis/` (or `elis_agent/`; pick one and stick to it).
- Add `[project]` metadata to `pyproject.toml` (keep existing tooling blocks).
- Add `elis/cli.py` and `elis/__main__.py` exposing subcommands:
  - `elis harvest <source>`
  - `elis search` (MVP)
  - `elis screen` (MVP)
  - `elis validate <path>`
  - `elis report` (optional: combine validation artefacts)
- Keep `scripts/*.py` as thin wrappers calling into `elis.*` for backward compatibility.

### PE1 — Data Contract + Run Manifest (build on existing schemas)
**Goal:** standardise provenance and produce one manifest per stage run.

Deliverables:
- Extend `schemas/appendix_a.schema.json` (do not replace) with standard fields:
  - `run_id`, `query_id`, `source`, `source_record_id`, `retrieved_at`, `endpoint`, `api_version`, `raw_url`
- Add:
  - `schemas/run_manifest.schema.json`
  - `schemas/validation_report.schema.json`
- Update validation to emit:
  - `validation_reports/<timestamp>_validation_report.md` (already exists)
  - `validation_reports/<timestamp>_run_manifest.json` (new)
  - `validation_reports/validation-report.md` (already exists)

### PE2 — Source Adapter Layer + Shared HTTP Client (highest ROI)
**Goal:** collapse duplicated harvester logic into adapters and one resilient client.

Deliverables:
- Introduce `elis/sources/base.py` with a `SourceAdapter` interface:
  - `preflight()`, `harvest()`, `normalise()`, `summarise()`
- Implement `elis/http_client.py`:
  - retries with jitter
  - 429 / 5xx handling
  - per-source rate limits from config
  - structured log events
- Port 2–3 harvesters first (suggest: `crossref`, `openalex`, `semantic_scholar`).
- Keep the current scripts as wrappers so CI workflows do not break.

### PE3 — Canonical Merge + Normalise Stage
**Goal:** produce one authoritative Appendix A dataset.

Deliverables:
- `elis/pipeline/merge.py`
  - input: multiple per-source JSON/JSONL
  - output: `json_jsonl/ELIS_Appendix_A_Search_rows.jsonl` (canonical) + JSON array (compat)
  - deterministic ordering
  - merge report (counts per source, missing DOI ratio, etc.)

### PE4 — Cross-Source Dedup + Cluster IDs
**Goal:** deterministic dedup with transparent clusters.

Deliverables:
- `elis/pipeline/dedup.py`
  - DOI-first exact match
  - title/year/first-author exact match fallback
  - cluster IDs
  - `dedup_report.json` (and optional MD summary)

**Rule:** fuzzy matching is opt-in (`--fuzzy`) and never default.

### PE5 — Agentic Augmentation (defer; keep deterministic default)
**Goal:** keep ELIS protocol alignment; add AI only as an explicit tool.

Deliverables:
- Treat ASTA as a **discovery/synthesis tool**, not as the arbiter of inclusion.
- Any LLM screening/extraction lives under `elis/agentic/` and is opt-in:
  - strict evidence logging
  - prompt/version hashes
  - output schema validation
- Default pipeline remains deterministic and auditable.

---

## 6. Priority Recommendations (What to do next)

If you want the highest ROI sequence with minimal disruption:

1) **PE0 (package + CLI)**
2) **PE2 (adapter + shared HTTP)** for 2–3 sources only
3) **PE3 (merge)**
4) **PE1 (manifest)**
5) **PE4 (dedup)**
6) **PE5 (agentic) only after stable deterministic pipeline**

This sequencing preserves current workflows while you refactor behind stable interfaces.

---

## 7. Appendix — What I Recommend You Freeze as “Interfaces”

### 7.1 Interfaces to freeze
- Output record formats (Appendix A/B/C schemas)
- CLI flags and subcommand names (`elis harvest`, `elis validate`, etc.)
- Config file semantics (`config/*.yml` and `json_jsonl/config/*`)

### 7.2 What should remain flexible
- internal module layout
- adapter implementations per source
- retry policy tuning
- benchmark harness internals

---

*End of document.*
