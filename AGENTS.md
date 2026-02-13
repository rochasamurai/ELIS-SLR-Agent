# Agent Development Guide (AGENTS.md)

This file defines the **multi-agent development protocol** for ELIS SLR Agent v2.0.
It is mandatory for all PEs on `release/2.0`.

---

## 0) Canonical references (read first)

Before doing any work, every agent MUST read:

1. `docs/_active/RELEASE_PLAN_v2.0.md` (authoritative plan + acceptance criteria)
2. `docs/_active/INTEGRATION_PLAN_V2.md` (integration context)
3. `docs/_active/HARVEST_TEST_PLAN.md` (harvest testing expectations)
4. The PE-specific `HANDOFF.md` (implementer) or `REVIEW.md` (validator) on the working branch

---

## 1) Roles

Each PE is executed as an **implement/validate rotation**.

### 1.1 Implementer responsibilities
- Implement the PE scope **only** (no opportunistic refactors).
- Add/adjust unit tests for the code they write.
- Run all required local checks before handoff.
- Produce `HANDOFF.md` (template tracked in repo or copied from guidance).

### 1.2 Validator responsibilities
- Read `HANDOFF.md` then read **all changed files**.
- Run acceptance criteria **verbatim** from the release plan.
- Add adversarial tests (edge cases, malformed input, empty input, ordering).
- Attempt to break determinism and schema compliance.
- Produce `REVIEW.md` with a clear verdict.

---

## 2) Non-negotiable rules

### 2.1 One canonical pipeline
- `runs/<run_id>/` is the **authoritative** artefact layout.
- `json_jsonl/` is a **backward-compatibility export view** of the latest run (copy-only).
- No alternate pipeline outputs or legacy modes may be introduced.

### 2.2 Determinism
All stage outputs must be deterministic:
- stable ordering where ordering is defined
- stable IDs / cluster IDs
- no timestamps in test assertions
- no randomness without fixed seeds (avoid by default)

### 2.3 Secrets and logging
- Never print secrets.
- Never commit secrets.
- Logs must be structured, minimal, and safe (no API keys, tokens, auth headers).

### 2.4 File ownership / conflict prevention
- The implementer owns the branch initially.
- The validator may only:
  - modify files already listed in `HANDOFF.md`, **and/or**
  - add new test files, **and/or**
  - add `REVIEW.md`
- No “drive-by” edits outside PE scope.

---

## 3) Branching and PR flow

### 3.1 Base branches
- Use `release/2.0` for all v2.0 work.
- Do not commit directly to `main` for v2.0 development work.

### 3.2 Branch naming
Use one of:
- `feature/pe0a-package-skeleton`
- `feature/pe0b-migrate-mvp`
- `feature/pe1a-manifest-schema`
- `feature/pe2-<source>-adapter` (one PR per source)
- `feature/pe3-merge`
- `feature/pe4-dedup`
- `feature/pe5-asta-integration`
- `feature/pe6-cutover`

### 3.3 Standard sequence per PE
1. Implementer creates branch from `release/2.0`
2. Implementer implements + tests + docs updates
3. Implementer runs required checks (see §4)
4. Implementer commits with conventional message
5. Implementer writes `HANDOFF.md`

--- handoff point ---

6. Validator pulls branch
7. Validator reads `HANDOFF.md` then reviews all changed files
8. Validator executes acceptance criteria from `docs/_active/RELEASE_PLAN_v2.0.md`
9. Validator adds adversarial tests
10. Validator runs full checks (see §4)
11. Validator writes `REVIEW.md`
12. Validator commits review artefacts (tests + `REVIEW.md`, and fixes only within ownership rules)
13. PR merges to `release/2.0`

---

## 4) Environment setup (local)

### 4.1 Python environment
From repo root:

```
bash
python -m venv .venv
# Windows PowerShell:
. .\\.venv\\Scripts\\Activate.ps1
pip install -U pip
pip install -e ".[dev]"
