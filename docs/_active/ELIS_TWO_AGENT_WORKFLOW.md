# ELIS SLR Agent v2.0 — Two‑Agent Workflow (Codex × Claude Code)

This document defines the **standard operating workflow** for developing ELIS SLR Agent v2.0 with two AI coding agents (Codex and Claude Code) working as an **asynchronous engineering pair**.

It complements:
- `docs/_active/RELEASE_PLAN_v2.0.md` (authoritative scope + acceptance criteria)
- `AGENTS.md` (rules, conventions, and guardrails)

---

## 1. Purpose

Deliver v2.0 via a **single canonical pipeline** with:
- deterministic, reproducible run artefacts;
- audit-ready outputs for each stage;
- optional agentic augmentation (e.g., ASTA) as **append-only sidecars**.

The workflow is built to:
- make handoffs explicit;
- minimise merge conflicts;
- ensure every change is validated against acceptance criteria;
- allow either agent to pause/resume without losing context.

---

## 2. Roles and responsibilities

Each work unit follows **Implement → Validate** rotation.

### 2.1 Implementer (DEV)
The Implementer:
1. builds the change within scope;
2. adds unit tests;
3. runs required checks locally;
4. documents the change and verification steps in `HANDOFF.md`;
5. requests review via a review request file in `reports/agent_activity/queue/`.

### 2.2 Validator (REVIEW)
The Validator:
1. reads `HANDOFF.md` and all changed files;
2. executes acceptance criteria **verbatim** (from the Release Plan);
3. adds adversarial tests (edge cases + determinism checks);
4. runs required checks locally;
5. produces `REVIEW.md` with a clear verdict;
6. approves or requests changes and updates the review request file.

---

## 3. Artefacts and where they live

### 3.1 Authoritative plan
- `docs/_active/RELEASE_PLAN_v2.0.md`

### 3.2 Branch-local handoff artefacts (per PR)
These are created at the **repo root** on the feature branch:
- `HANDOFF.md` (written by Implementer)
- `REVIEW.md` (written by Validator)

These files travel with the PR branch and serve as durable, PR-specific context.

### 3.3 Asynchronous coordination artefacts (repo persistent)
Use the following structure:

```
reports/agent_activity/
  queue/        # open review requests
  done/         # completed requests (moved here after merge)
  templates/    # templates (optional)
```

---

## 4. Work unit granularity

To keep reviews fast and reliable:
- PE0, PE3, PE4, PE6 can be PE-sized PRs (or split if large).
- PE2 MUST be split: **one adapter per PR** (one source = one PR).
- PE6 may be split by concerns (workflows vs docs vs script archival).

Rule: a work unit should be reviewable by the Validator in ~30 minutes.

---

## 5. Naming conventions

### 5.1 Feature branches
Base branch: `release/2.0`

Examples:
- `feature/pe0a-package-skeleton`
- `feature/pe2-openalex-adapter`
- `feature/pe3-merge-pipeline`
- `feature/pe6-cutover-workflows`

### 5.2 Review request files (global queue) — include timestamp
**Yes**, include a timestamp to avoid collisions and allow natural ordering.

Format:
- `RQ-YYYYMMDD-HHMM-PE<id>-<topic>.md`

Examples:
- `RQ-20260213-0915-PE2-openalex-adapter.md`
- `RQ-20260214-1340-PE3-merge-pipeline.md`

### 5.3 Activity reports (optional) — prefer per work unit
To avoid merge conflicts, use **one file per unit**, not a single shared daily log.

Recommended format:
- `AR-YYYYMMDD-PE<id>-<topic>-<agent>.md`

Examples:
- `AR-20260213-PE2-openalex-claude.md`
- `AR-20260213-PE2-openalex-codex.md`

### 5.4 Handoff files — fixed names
Do **not** timestamp:
- `HANDOFF.md`
- `REVIEW.md`

They are branch-local, PR-scoped artefacts with fixed names for discoverability.

---

## 6. Review request lifecycle (state machine)

A review request moves through these states:

1. `READY_FOR_REVIEW` (Implementer finished; review requested)
2. `IN_REVIEW` (Validator started validation)
3. `CHANGES_REQUESTED` (Validator found issues; Implementer must respond)
4. `APPROVED` (Validator accepts)
5. `MERGED` (PR merged to `release/2.0`)
6. `DONE` (request moved to `reports/agent_activity/done/`)

Optional (recommended for critical path):
- `VERIFIED` (post-merge smoke check)

