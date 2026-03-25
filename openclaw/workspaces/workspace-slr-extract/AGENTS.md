# SLR Extraction Workspace — Agent Rules
## ELIS Multi-Agent Development Environment

> **Phase:** Extraction
> **Agents:** `extract-impl-codex` (Implementer) · `extract-val-claude` (Validator)
> **Protocol section:** Data and Appraisal

---

## 1. Purpose

This workspace governs structured field extraction, study metadata normalization, and
critical appraisal capture. It must not contain harvest, screening, synthesis, or
PRISMA layout rules.

---

## 2. Implementer Duties

- populate mandatory extraction fields
- preserve provenance to source study IDs
- capture appraisal outcomes using schema-aligned values
- record missing-field handling explicitly

---

## 3. Validator Duties

- verify mandatory fields are complete
- trace extracted rows back to included studies
- challenge schema violations and mixed-type values
- treat silent imputation as blocking

---

## 4. Run Manifest Compliance

Every extraction PE must record:

- extraction schema version
- mandatory field set
- appraisal scale or rubric
- included-study count processed
- unresolved missing-data count

---

## 5. Quality Rules

- no search-query logic in this workspace
- no inclusion/exclusion rule authoring in this workspace
- no evidence synthesis prose in this workspace
- no PRISMA checklist/diagram formatting in this workspace

---

## 6. Project Store Access

**Writes to:** `<project-store>/extract/`
**Reads from:** `<project-store>/harvest/` · `<project-store>/screen/`
**Must not write to:** `synth/` · `prisma/`

Structured extraction sheets (one JSONL per included study) are written to
`<project-store>/extract/`. Upstream harvest and screen artifacts are consumed
read-only.

Read `MANIFEST.md` to confirm review identity. Do not modify `MANIFEST.md` without PM approval.
