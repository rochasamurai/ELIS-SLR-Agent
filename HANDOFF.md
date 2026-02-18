# HANDOFF — PE6 Cut-over + v2.0.0 Release

## Summary

PE6 implemented on `feature/pe6-cutover`. Converges the dual-codepath architecture
into a single canonical pipeline behind the `elis` CLI. One codepath remains.

---

## Files Changed

### Tests
- `tests/test_cli.py` — Rewrote to match v2.0 CLI contract (removed stale `search`
  subcommand tests and `--data`/`--schema` flag tests; 14 tests, all pass).

### Package
- `elis/cli.py` — Added `elis export-latest` subcommand.
- `pyproject.toml` — Version bumped `0.3.0` → `2.0.0`.

### Scripts
- `scripts/_archive/` — Created. Moved 9 standalone harvesters + 2 MVP pipeline scripts here.
- `scripts/_archive/README.md` — Migration table (legacy script → `elis` CLI command).
- `scripts/_archive/elis/search_mvp.py`, `screen_mvp.py` — Archived here.

### Workflows (PE6.2)
- `.github/workflows/ci.yml` — validate job: `python scripts/validate_json.py` → `elis validate`.
- `.github/workflows/elis-validate.yml` — `python scripts/validate_json.py` → `elis validate`.
- `.github/workflows/elis-agent-screen.yml` — `python scripts/elis/screen_mvp.py` → `elis screen`.
- `.github/workflows/elis-agent-nightly.yml` — search+screen → `elis harvest crossref/openalex` + `elis merge` + `elis screen`.
- `.github/workflows/elis-agent-search.yml` — search+scopus → `elis harvest crossref/openalex/scopus` + `elis merge`.
- `.github/workflows/elis-search-preflight.yml` — `search_mvp.py --dry-run` → `elis harvest crossref --tier testing`.
- `.github/workflows/test_database_harvest.yml` — script-selection step removed; `elis harvest <database>` used directly.

### Release Docs
- `CHANGELOG.md` — v2.0.0 section added (breaking changes, added, removed).
- `docs/MIGRATION_GUIDE_v2.0.md` — full migration guide (old script → new CLI).
- `reports/audits/PE6_RC_EQUIVALENCE.md` — PE6.1 equivalence check results.

---

## Design Notes

### validate_json.py NOT archived
`scripts/validate_json.py` is retained in `scripts/` (not moved to `_archive/`). It is
imported by `elis/cli.py` via `from scripts.validate_json import main as legacy_main, validate_appendix`.
Archiving it would break `elis validate` (legacy mode). To be refactored in v2.1.

### Adapter coverage
Only 3 adapters exist in v2.0.0: `crossref`, `openalex`, `scopus`. The remaining 6 sources
(wos, ieee, semantic_scholar, core, google_scholar, sciencedirect) will error with
"Unknown source" on `elis harvest`. Planned for v2.1.

### Nightly workflow migration
`elis-agent-nightly.yml` previously called `search_mvp.py` which ran 3 sources with one
command. Now calls `elis harvest crossref/openalex` + `elis merge`. Tier downgraded from
production to `pilot` (100 results/query) to keep nightly fast. Update to `production`
when adapter coverage is complete.

### export-latest
`elis export-latest --run-id <id>` copies all non-manifest JSON/JSONL files from
`runs/<run_id>/` into `json_jsonl/` and writes `json_jsonl/LATEST_RUN_ID.txt`.

---

## Acceptance Criteria (PE6) + Status

- [x] All 19 workflows use `elis` CLI (no `python scripts/*.py` outside `_archive/`).
- [x] `pyproject.toml` version = `2.0.0`.
- [x] `scripts/_archive/` contains 9 harvesters + 2 MVP pipeline scripts.
- [x] CHANGELOG documents breaking changes.
- [x] Equivalence check results recorded (`runs/rc_equivalence/README.md`).
- [x] `elis export-latest` subcommand added.
- [x] `docs/MIGRATION_GUIDE_v2.0.md` written.
- [ ] Git tag `v2.0.0` — to be created by maintainer after PR merge.

---

## Validation Commands Executed

```bash
python -m black --check elis/ tests/
python -m ruff check elis/ tests/
python -m pytest
# Results: 437 passed, 0 failed, 17 warnings (deprecation only)
```
