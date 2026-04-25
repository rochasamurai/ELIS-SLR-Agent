# ADR-014: Control-plane workflow wiring

**Status:** Accepted
**Date:** 2026-04-24
**Deciders:** [PM, CODEX]

## Context

The v1.9 architecture keeps development agents local-first on `elis-server`
while preserving GitHub Actions as the bounded control plane for CI, guard
validation, dispatch, and audit evidence. Previous runner automation had the
right broad shape, but the boundary was not expressed as a reusable check:
future workflow edits could accidentally move Codex or Claude coding entrypoints
back to `ubuntu-latest`, or make CI workflows depend on bot credentials.

PE-INFRA-SLR-08 needs the workflow wiring to align with the state-machine
contract introduced by ADR-013 and with the review archive migration completed
by PE-INFRA-SLR-07.

## Decision

Development-agent coding entrypoints are allowed only in the local agent runner
workflows:

- `.github/workflows/implementer-runner.yml`
- `.github/workflows/validator-runner.yml`

Those workflows must run on the self-hosted `elis-server` execution surface.
GitHub-hosted workflows may verify guards, post comments/statuses, dispatch the
local runners, merge when gate conditions are satisfied, and report audit
evidence. They must not invoke Codex or Claude development-agent coding
entrypoints.

When a PR branch already contains complete implementer evidence but
`CURRENT_PE.md` still records `implementing`, validator dispatch may observe the
`implementing -> gate-1-pending` guard and then dispatch through
`gate-1-pending -> validating` in one bounded control-plane step. This keeps the
registry state machine authoritative while avoiding a manual registry edit as a
precondition for automated Gate 1 dispatch.

Portable CI workflows remain bounded to formatting, linting, validation, and
tests, and must not depend on bot/App credentials.

The boundary is enforced by `scripts/check_control_plane_wiring.py` and covered
by `tests/test_control_plane_workflow_wiring.py`.

## Consequences

### Positive

- The local-first development-agent boundary is testable instead of purely
  prose-based.
- Dispatch scripts now consume the canonical state-machine helpers rather than
  duplicating string checks.
- Model-agnostic validator assignment uses the existing resolver instead of
  brittle provider-name substring matching.

### Negative / trade-offs

- Workflow files that legitimately gain a new bounded role may need the
  control-plane check updated at the same time.
- The check is intentionally conservative: new agent coding entrypoints must be
  explicitly classified rather than silently accepted.

## Alternatives considered

### Keep the boundary documented only in architecture prose

Rejected because prose alone would not catch accidental workflow drift.

### Ban all agent-like scripts from GitHub-hosted workflows

Rejected because SLR workflow envelopes may still run bounded research tasks on
GitHub. The prohibition is specifically on development-agent coding entrypoints
that belong on the local `elis-server` surface.

## Evidence / references

- `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_9.md`
- `docs/workflow/PE_STATE_MACHINE.md`
- `elis/workflow_state_machine.py`
- `scripts/check_control_plane_wiring.py`
- `tests/test_control_plane_workflow_wiring.py`
