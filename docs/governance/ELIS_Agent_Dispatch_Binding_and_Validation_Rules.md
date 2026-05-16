# ELIS Agent Dispatch, Binding, and Validation Rules

**Status:** Canonical — v1.2
**Date:** 2026-05-16
**Owner:** Carlos Rocha, Product Owner
**Applies to:** All ELIS agents (PM, Implementer, Validator, Gatekeeper, Platform Monitor)
**Authoritative sources:** ELIS_PE_Operating_Protocol.md, ELIS_Worktree_Preflight_Checklist.md, LESSONS_LEARNED.md
**Canonical record:** GitHub (this document)

---

## 1. Purpose

Define the canonical rules for PE dispatch, worktree binding, runtime workspace distinction, and validation readiness. This document codifies the invariant that every agent has two distinct environments:

1. **OpenClaw runtime workspace** — agent identity, skills, memory, and runtime context (preserved across PEs)
2. **Authorised Git worktree** — disposable repo/task state for the current PE (reset at each PE boundary)

---

## 2. Scope

This document governs:
- PM dispatch packets
- implementer binding and refusal rules
- validator evidence rules
- deterministic readiness checks
- runtime workspace / Git worktree distinction
- persistent context preservation and exclusion from fixed worktrees
- valid-for-branch validator readiness (not detached-head)

---

## 3. Runtime Workspace and Git Worktree Binding

### 3.1 Distinct Environments

Every agent operates from two distinct directories:

| Agent | OpenClaw Runtime Workspace | Authorised Git Worktree |
|-------|---------------------------|------------------------|
| infra-impl-b | `/home/samurai/openclaw/workspace-infra-impl-b` | `/opt/elis/agent-worktrees/infra-impl-b` |
| infra-val-a | `/home/samurai/openclaw/workspace-infra-val` | `/opt/elis/agent-worktrees/infra-val-a` |
| PM (workspace-pm) | `/home/samurai/openclaw/workspace-pm` | `/opt/elis/agent-worktrees/pm` |

### 3.2 Runtime Workspace Contents
The runtime workspace hosts persistent agent identity and context files that must survive across PEs:
- `AGENTS.md` — agent workflow rules and operating model
- `SKILLS.md` or equivalent skill manifest
- `SOUL.md` — agent identity and character
- `MEMORY.md` — durable operational corrections
- `IDENTITY.md`, `USER.md` — agent authority and identity
- Tool manifests and capability declarations
- OpenClaw/Hermes bootstrap and system configuration files
- Session continuity and context cache files

### 3.3 Git Worktree Contents
The authorised Git worktree hosts only disposable repo/task state for the current PE:
- Git working tree (source code, tests, docs)
- `HANDOFF.md`, `REVIEW_PE<N>.md` (PE-specific artefacts)
- Branch-specific config and state
- CI caches and build artefacts
- Files within the `.elis/` PE workspace tree

### 3.4 Fixed Worktree Exclusion Rule
Fixed Git worktrees **must be clean** and **must not contain** any of the following persistent runtime/bootstrap files as untracked or committed content:
- `.openclaw/`
- `HEARTBEAT.md`
- `IDENTITY.md`
- `SOUL.md`
- `TOOLS.md`
- `USER.md`

If any of these files appear inside a fixed worktree, the worktree is considered contaminated. The agent must report the contamination to PM and must not proceed until the files are removed and the worktree is cleaned. Checks `check_fixed_worktrees.py` and `check_dispatch_binding.py` enforce this rule.

---

## 4. Required Dispatch Packet Fields

Every dispatch must name:
- **PE ID** — the canonical PE identifier from CURRENT_PE.md
- **Agent role** — infra-impl-b, infra-val-a, etc.
- **Branch** — feature branch for the PE
- **Starting HEAD** — commit SHA before any work begins
- **Runtime workspace** — OpenClaw workspace path (e.g. `/home/samurai/openclaw/workspace-infra-impl-b`)
- **Authorised Git worktree** — fixed worktree path (e.g. `/opt/elis/agent-worktrees/infra-impl-b`)
- **Git root** — output of `git rev-parse --show-toplevel`
- **Worktree status** — clean or expected state (output of `git status --short --untracked-files=all`)
- **Exact file scope** — list of allowed files from PE_TASK.md
- **Explicit forbidden files** — list of files the agent must not touch
- **Evidence paths** — expected artefact locations
- **Write scope** — the set of filesystem paths the agent may write to (the authorised Git worktree only)

