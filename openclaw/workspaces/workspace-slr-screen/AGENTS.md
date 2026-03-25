# SLR Screen Workspace — Agent Rules
## ELIS Multi-Agent Development Environment

> **Phase:** Screen
> **Agents:** `screen-impl-claude` (Implementer) · `screen-val-codex` (Validator)
> **Protocol section:** Study Selection

---

## 1. Purpose

This workspace governs title/abstract screening, full-text eligibility, and exclusion
reason capture. It must not contain harvest search logic, extraction schemas,
synthesis rules, or PRISMA appendix formatting instructions.

---

## 2. Implementer Duties

- apply inclusion/exclusion criteria consistently
- record exclusion reasons with protocol-compatible labels
- maintain stage-consistent screening counts
- log uncertainty and escalation cases explicitly

---

## 3. Validator Duties

- challenge boundary decisions and exclusion coding
- verify decision provenance on sampled records
- ensure screening counts reconcile with the PRISMA pipeline inputs
- treat undocumented eligibility rules as blocking

---

## 4. Run Manifest Compliance

Every screening PE must record:

- screening stage (`title-abstract` or `full-text`)
- applied eligibility criteria version
- included count
- excluded count
- exclusion reason summary

---

## 5. Quality Rules

- no search adapter rules in this workspace
- no extraction schema authoring in this workspace
- no synthesis claim drafting in this workspace
- no final PRISMA appendix formatting in this workspace
