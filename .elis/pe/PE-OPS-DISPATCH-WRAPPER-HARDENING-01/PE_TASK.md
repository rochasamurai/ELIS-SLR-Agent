# PE-OPS-DISPATCH-WRAPPER-HARDENING-01 — Harden PM Dispatch Wrapper and Add PO Dispatch Helper

## PE_ID
PE-OPS-DISPATCH-WRAPPER-HARDENING-01

## Objective
Harden the deterministic PM dispatch wrapper so approved OpenClaw runtime/bootstrap artefacts in fixed agent workspaces do not trigger false dispatch blocks, and add a PO-side helper to verify the safe PM start sequence for new PE/task flows.

## Baseline
`origin/main @ a486f05e8376afd227595b9f1ccad3f88369cf74`

## Branch
`feature/pe-ops-dispatch-wrapper-hardening-01`

## Lane
Strict

## Staffing
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`

## Phase 1
Phase 1 dry-run / check / generate only.

## Approved file scope
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-DISPATCH-WRAPPER-HARDENING-01/PE_TASK.md`
- `.elis/pe/PE-OPS-DISPATCH-WRAPPER-HARDENING-01/HANDOFF.md`
- `docs/governance/ELIS_Dispatch_Wrapper_Hardening.md`
- `scripts/pm_dispatch.py`
- `scripts/po_dispatch.py`
- `tests/test_pm_dispatch.py`
- `tests/test_pm_dispatch_contract.py`
- `tests/test_po_dispatch.py`

## Required rules
- `PRESERVED_RUNTIME_BOOTSTRAP_FILES_ARE_NOT_DISPATCH_BLOCKERS_RULE`
- `NEW_PE_REQUIRES_FRESH_THREAD_AND_RESET_ACK_RULE`
- `DISPATCH_CONTRACT_MUST_USE_TARGET_AGENT_WORKSPACE_RULE`
- `FRESH_VALIDATOR_SUBAGENT_DISPATCH_RULE`
- `VALIDATOR_MUST_NOT_USE_PM_WORKTREE_RULE`
- `VALIDATION_PASS_REQUIRES_PRIOR_RESET_ACK_RULE`
- `TARGET_REF_AVAILABLE_BEFORE_AGENT_BINDING_RULE`
- `FIXED_AGENT_WORKTREE_READINESS_BEFORE_DISPATCH_RULE`
- `ROLE_CORRECT_GIT_AUTHOR_IDENTITY_RULE`
- `COMPLETE_BRANCH_FILE_SCOPE_EVIDENCE_RULE`

## Runtime/bootstrap allow-list rule
Approved OpenClaw runtime/bootstrap files may be non-blocking only if all safety conditions in the packet are met. All other dirty/untracked files remain dispatch blockers unless PO explicitly approves an exception.

## `pm_dispatch.py` Phase 1 contract
- dry-run / check / generate only
- classify approved runtime/bootstrap residue separately from blockers
- block staged or modified tracked residue outside scope
- refuse live dispatch behaviour

## `po_dispatch.py` Phase 1 contract
- dry-run / check / generate only
- no Discord API calls
- no live message sending
- no thread creation
- no OpenClaw calls
- no repo mutation
- only generate/check the PO→PM start sequence and acknowledgement structure

## Phase 1 gates
1. Approved runtime/bootstrap residue does not block safe dispatch.
2. `po_dispatch.py` only generates/checks the safe start sequence.
3. The approved file scope is honoured exactly.
4. Tests cover both the false-positive allowance and the safety boundaries.
5. No live automation paths are present in Phase 1.

## Hard stops
- no Discord API automation
- no live message sending
- no OpenClaw/Hermes config changes
- no auth or secret changes
- no service restart
- no live dispatch replacement
- no GitHub push/PR/merge without PO approval
- no files outside approved scope
