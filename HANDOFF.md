# HANDOFF — PE6 Cut-over + v2.0.0 Release (+ hotfix/pe6-codex-findings)

## Summary

PE6 implemented on `feature/pe6-cutover`. Converges the dual-codepath architecture
into a single canonical pipeline behind the `elis` CLI. One codepath remains.

**Hotfix `hotfix/pe6-codex-findings` (PR #225)** — addresses 2 blocking findings from
CODEX post-merge validation (PR #223): archives `validate_json.py` as the release plan
required, and corrects the `elis-validate.yml` trigger path after cut-over.

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

## Hotfix Changes (PR #225 — `hotfix/pe6-codex-findings`)

Addresses 2 blocking findings from CODEX post-merge validation (PR #223).

### Files Changed

| File | Change |
|------|--------|
| `scripts/validate_json.py` | Moved → `scripts/_archive/validate_json.py` via `git mv` |
| `scripts/_archive/__init__.py` | Created — makes `_archive/` importable as a Python package |
| `elis/cli.py` | Import updated: `from scripts.validate_json` → `from scripts._archive.validate_json` |
| `tests/test_validate_json.py` | Import updated to new path |
| `tests/test_elis_cli.py` | Mock patch path updated |
| `tests/test_elis_cli_adversarial.py` | Mock patch paths updated (4 occurrences) |
| `.github/workflows/elis-validate.yml` | `paths:` trigger: `scripts/validate_json.py` → `elis/**` + `scripts/_archive/validate_json.py` |

### Acceptance Criteria (hotfix)

- [x] `validate_json.py` archived to `scripts/_archive/` per release plan PE6.3.
- [x] `elis validate` still functional (import chain updated throughout).
- [x] `elis-validate.yml` trigger watches `elis/**` (the actual source of `elis validate` behaviour).
- [x] All 437 tests pass (black PASS · ruff PASS · pytest 437 passed, 0 failed).

### Validation Commands (hotfix)

```bash
python -m black --check .
# All done! ✨ 🍰 ✨ — 95 files would be left unchanged.

python -m ruff check elis/ tests/
# All checks passed!

python -m pytest
# 437 passed, 17 warnings in 8.68s
```

---

## Design Notes

### validate_json.py — archived in hotfix (PR #225)
`scripts/validate_json.py` was retained in `scripts/` during PE6 due to the import
dependency in `elis/cli.py`. CODEX's post-merge validation (PR #223) correctly flagged
this as a release-plan compliance gap. Fixed in `hotfix/pe6-codex-findings` (PR #225):
file moved to `scripts/_archive/validate_json.py`; `scripts/_archive/__init__.py` added
to preserve import chain; all callers updated. Full refactor into `elis/` deferred to v2.1.

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

---

## Hotfix Changes (PR #236 — `hotfix/pe6-ft-packaging-validate`)

Addresses FT-01 packaging failure discovered during v2.0.0 qualification run (PR #233).

### Root cause
`pyproject.toml` `[tool.setuptools.packages.find]` only included `elis*`, excluding the
`scripts` package from the installed distribution. The `elis` CLI entrypoint imports
`scripts._archive.validate_json`, which is unavailable in installed mode (though masked
in tests by `pythonpath = ["."]` in `pytest.ini_options`).

### Files changed

| File | Change |
|------|--------|
| `pyproject.toml` | `include = ["elis*"]` → `include = ["elis*", "scripts*"]` |

---

## Hotfix Changes (PR TBD — `hotfix/pe3-merge-manifest-notfound`)

Addresses FT-01 CLI-contract failure found in qualification r2: `elis merge --from-manifest DOES_NOT_EXIST.json` returned an unhandled traceback.

### Root cause
`_load_inputs_from_manifest()` attempted to read the manifest path directly, allowing `FileNotFoundError` to bubble up and print a traceback.

### Fix
- Wrap manifest read in `try/except FileNotFoundError` and raise controlled CLI error:
  - `SystemExit("Manifest file not found: <path>")`

### Files changed

| File | Change |
|------|--------|
| `elis/cli.py` | Catch `FileNotFoundError` in `_load_inputs_from_manifest` and raise controlled `SystemExit` |
| `tests/test_elis_cli.py` | Add regression test for missing `--from-manifest` file path |

### Validation
```bash
python -m pytest -q tests/test_elis_cli.py -k "from_manifest_missing_file or from_manifest_no_usable_paths or merge_reads_inputs_from_manifest"
# Result: 3 passed
```

---

## Hotfix Changes (PR TBD — `hotfix/pe3-merge-manifest-invalid-content`)

Addresses FT-03 failure in qualification r3 where `elis merge --from-manifest` exited with an unhandled/opaque error for invalid manifest content.

### Root cause
`_load_inputs_from_manifest()` only handled missing-file paths. Existing manifest files with invalid structure/stage could still fail without a controlled CLI message.

### Fixes
- Controlled CLI errors in `elis/cli.py` for:
  - invalid JSON manifest (`Invalid manifest JSON: <path>`)
  - non-object manifest payload
  - non-harvest manifest stage
  - missing usable `input_paths`/`output_path`
- Added adversarial test for wrong-stage manifest handling.
- Updated post-release FT plan to isolate FT-02 validation sidecar outputs from FT-03 harvest manifest inputs.

### Files changed

| File | Change |
|------|--------|
| `elis/cli.py` | Added controlled `SystemExit` errors for invalid manifest content paths |
| `tests/test_elis_cli.py` | Added `test_merge_from_manifest_wrong_stage_raises_system_exit`; tightened no-usable-path assertion |
| `docs/_active/POST_RELEASE_FUNCTIONAL_TEST_PLAN_v2.0.md` | Isolated FT-02 validation paths to avoid manifest filename collision with FT-03 |

### Validation
```bash
python -m pytest -q tests/test_elis_cli.py -k "merge_from_manifest_missing_file_raises_system_exit or merge_from_manifest_no_usable_paths_raises or merge_from_manifest_wrong_stage_raises_system_exit or merge_reads_inputs_from_manifest"
# Result: 4 passed
```
