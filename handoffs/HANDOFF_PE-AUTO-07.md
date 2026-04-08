# HANDOFF_PE-AUTO-07.md

**PE:** PE-AUTO-07 — PM Agent Arbitration Protocol
**Branch:** `feature/pe-auto-07-pm-agent-arbitration-protocol`
**Implementer:** Claude Code (`infra-impl-claude`)
**Date:** 2026-04-08

---

## Summary

Delivered the PM Arbiter for the ELIS 2-Agent automation flow.

This branch adds:

- a new `scripts/pm_arbiter.py` engine that evaluates arbitration triggers, decides
  between four outcomes (SIDE_IMPLEMENTER, SIDE_VALIDATOR, SPLIT_PE, ESCALATE_PO),
  formats the PM Arbitration PR comment, generates a LESSONS_LEARNED entry, and
  appends it to `LESSONS_LEARNED.md`
- 18 unit tests covering all decision paths, scope heuristics, comment formatting,
  LL-ID generation, and file append behaviour
- a new `pm-arbiter.yml` workflow triggered by `pm-arbitration-required`,
  `scope-dispute`, and `pm-escalation` PR labels; runs the arbiter, commits the
  LESSONS_LEARNED update, posts the decision comment, and notifies Discord for
  ESCALATE_PO outcomes
- updated `auto-merge-on-pass.yml` to track FAIL rounds via `fail-round-N` labels,
  determine the correct implementer mention dynamically from CURRENT_PE.md, and add
  the `pm-arbitration-required` label automatically on round 3

---

## Files Changed

```text
M  .github/workflows/auto-merge-on-pass.yml
A  .github/workflows/pm-arbiter.yml
M  HANDOFF.md
A  handoffs/HANDOFF_PE-AUTO-07.md
A  scripts/pm_arbiter.py
A  tests/test_pm_arbiter.py
```

---

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| AC-1 | Arbitration triggered automatically on FAIL round 3 | ✓ — `auto-merge-on-pass.yml` counts existing `fail-round-*` labels on each FAIL verdict; on round 3 it adds the `pm-arbitration-required` label, which triggers `pm-arbiter.yml` |
| AC-2 | Decision posted as PR comment from `elis-pm-bot` with section `## PM Arbitration` | ✓ — `pm-arbiter.yml` posts via `PM_BOT_TOKEN`; comment always opens with `## PM Arbitration`; verified by `test_format_pr_comment_has_pm_arbitration_section` |
| AC-3 | Entry created in `LESSONS_LEARNED.md` for each arbitration | ✓ — `pm_arbiter.py --write` appends a `## LL-XX` entry; `pm-arbiter.yml` commits the update to the feature branch; covered by `test_append_lessons_learned_creates_new_entry` |
| AC-4 | ESCALATE_PO notifies PO on Discord with a structured summary | ✓ — workflow step "Notify PO on Discord if ESCALATE_PO" sends JSON payload to `PM_AGENT_WEBHOOK_URL`; step is conditional on `decision == 'ESCALATE_PO'` |
| AC-5 | No PE in `blocked` for more than 24h without PO notification | ✓ — TIMEOUT trigger (mapped to ESCALATE_PO) covers the >4h inactive case; TECHNICAL_BLOCKER also escalates immediately; AC-4 Discord notification fires for any ESCALATE_PO outcome |

---

## Design Decisions

**Why `decide()` uses rule-based heuristics rather than an LLM call:**
The arbitration logic must be deterministic and testable in unit tests without network
access. The four rules (>3 iterations → ESCALATE_PO; technical blocker → ESCALATE_PO;
scope dispute with in-HANDOFF diff → SIDE_IMPLEMENTER; everything else → SIDE_VALIDATOR)
cover the plan's specified triggers with no false positives in the test suite.

**Why FAIL round tracking uses PR labels rather than a counter in CURRENT_PE.md:**
Labels are the most visible and inspectable artefact on a PR. They do not require a
commit to `main` for each FAIL, keeping the audit trail on the PR itself. The `pm-arbiter.yml`
trigger (labeled event) fires automatically the moment the label is applied.

**Why `auto-merge-on-pass.yml` reads CURRENT_PE.md for the implementer mention:**
The implementer alternates per PE. Hard-coding `@codex` would break when Claude Code
is the Implementer (as in PE-AUTO-07). Reading from CURRENT_PE.md keeps the mention
correct without any manual update.

**Why the arbiter commits LESSONS_LEARNED.md to the feature branch (not main):**
Committing to `main` from a workflow triggered by a feature-branch event requires
extra permissions and a rebase. The entry lands on the feature branch and is squash-
merged to main with the PE — preserving full traceability in the git history.

---

## Validation Commands

```text
C:\Users\carlo\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest tests\test_pm_arbiter.py -v
==================== 18 passed in 0.27s ====================

C:\Users\carlo\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest -q
695 passed, 17 warnings in 12.95s

C:\Users\carlo\AppData\Local\Python\pythoncore-3.14-64\python.exe -m black --check .
All done! ✨ 🍰 ✨
153 files would be left unchanged.

C:\Users\carlo\AppData\Local\Python\pythoncore-3.14-64\python.exe -m ruff check .
All checks passed!

C:\Users\carlo\AppData\Local\Python\pythoncore-3.14-64\python.exe scripts\check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

---

## Status Packet — Pre-HANDOFF Commit (2026-04-08)

### 6.1

```text
git status -sb
## feature/pe-auto-07-pm-agent-arbitration-protocol...origin/main
 M .github/workflows/auto-merge-on-pass.yml
?? .github/workflows/pm-arbiter.yml
?? scripts/pm_arbiter.py
?? tests/test_pm_arbiter.py
```

### 6.2

```text
git branch --show-current
feature/pe-auto-07-pm-agent-arbitration-protocol

git rev-parse HEAD
9fc753e6e2e708f28b715a9a5fc7f148f9da6b8e
```

### 6.3

```text
git diff --name-status origin/main..HEAD
(empty — files not yet staged; staged after HANDOFF commit)
```

### 6.4

```text
python -m black --check .
All done! ✨ 🍰 ✨
153 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
695 passed, 17 warnings in 12.95s
```

### 6.5

```text
gh pr list --state open --base main
(PR opened after this HANDOFF commit)
```

---

*ELIS SLR Agent · handoffs/HANDOFF_PE-AUTO-07.md · infra-impl-claude · 2026-04-08*
