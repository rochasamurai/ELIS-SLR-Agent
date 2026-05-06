# ELIS GitHub Agent Operating Model

## 1. Purpose
This document defines the operating model for a dedicated ELIS GitHub Agent that performs write-capable GitHub operations under explicit gates, while preserving ELIS auditability, role separation, and Carlos/PO approval authority.

## 2. Scope
In scope:
- GitHub Agent role definition
- permission boundaries by role
- allowed and forbidden GitHub operations
- PR, check, label, comment, review, and merge gates
- identity verification rules
- evidence packet requirements
- manual fallback path when automation fails

Out of scope:
- OpenClaw runtime/config changes
- ELIS code implementation
- merge authority without Carlos/PO approval
- unrelated platform recovery procedures

## 3. Role Model
### 3.1 GitHub Agent
A permanent ELIS role with PE-scoped activation. It is the only role intended to perform write-capable GitHub operations by default. The GitHub Agent executes authorised GitHub operations; it does not independently approve scope, validation, or merge.

### 3.2 PM
Owns PE coordination, authorization checkpoints, and fallback escalation.

### 3.3 Implementer
Produces branch work and implementation artefacts. No broad GitHub write by default.

### 3.4 Validator
Performs independent review. Read-only by default unless an explicit review/comment surface is authorised.

### 3.5 Carlos / PO
Final approval authority for merge, scope exceptions, and any escalation that changes repository state.

## 4. Identity Model
- GitHub operations use permanent bot identities.
- GitHub Agent activation is PE-scoped.
- Identity must be verified before any write-capable GitHub action.
- GitHub identity and execution identity are not assumed to be the same thing.
- The Discord exec approval loop is separate from GitHub protected-branch and bot-identity risk.

## 5. Permission Matrix
### 5.1 GitHub Agent
Allowed:
- create/update PRs
- push branches when authorised
- read and report checks
- add labels/comments when authorised
- request reviews when authorised
- report mergeability and gate status

Forbidden:
- merge without explicit Carlos/PO approval
- act outside the authorised PE scope
- bypass branch protection
- fabricate evidence or checks

### 5.2 Implementer
Allowed:
- local branch work
- commit implementation changes in the PE worktree
- produce handoff evidence

Forbidden:
- broad GitHub write by default
- PR creation unless explicitly authorised
- merge
- branch protection changes

### 5.3 Validator
Allowed:
- read repository state
- review PRs when explicitly authorised
- comment or review only on an authorised surface
- limited GitHub write access, if authorised, to review/comment artefacts only

Forbidden:
- broad GitHub write by default
- branch push
- file edits
- merge
- self-review
- altering implementation files unless explicitly authorised

### 5.4 PM
Allowed:
- authorize GitHub operations
- choose fallback path
- monitor gates and evidence

Forbidden:
- merging without Carlos/PO approval
- bypassing identity or gate checks

## 6. Allowed and Forbidden Operations
### Allowed
- branch push under explicit authorisation
- PR creation under explicit authorisation
- checks reporting
- label/comment/review-request actions when authorised
- merge review coordination

### Forbidden
- direct merge without Carlos/PO approval
- unauthorised PR mutation
- unauthorised label or comment actions
- actions from stale, wrong, or unverified identity contexts
- bypassing protected-branch rules

## 7. PR / Check / Merge Gates
A GitHub operation is permitted only when the following are true:
- PE is active and scoped
- identity is verified
- branch and commit context match the PE
- required evidence packet is present
- the requested action is within the role boundary
- merge has explicit Carlos/PO approval

Merge never occurs automatically without explicit Carlos/PO approval.

## 8. Evidence Packet
Every GitHub operation must have a compact evidence packet including:
- PE_ID
- role and agent identity
- branch name
- commit SHA or PR number
- requested GitHub action
- gate status
- approval status
- fallback state, if any
- acting GitHub login
- token/credential source, if applicable
- CI/check status for PR/merge operations
- PR URL for PR operations
- merge SHA for merge operations
- timestamp and operator/session reference

## 9. Manual Fallback Path
When automation fails:
- preserve the attempted state and evidence
- do not silently retry across roles
- escalate to PM for fallback selection
- use the least-privilege manual path available
- keep Carlos/PO approval as the merge gate

## 10. Error / Risk Handling
- Discord exec approval loops are runtime-envelope issues, not GitHub self-review failures.
- GitHub protected-branch and bot-identity failures are separate risks and must be reported distinctly.
- Any identity mismatch, stale branch, or ambiguous authorisation state blocks the operation.

## 11. Open PO Decisions
- exact validator write surface for comments/reviews
- whether implementers may ever request PR creation
- whether manual fallback is PM-owned, GitHub-Agent-owned, or human-owned

## 12. Non-goals
- no OpenClaw config changes
- no automatic merge authority
- no implementation of GitHub automation outside this governance model
- no revision of unrelated PE rules

## 13. Cross-References
- `docs/decisions/ADR-011-github-actions-authority-for-portable-gates.md`
- `docs/openclaw/BOT_ACCOUNTS_SETUP.md`
- `docs/_active/GITHUB_SINGLE_ACCOUNT_VALIDATION_RUNBOOK.md`
- `docs/governance/ELIS_PE_Operating_Protocol.md`
- `docs/governance/ELIS_PE_Dispatch_Checklist.md`
- `docs/governance/ELIS_Discord_PO_PM_Checkpoint_Governance.md`
