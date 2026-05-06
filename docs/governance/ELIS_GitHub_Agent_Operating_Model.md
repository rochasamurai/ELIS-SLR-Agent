# ELIS GitHub Agent Operating Model

**Status:** Canonical — v1.1
**Date:** 2026-05-06
**Owner:** Carlos Rocha, Product Owner
**Applies to:** All ELIS agents with GitHub operations capability

## 1. Purpose
This document defines the GitHub Write Boundary Model for ELIS: the operating model that governs which roles may perform which GitHub write operations, under what gates, and with what approval. It supersedes ad-hoc permission patterns and codifies the boundary explicitly for every agent role.

## 2. Scope
In scope:
- Role-based permission boundaries for GitHub operations
- allowed and forbidden GitHub operations per role
- PR, check, label, comment, review, and merge gates
- identity verification rules
- evidence packet requirements
- manual fallback path when automation fails
- relationship to the fixed agent workspace model

Out of scope:
- OpenClaw runtime/config changes
- ELIS code implementation
- merge authority without Carlos/PO approval
- unrelated platform recovery procedures

## 3. Core Principle: No Default GitHub Write Access
No agent role has default GitHub write access. Every GitHub write operation requires:
1. The action is within the role's authorised boundary (see §5)
2. The agent's fixed workspace identity is verified
3. The PE is active and the branch is current
4. PM or PO has authorised the specific operation

## 4. Role Model
### 4.1 Implementer
Produces branch work and implementation artefacts in the fixed implementer workspace. Local git operations only (commit). No default remote write access.

**Workspace:** `/opt/elis/agent-worktrees/<role>-<slot>` (e.g. `infra-impl-b`)

### 4.2 Validator
Performs independent review. Local git operations only (commit REVIEW file, adversarial tests). PR comments and formal GitHub reviews when explicitly authorised by PM.

**Workspace:** `/opt/elis/agent-worktrees/<role>-<slot>` (e.g. `infra-val-a`)

### 4.3 PM
Owns PE coordination, authorisation checkpoints, and fallback escalation. Authorised for remote GitHub operations including push, PR creation, labels, comments.

### 4.4 GitHub Agent (Dedicated Bot)
A permanent ELIS role with PE-scoped activation for write-capable GitHub operations: push, PR lifecycle, labels, comments, review requests, check reporting. Does not independently approve scope, validation, or merge.

### 4.5 Carlos / PO
Final approval authority for merge, scope exceptions, and any escalation that changes repository state.

## 5. Permission Matrix

| Operation | Implementer | Validator | PM | GitHub Agent | PO/Carlos |
|-----------|-------------|-----------|----|-------------|-----------|
| Local commit | ✅ Allowed | ✅ Allowed | ✅ Allowed | N/A | N/A |
| git push (remote) | ❌ No | ❌ No | ✅ With PM discretion | ✅ When authorised | ❌ (delegates) |
| PR creation | ❌ No | ❌ No | ✅ With PM discretion | ✅ When authorised | ❌ (delegates) |
| PR merge | ❌ No | ❌ No | ❌ No | ❌ No | ✅ PO approval |
| PR comment | ❌ No | ✅ When authorised | ✅ With PM discretion | ✅ When authorised | ✅ |
| Formal GitHub review | ❌ No | ✅ When authorised | N/A | ❌ No | ✅ |
| Label management | ❌ No | ❌ No | ✅ With PM discretion | ✅ When authorised | ✅ |
| Branch protection changes | ❌ No | ❌ No | ❌ No | ❌ No | ✅ PO approval |
| Read repo state | ✅ Allowed | ✅ Allowed | ✅ Allowed | ✅ Allowed | ✅ Allowed |

### 5.1 Fixed Workspace Constraint
All agents are bound to their fixed workspace path. Remote GitHub operations must originate from the correct fixed workspace. A push or PR attempt from a wrong or unverified workspace path is a workflow violation regardless of role.

## 6. Allowed and Forbidden Operations
### Allowed
- local git commits in the fixed workspace (all execution roles)
- branch push under explicit PM authorisation (PM or GitHub Agent)
- PR creation under explicit PM authorisation (PM or GitHub Agent)
- checks reporting (GitHub Agent)
- PR comments and review requests when explicitly authorised (Validator, GitHub Agent)
- formal GitHub review when explicitly authorised (Validator)
- merge review coordination (PM)

### Forbidden
- any git push, PR creation, or merge by implementer or validator unless explicitly authorised
- direct merge without Carlos/PO approval (all roles)
- unauthorised PR mutation (any role)
- unauthorised label or comment actions (any role)
- actions from stale, wrong, or unverified fixed workspace identity (any role)
- bypassing protected-branch rules (any role)
- merging from the fixed implementer or validator workspace (implementer, validator)

## 7. PR / Check / Merge Gates
A GitHub write operation is permitted only when:
1. PE is active and scoped in CURRENT_PE.md
2. Agent fixed workspace identity is verified (pwd + git rev-parse --show-toplevel matches assigned path)
3. Branch and commit context match the PE
4. Required evidence packet is present (see §8)
5. The requested action is within the role boundary (see §5)
6. Merge has explicit Carlos/PO approval

Merge never occurs without explicit Carlos/PO approval. Gate 2 does not auto-merge.

## 8. Evidence Packet
Every GitHub write operation must have a compact evidence packet including:
- PE_ID
- role and agent identity (surface name, e.g. `infra-impl-b`)
- fixed workspace path
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
- Fixed workspace path mismatch blocks all GitHub operations, including local commits, until verified.

## 11. Non-goals
- no OpenClaw config changes
- no automatic merge authority
- no implementation of GitHub automation outside this governance model
- no revision of unrelated PE rules

## 12. Cross-References
- `docs/governance/ELIS_PE_Operating_Protocol.md` (worktree rules, fixed workspace model)
- `docs/governance/ELIS_Worktree_Preflight_Checklist.md` (path verification)
- `docs/governance/ELIS_PE_Dispatch_Checklist.md` (dispatch readiness)
- `docs/decisions/ADR-011-github-actions-authority-for-portable-gates.md`
- `docs/governance/ELIS_Discord_PO_PM_Checkpoint_Governance.md`

## 13. Version History

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.1     | 2026-05-06 | PM     | Adopt fixed workspace model. Replace bot-centric model with role-based permission matrix. Clarify no-default-write principle. Gate 2 no longer auto-merges. |
| 1.0     | 2026-05-03 | PM     | Initial GitHub Agent operating model. |
