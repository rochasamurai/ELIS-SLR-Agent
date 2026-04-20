# ADR-009: Model-agnostic agent-ID slots

**Status:** Accepted
**Date:** 2026-04-19
**Deciders:** CODEX, PM

## Context

Active ELIS workflow surfaces still encoded model/provider names directly in
agent identifiers such as `infra-impl-codex` and `infra-val-claude`. That
created repeated governance churn whenever staffing or engine assignments
changed, and it made validation/dispatch scripts infer execution engines by
parsing provider tokens out of the identifier itself.

PE-INFRA-SLR-04 requires active PM/Implementer/Validator surfaces to become
model-agnostic while keeping dispatch compatibility, audit continuity, and a
clear migration path from the live identifiers already present in plans,
runtime configuration, and CURRENT_PE records.

## Decision

ELIS adopts a canonical agent-ID naming rule of `<domain>-<role>-<slot>` for
active workflow surfaces.

- Slot `a` maps to the current CODEX engine assignment.
- Slot `b` maps to the current Claude Code engine assignment.
- Slot `c` is reserved for guest or overflow engines such as Gemini.
- Legacy model-coupled identifiers remain accepted only through an explicit
  compatibility map committed in `config/agent_id_migration_map.json`.
- Engine resolution must use the committed slot registry instead of substring
  parsing.

## Consequences

### Positive
- Agent identifiers stay stable across future model swaps.
- PM/validator tooling no longer depends on provider tokens embedded in IDs.
- Migration remains auditable because old-to-new mappings are explicit and committed.

### Negative / trade-offs
- The workflow now depends on a committed slot registry that must stay accurate.
- Historical documentation contains both old and new naming eras, which adds some
  cognitive overhead during the transition.

## Alternatives considered

### Alternative A — Keep provider names in active IDs

Rejected because it preserves the exact governance churn and dispatch drift risk
that PE-INFRA-SLR-04 was opened to remove.

### Alternative B — Rename IDs ad hoc without a compatibility registry

Rejected because it would break existing validation and assignment tooling, and
would erase the audit trail connecting live legacy IDs to the new canonical
surfaces.

## Evidence / references

- `ELIS_MultiAgent_Implementation_Plan_v1_8_3.md` — PE-INFRA-SLR-04
- `config/agent_id_migration_map.json`
- Issue #344 context on governance drift between formal review state and automation
