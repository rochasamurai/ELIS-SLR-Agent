# Two-Agent Session Continuity Runbook

> Purpose: keep 2-Agent PE execution resilient to session compaction, context loss,
> and mid-task interruption.
>
> Intended future use: reference in the `v3.x` implementation/deployment plan.

---

## 1. Problem Statement

In the ELIS 2-Agent model, long-lived chat sessions can be compacted while a PE is still
in progress. When too much live state exists only in the agent session, the workflow
becomes fragile:

- implementation context can be lost mid-PE
- validator state can drift between review rounds
- PM cannot reliably infer real progress from chat alone
- restarted sessions may repeat work or miss completed checkpoints

The correct response is not to depend on longer sessions. The correct response is to make
each PE operationally resumable from durable artifacts.

---

## 2. Core Principle

**The PR is the operational memory.**

Chat is for coordination.
The PR branch and its PE artifacts are the source of execution continuity.

If a fact is required to resume work, it must exist in one of these places:

- committed code or docs on the PE branch
- `HANDOFF.md`
- `REVIEW_PE<N>.md`
- PR comments with status packets
- `CURRENT_PE.md` for role/branch/plan authority

If it exists only in chat memory, it is not yet safe.

---

## 3. Recommended Monitoring Model

PM should monitor each PE from GitHub and repo artifacts, not from ongoing chat state.

### 3.1 Operational sources of truth

- `CURRENT_PE.md`
  - authoritative PE, branch, base branch, role assignment
- active PR for the PE
  - operational progress, checks, comments, and review state
- `HANDOFF.md`
  - implementer-side technical memory
- `REVIEW_PE<N>.md`
  - validator-side technical memory

### 3.2 Minimum PM dashboard per PE

For each active PE, PM should be able to see:

- PE ID
- branch name
- current PR number/status
- latest commit SHA
- latest Implementer update
- latest Validator update
- CI/check status
- current `CURRENT_PE.md` status value

This can be monitored directly through GitHub plus `CURRENT_PE.md`; no long-lived chat
session is required.

---

## 4. Session Continuity Rules

### 4.1 Short, checkpointed sessions

Agents should prefer short sessions with a closed objective, for example:

- implement the scoped files for the PE
- run and record quality gates
- update `HANDOFF.md`
- validate the PR and publish verdict
- fix specific blocking findings

Avoid open-ended sessions such as:

- "keep working until the PE is done"

That pattern maximizes the chance of compaction in the middle of ambiguous state.

### 4.2 Commit before any pause

Before any planned or unplanned pause:

- tree must be clean
- progress must be committed on the correct branch
- no implementation state may remain only in editor memory or chat context

This rule is mandatory for both Implementer and Validator.

### 4.3 PR comment after each meaningful milestone

After each significant checkpoint, the active agent should post a short PR update.

Examples:

- implementation checkpoint complete
- quality gates green
- `HANDOFF.md` updated
- validation started
- FAIL findings posted
- fixes verified
- PASS posted

These PR comments create a resumable operational timeline even if the session is compacted.

---

## 5. Required Checkpoints by Role

### 5.1 Implementer checkpoints

The Implementer should create a durable checkpoint at each of these milestones:

1. PE branch/worktree created and context read
2. first implementation commit pushed
3. draft PR opened
4. quality gates passing
5. `HANDOFF.md` completed
6. PR converted to ready for review

Each checkpoint should leave behind:

- a commit or clean tree state
- updated `HANDOFF.md` when relevant
- a short PR comment with status packet summary

### 5.2 Validator checkpoints

The Validator should create a durable checkpoint at each of these milestones:

1. validation assignment accepted
2. scope diff verified
3. acceptance criteria exercised
4. adversarial validation completed
5. `REVIEW_PE<N>.md` committed
6. PASS or FAIL posted in the PR

Each checkpoint should leave behind:

- committed `REVIEW_PE<N>.md` updates when relevant
- PR review/comment outcome
- enough evidence for re-validation without relying on prior session memory

---

## 6. Durable Memory Pattern

### 6.1 Technical memory

Technical state belongs in versioned PE artifacts:

- `HANDOFF.md`
- `REVIEW_PE<N>.md`
- tests
- scoped docs/runbooks created by the PE

### 6.2 Operational memory

Operational state belongs in the PR thread:

- latest milestone reached
- latest gate result
- current blocker if any
- next actor and next action

### 6.3 Authority memory

Governance state belongs in:

- `CURRENT_PE.md`

This avoids ambiguity about:

- active PE
- branch
- plan version
- Implementer/Validator roles

---

## 7. Anti-Patterns

The following behaviors increase session-compaction risk and should be avoided:

- relying on chat history as the only activity log
- leaving a dirty tree at session end
- delaying `HANDOFF.md` or `REVIEW_PE<N>.md` updates until the end
- making multiple large changes before the first checkpoint commit
- posting only one final PR comment after hours of work
- assuming PM can reconstruct progress from memory instead of artifacts

---

## 8. Best-Practice Workflow

The most effective continuity pattern for ELIS is:

1. PM assigns the PE in `CURRENT_PE.md`
2. Implementer works in a dedicated worktree/branch
3. Implementer commits in small, scoped increments
4. Implementer posts milestone updates in the PR
5. Implementer completes `HANDOFF.md` before ready-for-review
6. Validator validates from the same branch
7. Validator commits `REVIEW_PE<N>.md` updates on-branch
8. Validator posts PASS/FAIL in the PR
9. PM monitors the PR plus `CURRENT_PE.md`, not live chat memory

This makes the workflow robust even if either agent session is compacted or restarted.

---

## 9. Recommended Rule for Future v3.x Plan

Add the following operational rule to the future `v3.x` plan:

> Every active PE must remain resumable without chat history. Progress is considered
> durable only when recorded in branch commits, `HANDOFF.md` / `REVIEW_PE<N>.md`, and
> PR comments. PM monitors agent activity through PR state and `CURRENT_PE.md`, not by
> relying on long-lived session continuity.

---

## 10. Conclusion

The best way to avoid disruption from session compaction is not to fight compaction
directly. It is to design the 2-Agent workflow so that every PE is restart-safe.

For ELIS, that means:

- small checkpoints
- frequent commits
- clean-tree session boundaries
- PR-centered progress tracking
- durable technical memory in PE artifacts

That is the most effective and scalable continuity model for the current 2-Agent system.

---

*Two-Agent Session Continuity Runbook · for future Plan v3.x adoption*
