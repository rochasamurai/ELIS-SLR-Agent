# ELIS SLR Agent — Refactoring Plan (5 PEs)

> **Scope & intent**
>
> This plan upgrades the ELIS SLR Agent from “scripts-first” to a **package + pipeline-first** architecture while preserving your existing GitHub Actions workflows and source-specific scripts as thin wrappers.
>
> I’m basing this on the repository’s public structure/README plus standard SLR reproducibility and API-harvesting best practice. Where the current code differs, treat each PE as a **directional** PR blueprint and adjust file names to match your tree.

---

## Guiding principles (non-negotiables)

1. **Deterministic core; agentic layer is optional**  
   Harvest/normalise/validate/deduplicate must be deterministic and reproducible. Any LLM-based steps must be **separately versioned** and never overwrite raw records.

2. **Data Contract is first-class**  
   Every run produces:
   - `run_manifest.json` (config hash, repo SHA, timestamps, counts, source endpoints, rate limiting parameters)
   - `validation_report.json` (schema validation summary)
   - `dedup_report.json` (dedup keys, thresholds, clusters, collisions)

3. **Least privilege automation**  
   GitHub Actions use minimal `GITHUB_TOKEN` permissions; secrets are never exposed to fork PRs.

4. **Keep wrappers stable**  
   All existing scripts and Actions keep working during refactor. New internals are introduced behind them.

---

## PE1 — Establish the Data Contract + Run Manifest

### Goal
Make ELIS “audit-ready” by formalising the **Row schema** and introducing a uniform run manifest across all sources.

### Deliverables
- `schemas/` (or `elis/datacontract/`) containing:
  - `Row` schema (JSON Schema and/or Pydantic model)
  - `Provenance` schema: `source_id`, `source_record_id`, `query_id`, `retrieved_at`, `endpoint`, `api_version`, etc.
  - `RunManifest` schema: config hash, repo SHA, run_id, counts, tool versions
- A shared helper to write manifests & reports:
  - `elis/pipeline/manifest.py` (or equivalent)

### Changes (typical file list)
- Add:
  - `elis/datacontract/models.py`
  - `elis/pipeline/manifest.py`
  - `schemas/elis_row.schema.json`
  - `schemas/run_manifest.schema.json`
- Update:
  - Source scripts to emit provenance & manifest (thin wrapper calls)

### Acceptance criteria
- All source runs output:
  - a JSON/JSONL dataset aligned to schema
  - `run_manifest.json` + `validation_report.json`
- CI job fails if manifest or schema validation missing.

### Risks & mitigations
- **Breaking old downstream tools**: keep old fields; only add new fields; deprecate later.
- **Schema churn**: enforce schema_version + semver-like bumps.

### Codex task script (PE1)
**Objective**: implement data contract + manifest writer; update one source end-to-end (choose the lowest-risk source) and create templates for others.

**Codex prompt**
- Role: senior refactoring engineer.
- Constraints:
  - Minimal diffs.
  - Do not change query semantics.
  - Do not remove existing outputs; add new artefacts.
- Steps:
  1. Create `Row` + `Provenance` models.
  2. Add manifest writer and validation report writer.
  3. Wire one source script to emit manifest/report.
  4. Add tests for schema validation.

**Commands to run**
- `python scripts/validate_json.py` (or your existing validator)
- `pytest -q` (if tests exist)

### Claude Code review script (PE1)
- Review diff for:
  - Backward compatibility of output fields
  - Manifest completeness (hashes, timestamps, counts)
  - Validation gating (CI will fail if missing)
- Provide: 5–10 bullet findings with severity and concrete fixes.

---

## PE2 — Create a Common Source Adapter Layer (API + rate limiting + retries)

### Goal
Eliminate duplicated logic across scripts: HTTP client, retries/backoff, rate-limiting, pagination, and consistent logging.

### Deliverables
- `elis/sources/base.py`: `SourceAdapter` interface (`preflight()`, `harvest()`, `normalise()`).
- `elis/sources/http.py`: shared HTTP client with:
  - exponential backoff + jitter
  - 429/5xx handling
  - per-source rate limits
  - structured logs

### Changes (typical file list)
- Add:
  - `elis/sources/base.py`
  - `elis/sources/http.py`
- Update:
  - One or two source integrations to use adapter (start with easiest)

### Acceptance criteria
- At least one source uses the adapter layer for calls and pagination.
- Errors are structured; retries are visible in logs.
- Preflight returns deterministic “OK/FAIL + reason”.

### Risks & mitigations
- **Behaviour drift**: snapshot old outputs before switching; compare counts and key fields.
- **Rate-limit regressions**: make limits configurable in YAML.

