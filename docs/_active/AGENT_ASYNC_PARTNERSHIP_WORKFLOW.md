# ELIS v2.0 — Codex × Claude Code Async Partnership Workflow

This document defines an **asynchronous, two-agent development workflow** for ELIS SLR Agent v2.0, designed to work alongside:

- `docs/_active/RELEASE_PLAN_v2.0.md` (authoritative scope and acceptance criteria)
- `AGENTS.md` (multi-agent operating rules)

The goal is to make “who does what next” **explicit, auditable, and low-friction**, without relying on chat history.

---

## 1) Core principle: implement → validate rotation

For each work unit (PE or sub-task):

- **Implementer** writes code + tests + HANDOFF artefacts.
- **Validator** executes acceptance criteria + adds adversarial tests + attempts to break the change.
- The change only progresses when the Validator records a verdict.

This works because Codex and Claude Code tend to fail differently; validation is not passive review — it is **active falsification**.

---

## 2) Single source of truth

- **Scope / acceptance criteria:** `docs/_active/RELEASE_PLAN_v2.0.md`
- **Working rules:** `AGENTS.md`
- **State & handoffs (asynchronous):** lightweight files under `reports/agent_activity/`

Avoid using one shared “log file” that both agents append to (merge-conflict magnet). Use **one file per task** instead.

---

## 3) Work unit granularity

Use the following unit sizes:

- **PE-sized** units for PE0, PE3, PE4, PE6
- **Per-source PR** units for PE2 (one adapter per PR)
- **Per-script / per-workflow PR** units inside PE6 (if needed)

Each unit should be reviewable in < ~30 minutes for the Validator.

---

## 4) File-based asynchronous coordination

Create this structure in the repo:

```
reports/agent_activity/
  queue/                       # open review requests (Implementer creates)
  done/                        # completed requests (Validator moves)
  templates/
    ACTIVITY_REPORT_TEMPLATE.md
    REVIEW_REQUEST_TEMPLATE.md
```

### 4.1 Review request lifecycle (state machine)

A review request moves through these states:

1. **DRAFT** (optional): Implementer preparing
2. **READY_FOR_REVIEW**: Implementer has finished and requests validation
3. **IN_REVIEW**: Validator is actively validating
4. **CHANGES_REQUESTED**: Validator found issues; Implementer must respond
5. **APPROVED**: Validator accepts; PR can merge
6. **MERGED**: PR merged into `release/2.0`
7. **VERIFIED**: post-merge smoke check (optional, recommended for critical path)
8. **DONE**: request archived under `reports/agent_activity/done/`

---

## 5) Step-by-step workflow (dev × review)

### 5.1 Implementer steps (DEV)

1. Create branch from `release/2.0`:
   - `feature/<pe-id>-<short-desc>`
2. Implement only the scoped deliverables.
3. Add unit tests (minimum) + update docs if required by the plan.
4. Run required checks:
   - `ruff check .`
   - `black --check .`
   - `pytest -q`
5. Create `HANDOFF.md` at repo root (branch-local).
6. Open PR to `release/2.0`.
7. Create a review request file:
   - `reports/agent_activity/queue/RQ-<YYYYMMDD>-<HHMM>-<PE>-<topic>.md`
8. Set request state to `READY_FOR_REVIEW`.

### 5.2 Validator steps (REVIEW)

1. Pull the Implementer branch.
2. Open the review request file; change state to `IN_REVIEW`.
3. Read `HANDOFF.md`, then read **all changed files**.
4. Run acceptance criteria from the Release Plan (verbatim).
5. Add adversarial tests to cover:
   - malformed input
   - empty input
   - boundary conditions
   - determinism (ordering, IDs, hashes)
6. Run required checks:
   - `ruff check .`
   - `black --check .`
   - `pytest -q`
7. Write `REVIEW.md` at repo root.
8. Commit review artefacts (tests + REVIEW.md + any allowed fixes).
9. Set request state:
   - `APPROVED` or `CHANGES_REQUESTED`
10. If approved: merge PR, then move request file to `done/`.

---

## 6) Agent role assignment by PE

This table mirrors the recommended split (adjust as needed):

| PE / Unit | Implementer | Validator | Notes |
|---|---|---|---|
| PE0a Package skeleton | Codex | Claude Code | Validate editable install + CLI |
| PE0b MVP migration | Claude Code | Codex | Deep MVP script familiarity |
| PE1a Manifest schema (thin) | Codex | Claude Code | Schema & writer utility only |
| PE2 Adapters (per source) | Claude Code | Codex | One adapter per PR |
| PE3 Merge pipeline | Codex | Claude Code | Validator checks determinism |
| PE1b Manifest enforcement | Claude Code | Codex | Wire into stages + CI gating |
| PE4 Dedup | Codex | Claude Code | Validator checks cluster stability |
| PE5 ASTA integration | Claude Code | Codex | Sidecar-only outputs |
| PE6 Cut-over | Both (split) | Both | Workflows vs docs + archival |

---

## 7) Acceptance criteria discipline

- Every review request must list the **exact** acceptance criteria items it claims to satisfy.
- The Validator must mark each criterion PASS/FAIL with notes and commands executed.

If a criterion cannot be validated locally (e.g., missing API key), the Validator must record:
- what was validated
- what remains unvalidated
- what CI run is required to complete verification

---

## 8) Evaluation: strengths and risks

### Strengths
- Clear alternation reduces blind spots.
- File-based handoffs are auditable and survive chat loss.
- Per-task files minimise merge conflicts.

### Risks (and mitigations)
- **Merge conflicts in coordination files**: avoid shared append-only logs; use one file per request.
- **Validator becoming co-implementer**: allow only small, scoped fixes; prefer “changes requested”.
- **Flaky tests from nondeterministic sources**: use normalised set/hash comparisons and explicit tolerance policy.
- **Context drift**: force every unit to include HANDOFF/REVIEW artefacts and link to acceptance criteria.

---

## 9) Minimal adoption plan (do this first)

1. Add `AGENTS.md`.
2. Add the templates in `reports/agent_activity/templates/`.
3. For the next PE, use:
   - `HANDOFF.md`
   - `REVIEW.md`
   - `reports/agent_activity/queue/RQ-...md`

Once this works for two units, scale it across PE2 adapters.
