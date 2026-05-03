# PE-ARCH-10 — Verify Task Flow Controller Prototype Placement and API Imports

## Type
Discovery / design only

## Objective
Confirm repository placement, package conventions, TypeScript build/test pattern, and TaskFlow SDK import/API surface for a future inert controller prototype.

## Scope
- verify where plugin/controller code belongs
- verify whether `plugins/taskflow-controller-prototype` is a valid future location
- verify the TaskFlow import/API surface and trusted binding path
- verify whether the future prototype can stay inert and avoid production config changes
- verify test placement/conventions for a future prototype
- record the exact file list for a later implementation PE

## Constraints
- do not add controller source code
- do not add tests for missing controller code
- do not modify production OpenClaw config
- do not enable Lobster in production
- do not run production PE workflows
- do not resume PE-AGT-01
- do not resume PE-OPS-01 Increment 3
- do not touch PR #390

## Roles
- Implementer: `infra-impl-a`
- Validator: `infra-val-b`

## Suggested files
- `docs/architecture/PE_ARCH_10_TaskFlow_Controller_Prototype_Placement.md`
- `HANDOFF.md`

## Required checks
- `python scripts/check_current_pe.py`
- repo layout inspection for plugin/package conventions
- evidence for TaskFlow API alias / import surface
- canonical repo cleanliness
- confirmation that no production config changes are required

## Acceptance criteria
1. Repo placement is documented with evidence.
2. TaskFlow import/API surface is documented with evidence.
3. Test/package conventions for a future prototype are documented.
4. Production config remains untouched.
5. The future PE-ARCH-11 implementation file list is captured.
6. The task packet is readable without relying on chat history.