### Codex task script (PE2)
- Implement `SourceAdapter` and shared HTTP client.
- Convert one source script to use adapter.
- Add “golden” test: run the source in a mocked mode or against a tiny fixture.

### Claude Code review script (PE2)
- Review for:
  - correct retry conditions (429, 5xx; avoid retry on 4xx except 429)
  - timeouts set sanely
  - no secrets in logs

---

## PE3 — Merge + Normalise Pipeline Stage (single canonical output)

### Goal
Standardise the pipeline so that merging outputs from multiple sources yields a **single canonical dataset** with consistent fields.

### Deliverables
- `elis/pipeline/merge.py`: merge multiple JSONL/JSON inputs into canonical JSONL.
- `elis/pipeline/normalise.py`: normalise titles, authors, year, DOI, venue, identifiers, language.

### Acceptance criteria
- Given N source outputs, `merge` produces:
  - canonical `search_rows.jsonl`
  - `merge_report.json` (counts per source, dropped/invalid)
- Schema validation passes on merged output.

### Risks & mitigations
- **Field mapping disagreements**: define mapping table per source in config.
- **Encoding issues**: enforce UTF-8, normalise whitespace.

### Codex task script (PE3)
- Build merge/normalise utilities.
- Add CLI entrypoint: `python -m elis merge ...`
- Add tests with fixture JSONL files.

### Claude Code review script (PE3)
- Review for:
  - deterministic ordering (stable sorting)
  - provenance retention (do not lose source_record_id)
  - correct null-handling and data loss avoidance

---

## PE4 — Dedup Engine + Cluster IDs + Reports

### Goal
Complete deduplication before screening, with a transparent deterministic policy.

### Dedup policy (recommended)
1. If DOI exists → dedup key = `doi_normalised`
2. Else → dedup key = `norm_title + year + first_author`  
   Optionally add fuzzy matching for near-duplicates, with documented threshold.
3. Output:
   - `cluster_id` for each record
   - `cluster_members` list (source IDs + record IDs)
   - `dedup_report.json` and `collisions.json`

### Deliverables
- `elis/pipeline/dedup.py`
- `reports/dedup_report.json` (artefact)
- Optional: `reports/collisions.csv` for manual review

### Acceptance criteria
- Dedup run is deterministic (same input => same cluster_ids).
- Report includes:
  - total records, unique clusters, DOI-based vs title-based dedups
  - top collision cases

### Codex task script (PE4)
- Implement dedup engine and reporting.
- Add unit tests:
  - DOI duplicates
  - title/year/author duplicates
  - tricky punctuation/case/diacritics

### Claude Code review script (PE4)
- Review for:
  - false-positive risk in fuzzy matching
  - explainability of clusters
  - performance on large JSONL files (streaming vs load-all)

---

## PE5 — Introduce Agentic Layer (Screening/Extraction) with Guardrails + Auditability

### Goal
Add LLM-based screening/extraction **without compromising reproducibility**.

### Design rules
- LLM outputs are **append-only**: never overwrite raw rows.
- Every decision has:
  - `model_id`, `prompt_hash`, `run_id`, timestamps
  - evidence spans (e.g., abstract snippets)
  - reviewer override fields

### Deliverables
- `elis/agentic/screening.py` and/or `elis/agentic/extraction.py`
- `prompts/` registry with versions
- `runs/agentic/<run_id>/` artefacts:
  - inputs snapshot
  - outputs JSONL
  - run manifest

### Implementation options
- **Option A (simple)**: Responses API + function calling with strict tools
- **Option B (scalable)**: OpenAI Agents SDK for multi-agent orchestration and tracing

### Acceptance criteria
- Agentic run produces `agentic_manifest.json` + outputs.
- Outputs are reviewable and reversible.
- CI ensures schemas still pass.

### Codex task script (PE5)
- Implement an agentic screening module that:
  - reads canonical dataset
  - outputs `screening_decisions.jsonl`
  - writes `agentic_manifest.json`
- Add a GitHub Action workflow_dispatch “agentic preflight”.

### Claude Code review script (PE5)
- Review for:
  - no hallucinated citations (decisions must cite evidence in row text)
  - prompt versioning + hashing
  - strict tool schemas and no arbitrary command execution

---

## Reference links (for implementation guidance)

```text
OpenAI Agents SDK docs:
https://platform.openai.com/docs/guides/agents-sdk

OpenAI Function Calling / Structured Outputs:
https://help.openai.com/en/articles/8555517-function-calling-in-the-openai-api

GitHub Actions token permissions (least privilege):
https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-guides/automatic-token-authentication
```
