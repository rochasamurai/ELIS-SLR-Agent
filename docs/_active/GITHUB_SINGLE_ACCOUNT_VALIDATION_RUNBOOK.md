# GitHub Single-Account Validation Runbook

## 1. Purpose

This runbook defines how ELIS PE validation works when both Implementer and Validator
operate under the same GitHub identity, and documents the migration path to stronger
separation-of-duties models.

This runbook is a companion to `AGENTS.md` and is referenced from enforcement section §12.

---

## 2. Problem Statement

In single-account repositories, GitHub blocks `request-changes` reviews on self-authored PRs.

Typical error:

```text
GraphQL: Review Can not request changes on your own pull request (addPullRequestReview)
```

Impact:
- Validator cannot always use `gh pr review --request-changes` for FAIL verdicts.
- Without an explicit fallback, FAIL outcomes can be ambiguous in branch-protection flows.

---

## 3. Operating Modes

### Mode A — Single account (current fallback model)

- Implementer and Validator actions are executed by the same GitHub user.
- PASS: can still use `gh pr review --approve`.
- FAIL: must use comment-based verdict fallback (below).

### Mode B — Per-agent machine identities (recommended target)

- Separate identities: one for CODEX, one for Claude Code.
- Native `request-changes` and `approve` semantics are fully available.

### Mode C — GitHub App + CI verdict gates (recommended target)

- Verdict is parsed from standardized artifacts/comments by CI.
- Merge gate depends on CI status checks rather than human review role separation.

---

## 4. Single-Account Fallback Protocol (Mode A)

### 4.1 Preconditions

1. Validator has PM assignment.
2. `HANDOFF.md` and scope checks are complete.
3. Validator has produced `REVIEW_PE<N>.md` on the same PR branch.

### 4.2 PASS flow

1. Post Stage 1 evidence comment.
2. Post PASS review:
   ```bash
   gh pr review <PR> --approve --body "<standard PASS verdict>"
   ```
3. Post/refresh Status Packet comment (optional but recommended).
4. PM merges if all required checks are green.

### 4.3 FAIL flow

1. Post Stage 1 evidence comment.
2. Post FAIL verdict as plain PR comment (not review):
   ```bash
   gh pr comment <PR> --body "<standard FAIL verdict with blocking findings>"
   ```
3. Add `pm-review-required` label:
   ```bash
   gh pr edit <PR> --add-label pm-review-required
   ```
4. PM assigns Implementer for fixes; do not merge while label is present.

### 4.4 Re-validation loop

1. Implementer pushes fixes on same branch.
2. Validator appends new dated section in `REVIEW_PE<N>.md`.
3. Repeat PASS/FAIL flow above.
4. On PASS, remove `pm-review-required` if present:
   ```bash
   gh pr edit <PR> --remove-label pm-review-required
   ```

---

## 5. Branch Protection Guidance

For single-account mode, configure branch protection to rely on automated checks:

1. Require status checks:
   - quality
   - tests
   - validate
   - review-evidence-check
   - secrets-scope-check
2. Require PR conversation resolution before merge.
3. Restrict direct pushes to protected branches.
4. Keep PM merge authority explicit.

Do not rely exclusively on `request-changes` gating in Mode A.

---

## 6. Migration Checklist (Mode B/C)

### 6.1 Move to per-agent identities

1. Create and secure bot/machine accounts per agent.
2. Grant least-privilege repo access.
3. Update PM assignment docs with reviewer identity mapping.
4. Enable required review from non-author before merge.
5. Retire single-account FAIL fallback after verification.

### 6.2 Move to GitHub App + CI verdict gate

1. Define canonical verdict schema in PR comment or `REVIEW_PE<N>.md`.
2. Extend workflow to parse verdict and fail CI on unresolved blocking findings.
3. Protect branch with required CI gate instead of human review identity rules.
4. Keep `REVIEW_PE<N>.md` as durable artifact on PR branch.

---

## 7. PM Decision Matrix

| Constraint | Recommended Mode |
|---|---|
| One GitHub account only | Mode A (fallback protocol mandatory) |
| Can create machine identities | Mode B |
| Want maximum automation + auditability | Mode C |

---

## 8. Compliance Notes

- This runbook does not replace `AGENTS.md`; it specializes enforcement for single-account
  GitHub constraints.
- If this runbook conflicts with `AGENTS.md`, update `AGENTS.md` first, then sync this file.
