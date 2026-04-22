# ADR-011: GitHub Actions authority for portable gates

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** [PM, CODEX, Claude Code]

## Context

The repository already runs `black`, `ruff`, validation jobs, and `pytest` in
GitHub Actions, but the workflow guide still framed pasted local command output
as the only valid evidence for those gates. That mismatch created two problems:

- merge authority was documented as if it depended on whichever agent or host
  ran commands locally
- `elis-server` was used operationally as the main local environment, but that
  role was not documented in the canonical workflow guidance

Phase A of the GitHub Actions CI Authority plan requires the repository guidance
to align with the actual open-source merge path: portable blocking gates run in
GitHub Actions, while local runs are for preflight feedback and diagnostics.

## Decision

GitHub Actions is the authoritative execution surface for portable blocking
gates (`black`, `ruff`, lint/validation, and `pytest`) on protected branches.
`elis-server` is the supported local preflight environment for maintainers and
agents, but local runs are advisory for merge authority.

## Consequences

### Positive
- Required checks are reproducible in the public PR flow and independent of
  agent-specific tokens or local machine state.
- `AGENTS.md` now matches the repository's existing CI enforcement model.
- Maintainers still have a documented local environment for quick feedback and
  environment-specific debugging.

### Negative / trade-offs
- Handoff and review artefacts must now distinguish between CI evidence and
  local diagnostic evidence.
- Environment-specific failures on `elis-server` may still require separate
  investigation even when portable CI is green.

## Alternatives considered

### Alternative A — Local `elis-server` runs remain authoritative

Rejected because it would make the merge gate depend on a private execution
surface rather than the reproducible GitHub PR workflow expected in an open
source project.

### Alternative B — Remove local testing guidance entirely

Rejected because maintainers and agents still need a documented preflight
environment for fast iteration, host-specific diagnostics, and parity checks.

## Evidence / references

- `docs/_active/GITHUB_ACTIONS_TEST_IMPROVEMENT_PLAN.md`
- `AGENTS.md`
- `CURRENT_PE.md`
