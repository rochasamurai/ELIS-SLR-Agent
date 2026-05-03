# HANDOFF — PE-ARCH-08

## Status
Discovery completed; implementation commit in progress.

## Scope
Determine the minimal safe OpenClaw plugin/controller needed for ELIS to create and manage a Task Flow around the isolated Lobster self-test.

## Current facts
- Task Flow CLI exists (`openclaw tasks flow list/show/cancel`).
- The canonical runtime shape is `api.runtime.tasks.flow` (with `api.runtime.taskFlow` as alias).
- Managed TaskFlow lifecycle methods are documented: `createManaged`, `runTask`, `setWaiting`, `resume`, `finish`.
- The safe path for PE-ARCH-08 is a minimal managed wrapper around the isolated Lobster self-test, not a general controller.

## Constraints
- no production config changes
- no production PE workflow execution
- no controller implementation unless separately authorised
- no touch of PR #390
- keep Lobster off production

## Checks
- `python scripts/check_current_pe.py` — pending in this worktree
- canonical repo state — must remain clean

## Next step
Commit the discovery artefacts, run `python scripts/check_current_pe.py`, and keep the worktree clean.
