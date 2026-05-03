# HANDOFF — PE-ARCH-08A

## Status
Opened for discovery only.

## Scope
Determine the minimal safe OpenClaw plugin/controller needed for ELIS to create and manage a Task Flow around the isolated Lobster self-test.

## Current facts
- Task Flow CLI exists (`openclaw tasks flow list/show/cancel`).
- A verified public create/run CLI was not found.
- A documented plugin/runtime API surface is now expected to be the likely path for creation/execution.

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
Run read-only discovery and prepare a short report on the plugin/controller surface.
