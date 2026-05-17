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

## Opening packet
- Lane: Strict
- Baseline HEAD: `20070320566b9c587eb6842598da74d74836e744`
- Branch: `feature/pe-ops-a2a-01-phase-1-communication-matrix-clean-opening`
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`

### Approved first-pass files
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-A2A-01/PE_TASK.md`
- `docs/governance/ELIS_A2A_Communication_Matrix.md`
- `docs/openclaw/ELIS_A2A_GATEWAY_SPEC.md`

### Explicit exclusions
- `schemas/a2a_envelope.schema.json`
- runtime code
- service units
- OpenClaw config
- Hermes config
- credentials/secrets/auth
- live routing changes

### Evidence requirements
- baseline HEAD on `origin/main`
- clean PM worktree before opening
- plan-complete `CURRENT_PE.md` before opening
- commit SHA, branch, diff summary, and clean status after opening

### Hard stops
- no A2A runtime deployment
- no service restart
- no OpenClaw/Hermes config mutation
- no credentials/secrets/auth changes
- no live inter-agent routing change
- no branch creation before PO approval
- no implementer/validator dispatch before PO approval

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
