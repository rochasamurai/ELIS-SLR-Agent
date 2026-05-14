# PE-OPS-CONTAINERS-02 — ELIS Advisor Hermes Container Pilot

## Objective
Prepare the first controlled container boundary for ELIS Advisor on Hermes, with rollback-first planning only.

## Scope
- ELIS Advisor only
- plan a low-risk container boundary
- preserve identity, mounts, logs, rollback, and secret isolation
- no OpenClaw production agent changes

## Constraints
- no live runtime changes
- no service restart
- no production container launch
- no Docker socket mount
- no broad `/home/samurai` or `/opt/elis` mount
- no `.env` contents in logs/evidence/messages
- no GitHub/Gateway, A2A, Dash, model/provider, PM, implementer, or validator runtime changes

## Planning outputs
- `.elis/pe/PE-OPS-CONTAINERS-02/HANDOFF.md`
- `.elis/pe/PE-OPS-CONTAINERS-02/implementation-plan.md`
- `.elis/pe/PE-OPS-CONTAINERS-02/rollback-plan.md`
- `.elis/pe/PE-OPS-CONTAINERS-02/runtime-inventory.md`
- `.elis/pe/PE-OPS-CONTAINERS-02/validation-evidence.md`
- `.elis/pe/PE-OPS-CONTAINERS-02/wrong-branch-recovery.md`
