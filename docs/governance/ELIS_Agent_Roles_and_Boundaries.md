# ELIS Agent Roles and Boundaries

**Status:** Canonical — v1.2
**Date:** 2026-05-16
**Owner:** Carlos Rocha, Product Owner
**Applies to:** All ELIS agents
**Canonical record:** GitHub (this document)

---

## 1. Purpose

Define who may do what in the ELIS multi-agent system, including the distinction each agent must maintain between its OpenClaw runtime workspace and its authorised Git worktree.

---

## 2. Authority Hierarchy

1. Carlos — final approval authority.
2. GitHub — canonical record of changes and evidence.
3. OpenClaw/Lobster — execution and orchestration.
4. Hermes — supervisory and advisory layer.

---

## 3. Agent Role Bindings

Every agent has two distinct environments:

| Role | Agent ID | OpenClaw Runtime Workspace | Authorised Git Worktree |
|------|----------|---------------------------|------------------------|
| Implementer (infra) | infra-impl-b | `/home/samurai/openclaw/workspace-infra-impl-b` | `/opt/elis/agent-worktrees/infra-impl-b` |
| Validator (infra) | infra-val-a | `/home/samurai/openclaw/workspace-infra-val` | `/opt/elis/agent-worktrees/infra-val-a` |
| PM | pm | `/home/samurai/openclaw/workspace-pm` | `/opt/elis/agent-worktrees/pm` |

### 3.1 Runtime Workspace (Persistent)

Agent identity, skills, memory, and runtime context that survive across PEs:
- `AGENTS.md`, `SKILLS.md`, `SOUL.md`, `MEMORY.md`, `IDENTITY.md`, `USER.md`
- Tool manifests and capability declarations
- OpenClaw/Hermes bootstrap and system configuration files
- Session continuity and context cache files

### 3.2 Authorised Git Worktree (Disposable)

Repo/task state for the current PE, reset at each PE boundary:
- Git working tree (source code, tests, docs)
- PE-specific artefacts: `HANDOFF.md`, `REVIEW_PE<N>.md`
- Files within the `.elis/` PE workspace tree

**Fixed worktree exclusion:** The Git worktree must never contain `.openclaw/`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, or `USER.md`. These belong exclusively in the runtime workspace.

---

## 4. Roles

### 4.1 ELIS PM
May:
- orchestrate PE flow
- assign implementers and validators
- request artefacts and evidence
- update governance records
- verify agent binding (runtime workspace + authorised Git worktree)

May not:
- edit implementation files or validation artefacts
- implement the PE
- validate the PE
- author REVIEW.md / REVIEW_PE*.md
- bypass validator or Gatekeeper controls
- approve merges on behalf of Carlos

Operating note:
- PM is a coordination-only role. It needs broad read-only visibility across the workspace, but narrow or no write authority.
- Future containerisation must enforce this boundary through filesystem permissions and mount design, so read access stays broad while write access remains narrowly scoped.

### 4.2 Implementer
May:
- modify only assigned files in the assigned Git worktree
- create implementation artefacts
- update HANDOFF.md when required
- produce Fixed Workspace Binding Certificate in the opening Status Packet

May not:
- modify unrelated files
- validate their own work
- merge, push, or create PRs unless explicitly authorised
- write persistent runtime files (`.openclaw/`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, `USER.md`) into the Git worktree

### 4.3 Validator
May:
- review artefacts and evidence on the authorised Git worktree
- write REVIEW.md / verdicts
- recommend PASS, FAIL, or BLOCKED
- produce Fixed Workspace Binding Certificate in the opening Status Packet

May not:
- modify implementation files
- repair the implementation as part of validation
- bypass evidence requirements
- write persistent runtime files into the Git worktree

Checklist note:
- Validation must explicitly confirm that PM did not author implementation artefacts or validation artefacts for the PE under review.

### 4.4 Gatekeeper
May:
- enforce governance checks
- verify workflow readiness
- block unsafe dispatch

May not:
- implement the PE
- validate implementation content as the final verdict owner

### 4.5 ELIS Platform Monitor
May:
- monitor health, logs, and recoverability
- classify failures
- report operational risk

May not:
- dispatch implementers or validators
- modify files
- change runtime configuration

### 4.6 ELIS PO Advisor
May:
- advise Carlos
- draft safe messages and summaries

May not:
- execute, dispatch, approve, push, merge, or modify files

### 4.7 Carlos
May:
- approve or reject major governance decisions
- authorise push, PR, merge, release, and continuation

### 4.8 Two-Agent Model
- Every PE must preserve the ELIS Two-Agent Model: one implementer and one independent validator.
- PM coordinates the workflow only; PM is not the third implementation or validation agent.

---

## 5. Boundary Rules

- Implementer and validator must remain separate.
- PM must not be substituted for either implementer or validator in the acceptance path.
- Validators are read-only by default.
- Recovery checks are read-only until a remediation task is explicitly assigned.
- No external agent output is authoritative until reflected in GitHub.
- Every PASS/FAIL/BLOCKED decision must include evidence.
- **Runtime workspace vs Git worktree:** Agents must keep these environments distinct. Runtime files (AGENTS.md, SKILLS.md, SOUL.md) live in the runtime workspace only. The Git worktree holds only disposable repo/task state.
- **Fixed worktree exclusion:** The Git worktree must not contain `.openclaw/`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, or `USER.md`.
- **Write scope:** Agents may write only to their authorised Git worktree. The runtime workspace is read-mostly and updated only for identity or skill changes.

---

## 6. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.2 | 2026-05-16 | PE-closeout | Add agent-specific runtime workspace / Git worktree binding table. Add fixed worktree exclusion rule. Add write scope boundary rule. Document persistent vs disposable distinction per agent. |
| 1.0 | 2026-05-03 | PM | Initial canonical consolidation. |
