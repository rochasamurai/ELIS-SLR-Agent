# HANDOFF_PE-AUTO-04.md

**PE:** PE-AUTO-04 — Implementer Agent Runner
**Branch:** `feature/pe-auto-04-impl-runner`
**Implementer:** CODEX (`infra-impl-codex`)
**Date:** 2026-04-03

---

## Summary

Delivered the first autonomous implementer-runner path for the ELIS 2-Agent
Automation Plan.

This branch adds:

- a dispatcher workflow triggered by `CURRENT_PE.md` changes on `main`
- a dedicated implementer-runner workflow for Codex / Claude engines
- shared runner logic to read `CURRENT_PE.md`, resolve acceptance criteria,
  build the implementer prompt, enforce GitHub bot identity, enforce commit/time
  budgets, and refuse `gh pr ready` unless `HANDOFF.md` is in the last commit
- thin entrypoint scripts for Codex and Claude
- unit tests for dispatcher resolution and runner guard behaviour

The runner prompt is aligned with the PE-AUTO-03 HANDOFF namespacing model:
future autonomous implementers are instructed to update
`handoffs/HANDOFF_{PE_ID}.md`, regenerate the root `HANDOFF.md` via
`python scripts/copy_handoff.py`, and only then convert the PR to ready.

---

## Files Changed

```text
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

---

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| AC-1 | Runner fires upon detecting a change in `CURRENT_PE.md` with status `implementing` | ✓ — `ci-current-pe.yml` triggers on `CURRENT_PE.md` pushes to `main`; `dispatch_implementer_runner.py` resolves `should_dispatch=true` for `implementing` state in targeted tests |
| AC-2 | Auth via `OPENAI_API_KEY` (Codex) / `CLAUDE_SETUP_TOKEN` (Claude) — injected from GitHub Secrets, never hardcoded | ✓ — workflow injects secrets via `env:` only; no token literals are committed |
| AC-3 | PR opened by the correct account (`elis-codex-bot` or `elis-claude-bot`) | ✓ — runner workflow checks out and runs with engine-specific bot tokens, and `ensure_expected_login()` hard-fails on identity mismatch |
| AC-4 | `HANDOFF.md` committed before the PR is converted to ready | ✓ — `mark_pr_ready()` refuses to proceed unless `HANDOFF.md` appears in the last commit |
| AC-5 | Runner exits with exit 1 if `MAX_COMMITS` or timeout are reached | ✓ — budget and timeout guards implemented and covered by unit tests |

---

## Design Decisions

**Why a shared runner module:**
The Codex and Claude entrypoints differ only by engine selection. The main
behaviour lives in `scripts/implementer_runner_common.py` so the identity,
prompt-construction, budget, PR, and HANDOFF rules stay consistent.

**Why the dispatcher is separate from the runner workflow:**
`ci-current-pe.yml` performs a small, deterministic resolution step and only
dispatches the implementer workflow when the active PE status is
`implementing`. This keeps trigger logic auditable and unit-testable.

**Why the runner prompt references `copy_handoff.py`:**
PE-AUTO-03 established the canonical HANDOFF model: namespaced file in
`handoffs/`, root `HANDOFF.md` as a generated copy. The implementer runner now
nudges future autonomous runs toward that contract instead of the old
single-root-only pattern.

**Why `runner_started_at()` accepts malformed/missing input safely:**
The first workflow draft passed an ISO timestamp into a float parser. The final
runner accepts epoch seconds, ISO-8601 timestamps, or no value at all, falling
back safely to the current time.

---

## Validation Commands

```text
git diff --name-status origin/main..HEAD
A	.github/workflows/ci-current-pe.yml
A	.github/workflows/implementer-runner.yml
A	scripts/dispatch_implementer_runner.py
A	scripts/implementer_runner_common.py
A	scripts/run_claude_agent.py
A	scripts/run_codex_agent.py
A	tests/test_dispatch_implementer_runner.py
A	tests/test_implementer_runner_common.py

& 'C:\Program Files\LibreOffice\program\python.exe' scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.

& 'c:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\ruff.exe' check .
All checks passed!
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)

Black library fallback check on changed files
black-equivalent check: PASS

$env:PYTHONPATH='c:\Users\carlo\ELIS-SLR-Agent\.venv\Lib\site-packages'; $env:PYTEST_DEBUG_TEMPROOT='c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-auto-04\tests'; & 'C:\Program Files\LibreOffice\program\python.exe' -m pytest tests/test_dispatch_implementer_runner.py tests/test_implementer_runner_common.py -q -p no:cacheprovider
.............                                                            [100%]
```

**Local environment note:**
The canonical local `python -m pytest -q` gate could not be reproduced on this
host because the repo `.venv` launcher points to a removed Python 3.14 runtime,
while the fallback LibreOffice Python 3.11 interpreter cannot import some
compiled dependencies from that venv (`rpds.rpds`). The full suite remains a CI
validator responsibility for this PE; targeted runner tests were executed
successfully.

---

*ELIS SLR Agent · handoffs/HANDOFF_PE-AUTO-04.md · infra-impl-codex · 2026-04-03*
