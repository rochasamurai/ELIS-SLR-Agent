# HANDOFF — PE-ARCH-10

## Status
Discovery / design opened; ready for validation.

## Scope
Verify repository placement, package conventions, TypeScript build/test pattern, and TaskFlow SDK import/API surface for a future inert controller prototype.

## Deliverables
- `docs/architecture/PE_ARCH_10_TaskFlow_Controller_Prototype_Placement.md`
- `HANDOFF.md`
- `.elis/pe/PE-ARCH-10/PE_TASK.md`

## Current facts
- The ELIS repo currently has no verified plugin/package tree for a controller prototype.
- Discovery notes document the managed TaskFlow surface as `api.runtime.tasks.flow` with alias `api.runtime.taskFlow`.
- This PE does **not** add controller source code.
- This PE does **not** add tests for missing controller code.
- This PE does **not** modify production OpenClaw config.
- This PE does **not** enable Lobster in production.
- This PE does **not** run production PE workflows.
- This PE does **not** touch PR #390.

## Constraints
- discovery/design only
- no production config changes
- no production Lobster enablement
- no production PE workflow execution
- no controller implementation unless separately authorised
- do not resume PE-AGT-01
- do not resume PE-OPS-01 Increment 3

## Checks
- `python scripts/check_current_pe.py`
- canonical repo state — must remain clean
- repo layout evidence — must support the placement decision
- TaskFlow API alias evidence — must support the import conclusion

## Evidence to capture on validation
- file contents
- current commit hash
- check_current_pe result
- repo-layout evidence
- placement decision

## Next step
Validate the discovery note, then only if approved move toward a future implementation PE in the OpenClaw runtime repository.
