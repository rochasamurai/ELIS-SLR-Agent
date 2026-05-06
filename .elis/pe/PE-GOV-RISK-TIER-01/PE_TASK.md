# PE-GOV-RISK-TIER-01 — Add Risk-Tiered PE Protocol

## PE_ID
PE-GOV-RISK-TIER-01

## Title
Add Risk-Tiered PE Protocol

## Governance lane
Standard-Light PE

## Fixed base HEAD
`d3043bd` (`origin/main`)

## Branch
`feature/pe-gov-risk-tier-01-add-risk-tiered-pe-protocol`

## Worktree proposal
`/opt/elis/agent-worktrees/PE-GOV-RISK-TIER-01-gov-impl-a` (or assigned governance worktree)

## Objective
Define a proportional governance model for ELIS so low-risk documentation and planning work can move faster, while strict controls remain mandatory for code, runtime, config, secrets, permissions, CI, OpenClaw/Hermes/Discord/GitHub token changes, and deployment.

## Background
ELIS currently uses one broad PE flow for work with very different risk profiles. This PE introduces tiered governance so small repo-only corrections can be handled quickly, documentation/governance work stays reviewable, and platform-risking changes remain fully controlled.

## Opening file scope
- `CURRENT_PE.md`
- `.elis/pe/PE-GOV-RISK-TIER-01/PE_TASK.md`

## PE deliverable file scope
- `docs/governance/ELIS_PE_Operating_Protocol.md`
- `docs/governance/ELIS_PE_Dispatch_Checklist.md`
- `docs/templates/PE_TASK.template.md`
- `docs/governance/ELIS_Worktree_Preflight_Checklist.md` only if needed

## Out of scope
- editing the governance/template deliverable files during the opening step
- Hermes/OpenClaw config changes
- dispatching agents during opening
- implementation outside the PE plan
- validation beyond packet drafting at this stage
- PR/merge actions during opening
- secrets, permissions, runtime, CI, or token changes in this opening step

## Required three-lane protocol

### 1) Fast PM Chore
For simple non-code low-risk repo updates, including:
- `CURRENT_PE.md` corrections
- PE opening/closeout packets
- typo/status/changelog notes
- narrow documentation housekeeping

Flow:
- PM proposes exact change
- PO approves
- PM may commit, push, open PR, and merge if checks pass and files are limited
- no implementer/validator unless the change materially affects governance rules

### 2) Standard-Light PE
For documentation/governance operating models, templates, policies, and workflow docs.

Flow:
- PM opens PE
- Implementer writes
- Validator reviews
- PR opened
- PO approves merge
- reduced patch-by-patch approval
- focused validation

### 3) Strict PE
For code, runtime, config, secrets, permissions, CI, OpenClaw/Hermes/Discord/GitHub token changes, deployment, or anything that can break the platform.

Flow:
- full protocol required
- preflight
- explicit worktree
- allowed file scope
- implementer
- validator
- evidence packet
- rollback
- final PO approval

## Role boundaries
- **PM:** coordinate, route, and record governance state
- **Implementer:** draft the governing documents for the protocol
- **Validator:** review for completeness, clarity, and boundary correctness
- **Carlos/PO:** final approval authority for merge and scope exceptions

## Implementation deliverables
- `docs/governance/ELIS_PE_Operating_Protocol.md`
- `docs/governance/ELIS_PE_Dispatch_Checklist.md`
- `docs/templates/PE_TASK.template.md`
- `docs/governance/ELIS_Worktree_Preflight_Checklist.md` if needed

## Validation deliverables
- protocol clearly defines the three lanes
- Fast PM Chore is separated from Standard-Light and Strict PE
- strict controls remain mandatory for risky platform changes
- governance boundaries are explicit and auditable
- packet remains within opening-step scope

## Acceptance criteria
- three lanes are clearly defined
- each lane has a distinct flow
- low-risk work can move faster without weakening platform controls
- strict work still requires full controls
- implementer/validator/PO boundaries are unambiguous
- no-dispatch/no-config/no-merge restrictions are preserved for opening

## Opening-step restrictions
- do not edit the governance/template deliverable files yet
- do not dispatch the implementer yet
- do not modify Hermes/OpenClaw config
- do not push/open PR/merge
- keep the opening step limited to `CURRENT_PE.md` and `.elis/pe/PE-GOV-RISK-TIER-01/PE_TASK.md`
