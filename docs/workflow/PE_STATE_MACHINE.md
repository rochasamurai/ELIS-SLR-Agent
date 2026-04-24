# PE Workflow State Machine

This document is the human-readable governance contract for PE lifecycle state.
The machine-readable mirror lives in `elis/workflow_state_machine.py`.

## Canonical States

| State | Meaning |
|-------|---------|
| `planning` | PE is defined, but no implementer work has started yet. |
| `implementing` | Implementer is actively coding on `elis-server`. |
| `gate-1-pending` | Implementer has finished; `HANDOFF.md` and Status Packet evidence are complete; ready for validator assignment. |
| `validating` | Validator is actively reviewing on `elis-server`. |
| `gate-2-pending` | Validator has posted evidence and verdict; awaiting formal approval or merge automation. |
| `merged` | PR merged; PE complete. |
| `blocked` | A guard failed, a runner is unavailable, or an external dependency prevents progress. |
| `superseded` | PE was replaced by a newer governance decision. |

## Allowed Transitions

```text
planning -> implementing
implementing -> gate-1-pending
gate-1-pending -> validating
gate-1-pending -> blocked
validating -> gate-2-pending
gate-2-pending -> merged
gate-2-pending -> blocked
any active state -> superseded
```

## Transition Guards

### Implementer completion

The `implementing -> gate-1-pending` transition requires:

- HANDOFF.md is present and complete.
- Status Packet sections are complete.
- Handoff artefacts are committed on the PE branch.
- The runner observes a matching PE and branch pair.

### Validator authorisation

The `gate-1-pending -> validating` transition requires:

- Explicit PM authorisation is recorded.
- Validator assignment evidence is present.
- The PE remains active in `CURRENT_PE.md`.

### Review completion

The `validating -> gate-2-pending` transition requires:

- REVIEW evidence is present.
- A formal verdict is recorded in the REVIEW file.
- CI gates are not broken by validator artefacts.

### Merge approval

The `gate-2-pending -> merged` transition requires:

- CI is green.
- Required review approval is satisfied.
- No `pm-review-required` veto label is present.

## GitHub Actions Boundary

GitHub Actions may observe state, validate guards, post audit evidence, and
dispatch bounded workflow steps. It must not perform agent coding unless the
current state explicitly permits that action and the active execution-surface
policy allows it.

Portable CI gates remain authoritative for formatting, linting, validation, and
tests. Agent implementation and validation sessions remain governed by
`CURRENT_PE.md`, `AGENTS.md`, and this state-machine contract.