---

## 5. Binding Rules

### 5.1 Implementer Binding Rules
- The implementer must refuse work on the wrong branch.
- The implementer must refuse work on the wrong worktree — if `git rev-parse --show-toplevel` does not match its assigned fixed worktree path.
- The implementer must refuse a dirty tracked worktree unless the PE explicitly allows and the PO approves it.
- The implementer must produce a **Fixed Workspace Binding Certificate** in its opening Status Packet (see ELIS_PE_Operating_Protocol.md §5.1b).
- The certificate must include: agent identity, role, runtime workspace, authorised Git worktree, git root, branch, HEAD, worktree status, and write scope.

### 5.2 PM Binding Rules
- The PM must not report "in progress" without reset/binding acknowledgement and active-run evidence.
- The PM must verify both the runtime workspace and the authorised Git worktree are correctly bound before dispatch.

### 5.3 Validator Binding Rules
- The validator must validate committed artefacts or a PO-approved snapshot, never a live implementer workspace.
- The validator **accepts the approved branch/HEAD on the fixed validator worktree** — there is no detached-head requirement for validators. The validator worktree is checked out to the same feature branch as the implementer, at the commit to be reviewed.
- The validator must produce a **Fixed Workspace Binding Certificate** in its opening Status Packet.
- The validator must verify the runtime workspace and authorised Git worktree are correctly bound.

---

## 6. Validation Classification

- Missing artefacts in an expected path are `WORKSPACE_MISMATCH`, not content failure.
- Wrong filesystem scope is a readiness failure, not a content failure.
- Stale PE artefacts are a validation failure when they are outside the expected scope or contradict the requested PE state.
- Wrong Git worktree is a `WORKSPACE_MISMATCH` and blocks all further work.
- Missing runtime workspace / Git worktree binding fields in the dispatch packet is a readiness failure.

## 6a. LATEST VALIDATOR REVIEW MUST BE ON FINAL PR BRANCH RULE

### 6a.1 Rule Statement
A validator PASS is valid **only when backed by a committed PE-specific REVIEW.md** that resides on the final implementation/PR branch (not a separate validation branch, not a detached-HEAD commit, not uncommitted).

### 6a.2 REVIEW.md Requirements
The REVIEW.md on the final PR branch must:
1. Be committed as part of the branch's commit history (visible via `git log --all -- REVIEW.md` on the target branch).
2. Reference the **final validated branch HEAD** or the **final validation target commit** (the exact commit SHA that was reviewed and deemed ready for closeout).
3. Record the final checks performed and the verdict (`PASS`, `FAIL`, or `BLOCKED`).
4. Be authored by the validator agent, not by the implementer, PM, or any other role.

### 6a.3 Commitment Requirement
The latest validator REVIEW.md update must be:
- **Committed** — not staged, not uncommitted, not in a stash
- **Present on the final implementation/PR branch** — the branch that will be merged or closed out
- Identifiable via `git log --oneline <branch> -- <REVIEW.md-path>` before push/PR/merge/closeout

### 6a.4 PASS Dependency
Validator must not report PASS until:
1. REVIEW.md is written with the full verdict packet.
2. REVIEW.md's tracked/committed/integration status is explicit (committed on the target branch, not floating on a separate validation branch).
3. The final checks match the branch HEAD that will be merged.

### 6a.5 Enforcement
- `check_validation_readiness.py` must include a `COMMITTED_REVIEW_ON_BRANCH` check that verifies the REVIEW.md is committed and reachable from the current branch HEAD.
- If the latest REVIEW.md update is not committed on the current branch, the validator must reject the state and report `REVIEW_NOT_ON_BRANCH`.

## 6b. AUTHORISED EXECUTION OWNER FOR BRANCH INTEGRATION RULE

### 6b.1 Rule Statement
PM coordinates PE workflow but **must not execute merges, pushes, PR actions, or any Git history rewrites directly**. All branch integration operations (push, PR creation, merge, rebase of the target branch) must be executed by the authorised execution owner in the authorised worktree.

