# ELIS PE Operating Protocol

**Status:** Canonical — v1.1  
**Date:** 2026-05-06  
**Owner:** Carlos Rocha, Product Owner  
**Applies to:** All ELIS agents (PM, Gatekeeper, Watchdog, Implementers, Validators, Platform Monitor)  
**Authoritative sources:** AGENTS.md, CLAUDE.md, ELIS_General_Guidance.md, LESSONS_LEARNED.md  
**Canonical record:** GitHub (repo artefacts, commits, PRs, CI logs — not chat history)

---

## 1. Purpose

This document codifies the operating protocol for PE execution within the ELIS multi-agent system. It consolidates rules that were previously enforced through ad-hoc chat directives, CLAUDE.md, AGENTS.md, and repeated PM instructions into a single, versioned, repository-housed protocol.

Every agent must follow this protocol. Exceptions require explicit Product Owner (Carlos Rocha) approval.

---

## 2. Core Principles

### 2.1 GitHub Is the Canonical Record
The authoritative state of every PE lives in repository artefacts: commits, PR descriptions, status checks, CI logs, and version-controlled documents. Chat history is ephemeral and must not be treated as authoritative.

### 2.2 OpenClaw / Lobster Executes
OpenClaw is the operational execution environment for PM coordination, PE gatekeeping, PE monitoring, implementers, and validators. Lobster is the controlled workflow manager for multi-step PE tasks.

### 2.3 Task Flow Manages Lifecycle
Task Flow is the substrate for PE lifecycle management: opening, dispatching, monitoring, and closing PEs across implementers and validators. It manages flow identity, child-task linkage, waiting state, revision-checked mutations, and user-facing emergence.

### 2.4 Hermes Supervises and Advises
Hermes (ELIS Platform Monitor) runs outside OpenClaw and handles platform health, recovery, diagnosis, and PO advisory. It does not dispatch PE agents.

### 2.5 Carlos Has Final Approval Authority
Carlos Rocha (PO) approves PE concepts, scope exceptions, merge decisions, branch-policy changes, runtime configuration mutations, credential changes, and any recovery action that could affect repository state.

### 2.6 Commit Before Validation
All implementation commits must precede validation. Validators review committed artefacts, not work-in-progress.

### 2.7 No Silent Failure Recovery
A run that produces no required artefacts (commit, HANDOFF, Status Packet, or REVIEW) is not a success. Valid outcomes are PASS, FAIL, or BLOCKED — each backed by evidence. Recovery from silent failure is a separate, PO-authorised process.

### 2.8 Fixed Agent Workspace Model
Every agent role has a persistent, dedicated worktree path that persists across PEs. This replaces the per-PE worktree pattern.

**Fixed worktree paths:**
- `infra-impl-a` → `/opt/elis/agent-worktrees/infra-impl-a`
- `infra-impl-b` → `/opt/elis/agent-worktrees/infra-impl-b`
- `infra-val-a`  → `/opt/elis/agent-worktrees/infra-val-a`
- `infra-val-b`   → `/opt/elis/agent-worktrees/infra-val-b`
- (same pattern for programme and SLR roles)

The worktree is reset and rebased at the start of each PE assignment. The branch checked out in the fixed worktree changes per PE. The worktree path itself does not.

**Advantages:**
- Agent sessions always bind to the same filesystem path
- Shell and PM know exactly where each agent works
- No stale worktrees accumulate per PE
- CI/CD runners, monitoring, and recovery scripts use stable paths

### 2.9 Worktree and Provider Preflight Required
Before any PE execution begins, the agent must verify:
- Correct fixed worktree path (role-specific, not PE-specific)
- Correct branch checked out for the current PE
- Provider/model availability and credentials
- Clean or expected working-tree state
- Task packet exists and is current

### 2.10 GitHub Write Boundary Model
gitHub write access is gated by role and explicit authorisation. No agent may perform a GitHub write operation unless the action is within its authorised boundary.

**Allowed GitHub writes per role:**
- **Implementer:** Local branch commits only. No git push, PR creation, or remote writes unless explicitly authorised by PM.
- **Validator:** Local commits to the shared PE branch (REVIEW file, adversarial tests only). PR comments and formal GitHub reviews when explicitly authorised.
- **PM:** All GitHub operations including push, PR creation, label/comment, merge (with PO approval for merge).
- **GitHub Agent (dedicated bot):** Push, PR ops, labels/comments, merge status reporting under PE-scoped activation.

