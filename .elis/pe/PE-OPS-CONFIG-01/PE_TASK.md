# PE-OPS-CONFIG-01 — PE-specific Agent Profile Binding Procedure

## Objective
Define and document the safe binding procedure for PE-specific agent profiles, session resets, and thread/worktree attribution so PM can transition to PE-OPS-CONFIG-01 without stale or misbound state.

## Status
Governance-only planning PE. Implementer/validator binding is TBD / blocked pending profile creation and safe binding verification.

## Setup Evidence
- Profile created and verified: `pe-ops-config-01-impl`
- Workspace binding verified: `/opt/elis/agent-worktrees/PE-OPS-CONFIG-01-impl`
- Worktree is a real ELIS Git worktree
- Verified HEAD: `294459694fe38f00968af298bc04c3de5552a3e7`
- Bootstrap evidence preserved: `/opt/elis/agent-worktrees/PE-OPS-CONFIG-01-impl.bootstrap-evidence.20260504T154049Z`
- Infra-impl-a/b unchanged
- No routing bindings added
- No secrets/auth profile changes made
- OpenClaw config changed only to add `pe-ops-config-01-impl`
- No implementer/validator dispatch occurred

## Repository
Canonical repo: `/opt/elis/repo`
Assigned worktree: TBD / blocked pending profile creation
Branch: `feature/pe-ops-config-01-pe-specific-agent-profile-binding-procedure`

All state-repair and documentation work must remain inside the authorised repo/worktree and must not modify OpenClaw agent profile files.

## Implementer
TBD / blocked pending profile creation

## Validator
TBD / blocked pending safe binding

## Allowed files
- `CURRENT_PE.md`
- `HANDOFF.md`
- `docs/governance/ELIS_PE_Operating_Protocol.md`
- `docs/governance/ELIS_PE_Dispatch_Checklist.md`
- `docs/governance/ELIS_Worktree_Preflight_Checklist.md`
- `docs/governance/ELIS_No_Silent_Failure_Recovery.md`
- `docs/governance/ELIS_Discord_PO_PM_Checkpoint_Governance.md`
- `docs/templates/PE_TASK.template.md`
- `docs/templates/HANDOFF.template.md`
- `docs/templates/REVIEW.template.md`
- `.elis/pe/PE-OPS-CONFIG-01/PE_TASK.md`

## Forbidden changes
- Do not modify OpenClaw agent profile files.
- Do not modify `~/.openclaw/openclaw.json`.
- Do not dispatch implementer or validator.
- Do not push, open PR, merge, or clean quarantined worktrees.
- Do not touch PE-ARCH-12 implementation artefacts.

## Acceptance criteria
1. `CURRENT_PE.md` reflects PE-OPS-CONFIG-01.
2. A PE-OPS-CONFIG-01 task packet exists.
3. No OpenClaw profile/config changes are made.
4. No dispatch occurs before safe binding is verified.
5. PE-OPS-WORKTREE-01 forensic diff remains preserved until explicitly resolved.

## Required artefacts
- CURRENT_PE.md update
- PE_TASK.md
- forensic evidence retained in git diff until repair completes

## Blocker reporting format
If blocked, report:
- blocker class
- exact file/path
- exact mismatch
- smallest safe next step
