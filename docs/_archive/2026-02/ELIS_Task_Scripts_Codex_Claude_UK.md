# ELIS SLR Agent — Task Scripts for Codex and Claude Code (UK English)

> **Purpose**
>
> These are copy/paste “operational scripts” (prompt templates) to run your two-agent loop:
> - **Codex = implementer**
> - **Claude Code = adversarial reviewer**
>
> Each PE has a Codex implementation script and a Claude review script.
> Use them as-is; replace the placeholders.

---

## Global rules (use in every PE)

### Repository constraints
- Keep diffs minimal and scoped.
- Do not change query semantics unless explicitly requested.
- Preserve existing GitHub Actions; introduce new ones gradually.
- All new outputs must be versioned or stored as CI artefacts.

### Definition of Done (DoD)
- Tests and validators pass locally in CI.
- Schema validation passes for all new/changed outputs.
- A run manifest is produced and includes config hash + commit SHA.
- README / docs updated only where behaviour changed.

---

## PE1 — Data Contract + Run Manifest

### Codex (Implementer) — Script
**Paste into Codex:**
```text
You are the implementer. Objective: introduce a formal Data Contract (Row + Provenance + RunManifest) and wire it end-to-end for ONE source without breaking existing outputs.

Context:
- Repo: ELIS SLR Agent.
- We want audit-ready runs: each run outputs run_manifest.json + validation_report.json alongside the dataset.
- Keep diffs minimal. Preserve existing fields; add new fields, do not remove old ones.

Tasks:
1) Create models/schemas:
   - Row schema (JSON Schema and/or Pydantic)
   - Provenance schema (source_id, source_record_id, query_id, retrieved_at, endpoint, api_version)
   - RunManifest schema (run_id, config_hash, commit_sha, timestamps, counts, tool versions)
2) Add a manifest writer utility and validation report utility.
3) Update one source script to write:
   - dataset JSON/JSONL
   - run_manifest.json
   - validation_report.json
4) Add unit tests (or a minimal validator test) ensuring schema correctness.

Acceptance criteria:
- CI fails if manifest/report missing.
- Existing scripts keep working.

Output:
- Provide a summary of files changed and commands run.
```

### Claude Code (Reviewer) — Script
```text
You are the adversarial reviewer. Review the PR diff for PE1 (Data Contract + Run Manifest).

Check for:
- Backward compatibility: no removal/renaming of existing output fields.
- Manifest completeness: commit SHA, config hash, run_id, counts, timestamps.
- Validation gating: CI should fail if manifest/report missing.
- Security: no secrets in logs, no tokens written to artefacts.

Deliver:
- 8–12 bullet findings, each with severity (Critical/High/Med/Low) and a concrete fix suggestion.
- Call out any silent data loss or schema mismatch risks.
```

---

## PE2 — Source Adapter Layer + HTTP client

### Codex — Script
```text
Objective: create a shared SourceAdapter interface and a shared HTTP client module (retry/backoff/jitter, rate limiting, structured logs). Convert ONE source to use it.

Constraints:
- Minimal behaviour change; compare old vs new outputs.
- Retry only on 429 and transient 5xx; do not retry on other 4xx.
- Rate limits must be configurable.

Tasks:
1) Implement elis/sources/base.py (SourceAdapter: preflight, harvest, normalise).
2) Implement elis/sources/http.py (timeouts, retries, backoff+jitter, 429 handling).
3) Convert one source integration to use the adapter.
4) Add tests using fixtures/mocking.

Acceptance:
- preflight returns deterministic OK/FAIL and a reason.
- logs are structured and do not include secrets.
```

### Claude Code — Script
```text
Review PE2 diff.

Focus on:
- Correct retry policy and backoff behaviour.
- Timeouts configured.
- Rate limiting implemented per source.
- No sensitive data leakage in logs or error dumps.

Deliver:
- Findings with severity + suggested patches.
```

---

## PE3 — Merge + Normalise Pipeline Stage

### Codex — Script
```text
Objective: implement a canonical merge + normalise pipeline stage producing one canonical dataset from multiple sources.

Tasks:
1) Create elis/pipeline/merge.py to merge N JSONL/JSON inputs.
2) Create elis/pipeline/normalise.py to normalise fields (title, DOI, authors, year, venue).
3) Ensure provenance is preserved per record.
4) Add merge_report.json with counts per source and invalid/dropped counts.
5) Add tests with fixtures and ensure deterministic ordering.

Acceptance:
- Same input order -> same output order and stable IDs.
- Schema validation passes.
```

### Claude Code — Script
```text
Review PE3 diff.

Check:
- Deterministic output ordering.
- Provenance retained and not collapsed incorrectly.
- Null handling and no silent data loss.
- Performance: streaming merge vs loading everything into memory.

Deliver: findings with severity + concrete fixes.
```

---

## PE4 — Dedup engine + cluster IDs + reports

### Codex — Script
```text
Objective: implement deterministic dedup with transparent policy and reports.

Dedup policy:
1) If DOI exists -> doi_normalised key.
2) Else -> normalised_title + year + first_author.
3) Optional fuzzy matching must be documented and thresholded.

Tasks:
1) Implement elis/pipeline/dedup.py streaming over JSONL.
2) Add cluster_id and cluster_members.
3) Emit dedup_report.json and collisions outputs.
4) Add unit tests for DOI and non-DOI duplicates.

Acceptance:
- Deterministic cluster IDs.
- Report includes counts and top collisions.
```

### Claude Code — Script
```text
Review PE4 diff.

Focus on:
- False positives in fuzzy matching.
- Explainability of cluster formation.
- Performance and memory behaviour.
- Reporting clarity and reproducibility.

Deliver: findings with severity + fixes.
```

---

## PE5 — Agentic layer (screening/extraction) with auditability

### Codex — Script
```text
Objective: add an agentic screening (and optionally extraction) layer WITHOUT overwriting canonical rows.

Rules:
- Append-only outputs: screening_decisions.jsonl.
- Every decision must include: model_id, prompt_hash, run_id, timestamps, evidence spans.
- Store run artefacts under runs/agentic/<run_id>/.

Tasks:
1) Implement elis/agentic/screening.py:
   - reads canonical dataset
   - outputs decisions JSONL (include/exclude/uncertain + rationale)
   - writes agentic_manifest.json
2) Create prompts/ registry with versioning and hashing.
3) Add a workflow_dispatch “agentic preflight” that runs on a tiny fixture dataset.

Acceptance:
- No hallucinated citations; evidence spans must be from the record text.
- Outputs are reviewable and reversible.
```

### Claude Code — Script
```text
Review PE5 diff.

Check:
- Evidence spans are actual substrings from the row text.
- Prompt versioning + hashing present.
- Tool usage is strict: no arbitrary shell execution unless explicitly allowed.
- Artefact structure is consistent and complete.

Deliver: findings with severity + concrete fixes.
```

---

## Reference links

```text
OpenAI Agents SDK:
https://platform.openai.com/docs/guides/agents-sdk

OpenAI Function Calling / Structured Outputs:
https://help.openai.com/en/articles/8555517-function-calling-in-the-openai-api

GitHub Actions token permissions guidance:
https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-guides/automatic-token-authentication
```
