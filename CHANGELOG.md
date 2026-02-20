# Changelog
<!--
  Format: Keep a Changelog (human-readable), newest first. Dates in UTC (YYYY-MM-DD).
  Scope: This file records user-visible changes across releases (features, fixes, CI behaviour,
  docs). Use concise, neutral UK English. Each release gets its own section.
-->

## [Unreleased]
### Fixed
- Closed PE6 review record after hotfix resolution (`PR #229`): `REVIEW_PE6.md` now records the final PASS closure linked to `PR #225`.
- Finalised SEV-1 corrections in post-release functional test planning (`PR #231`):
  - FT-06 clarifies that legacy full-mode validation must be judged by reported markers, not exit code.
  - FT-11 clarifies determinism checks must use normalized content hashing (exclude volatile fields).
- Added ignore rules for recurring local run artefacts (`dedup/`, `*_manifest.json`) to reduce accidental workspace noise (`PR #231`).

### Docs
- Backfilled missing per-PE validation artefacts to satisfy `AGENTS.md` per-PE review file policy (`PR #230`):
  - `REVIEW_PE0a.md`
  - `REVIEW_PE0b.md`
  - `REVIEW_PE1a.md`
  - `REVIEW_PE2.md`
  - `REVIEW_PE3.md`
  - `REVIEW_PE4.md`
- Added closure addendum in `REVIEW_PE6.md` tied to `PR #229`.

### Planned
- Optional strict RFC 3339 checking for `"format": "date-time"` using `jsonschema[format-nongpl]` and a `FormatChecker`.
- Broaden Data Contract fields once agreed (governance applies).
- Add adapters for remaining 6 sources (WoS, IEEE, Semantic Scholar, CORE, Google Scholar, ScienceDirect).
- Appendix C extraction pipeline.

---

## [2.0.0] — 2026-02-17

**v2.0.0** is a major release that converges the dual-codepath architecture into a single
canonical pipeline behind the `elis` CLI.

### Breaking Changes

- **All `scripts/*_harvest.py` scripts archived** to `scripts/_archive/`. Use `elis harvest <source>` instead.
- **`scripts/elis/search_mvp.py` archived** to `scripts/_archive/elis/`. Use `elis harvest <source>` + `elis merge`.
- **`scripts/elis/screen_mvp.py` archived** to `scripts/_archive/elis/`. Use `elis screen`.
- **`elis search` subcommand removed**. Replaced by `elis harvest <source>` (PE2).
- **`elis validate --data / --schema` flags removed**. Use positional args: `elis validate <schema> <data>`.
- **`elis` requires a subcommand** — `elis` with no args now exits non-zero (argparse required=True).
- **pyproject.toml version bumped** from `0.3.0` → `2.0.0`.

### Added

- **`elis harvest <source>`** — SourceAdapter-backed harvest for `openalex`, `crossref`, `scopus` (PE2).
- **`elis merge`** — canonical merge of per-source harvest outputs into Appendix A (PE3).
- **`elis dedup`** — deterministic deduplication with cluster IDs and sidecar `duplicates.jsonl` (PE4).
- **`elis screen`** — Appendix B screening (migrated from `screen_mvp.py`) (PE0b).
- **`elis agentic asta discover / enrich`** — ASTA sidecar integration (PE5).
- **`elis export-latest`** — copies canonical artefacts from `runs/<run_id>/` to `json_jsonl/` (PE6).
- **Run manifest sidecars** — every pipeline stage emits `<output_stem>_manifest.json` alongside output (PE1a/PE1b).
- **`elis merge --from-manifest`** — read merge inputs from a previous stage manifest (PE1b).
- **`elis harvest --tier`** — tier-based result caps: testing (25) / pilot (100) / benchmark (500) / production (1000) / exhaustive (∞) (PE2).
- **`elis harvest --max-results`** — always-wins cap override (PE2).
- **`scripts/_archive/README.md`** — migration table from legacy scripts to `elis` CLI.
- **`docs/MIGRATION_GUIDE_v2.0.md`** — full migration guide.
- **`reports/audits/PE6_RC_EQUIVALENCE.md`** — PE6.1 equivalence check results (crossref, openalex, scopus: PASS).

### Changed

- All workflows migrated from `python scripts/*.py` to `elis` CLI (PE6.2):
  - `ci.yml` validate job → `elis validate`
  - `elis-validate.yml` → `elis validate`
  - `elis-agent-screen.yml` → `elis screen`
  - `elis-agent-nightly.yml` → `elis harvest crossref/openalex` + `elis merge` + `elis screen`
  - `elis-agent-search.yml` → `elis harvest crossref/openalex/scopus` + `elis merge`
  - `elis-search-preflight.yml` → `elis harvest crossref --tier testing`
  - `test_database_harvest.yml` → `elis harvest <database>`

### Removed

- `elis search` subcommand (replaced by `elis harvest`).
- `--data` / `--schema` flags on `elis validate` (replaced by positional args).
- Legacy "no-args returns zero" CLI behaviour (now requires subcommand).

---

## [v0.1.1-mvp] — 2025-10-04
### Added
- Minimal **JSON Schemas** for Data Contract v1.0 (MVP): Appendices **A** (Search), **B** (Screening), **C** (Extraction) under `schemas/`.
- **README** overhaul with hyperlinks, repo map, CI model, workflows, runbook and troubleshooting.
- `.gitattributes` to **normalise line endings** (LF) and avoid formatting churn in CI.

### Changed
- **ELIS - Bot Commit** hardened: safer branch prepare, newline-safe content handling, idempotent commits, guarded PR creation.
- **ELIS - Autoformat**: formats with Black, **renormalises line endings**, and can open a PR to `main` when configured.
- **ELIS - Validate**: always produces a report; opens/updates a small PR **only when the report changed** (noise reduced).
- Workflow naming rule: prefer ASCII `-` hyphen in `name:` to avoid display/compatibility issues.

### Fixed
- Black “**would reformat** …” failures caused by inconsistent line endings (CRLF vs LF).
- **Non fast-forward** push errors in automation (work branch now reset/synchronised correctly).
- Base64/newline mishandling in Bot Commit (text path prefers raw content; CRLF→LF normalisation).
- Minor lint/format issues (Ruff import ordering, long lines) across scripts and tests.

### CI / Automation
- **ELIS - CI**: Ruff + Black (check); tests run only when present (tolerate pytest exit code 5); `validate` is non-blocking.
- **ELIS - Housekeeping**: routine clean-up for old runs and artefacts.
- **ELIS - Agent Run**: diagnostic agent execution with artefacts uploaded as build artifacts.

### Notes
- Tagged and published as **Latest** release.

---

## [v0.1.0-mvp] — 2025-10-01
### Added
- Initial MVP: toy agent (`scripts/agent.py`), basic validator, smoke tests and baseline CI.
- Branch protection requiring `quality` and `validate` checks; squash-merge policy.

---

<!--
  Link references (GitHub renders these at the bottom; keep them updated at release time).
  Unreleased compares the latest tag with HEAD.
-->
[Unreleased]: https://github.com/rochasamurai/ELIS-SLR-Agent/compare/v2.0.0...HEAD
[v2.0.0]: https://github.com/rochasamurai/ELIS-SLR-Agent/releases/tag/v2.0.0
[v0.1.1-mvp]: https://github.com/rochasamurai/ELIS-SLR-Agent/releases/tag/v0.1.1-mvp
[v0.1.0-mvp]: https://github.com/rochasamurai/ELIS-SLR-Agent/releases/tag/v0.1.0-mvp
