# PE-ARCH-09 — Minimal Task Flow Controller for Lobster Self-Test

## Objective
Design the smallest safe TaskFlow controller needed to wrap the isolated Lobster self-test without adding production dispatch side effects.

## Scope
- define the minimal controller responsibilities for a managed TaskFlow around the Lobster self-test
- specify the flow lifecycle, state fields, and completion/blocked transitions
- define how the controller binds to a fresh trusted session and an assigned PE worktree
- identify the smallest required runtime checks and artefacts for a harmless self-test run
- confirm the controller stays design-first and does not widen OpenClaw execution authority

## Constraints
- design-only unless a later PE explicitly authorises implementation
- no production OpenClaw config changes
- no automatic push / PR / merge
- no changes to `/opt/elis/repo`
- no validator or implementer dispatch from the design artefact itself
- PE-OPS-01 remains paused
- Increment 3 remains paused

## Roles
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`

## Suggested files
- `docs/architecture/ELIS_Minimal_Task_Flow_Controller_for_Lobster_Self_Test.md`
- `HANDOFF.md`

## Expected deliverable
A short architecture/design note that specifies the minimal TaskFlow controller for the Lobster self-test, including the controller boundary, the required state/data fields, the safe start/stop conditions, and the no-side-effect rules.

## Required checks
- `python scripts/check_current_pe.py`
- confirm the canonical repo remains clean
- confirm the task packet points at the correct PE worktree
- confirm the design does not require production config changes

## Acceptance criteria
1. The controller boundary is explicit and minimal.
2. The Lobster self-test remains harmless and isolated.
3. The design names the required TaskFlow state, lifecycle, and evidence expectations.
4. The design does not authorise production dispatch, merge, or runtime config changes.
5. The task packet is usable by implementer and validator without relying on chat history.
