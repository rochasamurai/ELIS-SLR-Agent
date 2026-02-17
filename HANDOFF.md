# HANDOFF - PE4 Deterministic Dedup + Clusters

## Summary
Implemented PE4 on `feature/pe4-dedup`:
- added deterministic dedup stage in `elis/pipeline/dedup.py`;
- added CLI subcommand `elis dedup` in `elis/cli.py`;
- added 33 tests (smoke + adversarial + unit) in `tests/test_pipeline_dedup.py`.

## Files Changed
- `elis/pipeline/dedup.py` (new)
- `elis/cli.py` (added `dedup` subparser + `_run_dedup` handler)
- `tests/test_pipeline_dedup.py` (new, 33 tests)
- `HANDOFF.md`

## Design Notes

### Dedup key
| Condition | Key |
|---|---|
| DOI present | `normalise_doi(doi)` |
| No DOI | `normalise_text(title) + "\|" + str(year) + "\|" + normalise_text(first_author)` |

- `normalise_doi`: lowercase + strip `https://doi.org/`, `http://doi.org/`, `doi:` prefixes.
- `normalise_text`: lowercase, strip non-word characters, collapse whitespace.

### Cluster ID
`sha256(dedup_key)[:12]` — 12-char hex, deterministic.

### Keeper selection
1. Most non-null fields (strings/lists must be non-empty to count).
2. Tie-break: source priority from `config/sources.yml` → `keeper_priority`.
   Code default (if config absent): scopus > wos > semanticscholar > crossref > openalex > ieee > core > sciencedirect > google_scholar.

### Output format
- JSON array `[_meta, ...keepers]` — `_meta: True` header retained for `elis screen` compatibility.
- Upstream `_meta` fields (`topics_enabled`, `protocol_version`, `sources`, `run_inputs`) forwarded.
- Each keeper gains: `cluster_id`, `cluster_size`, `cluster_sources`.
- Non-keepers written to `dedup/duplicates.jsonl` sidecar (traceability): each record has `cluster_id` + `duplicate_of` = keeper's `id`.

### Traceability (No data loss)
Every input record is either a keeper (in the output array) or a duplicate (in `duplicates.jsonl`).
`duplicate_of` links the dropped record to its keeper's `id`, enabling full round-trip traceability.

### Fuzzy mode
Off by default. `--fuzzy --threshold 0.85` enables `difflib.SequenceMatcher` title similarity across clusters. Emits `warnings.warn` + `logger.warning` when enabled.

### dedup_report.json fields
`input_records`, `unique_clusters`, `duplicates_removed`, `doi_based_dedup`, `title_year_author_dedup`, `fuzzy_dedup`, `keeper_priority_source`, `top_10_collisions`.

## Acceptance Criteria (PE4) + Status
- Same input → same cluster IDs (deterministic). **PASS** (`test_dedup_is_deterministic`)
- No data loss (all records traceable via `cluster_id`). **PASS** (`test_dedup_duplicates_sidecar_traces_all_dropped`, `test_dedup_sidecar_empty_when_no_duplicates`)
- Fuzzy off by default. **PASS** (`test_dedup_fuzzy_off_by_default`, `test_dedup_fuzzy_enabled_warns`)
- Keeper precedence read from config; code default used only if config absent. **PASS** (`test_dedup_keeper_tiebreak_by_source_priority`)

## Validation Commands Executed
```
python -m black --check elis/pipeline/dedup.py elis/cli.py tests/test_pipeline_dedup.py
# → All done! 3 files would be left unchanged.

python -m ruff check elis/pipeline/dedup.py elis/cli.py tests/test_pipeline_dedup.py
# → All checks passed!

python -m pytest tests/test_pipeline_dedup.py -v
# → 33 passed

python -m pytest -q
# → 10 failed (pre-existing test_cli.py failures, unchanged from PE3), 381 passed
```

## Known Issues (Pre-existing, not PE4)
`tests/test_cli.py` has 10 failures from outdated CLI contract (PE0b tests expect legacy
`search`/`screen` subcommands that no longer exist). Unchanged since PE3.
