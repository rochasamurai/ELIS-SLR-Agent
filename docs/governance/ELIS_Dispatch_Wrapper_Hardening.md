# ELIS Dispatch Wrapper Hardening

## Purpose
This note records the Phase 1 hardening contract for the deterministic PM dispatch wrapper and the PO-side safe-start helper.

## Scope
Phase 1 is **dry-run / check / generate only**.

There are no live dispatch actions, no Discord API calls, no OpenClaw live calls, no config changes, no auth or secret changes, and no service restarts.

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

## Hardening rules
The PE must encode the following rules explicitly:
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

## Runtime/bootstrap allow-list policy
Approved OpenClaw runtime/bootstrap files are non-blocking only when all safety conditions are met:
- untracked or workspace-local;
- not staged;
- not modified tracked repository files;
- not part of the PE-approved file scope;
- not secret-bearing;
- not being committed;
- not masking unsafe PE residue.

Examples of allowed runtime/bootstrap artefacts:
- `AGENTS.md`
- `TOOLS.md`
- `USER.md`
- `HEARTBEAT.md`
- `SOUL.md`
- `IDENTITY.md`
- `.openclaw/`
- `memory/`
- `skills/`
- `canvas/`

All other dirty/untracked files remain dispatch blockers unless PO explicitly approves an exception.

## `pm_dispatch.py` Phase 1 contract
The PM wrapper must:
- remain dry-run / check / generate only;
- classify allowed runtime/bootstrap residue separately from blockers;
- block staged/tracked residue outside scope;
- validate the approved file scope, rules, and hard stops;
- refuse live dispatch behaviour.

## `po_dispatch.py` Phase 1 contract
The PO helper must:
- generate or verify only the safe PO→PM start sequence;
- require a dedicated PE thread;
- require `/reset` before opening the PE instruction;
- require the complete `RESET_BINDING_ACK_FORMAT`;
- block generic reset acknowledgements;
- remind that the opening starts from current `origin/main` and `CURRENT_PE.md` must be plan-complete unless explicitly resuming a PE.

## Phase 1 gates
1. Approved runtime/bootstrap residue does not block safe dispatch.
2. `po_dispatch.py` only generates/checks the start sequence and acknowledgement contract.
3. The approved file scope is honoured exactly.
4. Tests cover the false-positive allowance and the safety boundaries.
5. No live automation paths are present in Phase 1.

## Hard stops
- no Discord API automation
- no live message sending
- no OpenClaw/Hermes config changes
- no auth or secret changes
- no service restart
- no live dispatch replacement
- no GitHub push/PR/merge without PO approval
- no files outside the approved scope
