# PE-ARCH-08A — Discover Task Flow Plugin Controller Surface

## Objective
Determine the minimal safe OpenClaw plugin/controller needed for ELIS to create and manage a Task Flow around the isolated Lobster self-test.

## Scope
- confirm plugin SDK access to `api.runtime.taskFlow`
- identify where an ELIS plugin/controller should live
- determine whether `createManaged` / `runTask` / `setWaiting` / `resume` / `finish` are sufficient
- determine how to bind a trusted session key safely
- determine how Task Flow state/revisions are inspected via CLI
- determine whether a harmless Task Flow can wrap `lobster-test` without production side effects

## Constraints
- discovery-only
- no production config changes
- no production PE workflow execution
- no actual Task Flow controller implementation unless separately authorised
- do not touch PR #390
- PE-AGT-01 remains held
- Increment 3 remains paused

## Roles
- Implementer: `infra-impl-a`
- Validator: `infra-val-b`

## Expected deliverable
- short discovery doc or HANDOFF-style report only

## Suggested files
- `docs/discovery/ELIS_TaskFlow_Plugin_Controller_Surface.md`
- `HANDOFF.md`

## Verification
- `python scripts/check_current_pe.py`
- confirm worktree path matches this PE
- confirm canonical repo remains clean
