# Architecture Decision Records

This directory stores the Architecture Decision Records (ADRs) for the ELIS SLR Agent project.

---

## What is an ADR?

An Architecture Decision Record captures a significant architectural decision:
the context that prompted it, what was decided, why, and what alternatives were
considered and discarded. ADRs are permanent audit history — they are never
deleted, only superseded.

---

## Numbering convention

Files are named `ADR-NNN-title-in-kebab-case.md`, where `NNN` is a zero-padded
three-digit integer assigned in creation order, starting at `001`.

Do not reuse numbers. If an ADR is superseded, keep the original file and update
its status field; create a new ADR for the replacement decision.

---

## Template

```markdown
# ADR-NNN: Decision Title

**Status:** Proposed | Accepted | Superseded by ADR-XXX | Deprecated
**Date:** YYYY-MM-DD
**Deciders:** [role or agent names]

## Context

What situation or constraint prompted this decision?
What problem needed to be solved?

## Decision

What was decided, in affirmative form. One decision per ADR.

## Consequences

### Positive
- …

### Negative / trade-offs
- …

## Alternatives considered

### Alternative A — [name]

[Description of the alternative and why it was discarded.]

### Alternative B — [name]

[Description of the alternative and why it was discarded.]

## Evidence / references

Links to PRs, LESSONS_LEARNED entries, or external sources that informed the
decision or confirmed the outcome.
```

---

## Status lifecycle

| Status | Meaning |
|---|---|
| `Proposed` | Under discussion; not yet adopted |
| `Accepted` | Adopted and currently in effect |
| `Superseded by ADR-XXX` | Replaced by a later decision; kept for history |
| `Deprecated` | No longer applies; not replaced |

---

## Creation rules

A new ADR **must** be created when any of the following occur:

- a structural choice is made that affects how PEs, agents, branches, or CI
  interact (e.g., worktree strategy, role alternation, merge policy)
- a previously-trialled approach is discarded in favour of a different one
  (e.g., rejecting symlinks for HANDOFF, rejecting Docker for native runtime)
- a new cross-cutting capability is introduced to the workflow
  (e.g., parallel tracks, session continuity model)
- a retrospective reveals that the team made a significant undocumented design
  choice that has driven subsequent decisions

An ADR is **not** required for:

- routine PE implementation choices (file layout, variable names, test structure)
- temporary fixes or workarounds expected to be revisited within one PE
- changes already fully documented in `LESSONS_LEARNED.md` that do not affect
  workflow structure

---

## Index

| ADR | Title | Status | Date |
|---|---|---|---|
| [ADR-001](ADR-001-two-agent-alternation-model.md) | Two-agent alternation model | Accepted | 2026-03-26 |
| [ADR-002](ADR-002-git-worktrees-pe-isolation.md) | Git worktrees for PE isolation | Accepted | 2026-03-26 |
| [ADR-003](ADR-003-parallel-track-model.md) | Parallel track model | Accepted | 2026-03-26 |
| [ADR-004](ADR-004-handoff-copy-not-symlink.md) | HANDOFF as generated copy, not symlink | Accepted | 2026-03-26 |
| [ADR-005](ADR-005-agent-browser-rejected-for-auth.md) | Agent browser rejected for auth | Accepted | 2026-03-26 |
| [ADR-006](ADR-006-openclaw-as-native-runtime.md) | OpenClaw as native orchestration runtime | Accepted | 2026-03-26 |
| [ADR-007](ADR-007-adoption-of-multica-as-task-orchestration-layer.md) | Adoption of Multica as task orchestration layer | Accepted | 2026-04-11 |
| [ADR-008](ADR-008-distinct-github-review-identities-for-active-agents.md) | Distinct GitHub review identities for active agents | Accepted | 2026-04-13 |

---

*ELIS SLR Agent · docs/decisions/README.md · PE-PLAN-01*