**All roles:** Merge requires explicit PO approval. No automatic merge.

### 2.11 No Automatic Push, PR, or Merge
Agents never push, open PRs, or merge without explicit PM direction. These actions are PM-owned.

### 2.12 Discord / PO Checkpoint Governance
Discord is for human-visible coordination, but the PE thread is the operational checkpoint trail. Use the main Discord channel for portfolio-level control and escalation, and use the PE thread for compact checkpoint updates, audit notes, and continuation markers. GitHub remains the canonical evidence record; Discord never replaces commits, PRs, CI output, or versioned artefacts.

See `docs/governance/ELIS_Discord_PO_PM_Checkpoint_Governance.md` for thread usage, message-boundary, and checkpoint packet rules.

---

## 3. PE Lifecycle

### 3.1 Planning
1. PO approves PE concept.
2. PM creates `.elis/pe/<PE-ID>/PE_TASK.md` (task packet) with objective, branch, allowed files, required artefacts, and acceptance criteria.
3. PM registers the PE in CURRENT_PE.md registry with status `planning`.
4. PM updates CURRENT_PE.md agent roles, branch, and PE ID.

### 3.2 Pre-Dispatch (Gatekeeper)
1. PM runs Gatekeeper preflight (or requests Gatekeeper readiness check).
2. Gatekeeper verifies: fixed worktree path for the role, branch matches PE, task packet existence, clean state after reset/rebase, provider readiness, artefact gates.
3. Gatekeeper returns one of: `READY`, `NOT_READY`, `NEEDS_PLATFORM_FIX`, `NEEDS_PO_DECISION`.
4. PM dispatches only on `READY` or PO-authorised override.

### 3.3 Implementation
1. PM dispatches Implementer with fresh session and assigned worktree.
2. Implementer verifies worktree, branch, and task packet (Step 0).
3. Implementer performs bounded implementation within assigned files.
4. Implementer runs required checks (black, ruff, pytest, PE-specific).
5. Implementer commits changes.
6. Implementer writes HANDOFF.md with Status Packet.
7. Implementer runs pre-commit scope gate and mid-session checkpoint.
8. Implementer pushes only when PM instructs.

### 3.4 Watchdog
1. After implementer commit, Watchdog confirms artefacts exist (commit, HANDOFF, Status Packet).
2. Watchdog returns: `RUNNING`, `STUCK`, `MISSING_ARTEFACTS`, `IMPLEMENTER_BLOCKED`, `VALIDATOR_BLOCKED`, `NEEDS_PLATFORM_FIX`, `NEEDS_PM_ACTION`, `NEEDS_PO_DECISION`, or `DONE`.

### 3.5 Validation
1. PM dispatches Validator with fresh session and separate validation worktree.
2. Validator verifies worktree, branch, commit SHA, and artefact completeness.
3. Validator reviews all changed files.
4. Validator runs required checks independently.
5. Validator writes REVIEW file with explicit PASS, FAIL, or BLOCKED verdict.
6. Validator delivers verdict as PR comment + formal GitHub PR review.
7. Validator never modifies implementation files without PM authorisation.

### 3.6 Gate 1 (Validator Assignment)
Gate 1 is a CI-driven automated check. On a READY verdict from Gatekeeper, PM dispatches the Validator. Gate 1 CI runs on the feature branch and assigns the Validator via PR comment. The Validator may start only after receiving explicit PM or CI-bot assignment.

### 3.7 Gate 2 (Merge)
Gate 2 is a PE-completion gate. On a PASS verdict from the Validator (PR comment + formal GitHub review), CI checks re-run. Merge is PM-owned and requires:
- Branch protection rules are satisfied
- No `pm-review-required` label is set
- Validator is the correct assigned agent
- Explicit PO approval (per §3.8)

Gate 2 does not auto-merge. The PM merges after confirming all gates are green and PO has approved.

### 3.8 PO Approval and Override
PO approval is required for:
- Merge when Gate 2 auto-merge is blocked or unavailable
- Scope redefinition mid-PE
- Role boundary exceptions
- Runtime configuration changes
- Credential/provider changes
- Recovery actions that modify repository state
- Branch protection changes

