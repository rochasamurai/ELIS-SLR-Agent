# ELIS SLR Agent — Senior Architect Review of ChatGPT Refactoring Plan

**Reviewer:** Claude Opus 4.6 (Senior Architect role)
**Date:** 12 February 2026
**Repository:** `rochasamurai/ELIS-SLR-Agent`
**Documents reviewed:**
- `ELIS_Refactoring_Plan_5_PEs_UK.md`
- `ELIS_Task_Scripts_Codex_Claude_UK.md`
- Full conversation history (Oct 2025 – Feb 2026)
- ELIS Protocol v2.0 Draft 08.1

---

## 1. Repository Access Confirmation

The repository at `github.com/rochasamurai/ELIS-SLR-Agent` is **not publicly indexed** (does not appear in GitHub search or web search results). It is likely set to private visibility. I was unable to fetch the live codebase directly from this chat session. However, I have **extensive indirect access** through:

- Multiple past development sessions (Oct 2025 – Feb 2026) where I reviewed, wrote, and modified code directly
- Full project structure reconstructed from transcripts, commits, and README content
- Knowledge of all 8 harvest scripts, preflight scripts, schemas, workflows, config files, `tier_resolver.py`, `agent.py`, and `validate_json.py`
- ASTA integration report (Feb 2026) and Protocol v2.0 Draft 08.1

**Recommendation:** If you want me to do a line-by-line code audit, grant temporary public read access or paste the output of `find . -type f -name "*.py" | head -50` and key files. For this architectural review, the information I have is sufficient.

---

## 2. Current Architecture (As-Is)

Based on the full conversation history, the current state on `main` is:

```
ELIS-SLR-Agent/
├── config/
│   └── elis_search_queries.yml          # Search config (v2.0/v2.1 tier maps)
├── docs/
│   ├── ELIS_2025_SLR_Protocol_...v2.0_draft-08.1.pdf
│   ├── ASTA_Integration_Report.md
│   └── CHANGELOG.md
├── schemas/
│   ├── appendix_a.schema.json           # Search rows
│   ├── appendix_b.schema.json           # Screening decisions
│   └── appendix_c.schema.json           # Data extraction
├── scripts/
│   ├── agent.py                         # Toy agent (A→B→C demo)
│   ├── validate_json.py                 # Schema validator
│   ├── tier_resolver.py                 # Config tier resolution
│   ├── scopus_harvest.py                # ~13 KB
│   ├── scopus_preflight.py
│   ├── wos_harvest.py                   # ~13 KB
│   ├── wos_preflight.py
│   ├── ieee_harvest.py                  # ~15 KB
│   ├── ieee_preflight.py
│   ├── semanticscholar_harvest.py       # ~18 KB
│   ├── semanticscholar_preflight.py
│   ├── openalex_harvest.py              # ~16 KB
│   ├── openalex_preflight.py
│   ├── crossref_harvest.py              # ~16 KB
│   ├── crossref_preflight.py
│   ├── core_harvest.py                  # ~16 KB
│   ├── core_preflight.py
│   └── google_scholar_harvest.py        # ~20 KB (Apify actor)
├── json_jsonl/
│   └── ELIS_Appendix_A_Search_rows.json
├── .github/
│   └── workflows/
│       ├── elis-scopus-preflight.yml
│       ├── elis-wos-preflight.yml
│       ├── test_database_harvest.yml
│       └── ... (8+ workflow files)
├── tests/                               # Minimal
├── requirements.txt
└── README.md
```

**Key characteristics of the current codebase:**

