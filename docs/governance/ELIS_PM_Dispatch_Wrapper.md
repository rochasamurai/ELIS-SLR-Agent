# ELIS PM Dispatch Wrapper

## Purpose

`PE-OPS-PM-DISPATCH-01` introduces a deterministic PM dispatch wrapper for the opening packet used by the PM. The wrapper is intentionally limited to Phase 1:

- dry-run
- check
- generate

It does not call live dispatch APIs and does not replace live dispatch behaviour.

## Approved scope

This PE is limited to:

- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-PM-DISPATCH-01/PE_TASK.md`
- `.elis/pe/PE-OPS-PM-DISPATCH-01/HANDOFF.md`
- `docs/governance/ELIS_PM_Dispatch_Wrapper.md`
- `scripts/pm_dispatch.py`
- `tests/test_pm_dispatch.py`
- `tests/test_pm_dispatch_contract.py`

## Wrapper contract

The wrapper produces a deterministic opening packet containing:

- objective
- branch
- baseline
- lane
- implementer
- validator
- exact file scope
- Phase 1 gates
- tests
- rollback
- hard stops
- explicit no-live-dispatch statement

## Interface

```bash
python scripts/pm_dispatch.py   --pe-id PE-OPS-PM-DISPATCH-01   --branch feature/pe-ops-pm-dispatch-01-deterministic-pm-dispatch-wrapper   --baseline "origin/main @ a790d605b673aa42fec7f17c805d8c7ce88c4aa2"   --lane Strict   --implementer infra-impl-b   --validator infra-val-a   --mode dry-run
```

### Modes

- `dry-run` — render the packet summary and confirm Phase 1 shape.
- `check` — render the packet summary and verify the approved PE artefacts exist in the clean PE worktree.
- `generate` — render the packet as JSON; optionally write it to a file if `--output` is provided.

## Hard stops

- Do not touch `openclaw.json`.
- Do not call live dispatch APIs.
- Do not restart services.
- Do not push, open PRs, or merge.
- Do not change auth/secret state.
- Do not alter files outside the approved scope.

## Phase 1 statement

Phase 1 only generates and checks dispatch contracts and does not call live dispatch APIs.
