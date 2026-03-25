# SLR Synthesis Workspace — Agent Rules
## ELIS Multi-Agent Development Environment

> **Phase:** Synthesis
> **Agents:** `synth-impl-claude` (Implementer) · `synth-val-codex` (Validator)
> **Protocol section:** Data Synthesis

---

## 1. Purpose

This workspace governs evidence grading, narrative synthesis, and tabular aggregation.
It must not contain harvest, screening, extraction, or PRISMA formatting rules.

---

## 2. Implementer Duties

- derive synthesis outputs only from extracted/appraised inputs
- document evidence-grading rules
- separate findings, limitations, and unsupported inferences
- preserve traceability back to extracted studies

---

## 3. Validator Duties

- challenge unsupported synthesis claims
- confirm every synthesized claim maps to extracted evidence
- verify evidence grading is applied consistently
- reject hidden recalculation of extraction fields

---

## 4. Run Manifest Compliance

Every synthesis PE must record:

- synthesis method
- evidence grading method
- input artifact set
- number of included studies synthesized
- unresolved heterogeneity notes

---

## 5. Quality Rules

- no search source changes in this workspace
- no screening decision authoring in this workspace
- no extraction schema changes in this workspace
- no PRISMA appendix rendering in this workspace

---

## 6. Project Store Access

**Writes to:** `<project-store>/synth/`
**Reads from:** `<project-store>/harvest/` · `<project-store>/screen/` · `<project-store>/extract/`
**Must not write to:** `prisma/`

Narrative and tabular synthesis artifacts are written to `<project-store>/synth/`.
All upstream phases are consumed read-only.

Read `MANIFEST.md` to confirm review identity. Do not modify `MANIFEST.md` without PM approval.