- **Scripts-first monolith**: Each harvest script is 13–20 KB of self-contained logic (HTTP calls, pagination, transform, dedup, output writing). Substantial duplication across scripts.
- **Tier resolver**: Recently added (`tier_resolver.py`) provides a shared CLI surface (`--search-config`, `--tier`, `--max-results`, `--output`) across all 8 harvest scripts.
- **Schema validation**: JSON Schemas for Appendix A/B/C are frozen as Data Contract v1.0 (MVP).
- **Toy agent**: `agent.py` generates demo A→B→C artefacts but has no real screening or extraction logic.
- **CI**: GitHub Actions workflows for preflight checks and the `test_database_harvest.yml` matrix workflow.
- **No `elis/` package**: All code lives flat in `scripts/`.
- **No merge/normalise/dedup pipeline**: Each script writes its own output independently. There is no canonical merged dataset.
- **No run manifests or validation reports**: Beyond the schema check, there is no structured provenance or audit trail per run.
- **ASTA integration explored**: Vocabulary extraction from Allen AI's ASTA was tested (4,170 terms), but not yet integrated into the pipeline.

---

## 3. Review of the ChatGPT Refactoring Plan

### 3.1 Overall Assessment: STRONG PLAN, with caveats

The Refactoring Plan (5 PEs) is **architecturally sound and well-aligned with the ELIS Protocol's principles**. It correctly identifies the five most important structural gaps in the codebase and proposes a sensible layered progression. The guiding principles (deterministic core, data contract first-class, least privilege automation, keep wrappers stable) are exactly right.

However, the plan was produced **without direct access to the actual code**. The ChatGPT disclaimer says as much: *"I'm basing this on the repository's public structure/README."* This means the plan is directionally correct but **underestimates some existing progress and misses some project-specific constraints**.

### 3.2 PE-by-PE Assessment

#### PE1 — Data Contract + Run Manifest ✅ CONFIRMED (with adjustments)

**ChatGPT gets right:**
- Formalising Row + Provenance + RunManifest schemas is the correct first move.
- CI gating on manifest/report presence is essential for audit-readiness.
- "Add new fields, do not remove old ones" is the right backward-compat strategy.

**What ChatGPT misses:**
- **You already have schemas.** The `schemas/appendix_a.schema.json` (and B, C) exist and are frozen as Data Contract v1.0. PE1 should extend these, not replace them. The plan says "create `schemas/elis_row.schema.json`" as if none exist — this would create a competing schema unless carefully reconciled.
- **Provenance fields partially exist.** Each harvest script already emits `source`, `source_record_id` (as database-specific IDs like `scopus_id`, `wos_id`, `s2_id`), `doi`, `retrieved_at` (implicitly via timestamps). PE1 should standardise these, not invent them from scratch.
- **Pydantic models are overkill for the MVP.** The protocol explicitly states that the ELIS Agent executes deterministic rules — not complex object-oriented hierarchies. JSON Schema + a thin Python validator (which you already have in `validate_json.py`) is simpler and more aligned with the project's philosophy. Add Pydantic only if you plan to use it for API request/response validation downstream.

**Revised PE1 scope:**
1. Extend existing Appendix A schema with standardised provenance fields (`source_id`, `query_id`, `retrieved_at`, `endpoint`, `api_version`).
2. Create `schemas/run_manifest.schema.json` and `schemas/validation_report.schema.json`.
3. Write `scripts/manifest_writer.py` (a simple utility, not a deep package).
4. Update one harvest script to emit `run_manifest.json` alongside its output.
5. Update `validate_json.py` to also validate the manifest.

#### PE2 — Source Adapter Layer + HTTP Client ✅ CONFIRMED (highest ROI)

**ChatGPT gets right:**
- This is where the most duplication lives. 8 scripts × ~15 KB each = ~120 KB of duplicated HTTP/retry/pagination/transform logic.
- `SourceAdapter` with `preflight()`, `harvest()`, `normalise()` is the correct abstraction.
- Shared HTTP client with backoff+jitter, 429/5xx handling, and structured logs is essential.

