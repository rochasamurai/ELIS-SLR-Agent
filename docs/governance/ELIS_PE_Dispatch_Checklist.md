# ELIS PE Dispatch Checklist

**Status:** Canonical — v1.0  
**Date:** 2026-05-03  
**Owner:** Carlos Rocha, Product Owner  
**Applies to:** ELIS PM (primary), Gatekeeper (advisory)  
**Authoritative sources:** AGENTS.md §2.4, ELIS_PE_Gatekeeper_Checklist.md, ELIS_General_Guidance.md, LESSONS_LEARNED.md  
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

### 2.3 Worktree

- [ ] Worktree exists at `/opt/elis/agent-worktrees/<PE-ID>-<agent-id>`
- [ ] Worktree is isolated (no other active agent writes here)
- [ ] Worktree branch matches the PE branch in CURRENT_PE.md
- [ ] Worktree is on the correct base branch commit (`git rebase origin/$BASE` is current)
- [ ] Worktree is clean or has only approved staged changes
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
- [ ] Validator session uses a separate validation worktree
- [ ] Validator knows the implementer's commit SHA

---

## 3. Dispatch Decision

After completing the checklist, PM decides:

| Condition | Action |
|-----------|--------|
| All checks pass | Dispatch implementer or validator |
| Worktree issue | Fix worktree; recheck |
| Registry/plan issue | Fix CURRENT_PE.md or PE_TASK.md; recheck |
| Provider/rate-limit issue | Platform Monitor investigates; recheck |
| Task packet incomplete | PM completes task packet; recheck |
| PO decision needed | Escalate to PO; wait for resolution |

---

## 4. Post-Dispatch Verification

- [ ] Agent confirms correct worktree path (Step 0 output evidence)
- [ ] Agent confirms correct branch
- [ ] Agent confirms task packet is accessible
- [ ] PM receives Status Packet at start of implementation/validation
- [ ] Watchdog confirms artefacts after implementer commit

---

## 5. Version History

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.0     | 2026-05-03 | PM     | Initial canonical consolidation. |
