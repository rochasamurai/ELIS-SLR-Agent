# ELIS PE Dispatch Checklist

**Status:** Canonical — v1.2  
**Date:** 2026-05-16  
**Owner:** Carlos Rocha, Product Owner  
**Applies to:** ELIS PM (primary), Gatekeeper (advisory)  
**Authoritative sources:** AGENTS.md §2.4, ELIS_PE_Gatekeeper_Checklist.md, ELIS_Agent_Dispatch_Binding_and_Validation_Rules.md, ELIS_General_Guidance.md, LESSONS_LEARNED.md  
**Canonical record:** GitHub (this document and PE artefacts)

---

## 1. Purpose

This checklist ensures every PE dispatch follows a consistent, verifiable process. PM runs this sequence before dispatching any implementer or validator. Gatekeeper may use the same checks for its readiness verdict.

---

## 2. Pre-Dispatch Checklist

### 2.1 PE Registry and Plan

- [ ] PE is registered in CURRENT_PE.md Active PE Registry with status `planning`
- [ ] PE ID, domain, implementer-agentId, validator-agentId, branch, status, and last-updated are filled
- [ ] Alternation rule is satisfied: implementer engine alternates for consecutive same-domain PEs
- [ ] Validator engine is opposite to implementer engine
- [ ] CURRENT_PE.md Release context is current (Release, Base branch, Plan file, Plan location)
- [ ] CURRENT_PE.md Current PE table is updated (PE ID, Branch)
- [ ] Agent roles table reflects correct implementer and validator assignments
- [ ] Controlling plan file exists and lists the PE
- [ ] PE dependency chain is satisfied (all prerequisite PEs are `merged`)

### 2.2 Task Packet

- [ ] `.elis/pe/<PE-ID>/PE_TASK.md` exists
- [ ] Objective is clearly defined
- [ ] Branch matches CURRENT_PE.md
- [ ] Implementer and validator are listed
- [ ] Allowed files are enumerated
- [ ] Forbidden files are enumerated
- [ ] Required artefacts are listed (commit, HANDOFF, Status Packet, REVIEW)
- [ ] Acceptance criteria are defined
- [ ] Required commands are listed (including `check_current_pe.py`)
- [ ] Blocker reporting format is included

### 2.3 Workspace and Worktree Binding

#### 2.3.1 Runtime Workspace
- [ ] Agent OpenClaw runtime workspace is correctly bound:
  - `infra-impl-b` → `/home/samurai/openclaw/workspace-infra-impl-b`
  - `infra-val-a` → `/home/samurai/openclaw/workspace-infra-val`
  - `pm` → `/home/samurai/openclaw/workspace-pm`
- [ ] Runtime workspace is distinct from the authorised Git worktree (different paths)
- [ ] Persistent identity/context files reside in the runtime workspace, not in the Git worktree

#### 2.3.2 Git Worktree
- [ ] Worktree exists at `/opt/elis/agent-worktrees/<role>-<slot>` (fixed workspace — e.g. `infra-impl-b`, not a PE-ID-based path)
- [ ] Worktree is isolated (no other active agent writes here)
- [ ] Worktree branch matches the PE branch in CURRENT_PE.md
- [ ] Worktree is on the correct base branch commit (`git rebase origin/$BASE` is current)
- [ ] Worktree is clean or has only approved staged changes
- [ ] No persistent runtime/bootstrap files (`.openclaw/`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, `USER.md`) exist inside the Git worktree
- [ ] Fixed Workspace Binding Certificate can be produced — agent will include in opening Status Packet
- [ ] Wrong-worktree quarantine understood: any path mismatch stops all work immediately
- [ ] No-copy rule understood: agents never copy/transfer files between worktrees
- [ ] Persistent agent runtime files (AGENTS.md, SKILLS.md, SOUL.md, tool manifests, OpenClaw/Hermes bootstrap) are outside the fixed worktree — only disposable repo/task state lives inside
- [ ] No OpenClaw workspace binding to `/opt/elis/repo`
- [ ] No shared mutable working directory between active agents

### 2.4 Provider and Rate-Limit Readiness