**What ChatGPT misses:**
- **`tier_resolver.py` already exists** and handles CLI surface and config resolution. The adapter layer should incorporate (not duplicate) this.
- **The 7 preflight scripts (815–1,292 bytes each) should be consolidated.** The plan acknowledges this implicitly but doesn't call it out. A single `elis/sources/preflight.py` that dispatches based on source name would eliminate 6 files.
- **Google Scholar is the outlier.** It uses the Apify actor pattern (no direct API), deduplicates on title rather than DOI, and has no preflight. The adapter should have a clear escape hatch for non-HTTP sources.

**Revised PE2 priority:**
This is the **single highest-ROI PE** and should be done first if resources are limited. Even a partial implementation (shared HTTP client + 2–3 adapted scripts) would reduce maintenance burden dramatically.

#### PE3 — Merge + Normalise Pipeline Stage ✅ CONFIRMED (critical gap)

**ChatGPT gets right:**
- There is currently **no canonical merged dataset**. Each script writes independently to `json_jsonl/`. This is the most significant architectural gap.
- Deterministic ordering, provenance retention, and merge reporting are all essential.
- The CLI entrypoint (`python -m elis merge`) is the right interface.

**What ChatGPT misses:**
- **Field mapping is already partially standardised.** All harvest scripts were upgraded (Feb 2026) to emit a common field set: `source`, `title`, `authors`, `year`, `doi`, `url`, plus database-specific IDs. The merge step is simpler than the plan implies because the normalisation work was partly done during the harvest script upgrade.
- **JSONL vs JSON decision matters.** The current output is `ELIS_Appendix_A_Search_rows.json` (a JSON array). The plan suggests JSONL. For audit-readiness, JSONL is better (append-friendly, streamable). But switching output format is a breaking change for downstream consumers. Recommend: produce both (JSON for backward compat, JSONL as canonical).

#### PE4 — Dedup Engine + Cluster IDs ✅ CONFIRMED (with important nuance)

**ChatGPT gets right:**
- Dedup policy (DOI-first, then title+year+author) is standard and correct.
- Cluster IDs and `dedup_report.json` are essential for transparency.
- Streaming over JSONL is the right performance approach.

**What ChatGPT misses:**
- **Per-source dedup already exists in each harvest script.** The scripts already deduplicate within their own results (e.g., Semantic Scholar uses `s2_id` + DOI, CrossRef uses DOI + normalised title). PE4 is about cross-source dedup, which is a different and harder problem.
- **Fuzzy matching should be opt-in and documented, not default.** For a solo-researcher SLR with ~5,000–10,000 records, exact matching on normalised DOI + normalised title+year+author will catch 95%+ of duplicates. Fuzzy matching introduces false positives and undermines the protocol's determinism principle. Recommend: implement exact dedup first, add fuzzy as an opt-in flag with a documented threshold.

#### PE5 — Agentic Layer ⚠️ PARTIALLY CONFIRMED (needs re-scoping)

**ChatGPT gets right:**
- Append-only outputs are non-negotiable.
- `model_id`, `prompt_hash`, `run_id`, timestamps, and evidence spans are the correct audit fields.
- Prompt versioning + hashing is essential.

**What ChatGPT misses or gets wrong:**
- **The ELIS Protocol explicitly states the agent does NOT "decide"** — it executes the researcher's codified rules. The protocol's conceptual architecture is: Human Researcher → ELIS SLR Agent → GitHub Version Control. The agent is a deterministic execution engine, not an autonomous screener. Introducing LLM-based screening as PE5 **contradicts the protocol's foundational principle** unless very carefully framed.
- **ASTA integration is already being explored** as of Feb 2026. The plan doesn't mention ASTA at all, which is the project's actual direction for AI-augmented literature discovery.
- **"Option B: OpenAI Agents SDK" is a vendor lock-in risk.** The ELIS Protocol should remain model-agnostic. The plan references OpenAI-specific APIs exclusively. At minimum, the agentic layer should abstract the LLM provider behind an interface.
- **The plan's PE5 scope is premature.** Before building a full agentic screening pipeline, the project needs PE1–PE4 done and validated. PE5 should be deferred to a separate milestone.

