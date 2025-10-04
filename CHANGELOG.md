# Changelog
<!--
  Format: Keep a Changelog (human-readable), newest first. Dates in UTC (YYYY-MM-DD).
  Scope: This file records user-visible changes across releases (features, fixes, CI behaviour,
  docs). Use concise, neutral UK English. Each release gets its own section.
-->

## [Unreleased]
### Planned
- Optional strict RFC 3339 checking for `"format": "date-time"` using `jsonschema[format-nongpl]` and a `FormatChecker`.
- Broaden Data Contract fields once agreed (governance applies).
- Expand agent logic beyond toy outputs; add property-based tests.

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
[Unreleased]: https://github.com/rochasamurai/ELIS-SLR-Agent/compare/v0.1.1-mvp...HEAD
[v0.1.1-mvp]: https://github.com/rochasamurai/ELIS-SLR-Agent/releases/tag/v0.1.1-mvp
[v0.1.0-mvp]: https://github.com/rochasamurai/ELIS-SLR-Agent/releases/tag/v0.1.0-mvp
