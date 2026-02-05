# `schemas/` — JSON Schemas

This folder contains JSON Schema v2020-12 definitions used to validate ELIS
Agent JSON files.

## Files
- `appendix_a.schema.json`
- `appendix_b.schema.json`
- `appendix_c.schema.json`
- `appendix_a_harvester.schema.json`

## Local validation
```powershell
python scripts/validate_json.py
python scripts/validate_json.py json_jsonl/ELIS_Appendix_A_Search_rows.json
```

## Notes
- The harvester subset schema is for standalone harvester outputs (no meta header).
