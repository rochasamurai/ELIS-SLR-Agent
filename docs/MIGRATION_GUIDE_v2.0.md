# ELIS SLR Agent — Migration Guide v2.0

**From:** standalone harvest scripts + MVP pipeline scripts
**To:** `elis` CLI package (v2.0.0)

---

## Quick Reference

| Before (v1.x) | After (v2.0) |
|---------------|--------------|
| `python scripts/crossref_harvest.py --search-config ... --tier testing` | `elis harvest crossref --search-config ... --tier testing` |
| `python scripts/openalex_harvest.py --search-config ... --tier testing` | `elis harvest openalex --search-config ... --tier testing` |
| `python scripts/scopus_harvest.py --search-config ... --tier testing` | `elis harvest scopus --search-config ... --tier testing` |
| `python scripts/elis/search_mvp.py --config config/elis_search_queries.yml` | `elis harvest crossref/openalex/scopus ... && elis merge ...` |
| `python scripts/elis/screen_mvp.py --input A.json --output B.json` | `elis screen --input A.json --output B.json` |
| `python scripts/validate_json.py` | `elis validate` |
| `python scripts/validate_json.py` _(single file)_ | `elis validate <schema.json> <data.json>` |

---

## Installation

```bash
pip install -e .        # install elis package and CLI entry point
elis --help             # verify installation
```

---

## Step-by-Step Pipeline Migration

### 1. Harvest (per source)

```bash
# Before
python scripts/openalex_harvest.py \
  --search-config config/searches/electoral_integrity_search.yml \
  --tier testing \
  --output json_jsonl/harvest_openalex.json

# After
elis harvest openalex \
  --search-config config/searches/electoral_integrity_search.yml \
  --tier testing \
  --output json_jsonl/harvest_openalex.json
```

Available sources in v2.0.0: `crossref`, `openalex`, `scopus`
Additional adapters (wos, ieee, semantic_scholar, core, google_scholar, sciencedirect) are planned for v2.1.

### 2. Merge (new in v2.0)

```bash
elis merge \
  --inputs json_jsonl/harvest_crossref.json \
           json_jsonl/harvest_openalex.json \
           json_jsonl/harvest_scopus.json \
  --output json_jsonl/ELIS_Appendix_A_Search_rows.json \
  --report json_jsonl/merge_report.json
```

Or using a manifest from a previous stage:

```bash
elis merge --from-manifest json_jsonl/harvest_crossref_manifest.json
```

### 3. Deduplication (new in v2.0)

```bash
elis dedup \
  --input  json_jsonl/ELIS_Appendix_A_Search_rows.json \
  --output dedup/appendix_a_deduped.json \
  --report dedup/dedup_report.json

# Fuzzy mode (opt-in only):
elis dedup --fuzzy --threshold 0.85 ...
```

### 4. Screening

```bash
# Before
python scripts/elis/screen_mvp.py \
  --input  json_jsonl/ELIS_Appendix_A_Search_rows.json \
  --output json_jsonl/ELIS_Appendix_B_Screening_rows.json

# After
elis screen \
  --input  json_jsonl/ELIS_Appendix_A_Search_rows.json \
  --output json_jsonl/ELIS_Appendix_B_Screening_rows.json
```

### 5. Validation

```bash
# Before
python scripts/validate_json.py

# After — full validation (all artefacts)
elis validate

# After — single file
elis validate schemas/appendix_a.schema.json json_jsonl/ELIS_Appendix_A_Search_rows.json
```

### 6. Export to json_jsonl/ (new in v2.0)

```bash
elis export-latest --run-id 20260217_143022_crossref
```

---

## CLI Argument Changes

### `elis validate` positional args (BREAKING)

Old flags `--data` and `--schema` are removed. Use positional arguments:

```bash
# Before (INVALID in v2.0)
elis validate --data data.json --schema schema.json

# After
elis validate schema.json data.json
```

### Subcommand required (BREAKING)

`elis` with no subcommand now exits non-zero. Use `elis --help` to list available subcommands.

---

## Archived Scripts

All standalone harvest scripts and MVP pipeline scripts have been moved to
`scripts/_archive/`. They are **not called by any workflow** and may be removed in v2.1.

See `scripts/_archive/README.md` for the full mapping.

---

## Environment Variables

The same environment variables used by the legacy scripts work with `elis harvest`:

| Variable | Used by |
|----------|---------|
| `SCOPUS_API_KEY` | `elis harvest scopus` |
| `SCOPUS_INST_TOKEN` | `elis harvest scopus` |
| `ELIS_CONTACT` | All adapters (User-Agent contact) |

---

## Run Manifests (new in v2.0)

Every pipeline stage now emits a companion manifest sidecar:

```
json_jsonl/ELIS_Appendix_A_Search_rows.json
json_jsonl/ELIS_Appendix_A_Search_rows_manifest.json   ← new
```

Manifests are JSON objects validated against `schemas/run_manifest.schema.json`.
They record: stage, source, commit_sha, config_hash, started_at, finished_at,
record_count, input_paths, output_path, tool_versions.

---

## Backward Compatibility

`json_jsonl/` remains writable by `elis harvest`, `elis merge`, `elis screen`.
In v2.1, `json_jsonl/` becomes a read-only export view populated by `elis export-latest`.

The `scripts/validate_json.py` file is retained in `scripts/` as it is imported
by `elis/cli.py` for legacy validation mode.
