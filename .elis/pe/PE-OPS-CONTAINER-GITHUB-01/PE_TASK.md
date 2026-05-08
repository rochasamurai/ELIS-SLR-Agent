# PE-OPS-CONTAINER-GITHUB-01 — Containerise ELIS GitHub Agent Runtime

## PE_ID
PE-OPS-CONTAINER-GITHUB-01

## Objective
Pilot a containerised execution boundary for the ELIS GitHub Agent so authorised GitHub writes can run as `elis-git-bot` without relying on host Linux-user/ACL workarounds.

## Background
The host-based `elis-github` / ACL approach exposed repeated runtime mismatches because OpenClaw routes subagents but does not reliably run them as per-agent Linux users. This PE moves the GitHub Agent execution boundary into a containerised runtime while keeping OpenClaw as the orchestration layer.

## Relationship to PE-OPS-GITHUB-02
PE-OPS-GITHUB-02 established the GitHub Agent deployment evidence and the host-level access boundaries that were needed to reach a valid closeout state. This PE reuses that evidence as input, but must not weaken the existing write boundary or reopen broad GitHub write access to implementers.

## GitHub Agent authority and prohibitions
The containerised GitHub Agent may write only to:
1. its own approved runtime/workspace boundary
2. GitHub, only after explicit PM/PO approval under the applicable governance lane

The containerised GitHub Agent may:
- read approved implementation and validation packets
- push approved branches
- open PRs
- update PR body/metadata
- report PR checks, status, and mergeability
- publish validator verdicts when explicitly approved
- merge only after explicit PO approval

The containerised GitHub Agent must not:
- write to PM, implementer, validator, Supervisor, PO Advisor, or other agent workspaces
- edit implementation files outside the approved packet
- bypass failed validation
- merge without explicit PO approval
- change repo settings, secrets, tokens, or branch protection unless separately authorised
- act outside the approved PE scope

## Required capabilities
- GitHub-authenticated branch push for approved work
- PR creation and metadata updates
- check/status reporting
- merge coordination under PO approval
- evidence capture for each GitHub action
- role separation from implementer and validator duties
- container runtime proof that the agent can execute as `elis-git-bot`

## Host cleanup review scope (post-pilot only)
Do not remove or weaken any of the following until the container pilot passes:
- `elis-github` Linux user
- `elis-github-secrets` group
- ACLs granting `samurai` read access to `/opt/elis/agent-worktrees/github-agent`
- runtime/context files copied into the GitHub Agent worktree
- `/opt/elis/agent-worktrees/github-agent.linked-backup.20260508T141916`
- `/tmp/github-agent-preserve`
- `/opt/elis/secrets/github-agent.env` ownership and permission model

Cleanup must be documented with rollback steps before any removal or narrowing.

## Opening file scope
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-CONTAINER-GITHUB-01/PE_TASK.md`

## Implementation file scope to be proposed/pinned before dispatch
- `ELIS_Containerised_GitHub_Agent_Runtime_Plan.md` (now present on `main`) or a migrated copy in the appropriate docs path
- GitHub Agent container runtime / runbook documentation
- controlled host cleanup checklist for the previous Linux-user / ACL workaround

## Out of scope
- implementation file edits during opening
- Docker, OpenClaw, Hermes, or GitHub config changes during opening
- secrets, tokens, or permissions changes during opening
- branch protection changes during opening
- bypassing failed validation
- code implementation work
- merging without PO approval

## Validation deliverables
- containerised GitHub Agent identity is explicit and verified as `elis-git-bot`
- container runtime boundary is defined and auditable
- approved GitHub capabilities are enumerated
- host cleanup is gated behind a successful pilot
- token/config questions are diagnosed before any deployment change
- evidence requirements exist for GitHub actions

## Acceptance criteria
- containerised GitHub Agent can perform approved GitHub operations as `elis-git-bot`
- PM cannot read the GitHub token
- GitHub Agent can push/open PR only through the approved container path
- old ACLs/helpers/users are either removed or explicitly retained with justification
- no secret/token/config changes occur in the opening step
- merge still requires explicit PO approval

## Rollback / evidence requirements
- preserve the pre-change state of workspace binding, token/config references, and repository permissions
- record the exact identity used for GitHub operations
- capture PR URL/number, branch SHA, and check status for every GitHub action
- if container changes fail, revert the smallest changed surface and report the failure before retrying

## Opening-step restrictions
- do not edit implementation files yet
- do not dispatch the implementer yet
- do not modify OpenClaw/Hermes/GitHub config or secrets
- do not push/open PR/merge
- check Docker / Docker Compose availability in Supervisor before implementation dispatch
- keep opening limited to `CURRENT_PE.md` and `.elis/pe/PE-OPS-CONTAINER-GITHUB-01/PE_TASK.md`
