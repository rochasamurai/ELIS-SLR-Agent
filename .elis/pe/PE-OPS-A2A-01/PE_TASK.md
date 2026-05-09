# PE-OPS-A2A-01 — Phase-1 A2A Communication Matrix

## PE_ID
PE-OPS-A2A-01

## Objective
Open Phase 1 of the A2A communication matrix for ELIS Advisor, ELIS PM, and ELIS Supervisor with read-only, governance-safe boundaries.

## Background
This PE defines the initial A2A operating surface for structured messages, evidence requests, advisory review, and read-only diagnostic/status exchange only.

## Opening file scope
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-A2A-01/PE_TASK.md`

## Core constraints
- A2A gateway remains local-only on `127.0.0.1`
- Phase-1 agents are only:
  - ELIS Advisor
  - ELIS PM
  - ELIS Supervisor
- Allowed communication pairs only:
  - Advisor ↔ PM
  - Advisor ↔ Supervisor
  - PM ↔ Supervisor
- No implementers, validators, GitHub Agent, or full OpenClaw agent inventory exposure in Phase 1
- No implementation, official validation, GitHub writes, service restarts, config edits, secret/token changes, PR creation, merges, or PO approvals via A2A

## Acceptance criteria
- Phase-1 agent set is limited to Advisor, PM, Supervisor
- Allowed pairs are limited to the three approved pairs
- A2A is local-only
- A2A remains read-only for governance, evidence, advice, and diagnostics
- Opening commit is metadata-only
- No code/config/service/secret changes occur in opening

## Out of scope
- implementation work
- validation work
- GitHub writes
- service restarts
- config edits
- secret/token changes
- PR creation or merges
- PO approvals
- dispatching the implementer before PO approval

## Handoff requirements
- Opening packet recorded in `CURRENT_PE.md`
- Task file created at the approved path
- Implementer dispatch deferred until PO approves the implementation packet
