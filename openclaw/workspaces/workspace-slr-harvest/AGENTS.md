# SLR Harvest Workspace — Agent Rules
## ELIS Multi-Agent Development Environment

> **Phase:** Harvest
> **Agents:** `harvest-impl-codex` (Implementer) · `harvest-val-claude` (Validator)
> **Protocol section:** Information Sources

---

## 1. Purpose

This workspace is dedicated to literature search, source-adapter usage, query capture,
and deduplication outputs. It must not contain screening, extraction, synthesis, or
PRISMA-specific execution rules.

---

## 2. Implementer Duties

- build or update search-source definitions
- record search strings, date windows, and adapter choices
- produce deterministic deduplication outputs
- document source coverage limits and protocol deviations

Required evidence:

- source list
- search manifest
- deduplication summary
- stable IDs for harvested records

---

## 3. Validator Duties

- verify source coverage and adapter usage against the protocol
- confirm search manifests are reproducible
- challenge duplicate-handling logic with adverse cases
- reject undocumented search drift

---

## 4. Run Manifest Compliance

Every harvest PE must leave a run manifest with:

- source name
- query or filter set
- execution date
- result count before dedup
- result count after dedup

---

## 5. Quality Rules

- no screening decisions in this workspace
- no extraction fields in this workspace
- no synthesis claims in this workspace
- no PRISMA flow arithmetic authored here except raw identification counts

---

## 6. Project Store Access

**Writes to:** `<project-store>/harvest/`
**Reads from:** none (harvest is the first phase)
**Must not write to:** `screen/` · `extract/` · `synth/` · `prisma/`

All harvest outputs (search exports, run manifests, dedup outputs) are written to
`<project-store>/harvest/`. The active project store path is provided by the PM Agent
at PE assignment time. Verify it against `MANIFEST.md` before writing.

Read `MANIFEST.md` to confirm review identity. Do not modify `MANIFEST.md` without PM approval.
