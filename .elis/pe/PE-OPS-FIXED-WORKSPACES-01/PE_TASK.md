# PE-OPS-FIXED-WORKSPACES-01 — PE Task Packet

## PE_ID
PE-OPS-FIXED-WORKSPACES-01

## Objective
Replace the PE-specific worktree model with a fixed agent workspace model and enforce a strict write-boundary rule.

## Background
ELIS governance must move from PE-scoped worktrees to agent-scoped fixed workspaces. GitHub remains the permanent system of record. Each agent has a fixed semi-persistent workspace, not a fully disposable one.

## Governance lane
Strict PE

## Reason PE-GOV-RISK-TIER-01 is paused
PE-GOV-RISK-TIER-01 is preserved as blocked pending fixed-workspace governance. This PE must not silently overwrite the active PE state.

## Fixed agent workspace model
Each agent writes only to its own fixed workspace path, bound to agent identity rather than PE ID.

Agent runtime/context files must be preserved or regenerated during workspace reset.
Disposable repo/task state may be cleaned after PE commit/PR/merge, abandonment, or supersession.

Preserve unless explicitly authorised:
- AGENTS.md
- SKILLS.md
- SOUL.md
- agent profile/config/context files
- tool manifests
- OpenClaw/Hermes bootstrap files required for agent operation

Cleanup must target only disposable repository/task state, stale branches, uncommitted PE outputs, build artefacts, and temporary files.

Canonical examples:
- /opt/elis/agent-worktrees/pm
- /opt/elis/agent-worktrees/infra-impl-a
- /opt/elis/agent-worktrees/infra-impl-b
- /opt/elis/agent-worktrees/infra-val-a
- /opt/elis/agent-worktrees/infra-val-b
- /opt/elis/agent-worktrees/github-agent

## System of record
GitHub is the permanent system of record. Local agent workspaces are fixed, semi-persistent execution workspaces.

## Agent write-boundary rule
- PM writes only to the PM workspace.
- Implementers write only to their own implementer workspace.
- Validators write only to their own validator workspace.
- Supervisor writes only to its own diagnostic/workspace area if explicitly allowed.
- PO Advisor has no repo/worktree/GitHub write authority.
- No PM, Implementer, Validator, Supervisor, or PO Advisor may push, open PRs, merge, comment, label, approve, request changes, or otherwise write to GitHub directly.
- GitHub Agent may write to GitHub only after explicit PM/PO approval, under the applicable governance lane.
- No agent may write to another agent’s workspace.

## Required documents
### Opening / planning
- CURRENT_PE.md
- .elis/pe/PE-OPS-FIXED-WORKSPACES-01/PE_TASK.md

### Deliverable scope
- AGENTS.md
- docs/governance/ELIS_PE_Operating_Protocol.md
- docs/governance/ELIS_GitHub_Agent_Operating_Model.md
- docs/governance/ELIS_Worktree_Preflight_Checklist.md
- docs/governance/ELIS_PE_Dispatch_Checklist.md
- docs/templates/PE_TASK.template.md
- docs/templates/HANDOFF.template.md
- docs/governance/ELIS_PO_Advisor_Operating_Model.md only if needed
- docs/governance/ELIS_OpenClaw_Native_Operating_Model.md only if needed
- docs/governance/ELIS_No_Silent_Failure_Recovery.md only if needed

## Acceptance gates
- pre-dispatch fixed workspace certificate
- workspace reset-to-clean procedure
- approved branch/base checkout
- proof of pwd, git root, branch, HEAD, and clean status
- post-run proof that writes occurred only inside the agent’s own fixed workspace
- confirmation no GitHub write occurred except by GitHub Agent
- wrong-worktree quarantine rule
- no-copy rule for wrong-worktree output

## Wrong-worktree quarantine rule
If an agent writes in the wrong workspace, quarantine the output, do not copy it into the correct workspace, and treat the run as invalid until explicitly re-established in the correct fixed workspace.

## No-copy rule
Wrong-worktree output must never be copied, replayed, or reused as canonical deliverable content.

## Opening-step restrictions
- opening edits are limited to CURRENT_PE.md and .elis/pe/PE-OPS-FIXED-WORKSPACES-01/PE_TASK.md
- do not edit deliverable governance/template files during opening
- do not dispatch implementer during opening
- do not modify Hermes/OpenClaw config
- do not perform GitHub actions
- do not push/open PR/merge during opening

## Out of scope
- Hermes/OpenClaw config changes
- dispatching implementers
- GitHub actions
- PR creation
- merges
- non-governance code changes

## Implementation deliverables
- Update governance documents to define the fixed workspace model
- Define the GitHub write-boundary rule and GitHub Agent exception
- Define fixed-workspace preflight and quarantine behavior
- Define PE task and handoff template requirements for workspace evidence
- Preserve PE-GOV-RISK-TIER-01 as blocked pending this governance

## Validation deliverables
- Verify all governance language is internally consistent
- Verify acceptance gates are explicit and testable
- Verify wrong-worktree and no-copy rules are unambiguous
- Verify no config/dispatch/PR/merge actions are introduced
- Verify the blocked state for PE-GOV-RISK-TIER-01 is preserved

## Acceptance criteria
This PE is acceptable when the governance texts clearly establish:
1. fixed agent workspace ownership,
2. GitHub as system of record,
3. strict write boundaries,
4. GitHub Agent exception only with explicit approval,
5. required preflight and proof gates,
6. wrong-worktree quarantine,
7. no-copy rule,
8. preservation of PE-GOV-RISK-TIER-01 as blocked pending this governance.
