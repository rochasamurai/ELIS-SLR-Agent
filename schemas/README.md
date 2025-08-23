# `schemas/` — JSON Schemas
<!-- Last updated: 2025-08-21 -->

This folder contains **JSON Schema v2020-12** definitions used to validate all ELIS Agent JSON/JSONL files.

## Files (from current `schemas/` folder)
- `ELIS_Agent_LogEntry.schema.json`
- `ELIS_Agent_LogRotationPolicy.schema.json`
- `ELIS_Agent_ValidationErrors.schema.json`
- `ELIS_Appendix_A_Search.schema.json`
- `ELIS_Appendix_B_InclusionExclusion.schema.json`
- `ELIS_Appendix_B_Screening.schema.json`
- `ELIS_Appendix_C_DataExtraction.schema.json`
- `ELIS_Appendix_D_AuditLog.schema.json`
- `ELIS_Appendix_E_Codebook.schema.json`
- `ELIS_Appendix_F_RunLogPolicy.schema.json`
- `ELIS_Data_Sheets_2025-08-19_v1.0.schema.json`

## Notes
- `ELIS_Agent_LogEntry.schema.json` defines a generic **log entry** record (used by JSONL logs).
- Audit logs in `json_jsonl/ELIS_Appendix_D_AuditLog_*.jsonl` validate against `ELIS_Appendix_D_AuditLog.schema.json` (which may reference `ELIS_Agent_LogEntry.schema.json`).
- Validation errors in `json_jsonl/ELIS_Agent_ValidationErrors*.jsonl` validate against `ELIS_Agent_ValidationErrors.schema.json`.
- All Appendix JSON files validate against their **Appendix-specific** schemas listed above.

---

## Local validation (standardised)

**Python (`jsonschema`) — the only supported method**

```bash
# from repo root
pip install jsonschema

python scripts/validate_json.py            # validate all files in json_jsonl/
python scripts/validate_json.py json_jsonl/ELIS_Appendix_A_Search.json   # single file
```

**Script location:** `scripts/validate_json.py`  
**Exit codes:** 0 ok, 1 validation error, 2 IO/config error.
