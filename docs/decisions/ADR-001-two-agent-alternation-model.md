# ADR-001: Two-Agent Alternation Model

**Status:** Accepted
**Date:** 2026-03-26
**Deciders:** PM (Carlo Rocha), CODEX, Claude Code

## Context

The ELIS project uses two AI agents — CODEX and Claude Code — to implement
and validate each Planned Execution step (PE). Early in the project, roles
were informally assigned without a structural rule, leading to questions about
review independence and cognitive diversity: when the same agent always
validates its own peer's work, systematic blind spots can accumulate.

A structural alternation rule was needed to ensure that no agent holds a fixed
role across all PEs, and that the validator perspective rotates across the
project lifecycle.

## Decision

For consecutive PEs in the same domain, the Implementer engine must alternate
(`codex` ↔ `claude`). The Validator engine is always the opposite of the
Implementer engine for the same PE.

The active roles for each PE are recorded in `CURRENT_PE.md` (`Agent roles`
table and `Active PE Registry`). Both agents read this file as Step 0 and must
not infer their role from any other source.

## Consequences

### Positive
- Each agent reviews the other's work on alternating PEs, reducing accumulated
  blind spots.
- Role assignment is deterministic and auditable from the registry.
- No agent can accumulate persistent Validator or Implementer bias.

### Negative / trade-offs
- Agents cannot specialise: a strong Implementer session cannot be extended
  into the next PE without switching roles.
- PM must update `CURRENT_PE.md` at every PE transition (PM-CHORE).

## Alternatives considered

### Alternative A — Fixed roles per agent

CODEX always implements; Claude Code always validates (or vice versa).

Discarded because a single reviewer accumulates systematic blind spots over
a long project, and does not benefit from the perspective of having also been
the Implementer.

### Alternative B — PM chooses roles per PE based on task fit

PM selects the agent best suited to each PE regardless of history.

Discarded because this requires PM judgement at every PE transition, adds
governance overhead, and loses the audit-trail simplicity of a deterministic
rule.

## Evidence / references

- `CURRENT_PE.md` — active registry implementing this rule from PE-INFRA-01 onwards
- `AGENTS.md` §5.3 — alternation rule documented in workflow
- `ELIS_2Agent_Automation_Plan_v2_0.md` §Phase 0 — structural baseline
- Historical registry: PE-MS series (PE-MS-01 to PE-MS-08) shows strict
  alternation between `infra-impl-claude` and `infra-impl-codex` across all 8 PEs
