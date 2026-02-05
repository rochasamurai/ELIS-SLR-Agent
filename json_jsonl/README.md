# `json_jsonl/` — Operational Data for the ELIS SLR Agent

This folder stores the **operational JSON artefacts** consumed by the Agent.
Every file must validate against its schema under `schemas/`.

## Canonical execution artefacts (Rows)
- **A (Search):** `ELIS_Appendix_A_Search_rows.json`  
  Schema: `schemas/appendix_a.schema.json`
- **B (Screening):** `ELIS_Appendix_B_Screening_rows.json`  
  Schema: `schemas/appendix_b.schema.json`
- **C (Data Extraction):** `ELIS_Appendix_C_DataExtraction_rows.json`  
  Schema: `schemas/appendix_c.schema.json`

## Validation (Python)
```powershell
python scripts/validate_json.py
python scripts/validate_json.py json_jsonl/ELIS_Appendix_A_Search_rows.json
```

## Notes
- Current canonical artefacts are **JSON arrays**, not JSONL.
- JSONL migration is planned but deferred (see repo hygiene plan).