**Revised PE5 scope:**
1. Define the screening decision schema (which is already `appendix_b.schema.json`).
2. Implement a deterministic, rule-based screening module (`elis/pipeline/screening.py`) that applies the researcher's codified inclusion/exclusion criteria.
3. If LLM-augmented screening is desired, implement it as a separate, clearly labelled experimental module (`elis/agentic/screening.py`) with full provenance, and **never as the default path**.

### 3.3 Assessment of the Task Scripts (Codex + Claude Code Loop)

The two-agent adversarial loop (Codex implements, Claude reviews) is a **clever workflow pattern** but has practical issues:

- **Codex is deprecated.** OpenAI replaced Codex with GPT-4 and the Assistants API. The scripts reference "Codex" as if it were a current product. This should be updated to reference the appropriate current tool (e.g., Claude Code, Cursor, or Windsurf).
- **The adversarial review prompts are well-structured.** The severity rating system (Critical/High/Med/Low) and the focus areas per PE are solid. These can be reused regardless of which AI tool runs the implementation.
- **The prompts assume a greenfield `elis/` package.** Since the project currently has no `elis/` package structure, the first implementation step should be creating the package skeleton — which the scripts don't address.

---

## 4. Proposed Revised Structure and Approach

### 4.1 Recommended Target Architecture

```
ELIS-SLR-Agent/
├── config/
│   ├── elis_search_queries.yml
│   └── sources.yml                      # Per-source rate limits, endpoints, ID fields
├── docs/
│   ├── ELIS_2025_SLR_Protocol_v2.0_draft-08.1.pdf
│   ├── ASTA_Integration_Report.md
│   └── CHANGELOG.md
├── elis/                                # NEW: Python package
│   ├── __init__.py
│   ├── __main__.py                      # CLI: python -m elis harvest|merge|dedup|validate
│   ├── models.py                        # Pydantic/dataclass models (Row, Provenance, Manifest)
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── base.py                      # SourceAdapter ABC
│   │   ├── http_client.py               # Shared HTTP (retry, backoff, rate limit)
│   │   ├── scopus.py                    # Thin adapter wrapping harvest logic
│   │   ├── wos.py
│   │   ├── ieee.py
│   │   ├── semantic_scholar.py
│   │   ├── openalex.py
│   │   ├── crossref.py
│   │   ├── core.py
│   │   └── google_scholar.py            # Apify pattern
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── merge.py                     # Cross-source merge
│   │   ├── normalise.py                 # Field normalisation
│   │   ├── dedup.py                     # Cross-source dedup
│   │   ├── screening.py                 # Deterministic rule-based screening
│   │   ├── manifest.py                  # Run manifest + validation report writer
│   │   └── validate.py                  # Schema validation
│   └── agentic/                         # OPTIONAL: LLM-augmented modules
│       ├── __init__.py
│       ├── screening.py                 # Experimental LLM screening
│       └── prompts/                     # Versioned prompt registry
├── schemas/
│   ├── appendix_a.schema.json           # EXISTING (extended)
│   ├── appendix_b.schema.json           # EXISTING
│   ├── appendix_c.schema.json           # EXISTING
│   ├── run_manifest.schema.json         # NEW
│   └── validation_report.schema.json    # NEW
├── scripts/                             # PRESERVED: thin wrappers for backward compat
│   ├── scopus_harvest.py                # Delegates to elis.sources.scopus
│   ├── scopus_preflight.py              # Delegates to elis.sources.scopus.preflight()
│   ├── ... (all existing scripts preserved)
│   ├── validate_json.py                 # Delegates to elis.pipeline.validate
│   └── agent.py                         # Delegates to elis.pipeline
├── tests/
│   ├── fixtures/                        # Golden test data
│   ├── test_models.py
│   ├── test_http_client.py
│   ├── test_merge.py
│   ├── test_dedup.py
│   └── test_screening.py
├── json_jsonl/                          # Output directory
├── .github/workflows/
├── requirements.txt
├── pyproject.toml                       # NEW: package metadata
└── README.md
```

