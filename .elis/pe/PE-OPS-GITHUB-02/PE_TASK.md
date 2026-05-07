# PE-OPS-GITHUB-02 — Deploy ELIS GitHub Agent

## PE_ID
PE-OPS-GITHUB-02

## Objective
Deploy and configure the ELIS GitHub Agent under the fixed workspace and GitHub write-boundary model so it can perform authorised GitHub operations without bypassing implementation, validation, or approval controls.

## Background
PE-OPS-FIXED-WORKSPACES-01 established the fixed workspace and GitHub write-boundary model. This PE operationalises that model for GitHub-specific execution, with GitHub Agent write authority separated from implementer and validator duties.

## Fixed GitHub Agent workspace
`/opt/elis/agent-worktrees/github-agent`

## Relationship to PE-OPS-FIXED-WORKSPACES-01
PE-OPS-FIXED-WORKSPACES-01 defines the fixed workspace and write-boundary doctrine.
PE-OPS-GITHUB-02 implements the GitHub Agent deployment/configuration required to use that doctrine safely.
This PE must not weaken the boundary model or reintroduce broad GitHub write access to implementers.

## GitHub Agent authority and prohibitions
The GitHub Agent may write only to:
1. its own fixed workspace: `/opt/elis/agent-worktrees/github-agent`
2. GitHub, only after explicit PM/PO approval under the applicable governance lane.

The GitHub Agent may:
- read approved implementation and validation packets
- push approved branches
- open PRs
- update PR body/metadata
- report PR checks, status, and mergeability
- publish validator verdicts when explicitly approved
- merge only after explicit PO approval

The GitHub Agent must not:
- write to PM, implementer, validator, Supervisor, PO Advisor, or other agent workspaces
- edit implementation files
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

## Expected config/token questions to diagnose before any deployment change
- Which GitHub identity/token backs the GitHub Agent?
- Is the workspace binding to `/opt/elis/agent-worktrees/github-agent` already provisioned and valid?
- Are any OpenClaw, Hermes, or Discord config changes needed to expose the agent safely?
- Do GitHub permissions or branch protection settings require separate authorisation?
- Can the required write boundary be enforced without granting broader write access to implementers?

## Opening file scope
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-GITHUB-02/PE_TASK.md`

## Implementation file scope to be proposed/pinned before dispatch
- deployment/configuration docs or runbook files required to safely define the GitHub Agent
- GitHub-boundary governance docs required by the PE task packet
- any additional file scope must be explicitly pinned before dispatch

## Out of scope
- implementation file edits during opening
- Hermes/OpenClaw config changes during opening
- secrets, tokens, or permissions changes during opening
- branch protection changes during opening
- bypassing failed validation
- code implementation work
- merging without PO approval

## Validation deliverables
- GitHub Agent role and boundary model are explicit
- fixed workspace binding is defined and verified
- approved GitHub capabilities are enumerated
- prohibitions are explicit and enforceable
- token/config questions are diagnosed before any deployment change
- evidence requirements exist for GitHub actions

## Acceptance criteria
- fixed workspace is clearly identified
- GitHub Agent capabilities are limited to authorised GitHub operations
- implementers remain unable to perform broad GitHub writes by default
- validator boundaries remain intact
- no secret/token/config changes occur in the opening step
- merge still requires explicit PO approval

## Rollback / evidence requirements
- preserve the pre-change state of workspace binding, token/config references, and repository permissions
- record the exact identity used for GitHub operations
- capture PR URL/number, branch SHA, and check status for every GitHub action
- if deployment changes fail, revert the smallest changed surface and report the failure before retrying

## Opening-step restrictions
- do not edit implementation files yet
- do not dispatch the implementer yet
- do not modify OpenClaw/Hermes/GitHub config or secrets
- do not push/open PR/merge
- keep opening limited to `CURRENT_PE.md` and `.elis/pe/PE-OPS-GITHUB-02/PE_TASK.md`
