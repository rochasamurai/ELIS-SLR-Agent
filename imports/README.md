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

- `json_jsonl/ELIS_Appendix_A_Search_rows.json`

## Intended workflow

1. Export results from the provider UI (for example, Scopus) as
   **UTF-8 CSV**, with the fields listed above.
2. Save the file into `imports/` in this repository.
3. Run the **“ELIS - Imports Convert”** workflow from the Actions tab,
   selecting:
   - Provider: `scopus_csv`
   - Input path: the CSV you placed under `imports/`
   - Topic / query details for provenance
4. The workflow converts the CSV into canonical Appendix A JSON and
   uploads it as an artefact. You can then review and optionally commit
   the JSON into `json_jsonl/`.

Future work will extend the converter to additional providers
(IEEE Xplore, Web of Science, JSTOR, …) and formats as needed.
