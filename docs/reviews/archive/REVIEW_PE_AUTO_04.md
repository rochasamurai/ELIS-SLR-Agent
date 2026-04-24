# REVIEW_PE_AUTO_04.md

**PE:** PE-AUTO-04 — Implementer Agent Runner
**PR:** #311
**Validator:** Claude Code (`infra-val-claude`)
**Date:** 2026-04-03

---

### Verdict

PASS

---

### Gate results

```
CI — all checks green on latest SHA:
  black (quality job)         PASS
  ruff (quality job)          PASS
  pytest (tests job)          PASS  — 636 passed, 17 warnings (CI)
  validate                    PASS
  quality                     PASS
  current-pe-check            PASS
  secrets-scope-check         PASS
  review-evidence-check       PASS
  openclaw-* checks           PASS (5/5)
```

---

### Scope

```
A  .github/workflows/ci-current-pe.yml
A  .github/workflows/implementer-runner.yml
M  HANDOFF.md
A  handoffs/HANDOFF_PE-AUTO-04.md
A  scripts/dispatch_implementer_runner.py
A  scripts/implementer_runner_common.py
A  scripts/run_claude_agent.py
A  scripts/run_codex_agent.py
A  tests/test_dispatch_implementer_runner.py
A  tests/test_implementer_runner_common.py
```

All files are within PE-AUTO-04 scope. No unrelated changes.

---

### Required fixes

None.

---

### Evidence

**AC-1 — Runner fires on `implementing` status:**
`ci-current-pe.yml` triggers on push to `main` paths `CURRENT_PE.md`.
`dispatch_implementer_runner.py` sets `should_dispatch=true` when registry
status is `implementing` and dispatches `implementer-runner.yml` with all
required inputs. Tested: `test_dispatches_when_active_pe_is_implementing`,
`test_skips_when_active_pe_not_implementing`.

**AC-2 — Auth via secrets only, never hardcoded:**
`implementer-runner.yml` injects `OPENAI_API_KEY` / `CLAUDE_SETUP_TOKEN`
through `env:` blocks. `verify_codex_auth.py` / `verify_claude_auth.py`
run before the agent. No token literals in any committed file.

**AC-3 — PR opened by correct account:**
Workflow configures `git config user.name` as `elis-codex-bot` /
`elis-claude-bot`. `ensure_expected_login(engine)` in `run_implementer()`
calls `gh api user` and raises `RunnerError` on identity mismatch.
Checkout uses `CODEX_BOT_TOKEN` / `CLAUDE_BOT_TOKEN` respectively.
Tested: `test_expected_login_guard_detects_wrong_identity`.

**AC-4 — HANDOFF.md committed before PR ready:**
`mark_pr_ready()` calls `last_commit_touches("HANDOFF.md")` and raises
`RunnerError` if false, blocking `gh pr ready`.
Tested: `test_last_commit_touches_returns_true/false`.

**AC-5 — Exits 1 on MAX_COMMITS or timeout:**
`ensure_budget()` raises `RunnerError` when commit count > `MAX_COMMITS`
or elapsed > `timeout_seconds`. `run_implementer()` catches all
`RunnerError` and returns `1`.
Tested: `test_budget_guard_fails_when_commit_limit_exceeded`,
`test_budget_guard_fails_when_timeout_exceeded`.

**HANDOFF:**
```
python scripts/check_handoff.py
HANDOFF OK (handoffs\HANDOFF_PE-AUTO-04.md) — all required sections present.
```

**Non-blocking observation:**
`ci-current-pe.yml` uses `secrets.PM_BOT_TOKEN` to trigger
`implementer-runner.yml` via `workflow_dispatch`. This secret was not in
the PE-AUTO-01 provisioned set. PM must add `PM_BOT_TOKEN` to repo secrets
before the dispatcher can fire autonomously. No code change required.

---

*ELIS SLR Agent · REVIEW_PE_AUTO_04.md · infra-val-claude · 2026-04-03*
