# ELIS imports — raw database exports

This folder is reserved for **raw exports** downloaded from external
databases and platforms, for example:

- Scopus
- Web of Science
- IEEE Xplore
- JSTOR
- Other bibliographic / index services

These files are **inputs** to the ELIS SLR Agent. They are not part of
the canonical Appendix artefacts (A/B/C), but can be converted into
Appendix A JSON via the `ELIS - Imports Convert` workflow.

## JSON-only policy
- Vendor exports (CSV/TSV/XLSX) are **local-only** and should live under:
  - `imports/raw/` (ignored)
- Converted JSON should live under:
  - `imports/staging/` (ignored)
- Only **canonical JSON/JSONL** belongs in `json_jsonl/`.

## Current scope (MVP)

At this stage, the converter supports:

- **Scopus CSV exports** (UTF-8, comma-separated)

Expected format for Scopus CSV:

- File lives under `imports/` (for example:
  `imports/scopus_export_2025-10-31.csv`).
- Columns (case-insensitive) include at least:
  - `Title` or `Document Title`
  - `Authors` or `Author(s)`
  - `Year`
  - `DOI`
  - `Source title` / `Publication Title` / `Source Title`
  - `Publisher`
  - `Abstract`
  - `Language of Original Document` or `Language`
  - `EID`
  - `Link` or `URL`

The converter will map and normalise these into the canonical ELIS
Appendix A schema, writing:

- `imports/staging/scopus_export_YYYY-MM-DD.json`

## Converter (local)
Use the local converter script:

```powershell
python scripts/convert_scopus_csv_to_json.py `
  --in  imports/raw/scopus_export.csv `
  --out imports/staging/scopus_export_2026-02-05.json `
  --query-topic "<topic_id>" `
  --query-string "<original query string>"
```

Then validate:

```powershell
python scripts/validate_json.py --schema schemas/appendix_a.schema.json --input imports/staging/scopus_export_2026-02-05.json
```

## Intended workflow

1. Export results from the provider UI (for example, Scopus) as
   **UTF-8 CSV**, with the fields listed above.
2. Save the file into `imports/raw/` (local only).
3. Convert to JSON with `scripts/convert_scopus_csv_to_json.py`.
4. Validate with `scripts/validate_json.py`.
5. If approved, move the JSON into `json_jsonl/` as a canonical artefact.

Future work will extend the converter to additional providers
(IEEE Xplore, Web of Science, JSTOR, …) and formats as needed.