### 6b.2 Eligible Execution Owners
Branch integration may be performed by:
- **GitHub Agent** — after explicit PM/PO approval for each operation
- **Implementer** — local branch commits only; push only when PM/PO explicitly instructs
- **Validator** — local REVIEW.md commits on the shared PE branch only; no push or PR operations

### 6b.3 PM Coordination Boundary
PM is authorised to:
- Propose and plan PEs
- Maintain CURRENT_PE.md registry
- Create and maintain PE_TASK.md
- Dispatch implementers and validators
- Interpret PE status and coordinate workflow
- Request PO approval when needed

PM is **explicitly forbidden** from:
- Running `git push` (any remote)
- Creating or modifying PRs
- Running `git merge` (local or remote)
- Running `git rebase` (of target branches; local task-branch rebase requires authorisation)
- Running `git commit --amend` or any history-rewriting operation
- Writing to GitHub via any tool (gh CLI, API, browser)

### 6b.4 Authorised Worktree Requirement
Branch integration must be executed from the **authorised Git worktree** for the executing role, not from the OpenClaw runtime workspace, the canonical repo (`/opt/elis/repo`), or any other filesystem location.

### 6b.5 Enforcement
- `check_pm_no_write.py` enforces the PM no-write rule across all PE evidence directories.
- The Supervisor agent monitors for role boundary violations.
- Any detection of PM-authored commits outside `PE_TASK.md` is a `PM_WRITE_VIOLATION`.

---

## 7. Persistent Context Preservation

The following paths carry agent identity and runtime state. They are **preserved across dispatch** and **must not be deleted or reset**. They must never appear inside a fixed Git worktree — they belong exclusively in the OpenClaw runtime workspace:

- `.openclaw/`
- `HEARTBEAT.md`
- `IDENTITY.md`
- `SOUL.md`
- `TOOLS.md`
- `USER.md`

---

## 8. Deterministic Checks

Required checks for every PE dispatch:
1. **Dispatch binding check** (`scripts/check_dispatch_binding.py`) — verifies branch, HEAD, worktree cleanliness, and runtime/worktree binding
2. **Implementation readiness check** (`scripts/check_implementation_readiness.py`) — verifies branch, HEAD, worktree cleanliness, PE task packet, and scope files
3. **Validation readiness check** (`scripts/check_validation_readiness.py`) — verifies worktree scope, expected commit, clean tracked state, and artefact completeness
4. **Fixed worktrees audit** (`scripts/check_fixed_worktrees.py`) — verifies each fixed worktree is registered, has correct origin, and is free of runtime/bootstrap files
5. **Persistent context check** (`scripts/check_persistent_context_files.py`) — verifies runtime/bootstrap files exist in the expected location

---

## 9. Dispatch Packet Reporting Format

Every opening Status Packet must include a binding table:

```text
### Fixed Workspace Binding Certificate
| Field | Value |
|-------|-------|
| PE ID | <PE-ID> |
| Agent ID | <agent-id> |
| Role | <role> |
| Runtime workspace | <OpenClaw workspace path> |
| Authorised Git worktree | <fixed worktree path> |
| Git root | <git rev-parse --show-toplevel> |
| Branch | <git branch --show-current> |
| HEAD | <git rev-parse HEAD> |
| Worktree status | <git status --short --untracked-files=all> |
| Allowed file scope | <list from PE_TASK.md> |
| Write scope | <authorised Git worktree only> |
| Timestamp | <ISO 8601> |
| Result | PASS / FAIL |
```

A FAIL result blocks all further work until PM resolves the mismatch.

---

## 10. Exclusions

Live workspace-local `SKILLS.md` files are excluded from this PE. This PE only authors repo-tracked governance/specification files and PE evidence files.

---

## 11. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.3 | 2026-05-16 | PE-closeout | Add §6a LATEST_VALIDATOR_REVIEW_MUST_BE_ON_FINAL_PR_BRANCH_RULE and §6b AUTHORISED_EXECUTION_OWNER_FOR_BRANCH_INTEGRATION_RULE. |
| 1.2 | 2026-05-16 | PE-closeout | Encode runtime workspace / Git worktree distinction. Add binding table for dispatch packets. Add fixed worktree exclusion rule. Change validator readiness to accept branch (not detached-head). Document agent-specific path pairs. |
| 1.0 | 2026-05-03 | PM | Initial canonical consolidation.
