# HANDOFF — PE2 Scopus Adapter (PR 3 of 3)

## Summary
Added the Scopus adapter on `feature/pe2-scopus`, building on the base adapter layer from PR 1 and CrossRef from PR 2:
- ported Scopus harvester to adapter pattern (required auth, offset pagination max 25/page, `dc:creator` single author, `SCOPUS_ID:` prefix stripping);
- converted `scripts/scopus_harvest.py` to thin wrapper delegating to `elis harvest scopus`;
- registered Scopus in the adapter registry;
- removed stale `tests/test_scopus_harvest.py` (replaced by new adapter tests);
- added 33 unit tests.

## Files Changed (complete list)

### New files
- `elis/sources/scopus.py` — Scopus adapter
- `tests/test_scopus_adapter.py` — Scopus adapter tests (33 tests)

### Modified files
- `elis/sources/__init__.py` — added scopus import for registration
- `scripts/scopus_harvest.py` — replaced with thin wrapper

### Removed files
- `tests/test_scopus_harvest.py` — old monolithic tests replaced by `test_scopus_adapter.py`

## Design Decisions

### Scopus adapter
- **Required auth**: `SCOPUS_API_KEY` + `SCOPUS_INST_TOKEN` env vars → `X-ELS-APIKey` and `X-ELS-Insttoken` headers.
- **Graceful degradation**: `harvest()` returns empty iterator (with warning log) if credentials are missing, rather than crashing.
- **Offset-based pagination**: `start` + `count` params, `_COUNT_PER_PAGE = 25` (API maximum).
- **Scopus ID**: `dc:identifier` with `SCOPUS_ID:` prefix stripped.
- **Authors**: `dc:creator` as single-author string → list (Scopus search API returns first author only).
- **Year**: From `prism:coverDate` (`YYYY-MM-DD`), first 4 chars parsed as int.
- **DOI**: From `prism:doi`.
- **Abstract**: From `dc:description`.
- **Citations**: `citedby-count` as string → int, defaults to 0.
- **Preflight**: Verifies credentials exist, then sends `count=1` query to test API reachability.

### Thin wrapper
- `scripts/scopus_harvest.py` delegates to `elis.cli.main(["harvest", "scopus"] + sys.argv[1:])`.
- Preserves identical CLI interface.

## Acceptance Criteria (from RELEASE_PLAN_v2.0.md PE2) + Status
- `elis harvest scopus` passes `appendix_a_harvester.schema.json` validation — PASS (schema compliance verified in `test_scopus_adapter.py::TestTransformEntry::test_schema_compliance`)
- Thin wrapper script produces identical output to old monolithic version — PASS
- CI (`ci.yml`) passes — ruff + black + pytest all green

## Scope Notes
- This is PR 3 of 3 for PE2. Depends on PR 1 (base layer + OpenAlex) and PR 2 (CrossRef).
- Only Scopus-specific files are changed; no modifications to base layer, HTTP client, config, or CLI handler.
- Completes the full PE2 source adapter layer.

## Ready for Validator
Please validate against PE2 criteria and rerun:
- `python -m pip install -e ".[dev]"`
- `python -m ruff check .`
- `python -m black --check .`
- `python -m pytest -q`
- `python -m elis harvest --help`
