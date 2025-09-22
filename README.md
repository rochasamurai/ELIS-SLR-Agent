# ELIS SLR Agent — Data & Validation

[![ELIS Validation](https://github.com/rochasamurai/ELIS-SLR-Agent/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/rochasamurai/ELIS-SLR-Agent/actions/workflows/validate.yml)

**Language:** UK English • **Spec Lock:** see `docs/Data_Contract_v1.0.md`.

This repository hosts the operational data (JSON/JSONL) and schemas used by the ELIS SLR Agent.  
All execution artefacts (**Rows**) must validate against the schemas via the validator script and CI.

## How to validate
- Local: `python scripts/validate_json.py --strict`
- CI: GitHub Actions runs on every push/PR (see `.github/workflows/validate.yml`).

## Key folders
- `docs/` — Contract/specs (frozen), Pilot Plan, PM Glossary, Handover Note.  
- `json_jsonl/` — Execution data (**Rows**), logs (JSONL) and governance configs.  
- `schemas/` — JSON Schemas (draft-07 and 2020-12).  
- `scripts/` — Validation tools (`validate_json.py`).

## Policy highlights
- Rows = top-level **array**, only schema fields, `additionalProperties:false`.
- Config files (`*_config.json`) are authoring artefacts and **not** used at runtime.
- Codebook: root is **array**; each item validated against `schemas/ELIS_Appendix_E_Codebook.schema.json`.
- Dates/times: ISO 8601 (UTC). Free text in UK English.

## Smoke test - PR Path
