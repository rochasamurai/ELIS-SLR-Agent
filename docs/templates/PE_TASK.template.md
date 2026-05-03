# <PE-ID> — <PE Objective>

## Overview
This template defines the structured approach for implementing a PE within the ELIS multi-agent system.

## Objective
<What this PE accomplishes. One to three sentences.>

## Repository Structure
- Canonical repository: `/opt/elis/repo`
- Assigned worktree root: `/opt/elis/agent-worktrees/`
- Assigned worktree: `/opt/elis/agent-worktrees/<PE-ID>-<agent-id>`

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

## Worktree Safety Practices
- No OpenClaw workspace directly bound to `/opt/elis/repo`
- No shared mutable working directory between active agents
- Mandatory wrong-path checks before execution: `pwd`, `git rev-parse --show-toplevel`, `git branch --show-current`
- All artefacts committed to worktree only; no writes to canonical repo
- Rebase onto `origin/$BASE` before starting if other PEs merged since branch creation

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
