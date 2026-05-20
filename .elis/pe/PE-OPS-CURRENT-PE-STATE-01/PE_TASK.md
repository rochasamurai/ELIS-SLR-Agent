# PE-OPS-CURRENT-PE-STATE-01 — Add Machine-Readable CURRENT_PE State

## PE_ID
PE-OPS-CURRENT-PE-STATE-01

## Objective
Move canonical PE machine state out of `CURRENT_PE.md` into structured state. `CURRENT_PE.md` becomes a validated human-readable summary only.

## Baseline
`origin/main @ f686e92ac64f9d174d2cf64b781ce95312d7a090`

## Branch
`feature/pe-ops-current-pe-state-01`

## Lane
Strict

## Staffing
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`

## Staffing rationale
Use merge-based alternation from the last merged same-domain ops PE in `CURRENT_PE.md`.
The most recent merged ops row is `PE-OPS-ADVISOR-01`, which uses `infra-impl-a`, so this PE must alternate to `infra-impl-b` with opposite validator `infra-val-a`.

## Approved file scope
- `CURRENT_PE.md`
- `.elis/state/current_pe.json`
- `schemas/current_pe.schema.json`
- `scripts/check_current_pe.py`
- `scripts/check_pe_opening_context.py`
- `scripts/pm_dispatch.py`
- `tests/test_check_current_pe.py`
- `tests/test_check_pe_opening_context.py`
- `tests/test_pm_dispatch.py`
- `tests/test_pm_dispatch_contract.py`
- `docs/governance/ELIS_Current_PE_State_Model.md`
- `.elis/pe/PE-OPS-CURRENT-PE-STATE-01/PE_TASK.md`
- `.elis/pe/PE-OPS-CURRENT-PE-STATE-01/HANDOFF.md`

## State model
- `.elis/state/current_pe.json` is the canonical machine-readable PE state.
- `schemas/current_pe.schema.json` is the canonical schema.
- `CURRENT_PE.md` is a human summary that must match the structured state.
- `scripts/check_current_pe.py` validates schema + JSON/CURRENT_PE consistency.
- Markdown string matching must not be the canonical machine validation mechanism.
- `elis/workflow_state_machine.py` is out of scope for this PE.

## Tests
- active PE JSON validates
- plan-complete / no-active-PE JSON validates
- JSON / `CURRENT_PE.md` mismatch fails
- missing required JSON fields fail
- invalid role pair fails
- stale branch / baseline fails where applicable
- `pm_dispatch.py` consumes structured state and does not treat Markdown as canonical source

## Hard stops
- do not create the branch before PO approval
- do not dispatch the implementer before `pm_dispatch.py` passes
- do not rely on Markdown string matching as canonical state
- do not change runtime/config/auth/service files
- do not restart services
