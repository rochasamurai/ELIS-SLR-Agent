# <PE-ID> — <PE Objective>

## Overview
This template defines the structured approach for implementing a PE within the ELIS multi-agent system.

## Objective
<What this PE accomplishes. One to three sentences.>

## Repository Structure
- Canonical repository: `/opt/elis/repo`
- Assigned worktree root: `/opt/elis/agent-worktrees/`
- Assigned worktree: `/opt/elis/agent-worktrees/<role>-<slot>` (fixed workspace — e.g. `infra-impl-b`)
  - Implementer: `/opt/elis/agent-worktrees/<implementer-role-slot>`
  - Validator: `/opt/elis/agent-worktrees/<validator-role-slot>`

## Branch
`feature/<pe-id-branch-name>`

## Implementer
`<implementer-agent-id>`

## Validator
`<validator-agent-id>`

## Controlling Documents
- `CURRENT_PE.md` — active PE assignment and registry
- `docs/governance/ELIS_PE_Operating_Protocol.md` — PE lifecycle and role boundaries
- `docs/governance/ELIS_PE_Dispatch_Checklist.md` — dispatch readiness
- `docs/governance/ELIS_Worktree_Preflight_Checklist.md` — worktree safety
- `docs/governance/ELIS_Provider_Preflight_Checklist.md` — provider readiness
- `docs/governance/ELIS_No_Silent_Failure_Recovery.md` — artefact and evidence requirements

## Fixed Workspace Safety Practices
- No OpenClaw workspace directly bound to `/opt/elis/repo`
- No shared mutable working directory between active agents
- Mandatory wrong-path checks before execution: `pwd`, `git rev-parse --show-toplevel`, `git branch --show-current`
- Path must match the agent's fixed workspace (`/opt/elis/agent-worktrees/<role>-<slot>`), not a per-PE path
- All artefacts committed to fixed workspace only; no writes to canonical repo
- Fixed workspace reset at start of each PE: fetch + clean + checkout correct branch + rebase onto `origin/$BASE`
- **Runtime workspace distinct:** The OpenClaw runtime workspace (e.g. `/home/samurai/openclaw/workspace-infra-impl-b`) is a different path from the authorised Git worktree (e.g. `/opt/elis/agent-worktrees/infra-impl-b`)
- **Fixed worktree exclusion:** No persistent runtime/bootstrap files (`.openclaw/`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, `USER.md`) may exist inside the Git worktree
- **Fixed Workspace Binding Certificate** required in opening Status Packet (see `docs/governance/ELIS_PE_Operating_Protocol.md §5.1b`) — must include runtime workspace, authorised Git worktree, and write scope
- **Wrong-worktree quarantine:** if path does not match, stop immediately, do not copy/commit files, report to PM
- **No-copy rule:** never copy or transfer files between worktrees; use commit+fetch from correct worktree
- **Persistent vs disposable separation:** runtime/context files (AGENTS.md, SKILLS.md, SOUL.md, tool manifests, OpenClaw/Hermes bootstrap) reside outside worktree in the runtime workspace; only repo/task state lives inside the Git worktree
- GitHub write boundary: implementer/validator/supervisor do not push/PR/merge. PM does not write to GitHub directly. Only GitHub Agent executes remote GitHub writes after explicit PM/PO approval.
- **Validator readiness:** The validator authorised Git worktree is checked out to the same feature branch as the implementer (not detached HEAD).

## Allowed Files
- <list files this PE may create or modify>

## Forbidden Files
- <list files this PE must not touch>
- Do not modify files outside the allowed list
- Do not run blanket permission changes (e.g. `chmod +x scripts/*.py`)
- Do not run broad destructive commands (`rm -rf`, `git reset --hard`, `git clean -fdx`) without PO approval

## Deliverables
- <list required artefacts: files to create, modify, or produce>
- `HANDOFF.md` (update — must include Status Packet)
- Commit with descriptive message

## Acceptance Criteria
- [ ] <AC-1: description>
- [ ] <AC-2: description>
- [ ] <AC-3: description>

## Required Commands
- `python scripts/check_current_pe.py`
- <other PE-specific checks>

## Blocker Reporting Format
```text
BLOCKER: <description>
Evidence: <command output or file excerpt>
Suggested resolution: <what needs to happen>
```

## Status
- [ ] Initial setup completed (worktree, branch, preflight)
- [ ] Implementation completed
- [ ] Required checks run
- [ ] HANDOFF.md updated
- [ ] Artefacts committed

---

## Artefact Validation
Required artefacts:
- HANDOFF.md (Status Packet included)
- Implementation commits
- check_current_pe.py passes
- No forbidden files modified
