# PE-OPS-ADVISOR-HANDOFF-01 — Finalise ELIS Advisor Handoff and Operating Mode

## PE_ID
PE-OPS-ADVISOR-HANDOFF-01

## Objective
Make ELIS Advisor operationally useful on elis-server by giving it a stable, governed handoff and role context.

## Background
ELIS Advisor is already running on elis-server as a separate Hermes profile, Discord bot, and systemd service.

## Known details
- Hermes profile: `elis-advisor`
- Advisor channel: `<#1502602267931578378>`
- Advisor channel ID: `1502602267931578378`
- Service: `elis-advisor-gateway.service`
- Existing handoff file: `ELIS_ADVISOR_HANDOFF_elis-server_2026-05-09.md`

## Staffing
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`

## Branch
`feature/pe-ops-advisor-handoff-01-finalise-elis-advisor-handoff-operating-mode`

## Opening scope
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-ADVISOR-HANDOFF-01/PE_TASK.md`

## Approved implementation scope
- reference or evidence placement for `ELIS_ADVISOR_HANDOFF_elis-server_2026-05-09.md`
- concise Advisor bootstrap / operating-mode docs under `docs/ops/elis-advisor/`
- Advisor role boundaries
- Advisor request/response templates
- test of Advisor response to a PM validation/status packet

## Hard boundaries
Advisor must not dispatch, implement, validate officially, restart services, modify config/secrets, perform GitHub writes, open PRs, merge, or approve.

## Acceptance criteria
- Advisor handoff is governed and referenced as an evidence artefact
- concise Advisor operating mode / bootstrap document exists
- Advisor role boundaries are explicit
- Advisor request/response templates are explicit
- PM can access the handoff path or GitHub link
- Advisor can respond to a PM validation/status packet

## Reset / binding acknowledgement plan
1. Confirm fixed worktree bindings.
2. Confirm handoff path/link access.
3. Confirm no dispatch until explicit in-thread acknowledgement.

## Confirmation required before dispatch
- no OpenClaw/Hermes config changes
- no service changes/restarts
- no secret/token changes
- no Discord permission changes
- no GitHub write actions without explicit PO approval
- no PE-specific runtime worktrees
