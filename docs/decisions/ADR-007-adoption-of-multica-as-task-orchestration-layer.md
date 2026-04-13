# ADR-007: Adoption of Multica as Task Orchestration Layer

**Status:** Accepted
**Date:** 2026-04-11
**Deciders:** ELIS PM / two-agent validation workflow

> Source note: migrated from `DEC-004_v1.2_Final.md` into ADR format for permanent decision history.

---

## Context

ELIS adopts Multica as a task orchestration layer supporting a model-agnostic, role-based 2-agent protocol.

This version incorporates final validation feedback and resolves residual observations from v1.1.

---

## Decision Clarifications

## 2.1 Adoption Signal Normalisation

| Tool | GitHub Stars | Interpretation |
|------|-------------|----------------|
| Multica | ~7K+ | Strong adoption signal |
| Claw Orchestra | ~0 | Minimal adoption |
| ClawCode | Low (<100) | Limited visibility |
| ClawX | Low (<100) | Limited visibility |
| Paperclip | ~1K+ (approx) | Moderate adoption |

> Note: Adoption signals are indicative only and do not imply production readiness.

---

## 2.2 Validation Independence — Correct Scope

### Clarification

Validation independence is enforced at the **agent instance level**, not strictly at the model level.

### Correct Rule

```text
validator_agent_id ≠ implementer_agent_id (same artifact lineage)
```

### Updated Enforcement

1. Task metadata tracks:
   - implementer_agent_id
   - validator_agent_id

2. Pre-assignment check:
```
if validator_agent_id == implementer_agent_id:
    reject assignment
```

3. CI validation gate confirms constraint before closure

---

## Decision

Multica → Control Plane  
OpenClaw → Execution Runtime  
Models → Execution Layer  

---

## Constraints

- Multica restricted to orchestration only  
- ELIS retains validation authority  
- Model-agnostic routing enforced  
- Validation independence enforced at ELIS layer  

---

## Consequences

### Positive

This decision remains:

> **Pilot-conditional**

No production ELIS workloads have yet validated Multica.

---

### Negative / trade-offs

With validation feedback incorporated, Multica is confirmed as:

- architecturally aligned  
- operationally viable (subject to pilot)  
- the best current orchestration candidate for ELIS  

---

## Final Statement

DEC-004 is approved. Multica is adopted as ELIS orchestration layer under defined constraints and validation controls.