### 3.9 Cleanup
1. After merge, PM updates CURRENT_PE.md registry to `merged`.
2. PM may close or archive the worktree.
3. PM advances to the next PE or release.

---

## 4. Role Boundaries

### 4.1 PM (Project Manager)
- Owns PE workflow and state machine
- Proposes PEs, maintains PE state, and updates CURRENT_PE.md
- Creates and maintains PE task packets
- Requests Gatekeeper preflight
- Dispatches implementers and validators
- Interprets PE status
- Coordinates PR flow after validation
- Requests PO approval when needed

**PM must not:**
- Fix OpenClaw gateway/auth/path/config problems directly
- Perform Platform Monitor duties
- Bypass Gatekeeper without PO approval
- Treat silent or artefact-free runs as success
- Merge without approved process
- Override role boundaries

### 4.2 Implementer
- Works only in the assigned PE worktree
- Uses the approved branch
- Modifies only allowed files
- Runs required checks
- Produces a commit
- Produces HANDOFF.md with Status Packet
- Reports blockers with evidence

**Implementer must not:**
- Validate their own work
- Merge PRs
- Approve PRs
- Change branch protection
- Perform unrelated cleanup
- Run blanket permission changes (e.g. `chmod +x scripts/*.py`)
- Write outside the assigned worktree

### 4.3 Validator
- Independently reviews implementer output
- Uses assigned validation worktree
- Verifies correct branch and commit
- Reviews changed files
- Runs required checks independently
- Produces REVIEW file with explicit verdict
- Delivers verdict as PR comment + formal GitHub review

**Validator must not:**
- Validate the wrong repo or stale branch
- Modify implementation files unless PM-authorised
- Validate their own implementation
- Merge
- Approve on behalf of the PO

### 4.4 PE Gatekeeper
- Performs pre-dispatch readiness checks
- Verifies: path, branch, task packet, clean state, provider readiness, artefact gates
- Returns READY, NOT_READY, NEEDS_PLATFORM_FIX, or NEEDS_PO_DECISION

**Gatekeeper must not:**
- Dispatch agents
- Modify files
- Commit, push, or merge
- Change runtime configuration

### 4.5 PE Watchdog
- Monitors PE progress after dispatch
- Detects: stuck runs, wrong paths, missing artefacts, silent success, rate-limit failures
- Returns: RUNNING, STUCK, MISSING_ARTEFACTS, IMPLEMENTER_BLOCKED, VALIDATOR_BLOCKED, NEEDS_PLATFORM_FIX, NEEDS_PM_ACTION, NEEDS_PO_DECISION, DONE

**Watchdog must not:**
- Dispatch agents
- Perform implementation or validation
- Approve or merge

### 4.6 Platform Monitor (Hermes)
- Monitors and repairs platform health
- Diagnoses Hermes/OpenClaw gateway issues
- Verifies auth, provider, model, path, and service status
- Inspects logs
- Runs approved platform recovery steps
- Verifies Discord connectivity

**Platform Monitor must not:**
- Dispatch OpenClaw implementers or validators
- Manage PE workflow state
- Approve or merge PRs
- Modify PE state without PO authorisation
- Alter OpenClaw runtime config without PO approval

---

## 5. Worktree and Workspace Rules

### 5.1 Fixed Agent Worktree Model
Each agent role has a persistent, dedicated worktree path that does not change between PEs:
```
/opt/elis/agent-worktrees/<role>-<slot>
```
Examples: `/opt/elis/agent-worktrees/infra-impl-b`, `/opt/elis/agent-worktrees/infra-val-a`

### 5.2 Worktree Reset Between PEs
At the start of each PE assignment, the fixed worktree is:
1. Cleaned of uncommitted changes (stash or discard disposable state)
2. Fetched from origin
3. Rebased onto the current `origin/$BASE`
4. Switched to the PE branch (created if new)

### 5.3 No Shared Mutable Working Directory
Two active agents must never write to the same working directory. Each fixed worktree hosts exactly one role. Rule: one PE branch + one active writer at a time.

### 5.4 Canonical Repository
`/opt/elis/repo` is the canonical ELIS repository. It must remain clean unless a controlled, approved PE is actively modifying it.