- [ ] OpenClaw gateway is running (`openclaw gateway status`)
- [ ] Required providers are authenticated (API keys, OAuth tokens configured)
- [ ] Model accessibility confirmed (model responds to test request)
- [ ] No active 429 rate-limit backlog
- [ ] No usage-limit messages in recent platform logs
- [ ] If Codex OAuth: token is valid and not expired
- [ ] If token estimate is unavailable, use conservative behaviour

### 2.5 Artefact Gates

- [ ] Implementer artefact gates are defined:
  - [ ] Commit with descriptive message
  - [ ] Changed file list
  - [ ] Tests/checks run (black, ruff, pytest)
  - [ ] HANDOFF.md with Status Packet
  - [ ] `python scripts/check_current_pe.py` passes
- [ ] Validator artefact gates are defined:
  - [ ] REVIEW.md or verdict packet
  - [ ] Explicit PASS, FAIL, or BLOCKED verdict
  - [ ] Tests/checks run independently
  - [ ] Evidence section with fenced code block(s)
  - [ ] PR comment + formal GitHub PR review

### 2.6 Implementer Start

- [ ] Implementer has a fresh session ID (`<PE-ID>-impl-YYYYMMDD-HHMMSS`)
- [ ] Implementer session is bound to the assigned worktree
- [ ] Implementer knows the current commit hash of the base branch
- [ ] Implementer has read CURRENT_PE.md and PE_TASK.md (Step 0 complete)

### 2.7 Validator Start

- [ ] Implementer has committed: HANDOFF.md, implementation commits, Status Packet
- [ ] Gate 1 has passed or CI bot has assigned the Validator
- [ ] Validator has explicit PM or CI-bot assignment (`@agent — assigned as Validator. Begin review.`)
- [ ] Validator has a fresh session ID (`<PE-ID>-val-YYYYMMDD-HHMMSS`)
- [ ] Validator session uses a fixed validation workspace (`/opt/elis/agent-worktrees/<role>-<slot>`, distinct from implementer workspace)
- [ ] Validator fixed workspace has been reset: clean state, correct branch checked out
- [ ] Validator knows the implementer's commit SHA
- [ ] Validator runtime workspace is correctly bound (e.g. `infra-val-a` → `/home/samurai/openclaw/workspace-infra-val`)
- [ ] Validator authorised Git worktree is checked out to the feature branch (not detached HEAD) — the validator reviews from the approved branch

---

## 3. Dispatch Decision

After completing the checklist, PM decides:

| Condition | Action |
|-----------|--------|
| All checks pass | Dispatch implementer or validator |
| Fixed worktree issue | Reset fixed workspace or create PE branch; recheck |
| Registry/plan issue | Fix CURRENT_PE.md or PE_TASK.md; recheck |
| Provider/rate-limit issue | Platform Monitor investigates; recheck |
| Task packet incomplete | PM completes task packet; recheck |
| GitHub boundary violation | Report to PM; do not dispatch; escalate to PO |
| PO decision needed | Escalate to PO; wait for resolution |

---

## 4. Post-Dispatch Verification

- [ ] Agent confirms correct fixed worktree path (Step 0 output evidence — must match role+slot path)
- [ ] Agent confirms correct branch for the current PE
- [ ] Agent confirms task packet is accessible
- [ ] PM receives Status Packet at start of implementation/validation
- [ ] Watchdog confirms artefacts after implementer commit
- [ ] No GitHub write operations originated from the wrong role or workspace

---

## 5. Version History

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.2     | 2026-05-16 | PE-closeout | Add runtime workspace binding checks for all agents. Split worktree into workspace and worktree subsections. Add fixed worktree exclusion rule (no persistent files). Remove detached-head requirement for validators — they use the same feature branch. Add validator workspace binding items. |
| 1.1     | 2026-05-06 | PM     | Adopt fixed workspace paths. Add GitHub write boundary gates to artefact checklist. Update worktree, implementer start, validator start sections for fixed workspaces. |
| 1.0     | 2026-05-03 | PM     | Initial canonical consolidation. |
