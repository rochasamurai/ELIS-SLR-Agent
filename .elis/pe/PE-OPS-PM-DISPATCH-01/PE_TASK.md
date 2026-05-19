# PE-OPS-PM-DISPATCH-01 — Deterministic PM Dispatch Wrapper

**Approved branch:** `feature/pe-ops-pm-dispatch-01-deterministic-pm-dispatch-wrapper`  
**Baseline:** `origin/main @ a790d605b673aa42fec7f17c805d8c7ce88c4aa2`  
**Lane:** Strict  
**Implementer:** `infra-impl-b`  
**Validator:** `infra-val-a`  
**Date opened:** 2026-05-19

---

## Objective

Implement a deterministic PM dispatch wrapper that only supports Phase 1 dry-run / check / generate behaviour for the opening packet. The wrapper must validate the approved packet shape, keep the scope bounded to the approved files, and explicitly avoid calling live dispatch APIs.

---

## Approved file scope

- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-PM-DISPATCH-01/PE_TASK.md`
- `.elis/pe/PE-OPS-PM-DISPATCH-01/HANDOFF.md`
- `docs/governance/ELIS_PM_Dispatch_Wrapper.md`
- `scripts/pm_dispatch.py`
- `tests/test_pm_dispatch.py`
- `tests/test_pm_dispatch_contract.py`

---

## Phase 1 gates

1. Dry-run only.
2. Check the opening packet contract.
3. Generate the packet in deterministic JSON form.
4. Do not call live dispatch APIs.
5. Do not replace live dispatch behaviour.
6. Do not alter files outside the approved scope.

---

## Acceptance criteria

- `scripts/pm_dispatch.py` supports Phase 1 dry-run / check / generate modes only.
- The wrapper emits a deterministic packet for the approved PE.
- The packet includes objective, branch, baseline, lane, implementer, validator, exact file scope, Phase 1 gates, tests, rollback, hard stops, and the explicit no-live-dispatch statement.
- `CURRENT_PE.md` opens the PE and assigns the approved roles.
- `PE_TASK.md` and `HANDOFF.md` exist under `.elis/pe/PE-OPS-PM-DISPATCH-01/`.
- The approved tests pass.
- No OpenClaw/Hermes config, auth, secret, service, or runtime files are changed.

---

## Tests to run

- `python -m pytest tests/test_pm_dispatch.py -q`
- `python -m pytest tests/test_pm_dispatch_contract.py -q`

---

## Hard stops

- Do not touch `openclaw.json`.
- Do not call live dispatch APIs.
- Do not restart services.
- Do not push, open PRs, or merge.
- Do not change auth/secret state.
- Do not alter files outside the approved scope.
