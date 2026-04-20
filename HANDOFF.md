# HANDOFF — PE-INFRA-SLR-05 · Gate 2 Auto-Merge Alignment

**Date:** 2026-04-20
**PE:** `PE-INFRA-SLR-05`
**Branch:** `feature/pe-infra-slr-05-gate2-auto-merge-alignment`
**Implementer:** `infra-impl-b` (Claude Code)
**Validator:** `infra-val-a` (CODEX @ `elis-server`)

---

## 1) Summary

Eliminates the Gate 2 approval-without-merge deadlock documented in issue #344.

The root cause was that `auto-merge-on-pass.yml` only triggered on `push` events. When
`elis-codex-bot` submitted a formal GitHub `APPROVED` review, no push event fired, so
the workflow never re-evaluated the PR's mergeable state. The PR sat `blocked` until a
human force-merged it.

This PE adds a `pull_request_review: submitted` trigger as a second Gate 2 path. When
a mapped bot submits an approved review, the workflow now:
1. Verifies the reviewer's GitHub login matches the mapped identity for the PE's validator
   role (`scripts/check_reviewer_identity.py`).
2. Still validates the REVIEW file via `check_review.py` (AC-4 compliance).
3. Checks `pm-review-required` label and `mergeable_state == 'clean'`.
4. Auto-merges if all conditions are met.

The push-triggered path is retained unchanged.

---

## 2) Deliverables

| File | Change |
|------|--------|
| `.github/workflows/auto-merge-on-pass.yml` | Added `pull_request_review: submitted` trigger; new `ctx`, `reviewer_check`, `auth` steps; unified merge gate condition |
| `scripts/check_reviewer_identity.py` | New script — verifies reviewer login against mapped bot for PE's validator role |
| `tests/test_gate2_auto_merge.py` | New file — 20 acceptance tests covering AC-1 through AC-7 |
| `docs/decisions/ADR-010-gate2-review-trigger.md` | New ADR — records Gate 2 review-trigger design decision |
| `docs/decisions/README.md` | ADR index updated with ADR-010 row |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | `auto-merge-on-pass.yml` adds `pull_request_review: submitted` trigger | PASS |
| AC-2 | Merge condition requires: mapped bot approval + green CI + no veto label + `mergeable_state == 'clean'` | PASS |
| AC-3 | Workflow verifies approving identity against `config/reviewer_identity_map.json` | PASS |
| AC-4 | `REVIEW_PE<N>.md` remains required audit artefact; `check_review.py` runs on both trigger paths | PASS |
| AC-5 | Mapped-bot approval merges without requiring additional push | PASS |
| AC-6 | `pm-review-required` label blocks auto-merge even if all other conditions met | PASS |
| AC-7 | `python -m pytest tests/test_gate2_auto_merge.py -v` passes (20/20) | PASS |

---

## 4) Validation Commands

```bash
# PE-specific tests
python -m pytest tests/test_gate2_auto_merge.py -v

# Quality gates
python -m black --check .
python -m ruff check .

# Full suite (2 pre-existing failures in test_verify_claude_auth.py — not introduced by this PE)
python -m pytest -q

# Scope gate
git diff --name-status origin/main..HEAD
```

---

## 5) Scope Gate

```
git diff --name-status origin/main..HEAD

M	.github/workflows/auto-merge-on-pass.yml
M	HANDOFF.md
A	docs/decisions/ADR-010-gate2-review-trigger.md
M	docs/decisions/README.md
A	scripts/check_reviewer_identity.py
A	tests/test_gate2_auto_merge.py

6 files changed, 701 insertions(+), 38 deletions(-)
```

No files outside PE-INFRA-SLR-05 scope are modified.

---

## 6) Design Notes

### Trigger context step (`ctx`)

The `pull_request_review` event does not expose `GITHUB_REF_NAME` as the feature branch
name — it resolves to `N/merge`. The `ctx` step captures branch name from
`github.event.pull_request.head.ref` for the review path and `GITHUB_REF_NAME` for the
push path.

### Reviewer identity check (`check_reviewer_identity.py`)

The script derives the expected reviewer login from three sources:
1. `CURRENT_PE.md` — extracts the validator agent ID (e.g. `infra-val-a`) from the PE line.
2. Slot suffix (`a` → `codex`, `b` → `claude`, `c` → `gemini`) — inlined constant
   `_SLOT_TO_ENGINE` to keep the script self-contained on the CI runner.
3. `config/reviewer_identity_map.json` — looks up `review_login` for the engine, only
   for entries where `validator_capable_on_protected_branches: true`.

Exits 0 if the incoming `REVIEWER_LOGIN` matches exactly; exits 1 otherwise.

### Unified auth step

The `auth` step outputs `authorized=true` for either:
- push path: `verdict == PASS`
- review path: `reviewer_check.outcome == success`

All downstream steps (gate2b, veto check, mergeable check, merge action) are gated on
`steps.auth.outputs.authorized == 'true'`, so the merge condition is identical for both
paths.

### Pre-existing test failures

`tests/test_verify_claude_auth.py::test_fails_when_credentials_file_missing` and
`::test_fails_when_credentials_file_lacks_oauth_key` fail pre-commit on this branch.
Both are pre-existing failures unrelated to this PE (they test a credential-file path
that does not exist in the CI environment). Confirmed by `git log --follow
tests/test_verify_claude_auth.py` — last modified before this PE branch diverged.

---

## 7) Notes for Validator

**Key things to verify:**

1. **AC-1**: `auto-merge-on-pass.yml` `on:` block contains both `push` and
   `pull_request_review: types: [submitted]`.

2. **AC-2**: Auto-merge step `if:` condition (step 9) references all four:
   `auth.outputs.authorized == 'true'`, `gate2b.outcome == 'success'`,
   `labels.outputs.veto == 'false'`, `mergeable.outputs.state == 'clean'`.

3. **AC-3**: `scripts/check_reviewer_identity.py` exists; workflow calls it in the
   `reviewer_check` step; `_SLOT_TO_ENGINE` map covers `a/b/c` slots.

4. **AC-4**: `gate2b` step calls `check_review.py` and is gated on
   `steps.auth.outputs.authorized == 'true'` (runs for both trigger paths, not just push).

5. **AC-5**: No step in the merge path conditions on `GITHUB_REF_NAME` or requires a
   new push event after review — confirm by inspecting all `if:` conditions on steps 6–9.

6. **AC-6**: `labels` step (step 7) reads the `pm-review-required` label; merge step
   conditions on `labels.outputs.veto == 'false'`.

7. **Pre-existing failures**: `test_verify_claude_auth.py` 2 failures existed before
   this PE. Run `git log --follow tests/test_verify_claude_auth.py` to confirm.
