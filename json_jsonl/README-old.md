# `json_jsonl/` — Operational Data for the ELIS SLR Agent

**Language policy:** All content in this repository is authored in **UK English**. Dates/times use ISO 8601 (UTC). [Spec: Data Contract v1.0]  

This folder stores the **operational JSON/JSONL artefacts consumed by the Agent** (“Rows”), plus governance logs. Every file **must validate** against its schema under `/schemas/`.

## Canonical execution artefacts (Rows)
- **A (Search):** `ELIS_Appendix_A_Search_rows.json`  
  Schema: `schemas/ELIS_Appendix_A_Search.schema.json`
- **B.Screening:** `ELIS_Appendix_B_Screening_rows.json`  
  Schema: `schemas/ELIS_Appendix_B_Screening.schema.json`
- **B.InclusionExclusion:** `ELIS_Appendix_B_InclusionExclusion_rows.json`  
  Schema: `schemas/ELIS_Appendix_B_InclusionExclusion.schema.json`
- **C (DataExtraction):** `ELIS_Appendix_C_DataExtraction_rows.json`  
  Schema: `schemas/ELIS_Appendix_C_DataExtraction.schema.json`

> Content rules for Rows: top-level **array**; fields exactly as per the schemas; `additionalProperties: false`. Free-text in UK English.  
> (See `docs/Data_Contract_v1.0.md` for full rules.)

## Authoring/Config (not consumed by the Agent)
- `ELIS_Appendix_A_Search_config.json`
- `ELIS_Appendix_B_Screening_config.json`
- `ELIS_Appendix_B_InclusionExclusion_config.json`
- `ELIS_Appendix_C_DataExtraction_config.json`
These files may include metadata, templates, and `records`; they are out of the runtime surface and may evolve independently.

## Logs & releases
- **Audit Log (JSONL):** `ELIS_Appendix_D_AuditLog_YYYY-MM-DD.jsonl`  
  Schema: `schemas/ELIS_Appendix_D_AuditLog.schema.json`
- **Validation Errors (JSONL):** `ELIS_Agent_ValidationErrors_YYYY-MM-DD.jsonl`  
  Schema: `schemas/ELIS_Agent_ValidationErrors.schema.json`
- **Run/Policy Config:** `ELIS_Appendix_F_RunLogPolicy_YYYY-MM-DD.json`  
  Schema: `schemas/ELIS_Appendix_F_RunLogPolicy.schema.json`
- **Codebook (array):** `ELIS_Appendix_E_Codebook_YYYY-MM-DD.json`  
  Validation: each item is validated against `schemas/ELIS_Appendix_E_Codebook.schema.json` (root is array; no separate array schema).
- **Optional composite dump:** `ELIS_Data_Sheets_YYYY-MM-DD_v1.0.json`  
  Schema: `schemas/ELIS_Data_Sheets_2025-08-19_v1.0.schema.json`

## Validation (Python-only, standard)
```bash
# from repository root
pip install jsonschema

python scripts/validate_json.py                               # validate all in json_jsonl/
python scripts/validate_json.py json_jsonl/ELIS_Appendix_B_Screening_rows.json  # single file
