# HANDOFF — PE-ARCH-09

## Status
Draft completed; ready for validation.

## Scope
Design the minimal OpenClaw plugin/controller needed to create and manage a Task Flow around the isolated Lobster self-test.

## Deliverables
- `docs/architecture/ELIS_Minimal_Task_Flow_Controller_for_Lobster_Self_Test.md`
- `HANDOFF.md`

## Current facts
- The design is minimal and TaskFlow-based.
- It uses the managed TaskFlow surface only.
- It keeps Lobster isolated and off production config.
- It does not implement the controller.
- It does not authorise production PE workflow execution.
- It does not create PRs, push, or merge.

## Constraints
- design only
- no production config changes
- no production Lobster enablement
- no production PE workflow execution
- no controller implementation unless separately authorised
- do not resume PE-AGT-01
- do not resume PE-OPS-01 Increment 3
- do not touch PR #390

## Checks
- `python scripts/check_current_pe.py` — to run in this worktree
- canonical repo state — must remain clean
- worktree path — must match PE-ARCH-09

## Evidence to capture on validation
- file contents
- current commit hash
- check_current_pe result
- worktree cleanliness

## Next step
Run validation against the design artefacts and confirm the task flow boundary remains minimal and side-effect free.
