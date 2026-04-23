# ELIS End-to-End Multi-Agent Process — Test Plan

**Version:** 1.0
**Date:** 2026-04-22
**Author:** PM / Claude Code
**Scope:** Full PE lifecycle from plan ingestion to auto-merge and PM housekeeping

---

## 1) Process Description

| Step | Actor | Action |
|------|-------|--------|
| 1 | PO | Delivers a new plan document to ELIS PM via Discord (`/plan load` or direct message) |
| 2 | PM | Reads the plan, opens the first PE in `CURRENT_PE.md`, commits to `main`, notifies Implementer |
| 3 | GitHub Actions | `implementer-runner.yml` dispatches Agent1 (Implementer) session on elis-server |
| 4 | Agent1 | Implements the PE on a feature branch; commits `HANDOFF.md`; pushes; opens PR |
| 5 | GitHub Actions | CI runs portable blocking gates: `black`, `ruff`, `pytest`, `current-pe-check`, `secrets-scope-check`, `review-evidence-check`, `slr-quality-check` |
| 6 | GitHub Actions | Gate 1: CI bot posts Validator assignment comment on the PR |
| 7 | GitHub Actions | `validator-runner.yml` dispatches Agent2 (Validator) session on elis-server |
| 8 | Agent2 | Reviews the PR; writes `REVIEW_PE_XX.md`; posts PR comment + formal GitHub review (PASS or FAIL) |
| 9 | GitHub Actions | `auto-merge-on-pass.yml` checks: PASS verdict + CI green + `mergeable_state == clean` → auto-merges PR |
| 10 | PM | Closes PE in `CURRENT_PE.md` (PM-CHORE), opens next PE; cycle repeats |

---

## 2) Test Cases

### TC-01 — Plan Ingestion

**Objective:** PM correctly reads a new plan and opens the first PE.

| # | Action | Expected Result |
|---|--------|-----------------|
| 1.1 | PO delivers plan file to PM via Discord | PM acknowledges receipt, confirms plan file path |
| 1.2 | PM commits updated `CURRENT_PE.md` to `main` | `Release`, `Plan file`, `PE`, `Branch`, and `Agent roles` fields all populated |
| 1.3 | Read `CURRENT_PE.md` on `main` | No blank fields; PE status = `implementing` |

---

### TC-02 — Implementer Dispatch

**Objective:** `implementer-runner.yml` correctly launches Agent1 on elis-server.

| # | Action | Expected Result |
|---|--------|-----------------|
| 2.1 | PM triggers `implementer-runner.yml` (manual dispatch or pe-sequencer) | GitHub Actions job starts without error |
| 2.2 | Agent1 session appears on elis-server | `openclaw sessions --agent <impl-id>` shows an active session |
| 2.3 | Agent1 reads `CURRENT_PE.md` (Step 0) | Session log confirms correct PE, base branch, and plan file |

---

### TC-03 — Implementation and PR

**Objective:** Agent1 delivers a valid, in-scope PR with `HANDOFF.md` committed before push.

| # | Action | Expected Result |
|---|--------|-----------------|
| 3.1 | Agent1 implements PE on feature branch | Branch exists on origin; all deliverables committed |
| 3.2 | `HANDOFF.md` committed before PR opened | `git log --oneline` shows HANDOFF commit predates PR creation timestamp |
| 3.3 | PR opened against correct base branch | PR base = `main`; title follows convention |
| 3.4 | `git diff --name-status origin/main..HEAD` | Only PE-scope files modified; no unrelated changes |

---

### TC-04 — CI Blocking Gates

**Objective:** All 7 required checks run and gate the PR correctly.

| # | Action | Expected Result |
|---|--------|-----------------|
| 4.1 | PR opened | CI triggers automatically |
| 4.2 | `quality` job | `black` and `ruff` pass |
| 4.3 | `tests` job | `pytest` passes (pre-existing failures documented in HANDOFF) |
| 4.4 | `validate` job | Schema/manifest validation passes |
| 4.5 | `current-pe-check` | PE metadata consistent with `CURRENT_PE.md` |
| 4.6 | `secrets-scope-check` | No secret-pattern files in worktree |
| 4.7 | `review-evidence-check` | REVIEW file present and well-formed (when applicable) |
| 4.8 | `slr-quality-check` | SLR quality gates pass |
| 4.9 | Intentionally break `black` | PR cannot merge; `mergeable_state ≠ clean` |

