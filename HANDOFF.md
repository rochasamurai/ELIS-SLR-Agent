# HANDOFF — PE2 CrossRef Adapter (PR 2 of 3)

## Summary
Added the CrossRef adapter on `feature/pe2-crossref`, building on the base adapter layer from PR 1:
- ported CrossRef harvester to adapter pattern (offset pagination, title array[0], uppercase DOI key, published-print/online year);
- converted `scripts/crossref_harvest.py` to thin wrapper delegating to `elis harvest crossref`;
- registered CrossRef in the adapter registry;
- added 30 unit tests.

## Files Changed (complete list)

### New files
- `elis/sources/crossref.py` — CrossRef adapter
- `tests/test_crossref_adapter.py` — CrossRef adapter tests (30 tests)

### Modified files
- `elis/sources/__init__.py` — added crossref import for registration
- `scripts/crossref_harvest.py` — replaced with thin wrapper

## Design Decisions

### CrossRef adapter
- **Offset-based pagination**: `offset` + `rows` params, `_ROWS_PER_REQUEST = 1000` (API max).
- **Title**: Extracted from `title` array (`title[0]`), empty string if missing.
- **Authors**: Built from `given` + `family` fields in `author` array; falls back to `family`-only.
- **Year**: Prefers `published-print.date-parts[0][0]`, falls back to `published-online`.
- **DOI**: Uppercase `DOI` key in CrossRef response, stored as-is (no URL prefix).
- **Citations**: `is-referenced-by-count` field, defaults to 0.
- **Abstract**: Raw `abstract` field (may contain XML tags from CrossRef).
- **URL**: From `URL` field in response.
- **Preflight**: Sends `rows=1` query to verify API reachability.

### Thin wrapper
- `scripts/crossref_harvest.py` delegates to `elis.cli.main(["harvest", "crossref"] + sys.argv[1:])`.
- Preserves identical CLI interface.

## Acceptance Criteria (from RELEASE_PLAN_v2.0.md PE2) + Status
- `elis harvest crossref` passes `appendix_a_harvester.schema.json` validation — PASS (schema compliance verified in `test_crossref_adapter.py::TestTransformEntry::test_schema_compliance`)
- Thin wrapper script produces identical output to old monolithic version — PASS
- CI (`ci.yml`) passes — ruff + black + pytest all green

## Scope Notes
- This is PR 2 of 3 for PE2. Depends on PR 1 (base layer + OpenAlex).
- Only CrossRef-specific files are changed; no modifications to base layer, HTTP client, config, or CLI handler.

## Ready for Validator
Please validate against PE2 criteria and rerun:
- `python -m pip install -e ".[dev]"`
- `python -m ruff check .`
- `python -m black --check .`
- `python -m pytest -q`
- `python -m elis harvest --help`
