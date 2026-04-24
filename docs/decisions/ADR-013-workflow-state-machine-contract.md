# ADR-013: Workflow State Machine Contract

**Status:** Accepted
**Date:** 2026-04-24
**Deciders:** [PM, CODEX]

## Context

The v1.9 architecture formalises PE lifecycle states, but the same labels and
guards also need to be discoverable by scripts, validators, and future PEs.
Without one reusable contract, workflow state can drift between architecture,
AGENTS.md, implementation plans, and CI/orchestration helpers.

## Decision

PE lifecycle state is governed by a first-class state-machine contract:

- `docs/workflow/PE_STATE_MACHINE.md` is the human-readable state and guard
  reference.
- `elis/workflow_state_machine.py` is the machine-readable mirror used by tests
  and validation scripts.
- `AGENTS.md`, the v1.9 architecture, and the active implementation plan must
  use the same canonical labels and guard names.

GitHub Actions may observe the state machine, validate guards, and dispatch
bounded workflow steps. It must not perform agent coding unless the current
state and execution-surface policy permit it.

## Consequences

### Positive

- State labels are no longer scattered as undocumented string sets.
- Transition guards are testable and visible to both agents.
- Future runner and archive PEs can depend on one lifecycle vocabulary.

### Negative / trade-offs

- Documentation and code must be kept aligned when the state machine changes.
- State-machine changes now require both documentation and targeted test updates.

## Alternatives considered

### Keep state labels only in `CURRENT_PE.md`

Rejected because `CURRENT_PE.md` is assignment state, not a reusable governance
contract. It is edited frequently and is not the right place to explain guards.

### Keep state labels only in architecture prose

Rejected because prose alone is not easy for scripts and tests to consume.

## Evidence / references

- `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_9.md`
- `ELIS_MultiAgent_Implementation_Plan_v1_9.md`
- `docs/workflow/PE_STATE_MACHINE.md`
- `elis/workflow_state_machine.py`
