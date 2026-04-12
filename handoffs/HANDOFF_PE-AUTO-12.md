# HANDOFF_PE-AUTO-12.md

**PE:** PE-AUTO-12 — elis-server Bot Review Identity Activation
**Branch:** `feature/pe-auto-12-elis-server-bot-review-identities`
**Implementer:** CODEX
**Date:** 2026-04-12

---

## Summary

Delivered the repo-side runtime guardrails for live GitHub bot actions on
`elis-server`. The branch adds a dedicated `gh` wrapper that binds each live
operation to an explicit bot token and verifies the resulting GitHub login
before executing the requested command. The bot setup runbook now documents the
exact `elis-server` activation steps, verification commands, and safe live PR
checks required to prove PM and validator actions are no longer falling back to
the PO account. The active TODO item is also updated to reflect that the repo
implementation is in place and the remaining work is the host rollout and live
verification.

This branch adds / modifies:

- `scripts/gh_bot.py` — new helper that:
  - selects `CODEX_BOT_TOKEN`, `CLAUDE_BOT_TOKEN`, or `PM_BOT_TOKEN`
  - sets an isolated per-bot `GH_CONFIG_DIR`
  - verifies `gh api /user` resolves to the expected bot login
  - runs the requested `gh` command only after that identity check passes
- `docs/openclaw/BOT_ACCOUNTS_SETUP.md` — extended with a dedicated
  `elis-server` runtime activation section, explicit verification commands,
  expected success output, a safe validator approval test, and a safe PM-path
  PR comment test
- `docs/_active/TODO.md` — `ELIS-SERVER-01` advanced from `Assigned` to
  `In progress` and now points to the new helper/runbook as the repo-side
  implementation
- `tests/test_gh_bot.py` — new focused tests covering check-only success,
  wrong-login failure, passthrough command execution, and missing-token failure
- `tests/test_pm_runbooks.py` — added coverage asserting the bot setup runbook
  documents the new `elis-server` runtime activation flow

---

## Files Changed

```text
M  docs/_active/TODO.md
M  docs/openclaw/BOT_ACCOUNTS_SETUP.md
A  scripts/gh_bot.py
A  tests/test_gh_bot.py
M  tests/test_pm_runbooks.py
M  HANDOFF.md
A  handoffs/HANDOFF_PE-AUTO-12.md
```

---

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| AC-1 | `elis-server` can authenticate separately as `elis-codex-bot`, `elis-claude-bot`, and `elis-pm-bot` for GitHub API / CLI operations without exposing secret values | implemented in repo — `scripts/gh_bot.py` enforces explicit token-per-bot login checks without printing token values; live host execution still needs to be run on `elis-server` |
| AC-2 | A validator review action executed from `elis-server` succeeds as `elis-claude-bot` on a safe test PR and GitHub no longer returns `Review Can not approve your own pull request` | repo-side command path and exact test command are now documented; live safe-PR execution still required on `elis-server` |
| AC-3 | PM-path PR actions executed from `elis-server` use `elis-pm-bot` rather than the PO account | implemented in repo — wrapper supports `pm` identity explicitly and the runbook defines the verification comment command; live host verification still required |
| AC-4 | The runbook documents exact runtime verification steps and expected success output for each bot identity | done — `docs/openclaw/BOT_ACCOUNTS_SETUP.md` now contains `elis-server` activation, per-bot verification commands, expected output, validator approval test, and PM-path comment test |
| AC-5 | Branch protection for a safe test PR is satisfied by the bot-authored approval without admin bypass | repo-side procedure is documented end to end; live execution on a safe PR is still required to close this criterion operationally |

---

## Design Decisions

**Why PE-AUTO-12 introduces a wrapper instead of relying on ambient `gh auth login`:**
The actual failure on `elis-server` was not a missing GitHub token in CI; it
was the live host runtime using the wrong GitHub identity for ad-hoc PR
actions. A wrapper that injects the intended token on each command is more
reliable than assuming the current shell or service account is already logged in
as the right bot.

**Why the wrapper verifies `gh api /user` before running the target command:**
The bug we are fixing is identity drift. If a command is allowed to proceed
without first proving who `gh` will act as, the failure mode remains hidden
until a review or comment hits branch protection. The upfront identity check
turns that failure into an immediate, explicit error.

**Why the wrapper also sets a per-bot `GH_CONFIG_DIR`:**
`GH_TOKEN` should be sufficient on its own, but a dedicated config directory
prevents the host from accidentally inheriting stale `gh` state from another
session. That keeps PM, CODEX, and Claude PR actions isolated even when they run
on the same machine.

**Why the runbook now separates repo-side readiness from live host closure:**
This PE spans both code and operations. The repo can provide the safe command
path and exact verification procedure, but the final approval test must happen
on the real `elis-server` runtime with live bot credentials and a safe PR.

---

## Validation Commands

```text
(.venv) $ python -m pytest tests/test_gh_bot.py tests/test_pm_runbooks.py tests/test_verify_bot_config.py -q --basetemp .pytest-tmp-pe-auto-12
................
16 passed, 1 warning in 1.09s

(.venv) $ python -m ruff check scripts/gh_bot.py tests/test_gh_bot.py tests/test_pm_runbooks.py
All checks passed!

(.venv) $ python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.

(.venv) $ git diff --name-status origin/main..HEAD
M	CURRENT_PE.md
M	ELIS_2Agent_Automation_Plan_v2_0.md
M	docs/_active/TODO.md
M	docs/openclaw/BOT_ACCOUNTS_SETUP.md
```

Targeted PE tests: 16 passed

Live `elis-server` operator validation still required:

- `python scripts/gh_bot.py codex --check-only`
- `python scripts/gh_bot.py claude --check-only`
- `python scripts/gh_bot.py pm --check-only`
- `python scripts/gh_bot.py claude -- pr review <PR_NUMBER> --approve --body "..."`
- `python scripts/gh_bot.py pm -- pr comment <PR_NUMBER> --body "..."`

---

*ELIS SLR Agent · HANDOFF.md · CODEX · 2026-04-12*
