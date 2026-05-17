# PE-OPS-ADVISOR-CUTOVER-01 — Finalise ELIS Advisor Production Handoff / Cutover

## PE_ID
PE-OPS-ADVISOR-CUTOVER-01

## Objective
Open the ELIS Advisor production handoff/cutover on Hermes, including ownership, runtime boundary, monitoring/log validation, rollback, secret handling, identity preservation, and confirmation that only one Advisor gateway/session is active.

## Background
ELIS Advisor has an existing operational handoff. This PE formalises the cutover boundary and the evidence required before any runtime transition work.

## Staffing
- Implementer: `infra-impl-a`
- Validator: `infra-val-b`

## Branch
`feature/pe-ops-advisor-cutover-01`

## Opening scope
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-ADVISOR-CUTOVER-01/PE_TASK.md`

## Opening pass scope
- update current PE metadata
- create the PE task artefact
- define the cutover objective, boundaries, evidence gates, and rollback expectations
- no live cutover execution in the opening pass

## Hard boundaries
- no Hermes service restart
- no OpenClaw restart
- no config edits
- no secret/auth changes
- no Advisor cutover execution
- no GitHub writes, push, PR, or merge
- no implementer dispatch until PO approves opening
- no validator dispatch until PO approves opening

## Acceptance criteria
- PE metadata is opened on the approved branch
- PE task exists and states the cutover objective clearly
- opening scope is restricted to metadata only
- runtime/service/config/secret boundaries are explicit
- evidence gates and rollback expectations are documented
- no dispatch occurs before PO approval

## Evidence requirements
- `git status -sb`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git remote -v`
- diff showing only the approved opening files
- clean status after commit

## Rollback plan
- revert `CURRENT_PE.md`
- remove `.elis/pe/PE-OPS-ADVISOR-CUTOVER-01/PE_TASK.md`
- delete the feature branch if required
- reset the worktree back to the verified `main` baseline
