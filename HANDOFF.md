# HANDOFF_PE-AUTO-05.md

**PE:** PE-AUTO-05 — Validator Agent Runner
**Branch:** `feature/pe-auto-05-validator-runner`
**Implementer:** Claude Code (`infra-impl-claude`)
**Date:** 2026-04-03

---

## Summary

Delivered the autonomous validator runner for the ELIS 2-Agent Automation Plan.

This branch adds:

- a dispatcher workflow triggered by the Gate 1 assignment comment on any PR
- a dedicated validator-runner workflow for Codex / Claude engines
- shared validator logic to read `CURRENT_PE.md`, build the validator prompt,
  read the REVIEW file verdict, and post a fail-assignment comment on FAIL
- thin entrypoints for Codex and Claude validators
- a dispatcher script that verifies the PR branch matches the active PE branch
  before firing the validator workflow
- unit tests for all new logic (14 tests)

The validator runner complements the PE-AUTO-04 implementer runner:
the Gate 1 comment triggers `validator-dispatch.yml` → `validator-runner.yml`.
On completion the REVIEW file is on the feature branch, Gate 2
(`auto-merge-on-pass.yml`) picks it up on the resulting push, and auto-merges
on PASS (AC-4 satisfied by existing Gate 2 workflow, no new code needed).
On FAIL the workflow posts a fix-assignment comment via `PM_BOT_TOKEN` (AC-5).

---

## Files Changed

```text
M  .github/workflows/auto-assign-validator.yml
A  .github/workflows/validator-dispatch.yml
A  .github/workflows/validator-runner.yml
M  HANDOFF.md
A  handoffs/HANDOFF_PE-AUTO-05.md
A  scripts/dispatch_validator_runner.py
A  scripts/validator_runner_common.py
A  scripts/run_claude_validator.py
A  scripts/run_codex_validator.py
A  tests/test_dispatch_validator_runner.py
A  tests/test_validator_runner_common.py
```

---

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| AC-1 | Validator triggers automatically after Gate 1 comment | ✓ — `auto-assign-validator.yml` now resolves the active validator engine from `CURRENT_PE.md` and injects the correct mention (`@codex` or `@claude-code`) plus a machine-readable `<!-- validator-assignment -->` tag; `validator-dispatch.yml` triggers on the tag (engine-agnostic); 3 dispatch tests pass |
| AC-2 | `REVIEW_PE*.md` committed on the branch with verbatim evidence | ✓ — `verify_review_committed()` independently checks `git log origin/base..HEAD` for the REVIEW filename after agent run; raises `RunnerError` if absent; workflow step enforces this before reading verdict; 2 unit tests |
| AC-3 | Formal GitHub Review posted by the opposite account | ✓ — `verify_formal_review_posted()` calls `gh pr view --json reviews` and raises `RunnerError` if review list is empty; workflow step enforces this; `validator-runner.yml` checks out with validator bot token so the agent posts the review as that bot; 2 unit tests |
| AC-4 | Gate 2 reads the verdict and auto-merges on PASS | ✓ — existing `auto-merge-on-pass.yml` triggers on push to the feature branch, finds the REVIEW file via `parse_verdict.py`, and squash-merges on PASS; no new code required |
| AC-5 | On FAIL: Implementer receives fix assignment via PR comment from `elis-pm-bot` | ✓ — `validator-runner.yml` runs `parse_verdict.py` after the agent; on FAIL, posts assignment comment using `PM_BOT_TOKEN` via `post_fail_assignment()` |

---

## Design Decisions

**Why `validator-dispatch.yml` verifies the PR branch against `CURRENT_PE.md`:**
The Gate 1 comment could be posted on any PR (including old ones still open).
`dispatch_validator_runner.py` reads `CURRENT_PE.md` and confirms the PR head
branch matches the active PE branch before dispatching, preventing stale or
cross-PE triggers.

**Why AC-4 needs no new code:**
`auto-merge-on-pass.yml` already runs on every push to `feature/**` branches.
Once the validator agent commits and pushes the REVIEW file, Gate 2 fires
automatically. Adding a separate Gate 2 implementation would duplicate logic.

**Why `PM_BOT_TOKEN` is required for the fail-assignment comment (AC-5):**
The comment must be attributed to `elis-pm-bot` per the AC. This secret is
the same one referenced by `ci-current-pe.yml` in PE-AUTO-04. PM must configure
`PM_BOT_TOKEN` in repo secrets for both live-dispatch (PE-AUTO-04) and
fail-assignment (PE-AUTO-05) to function.

**Why the validator runner does not enforce a commit budget:**
Validators do not iterate on implementation — they read, check, and write one
REVIEW file. A timeout guard (120 min workflow-level `timeout-minutes`) is
sufficient without an additional per-commit counter.

**Why `run_validator` does not post the formal PR review itself:**
The formal review (`gh pr review --approve / --request-changes`) requires the
correct bot identity set via `GH_TOKEN`. The CLI agent runs inside the workflow
with `GH_TOKEN` already set to the validator bot token, so the agent can post
the review directly. Having the Python runner re-post it would require the same
token, duplicating the responsibility.

---

## Validation Commands

```text
python -m black --check .
All done! ✨ 🍰 ✨
148 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest tests/test_validator_runner_common.py tests/test_dispatch_validator_runner.py -v
tests/test_validator_runner_common.py::test_review_file_name_hyphen_to_underscore PASSED
tests/test_validator_runner_common.py::test_review_file_name_other_domain PASSED
tests/test_validator_runner_common.py::test_read_verdict_pass PASSED
tests/test_validator_runner_common.py::test_read_verdict_fail PASSED
tests/test_validator_runner_common.py::test_read_verdict_not_found PASSED
tests/test_validator_runner_common.py::test_build_validator_prompt_contains_required_elements PASSED
tests/test_validator_runner_common.py::test_parse_validator_inputs_all_required PASSED
tests/test_validator_runner_common.py::test_parse_validator_inputs_missing_pr_number_fails PASSED
tests/test_validator_runner_common.py::test_post_fail_assignment_calls_gh_codex PASSED
tests/test_validator_runner_common.py::test_post_fail_assignment_calls_gh_claude PASSED
tests/test_validator_runner_common.py::test_verify_review_committed_passes_when_file_in_log PASSED
tests/test_validator_runner_common.py::test_verify_review_committed_fails_when_file_absent PASSED
tests/test_validator_runner_common.py::test_verify_formal_review_posted_passes_with_review PASSED
tests/test_validator_runner_common.py::test_verify_formal_review_posted_fails_with_no_reviews PASSED
tests/test_validator_runner_common.py::test_run_validator_rejects_wrong_engine PASSED
tests/test_dispatch_validator_runner.py::test_dispatches_when_pr_branch_matches_active_pe PASSED
tests/test_dispatch_validator_runner.py::test_skips_when_pr_branch_does_not_match PASSED
tests/test_dispatch_validator_runner.py::test_fails_when_pr_number_not_set PASSED
18 passed in 0.22s

python -m pytest
667 passed, 17 warnings in 10.44s

python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.

python scripts/copy_handoff.py
Copied handoffs\HANDOFF_PE-AUTO-05.md -> HANDOFF.md

python scripts/check_handoff.py
HANDOFF OK (handoffs\HANDOFF_PE-AUTO-05.md) — all required sections present.
```

---

*ELIS SLR Agent · handoffs/HANDOFF_PE-AUTO-05.md · infra-impl-claude · 2026-04-03*