---

### TC-05 — Gate 1 and Validator Dispatch

**Objective:** Validator is assigned and dispatched without PM manual intervention.

| # | Action | Expected Result |
|---|--------|-----------------|
| 5.1 | CI green + PR open | CI bot posts Gate 1 assignment comment naming Agent2 as Validator |
| 5.2 | `validator-runner.yml` triggers | GitHub Actions job starts; Agent2 session appears on elis-server |
| 5.3 | Agent2 reads Step 0 without self-starting | Session log confirms assignment came from Gate 1 comment, not self-initiated |

---

### TC-06 — Validation and Verdict

**Objective:** Agent2 delivers a complete, correctly formatted verdict.

| # | Action | Expected Result |
|---|--------|-----------------|
| 6.1 | Agent2 reviews PR | `REVIEW_PE_XX.md` committed on feature branch |
| 6.2 | `check_review.py` passes | All required sections present; fenced code block in `### Evidence` |
| 6.3 | PR comment posted | Verdict summary and blocking findings (if any) visible on PR |
| 6.4 | Formal GitHub review submitted | `approve` for PASS; `request-changes` for FAIL |
| 6.5 | FAIL path: Agent2 posts FAIL | PR not auto-merged; Implementer receives required fixes |
| 6.6 | FAIL path: Agent1 fixes and re-pushes | CI re-runs; Validator re-validates |

---

### TC-07 — Gate 2 and Auto-Merge

**Objective:** `auto-merge-on-pass.yml` merges exactly when all conditions are met — and not before.

| # | Action | Expected Result |
|---|--------|-----------------|
| 7.1 | PASS verdict + CI green | `auto-merge-on-pass.yml` detects `mergeable_state == clean` and merges |
| 7.2 | PASS verdict + CI failing | Auto-merge does not fire; PR stays open |
| 7.3 | CI green + no PASS verdict | Auto-merge does not fire |
| 7.4 | `pm-review-required` label present | Auto-merge blocked regardless of verdict or CI state |
| 7.5 | Merge committed by correct bot identity | Merge commit author = mapped bot account (not PO) |

---

### TC-08 — PM Housekeeping and Cycle Continuity

**Objective:** PM closes the PE and opens the next one without manual PO intervention.

| # | Action | Expected Result |
|---|--------|-----------------|
| 8.1 | PR merged | PM-CHORE branch created; `CURRENT_PE.md` updated (merged status, next PE opened) |
| 8.2 | `CURRENT_PE.md` on `main` after chore | Previous PE = `merged`; new PE = `implementing`; roles alternated |
| 8.3 | Alternation rule | Implementer and Validator roles swapped from previous PE in same domain |
| 8.4 | Next `implementer-runner.yml` dispatch | New Implementer session starts without PO action |

---

### TC-09 — Failure and Escalation Paths

**Objective:** Exceptional conditions are handled without silent failure.

| # | Condition | Expected Result |
|---|-----------|-----------------|
| 9.1 | Agent session fails to start on elis-server | PM escalates to PO via Discord |
| 9.2 | >2 FAIL iterations on same PE | PM escalates to PO per AGENTS.md §2.10 |
| 9.3 | CI `pm-escalation` flag set | PM notifies PO before proceeding |
| 9.4 | `CURRENT_PE.md` missing or blank field | Both agents stop and notify PM/PO |
| 9.5 | Branch protection blocks merge | `mergeable_state ≠ clean`; PR stays open; no silent bypass |

---

## 3) Pass Criteria

The end-to-end process is considered validated when:

- TC-01 through TC-08 happy-path cases all produce the expected results
- TC-04.9 (broken gate) and TC-07.2–7.4 (premature merge guards) all hold
- TC-09 escalation paths produce a PM Discord notification in each scenario
- No PO manual intervention required between Steps 3 and 10 (fully autonomous cycle)

---

*ELIS SLR Agent · docs/_active/E2E_MULTI_AGENT_TEST_PLAN.md · 2026-04-22*
