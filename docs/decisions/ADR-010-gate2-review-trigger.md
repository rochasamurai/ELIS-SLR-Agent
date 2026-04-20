# ADR-010 — Gate 2 Triggered by Mapped-Bot Approval Review

**Status:** Accepted  
**Date:** 2026-04-20  
**PE:** PE-INFRA-SLR-05  
**Deciders:** PM, `infra-impl-b` (Claude Code)

---

## Context

Gate 2 auto-merge (`auto-merge-on-pass.yml`) previously triggered only on `push` events to
feature branches. The workflow parsed the `REVIEW_PE*.md` file for a `PASS` verdict and
merged if conditions were met.

PR #343 revealed a deadlock: `elis-codex-bot` submitted a formal `APPROVED` review with
all required CI checks green and no `pm-review-required` label present, yet the PR did not
auto-merge. The root cause was the push-only trigger — the bot review submission fired no
push event, so the workflow never re-evaluated the PR's mergeable state. When the Validator
committed the REVIEW file (triggering the workflow), the bot review had not yet been
submitted, so `mergeable_state` was `blocked`.

The deadlock was documented in issue #344.

## Decision

Add `pull_request_review: types: [submitted]` as a second trigger for `auto-merge-on-pass.yml`.

When a `pull_request_review` event fires:

1. The workflow checks that the review state is `approved` (non-approval events are skipped).
2. `scripts/check_reviewer_identity.py` verifies the reviewer's GitHub login matches the
   mapped bot identity for the current PE's validator role (derived from `CURRENT_PE.md` +
   `config/reviewer_identity_map.json`). Reviews from unmapped identities are rejected.
3. The REVIEW file is still required to be present on the branch and to pass
   `scripts/check_review.py` (AC-4 compliance).
4. The existing checks — `pm-review-required` label absent and `mergeable_state == 'clean'`
   — are preserved unchanged.
5. If all conditions are met, the PR is merged automatically.

The push-triggered path is retained unchanged. Its merge signal remains `PASS` in the
`REVIEW_PE*.md` file. Both paths share the same final gate steps (Gate 2b, PM veto check,
mergeable check, merge action).

## Consequences

**Positive**

- Eliminates the approval-without-merge deadlock: a mapped-bot APPROVED review now
  triggers Gate 2 immediately.
- The `mergeable_state == 'clean'` check at merge time handles the race: after the bot
  approves, GitHub marks the required-review check as satisfied; CI was already green from
  the earlier push; so `mergeable_state` transitions to `clean` before the workflow acts.
- Identity verification (`check_reviewer_identity.py`) prevents any arbitrary GitHub account
  from triggering auto-merge via a review.
- REVIEW file as an audit artefact is preserved — Gate 2b still validates it before merge
  on both trigger paths.

**Neutral**

- The workflow now has two code paths that share common tail steps. The `auth` step
  encapsulates the path-specific merge authorisation logic, keeping the shared steps clean.
- The push-triggered path continues to work as before for repositories or PEs that do not
  use mapped bot review identities.

**Negative / trade-offs**

- The `pull_request_review` trigger fires for every review event on every matching PR,
  including comment and change-request reviews. The `proceed=false` early exit handles
  non-approval events at negligible cost (the job still starts and exits quickly).
- The slot-to-engine mapping in `check_reviewer_identity.py` is inlined rather than
  imported from `elis/agent_id.py` to keep the script self-contained on the CI runner.
  This creates a second copy of the slot-registry constants; both must be kept in sync
  with `config/agent_id_migration_map.json` and `AGENTS.md §14`.

## Alternatives Considered

**Re-trigger the push workflow via a dummy push.** Rejected — fragile, creates noise in
git history, and does not address the root cause.

**Use `workflow_run` to retrigger on the CI workflow completing.** Rejected — `workflow_run`
events do not carry PR approval context; would require additional API calls to determine
whether an approval was submitted.

**Allow any APPROVED review to trigger merge.** Rejected — violates the mapped-identity
requirement established in PE-INFRA-SLR-02. Any GitHub account could trigger auto-merge.