---

## 7. Step-by-step process

### 7.1 Implementer workflow (DEV)

1) **Create branch**
- Branch from `release/2.0`.

2) **Implement**
- Only within the PE/unit scope.
- Keep outputs deterministic and schema-valid.

3) **Add tests**
- Unit tests for new behaviour.
- If touching nondeterministic providers, use normalised set/hash comparisons where appropriate.

4) **Run checks**
Run from repo root:
- `ruff check .`
- `black --check .`
- `pytest -q`
Plus any PE-specific commands referenced by the Release Plan.

5) **Write `HANDOFF.md`**
Include:
- files changed (complete list);
- design decisions;
- known limitations;
- exact acceptance criteria to verify (copy from Release Plan);
- commands to reproduce validation.

6) **Open PR**
- Target: `release/2.0`
- One unit per PR (especially for PE2).

7) **Create review request file**
Create:
- `reports/agent_activity/queue/RQ-YYYYMMDD-HHMM-PE<id>-<topic>.md`
Set state to `READY_FOR_REVIEW` and include:
- branch name;
- PR link;
- files changed list;
- acceptance criteria to validate;
- quick validation commands.

---

### 7.2 Validator workflow (REVIEW)

1) **Pick next request**
- Select the oldest request in `queue/` with `READY_FOR_REVIEW`.

2) **Claim it**
- Edit the request file: set state to `IN_REVIEW`.

3) **Read**
- `HANDOFF.md`
- all changed files listed
- relevant acceptance criteria in `docs/_active/RELEASE_PLAN_v2.0.md`

4) **Run acceptance criteria (verbatim)**
- Execute each criterion and mark PASS/FAIL with notes.

5) **Add adversarial tests**
At minimum:
- empty input
- malformed input / missing fields
- boundary conditions
- determinism checks (ordering, IDs, hashes)

6) **Run checks**
- `ruff check .`
- `black --check .`
- `pytest -q`
Plus PE-specific validation steps.

7) **Write `REVIEW.md`**
Include:
- verdict: `PASS`, `PASS WITH CHANGES`, or `FAIL`
- acceptance criteria results
- adversarial tests added
- issues found (file:line)
- files modified by validator (respecting file ownership rules)

8) **Update request state**
- `APPROVED` or `CHANGES_REQUESTED`
- If changes requested: list required fixes precisely.

9) **Merge & archive**
If approved:
- merge PR to `release/2.0`
- update state to `MERGED`
- move request file from `queue/` → `done/`
- set state to `DONE`

---

## 8. File ownership and conflict avoidance

To prevent “two agents editing the same thing”:

- Each PR must list touched files in `HANDOFF.md`.
- The Validator may only:
  - modify files already listed in `HANDOFF.md` **and/or**
  - add new test files **and/or**
  - add `REVIEW.md`
- Avoid a single shared log file. Prefer one request file per unit and one activity report per unit.

---

## 9. Worked example (PE2 OpenAlex adapter)

### Implementer (Claude Code)
- Creates `feature/pe2-openalex-adapter`
- Implements adapter + unit tests
- Writes `HANDOFF.md`
- Opens PR to `release/2.0`
- Creates `reports/agent_activity/queue/RQ-20260213-0915-PE2-openalex-adapter.md` with `READY_FOR_REVIEW`

### Validator (Codex)
- Changes state to `IN_REVIEW`
- Runs acceptance criteria and breaks edge cases
- Adds adversarial tests
- Writes `REVIEW.md` with verdict
- Sets state to `APPROVED` (or `CHANGES_REQUESTED`)
- If approved: merges PR and moves request file to `done/`

---

## 10. Recommended “start of session” instruction snippet

Give each agent, at session start:

- Role: `IMPLEMENTER` or `VALIDATOR`
- Unit: `PE<id> <topic>`
- Branch: `feature/...`
- Read-first list:
  1) `docs/_active/RELEASE_PLAN_v2.0.md`
  2) `AGENTS.md`
  3) `HANDOFF.md` (if validating)

Rules reminder:
- Run ruff/black/pytest before handoff.
- Keep outputs deterministic.
- Acceptance criteria are the contract.

---

## 11. Adoption checklist

- [ ] Add this document to `docs/_active/`
- [ ] Create `reports/agent_activity/{queue,done,templates}/`
- [ ] Use review request files for the next two PRs
- [ ] Iterate only if friction appears (do not over-process early)
