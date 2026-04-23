# PE-E2E-01 Dry Run Runbook

**Version:** 1.0
**Date:** 2026-04-23
**Scope:** End-to-end multi-agent drill against production repo using a disposable PE
**Prerequisite:** Read `docs/_active/E2E_MULTI_AGENT_TEST_PLAN.md` before executing

---

## Before You Start

Run the drill against a disposable feature branch (`feature/pe-e2e-01-smoke`), not
directly against a plan branch. This exercises real PM, implementer, validator, CI,
and auto-merge behaviour without risk to active PE work.

Two passes are required:

1. **Happy path** — green CI, PASS verdict, auto-merge fires
2. **Negative path** — broken formatting, CI blocks merge (TC-04.9)

---

## Phase 1 — Environment verification

### 1.1 — Pull latest and verify auth

```bash
cd /opt/elis/repo && git pull --ff-only origin main
gh auth status
python scripts/verify_codex_auth.py
python scripts/verify_claude_auth.py
python scripts/check_openclaw_health.py
python scripts/check_openclaw_doctor.py
```

### 1.2 — Confirm branch protection on main

```bash
gh api repos/rochasamurai/ELIS-Multi-AI-Agent-Platform/branches/main --jq '.protection.required_status_checks.checks[].context'
```

Expected output:

```
quality
tests
validate
current-pe-check
secrets-scope-check
review-evidence-check
slr-quality-check
```

All 7 checks must be present before proceeding.

---

## Phase 2 — Happy path

### 2.1 — Trigger implementer

```bash
gh workflow run "Implementer Agent Runner" -f pe_id=PE-E2E-01 -f branch=feature/pe-e2e-01-smoke -f engine=codex -f plan_file=docs/_active/E2E_MULTI_AGENT_TEST_PLAN.md -f base_branch=main
```

### 2.2 — Confirm implementer session on elis-server

```bash
gh run list --limit 5
openclaw sessions --agent codex
```

Wait until a session is active before continuing.

### 2.3 — Wait for PR and HANDOFF.md

```bash
gh pr list --state open
```

Agent1 must open the PR with `HANDOFF.md` committed before the PR is created
(LL-01). Confirm:

```bash
gh pr view <PR_NUMBER> --json headRefName,createdAt
git log --oneline origin/feature/pe-e2e-01-smoke | head -5
```

HANDOFF commit must predate the PR creation timestamp.

### 2.4 — Monitor CI

```bash
gh pr checks <PR_NUMBER>
```

Wait for all 7 required checks to go green before Gate 1.

### 2.5 — Gate 1: assign Validator

**Default path — PM direct dispatch:**

```bash
openclaw message send --agent codex --session agent:pm:main "PE-E2E-01 — assign validator: claude"
```

**Fallback path — PR comment (use if direct dispatch unavailable):**

```bash
gh pr comment <PR_NUMBER> --body "<!-- validator-assignment --> @elis-claude-bot — assigned as Validator for PE-E2E-01. Begin review."
```

### 2.6 — Confirm Validator session starts

```bash
gh run list --limit 5
openclaw sessions --agent claude
```

`validator-runner.yml` must start and Agent2 session must appear.

### 2.7 — Wait for verdict

```bash
gh pr view <PR_NUMBER> --json reviews,comments
```

Agent2 must:
- Commit `REVIEW_PE_E2E_01.md` on the feature branch
- Post a PR comment with verdict summary
- Submit a formal GitHub review (`approve` for PASS)

### 2.8 — Verify auto-merge

```bash
gh pr view <PR_NUMBER> --json mergeStateStatus,reviews
gh run list --workflow=auto-merge-on-pass.yml --limit 3
```

PASS + CI green + `mergeStateStatus == CLEAN` → `auto-merge-on-pass.yml` fires.
Merge commit author must be the mapped bot account (not PO).

### 2.9 — Verify PM housekeeping after merge

```bash
git pull --ff-only origin main
grep -A5 "## Current PE" CURRENT_PE.md
grep "PE-E2E-01" CURRENT_PE.md
```

PE-E2E-01 must show `merged`; next PE must be opened with roles alternated.

---

## Phase 3 — Negative path (TC-04.9)

### 3.1 — Trigger a second implementer run with a formatting violation

After Agent1 opens the PR in Phase 2 (or in a separate run), verify that a
`quality` failure blocks merge:

```bash
gh pr checks <PR_NUMBER>
gh pr view <PR_NUMBER> --json mergeStateStatus
```

To simulate: push a Python file with a black violation to the feature branch, then
confirm `mergeStateStatus` is `BLOCKED` and auto-merge does not fire.

### 3.2 — Confirm auto-merge is blocked

```bash
gh run list --workflow=auto-merge-on-pass.yml --limit 3
```

`auto-merge-on-pass.yml` must not appear as a successful run while CI is failing.

---

## Phase 4 — Evidence collection

Record the following for each pass:

```bash
# All workflow run URLs and statuses
gh run list --limit 20 --json url,name,status,conclusion

# PR URL and final state
gh pr view <PR_NUMBER> --json url,state,mergeStateStatus,mergedAt,mergedBy

# Final merge commit and author
git log -1 --format="%H %an %ae %s" origin/main

# CURRENT_PE.md diff after PM housekeeping
git diff HEAD~1 HEAD -- CURRENT_PE.md

# Session evidence
openclaw sessions --all-agents
```

---

## Pass Criteria

The drill is complete when:

| Check | Condition |
|-------|-----------|
| TC-03 | HANDOFF.md committed before PR creation timestamp |
| TC-04 | All 7 CI checks green on happy path |
| TC-04.9 | `mergeStateStatus == BLOCKED` when `quality` fails |
| TC-05 | Validator session started via Gate 1 (not self-started) |
| TC-06 | `REVIEW_PE_E2E_01.md` present; formal approval review submitted |
| TC-07 | Auto-merge fired on PASS + CI green; did not fire on failing CI |
| TC-07.5 | Merge commit author = mapped bot account |
| TC-08 | PM housekeeping updated `CURRENT_PE.md`; roles alternated |

---

*ELIS SLR Agent · docs/_active/E2E_DRILL_RUNBOOK.md · 2026-04-23*