### 5.5 No OpenClaw Workspace on Canonical Repo
OpenClaw workspace must not be directly bound to `/opt/elis/repo`. OpenClaw may write bootstrap/context files into its workspace.

### 5.6 Path Preflight
Before any PE work, the agent must run:
```bash
pwd
git rev-parse --show-toplevel
git status --short --branch
git branch --show-current
```
The verified path must match the agent's fixed worktree path. The branch must match the current PE branch from CURRENT_PE.md.

---

## 6. Artefact Requirements

### 6.1 Implementation Artefacts
- Commit with descriptive message
- Changed file list
- Tests/checks run
- HANDOFF.md with Status Packet
- Blocker evidence (if blocked)

### 6.2 Validation Artefacts
- Explicit PASS, FAIL, or BLOCKED verdict
- REVIEW.md or validator verdict packet
- Tests/checks run independently
- Evidence reviewed with command output
- Blocker details (if any)

### 6.3 Status Packet (in every PM update)
```text
### §6.1 Working-tree state
git status -sb
git diff --name-status
git diff --stat

### §6.2 Repository state
git fetch --all --prune
git branch --show-current
git rev-parse HEAD
git log -5 --oneline --decorate

### §6.3 Scope evidence
git diff --name-status origin/$BASE..HEAD
git diff --stat origin/$BASE..HEAD

### §6.4 Quality gates
python -m black --check .
python -m ruff check .
python -m pytest -q

### §6.5 PR evidence
gh pr list --state open --base $BASE
gh pr view <PR_NUMBER>
```

---

## 7. Commit and Push Rules

### 7.1 Commit Before Ending Session
Before ending a session, `git status -sb` must show a clean tree. Stashing across sessions is prohibited; use WIP commits instead.

### 7.2 HANDOFF Before PR
`HANDOFF.md` must be committed on the feature branch before `git push` and PR creation. Opening a PR without a committed HANDOFF.md is a workflow violation.

### 7.3 No Automatic Push
Agents must not push unless PM instructs. Implementer pushes are triggered by PM explicitly.

### 7.4 No Automatic PR
PRs are created by PM, not by agents. Agents may prepare the branch with committed artefacts; PM opens the PR.

### 7.5 No Automatic Merge
Validators do not merge. PM merges after PASS verdict and Gate 2 satisfaction. PO merges when override is needed.

---

## 8. Mid-Session Checkpoint

Before every `git commit`:
1. Re-read CURRENT_PE.md → Plan file → re-read PE acceptance criteria.
2. Confirm role unchanged.
3. Run `git diff --name-status origin/$BASE..HEAD`.
4. Confirm no unrelated files in diff.

---

## 9. Provider Preflight

Before dispatch, verify:
- OpenClaw gateway is running (`openclaw gateway status`)
- Required providers are available
- Authentication is configured (API keys, OAuth tokens)
- Rate limits are acceptable (no active 429 backlog)
- Model accessibility is confirmed

---

## 10. Recovery and No Silent Failure

### 10.1 Detection
Detect silent failure when:
- Agent reports "OK" with no artefacts
- Agent reports "completed" with no commit, HANDOFF, or REVIEW
- Status shows `deliveryStatus=not_applicable`
- UI response failure is treated as success without repository verification
- Agent output originates from the wrong repo/worktree

### 10.2 Response to Silent Failure
1. Read-only diagnosis: verify reported state against actual repo artefacts.
2. Determine gap: what artefact is missing?
3. Report to PM with evidence of the gap.
4. PM decides resolution: retry, re-scope, or escalate to PO.

### 10.3 No Automatic Recovery
Agents must not self-initiate recovery from silent failure. All recovery is PM-directed.

---

## 11. Version History

| Version | Date       | Author     | Changes |
|---------|------------|------------|---------|
| 1.1     | 2026-05-06 | PM         | Adopt fixed agent worktree model and GitHub write boundary model. Worktree paths are now role+slot based, not PE-ID based. Gate 2 no longer auto-merges. Explicit write boundaries per role. |
| 1.0     | 2026-05-03 | PM         | Initial canonical consolidation from AGENTS.md, CLAUDE.md, ELIS_General_Guidance.md, LESSONS_LEARNED.md, and accumulated PM directives. |
