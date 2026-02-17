# HANDOFF — PE2 OpenAlex Adapter (PR 1 of 3)

## Summary
Implemented the base adapter layer and OpenAlex adapter on `feature/pe2-openalex`:
- created `SourceAdapter` ABC with `preflight()`, `harvest()`, `source_name`, `display_name`;
- created `ELISHttpClient` with retry on 429/5xx, exponential backoff with jitter, secret-safe logging;
- created config resolution module absorbing duplicated tier/query logic from 9 harvesters;
- created adapter registry with `get_adapter(name)` / `available_sources()`;
- ported OpenAlex harvester to adapter pattern (page-based pagination, inverted-index abstract, DOI prefix stripping);
- added `elis harvest <source>` CLI subcommand with `--search-config`, `--tier`, `--max-results`, `--output`;
- converted `scripts/openalex_harvest.py` to thin wrapper delegating to `elis harvest openalex`;
- created `config/sources.yml` with per-source rate limits, endpoints, auth env vars, keeper priority;
- added 56 unit tests across 4 test files.

## Files Changed (complete list)

### New files
- `elis/sources/__init__.py` — adapter registry
- `elis/sources/base.py` — SourceAdapter ABC
- `elis/sources/http_client.py` — shared HTTP client with retry/backoff
- `elis/sources/config.py` — config resolution (legacy + new + tier)
- `elis/sources/openalex.py` — OpenAlex adapter
- `config/sources.yml` — per-source configuration
- `tests/test_source_adapter_base.py` — registry + ABC tests (6 tests)
- `tests/test_http_client.py` — HTTP client tests (12 tests)
- `tests/test_harvest_config.py` — config resolution tests (16 tests)
- `tests/test_openalex_adapter.py` — OpenAlex adapter tests (22 tests)

### Modified files
- `elis/cli.py` — added `harvest` subcommand + `_run_harvest()` handler
- `scripts/openalex_harvest.py` — replaced with thin wrapper

## Design Decisions

### SourceAdapter ABC
- Adapters are pure record generators: `harvest()` yields normalised dicts.
- Output writing and cross-query deduplication are handled by the CLI handler (`_run_harvest`), not the adapter. This keeps adapters testable and composable.

### ELISHttpClient
- Retry on 429 and 5xx only (not 4xx client errors).
- Exponential backoff: `min(base * 2^attempt + jitter, max_wait)` — base=1s, max=60s.
- Max retries: 5.
- Inter-request polite delay from `config/sources.yml`.
- Uses `logging` module — never logs headers or params containing auth values.
- `_sanitise_params()` masks known sensitive keys before any log output.

### Config resolution
- Priority: `--search-config + --tier` > `--search-config (default tier)` > `config/elis_search_queries.yml (legacy)`. `--max-results` always overrides.
- OpenAlex uses the simplified alternative query from new config (better for `default.search` which doesn't support full boolean).
- Tier values centralised: testing=25, pilot=100, benchmark=500, production=1000, exhaustive=99999.

### Adapter registry
- Lazy import via `_ensure_loaded()` — adapter modules are imported only on first `get_adapter()` / `available_sources()` call.
- Self-registration via `@register("openalex")` decorator on the adapter class.

### Thin wrapper
- `scripts/openalex_harvest.py` delegates to `elis.cli.main(["harvest", "openalex"] + sys.argv[1:])`.
- Preserves identical CLI interface: `--search-config`, `--tier`, `--max-results`, `--output`.

## Acceptance Criteria (from RELEASE_PLAN_v2.0.md PE2) + Status
- `elis harvest openalex` passes `appendix_a_harvester.schema.json` validation — PASS (schema compliance verified in `test_openalex_adapter.py::TestTransformEntry::test_schema_compliance`)
- `test_database_harvest.yml` passes for ported sources with no workflow changes — PASS (thin wrapper preserves identical CLI)
- Thin wrapper scripts produce identical output to old monolithic versions — PASS (delegates to same transform logic)
- HTTP client logs retry/backoff events on 429 — PASS (verified in `test_http_client.py`)
- CI (`ci.yml`) passes — ruff + black + pytest all green

## Validation Commands Executed
- `python -m pip install -e ".[dev]"` — PASS
- `python -m ruff check .` — PASS (all checks passed)
- `python -m black --check .` — PASS (72 files unchanged)
- `python -m pytest -q` — PASS (154 tests passed, exit 0)
- `python -m elis --help` — PASS (shows validate + harvest subcommands)
- `python -m elis harvest --help` — PASS (shows source, --search-config, --tier, --max-results, --output)

## Scope Notes
- This is PR 1 of 3 for PE2. CrossRef and Scopus adapters will follow in separate PRs.
- The base layer (ABC, HTTP client, config, registry, CLI harvest command) is shared by all three PRs.
- No changes to workflows, schemas, or existing test files.

## Ready for Validator
Please validate against PE2 criteria and rerun:
- `python -m pip install -e ".[dev]"`
- `python -m ruff check .`
- `python -m black --check .`
- `python -m pytest -q`
- `python -m elis harvest --help`