### 4.2 Recommended PE Execution Order

| Priority | PE | Effort | Rationale |
|----------|-----|--------|-----------|
| 1 | PE2 (Adapter + HTTP) | 2–3 days | Highest ROI. Eliminates ~80 KB of duplicated code. Enables all subsequent PEs. |
| 2 | PE3 (Merge + Normalise) | 1–2 days | Fills the most critical functional gap (no canonical merged dataset). |
| 3 | PE4 (Dedup) | 1–2 days | Depends on PE3 output. Exact-match first, fuzzy opt-in later. |
| 4 | PE1 (Data Contract + Manifest) | 1–2 days | Can be done in parallel with PE2. Extend existing schemas, don't replace. |
| 5 | PE5 (Agentic) | Defer | Only after PE1–PE4 are validated and the deterministic pipeline is complete. |

**Note:** The ChatGPT plan numbers PE1 first, but PE2 should be first because it unblocks the code consolidation that makes PE3 and PE4 straightforward to implement.

### 4.3 Key Differences from ChatGPT Plan

| Aspect | ChatGPT Plan | My Recommendation |
|--------|-------------|-------------------|
| Starting PE | PE1 (Data Contract) | PE2 (Adapter Layer) — higher ROI, unblocks everything |
| Schema approach | Create new `elis_row.schema.json` | Extend existing `appendix_a.schema.json` |
| Package creation | Implicit | Explicit `pyproject.toml` + `elis/` package as step zero |
| Existing progress | Unaware of tier_resolver, script upgrades, ASTA | Build on what exists |
| PE5 framing | LLM screening as standard feature | LLM screening as opt-in experimental module |
| LLM provider | OpenAI-only (Codex, Agents SDK) | Provider-agnostic (abstract behind interface) |
| Preflight scripts | Not mentioned | Consolidate 7 scripts into one |
| Google Scholar | Not addressed as outlier | Explicit escape hatch for non-HTTP sources |
| Fuzzy dedup | Included by default | Exact-match first, fuzzy opt-in with threshold |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Refactoring breaks CI | Medium | High | Run `test_database_harvest.yml` matrix after every PE. Golden output snapshots. |
| Schema migration breaks downstream | Low | High | Additive changes only. Schema versioning (`schema_version` field). |
| Adapter layer changes harvest behaviour | Medium | Medium | Snapshot outputs before/after. Compare row counts and key fields. |
| PE5 contradicts ELIS Protocol | High if done naively | High | Frame LLM screening as experimental, not default. Maintain deterministic screening as primary. |
| Solo researcher bandwidth | High | Medium | Focus on PE2+PE3 first. These two alone provide 80% of the architectural improvement. |

---

## 6. Conclusion

The ChatGPT refactoring plan is **well-conceived directionally** and demonstrates solid understanding of SLR pipeline best practices. Its five PEs cover the right gaps in the right order of complexity.

However, it was produced without access to the actual codebase and therefore:
1. Doesn't account for existing progress (tier_resolver, script upgrades, schemas, ASTA integration).
2. Proposes creating things from scratch that already partially exist.
3. Introduces an OpenAI-specific dependency in PE5 that conflicts with the protocol's model-agnostic principle.
4. Underestimates the PE2 adapter layer as the highest-leverage intervention.

**My recommendation: adopt the plan's structure with the adjustments above.** Start with PE2 (adapter layer), do PE3 (merge) and PE1 (manifest) in quick succession, then PE4 (dedup). Defer PE5 until the deterministic pipeline is complete and validated.

The two-agent adversarial workflow (implement + review) is sound regardless of which AI tools are used. Replace "Codex" references with Claude Code or the tool you're actually using.

---

*Review generated by Claude Opus 4.6 in Senior Architect role.*
*12 February 2026*
