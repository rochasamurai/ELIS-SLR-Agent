# Data Contract v1.0 — ELIS SLR Agent (Spec Lock)

**Effective date:** 2025-08-22  
**Status:** Frozen (no functional changes without a new version)

## 1. Scope
This contract defines the immutable formats **consumed by the ELIS SLR Agent** (“Rows”) and separates them from **authoring/governance files** (“Config”). The aim is deterministic validation and stable operation.

## 2. Principles
- **Rows = execution format**: top-level **array** of objects; **only** the columns defined in the schema; `additionalProperties: false`.
- **Config = authoring format**: may contain metadata, templates, codebooks, `records`, notes, etc. **Not** consumed by the agent.
- **Single source of truth** for execution is the validated Rows artefacts.
- **Definition of Done (DoD):** `scripts/validate_json.py` exits with **code 0** (no failures).
- **Versioning & auditability:** any change to this contract or to schemas requires a changelog entry and an audit log record.

## 3. Language & localisation
- **All files, field labels, free-text content, and project documentation must be written in UK English.**
- **Dates/times:** ISO 8601 (e.g., `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`).  
- **Numbers:** decimal point (`.`); avoid thousands separators in machine fields.

## 4. Canonical artefacts (consumed by the agent)
- A (Search): `ELIS_Appendix_A_Search_rows.json`
- B.Screening: `ELIS_Appendix_B_Screening_rows.json`
- B.InclusionExclusion: `ELIS_Appendix_B_InclusionExclusion_rows.json`
- C (DataExtraction): `ELIS_Appendix_C_DataExtraction_rows.json`
- E (Codebook): `ELIS_Appendix_E_Codebook_YYYY-MM-DD.json` (top-level = **array** of codes)
- F (RunLogPolicy): `ELIS_Appendix_F_RunLogPolicy_YYYY-MM-DD.json`
- Agent logs (JSONL):  
  - Audit Log: `ELIS_Appendix_D_AuditLog_YYYY-MM-DD.jsonl`  
  - Validation Errors: `ELIS_Agent_ValidationErrors_YYYY-MM-DD.jsonl`
- Optional composite workbook dump: `ELIS_Data_Sheets_YYYY-MM-DD_v1.0.json`

## 5. Mapping (Rows → Schemas)
- A → `schemas/ELIS_Appendix_A_Search.schema.json`
- B.Screening → `schemas/ELIS_Appendix_B_Screening.schema.json`
- B.InclusionExclusion → `schemas/ELIS_Appendix_B_InclusionExclusion.schema.json`
- C → `schemas/ELIS_Appendix_C_DataExtraction.schema.json`
- **E (Codebook; root is array) → each item validated against `schemas/ELIS_Appendix_E_Codebook.schema.json` (no separate array schema).**  
  (each item conforms to `ELIS_Appendix_E_Codebook.schema.json`)
- F → `schemas/ELIS_Appendix_F_RunLogPolicy.schema.json`
- Audit Log (JSONL) → `schemas/ELIS_Appendix_D_AuditLog.schema.json` (validated **per line**)
- Validation Errors (JSONL) → `schemas/ELIS_Agent_ValidationErrors.schema.json` (validated **per line**)
- Composite Workbook → `schemas/ELIS_Data_Sheets_2025-08-19_v1.0.schema.json`

## 6. Content rules for Rows (A/B/C)
- Top-level **array**; each element is one spreadsheet row.
- **No metadata** at the top level (no `project`, `extraction_template`, `codebook`, `records`, etc.).
- Fields exactly as per the schemas; `additionalProperties: false`.
- Respect declared types (`string/number/boolean/null`) and formats (`date`, `date-time`) where applicable.
- UK English for any free-text fields (titles, abstracts, notes).

## 7. Content rules for Config
- Free to include metadata, governance details, templates, codebooks and `records`.
- Naming: `*_config.json` (e.g., `ELIS_Appendix_A_Search_config.json`).
- **Not** consumed by the agent; validation optional (separate config schemas may be added).

## 8. File-naming conventions
- Execution Rows: `*_rows.json` for A/B/C.
- Authoring Config: `*_config.json`.
- D/E/F and the Composite use date-stamped names (`YYYY-MM-DD`) where applicable.
- Names are case-sensitive and must match exactly.

## 9. Validation policy
- The validator routes by filename pattern; it **auto-selects the JSON Schema draft** based on each schema’s `$schema` (draft-07 vs 2020-12).
- JSONL files are validated **line-by-line**.
- DoD: a batch run with **exit code 0** and a validation report stored in the repository’s validation logs.

## 10. Golden samples & regression
- Maintain at least one minimal valid sample Row file per appendix (A/B/S/C/E/F).  
- When schemas change, validate golden samples and real artefacts to prevent regressions.

## 11. Governance & change control
- Any change to this contract or to schemas requires:
  1) schema updates,  
  2) validator updates (if routing changes),  
  3) a `CHANGELOG.md` entry (version/date), and  
  4) an audit log event (Appendix D JSONL) including `run_id`, `action`, and a short message.
- UK English remains mandatory for all content and documentation.

