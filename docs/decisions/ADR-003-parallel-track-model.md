# ADR-003: Parallel Track Model

**Status:** Accepted
**Date:** 2026-03-26
**Deciders:** PM (Carlo Rocha), CODEX, Claude Code

## Context

The 2-Agent workflow executes PEs sequentially by default: one PE is
implemented, validated, and merged before the next begins. This guarantees
simplicity and avoids merge conflicts, but it also means that when a freed
agent (the one not assigned to the current PE) is idle, its capacity is wasted.

For PEs with non-overlapping file scopes, there is no technical reason to
serialise: both agents could work on independent PEs simultaneously. The
question was whether to formalise this as an operational model.

The concern was over merge conflicts: if two branches both modify the same
files, concurrent work produces conflicts that add resolution cost and risk.
This means eligibility for parallelism must be verified, not assumed.

## Decision

Two PEs may execute in parallel when both of the following hold:

1. **Structural eligibility:** the PE pair has no mutual dependency in the plan
   (neither PE is listed as a prerequisite of the other).
2. **Empirical eligibility:** `check_parallel_eligibility.py` confirms that
   the two branches have non-overlapping file scopes
   (`git diff --name-only origin/main..branch` for each; intersection must be
   empty).

The maximum concurrency is two active PEs at once (one per agent).

When Track A completes, the freed agent waits for Track B to reach Gate 1
(ready-for-validation) before beginning cross-track validation. It does not
begin validation whilst Track B is still implementing.

## Consequences

### Positive
- Both agents remain productive when PEs are independent.
- Total wall-clock time for the project is reduced when eligible PE pairs exist.
- The eligibility check is automated and auditable.

### Negative / trade-offs
- Adds coordination overhead: PM must identify eligible pairs, run the
  eligibility check, and manage two concurrent PE states.
- If branches diverge from main significantly, a previously-eligible pair may
  become ineligible mid-flight.
- Requires both agents to be available simultaneously.

## Alternatives considered

### Alternative A — Always sequential

PEs always execute one at a time, regardless of independence.

Discarded because it leaves one agent permanently idle during the other's PE,
wasting capacity that could be used on genuinely independent work.

### Alternative B — Parallelism with more than two concurrent PEs

Allow three or more PEs simultaneously.

Discarded because it exceeds the two-agent capacity of the current model.
With only two agents, maximum concurrency is two PEs. More concurrent tracks
would require additional agents or human oversight that is not currently
available.

## Evidence / references

- `ELIS_2Agent_Automation_Plan_v2_0.md` §Parallel Track Model (v3.0)
- `scripts/check_parallel_eligibility.py` — automated eligibility checker
- **Empirical case:** PE-MS-07 (`feature/pe-ms-07-slr-project-store`) ran
  in parallel with the plan review in PR #299
  (`docs/review/REVIEW_ELIS_2Agent_Automation_Plan_v2_0.md`) — confirmed
  non-overlapping file scopes; both merged without conflicts
- PE-AUTH-01 ∥ PE-AUTH-02 — identified as structurally eligible by the plan
  (Phase C), pending empirical verification at the time of writing
