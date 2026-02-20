# ELIS SLR Agent

ELIS SLR Agent is a reproducible pipeline for systematic literature reviews on electoral integrity.
Release `2.0` consolidates the workflow behind one CLI: `elis`.

## Current Release Line

- Active branch: `release/2.0`
- Package version in source: `2.0.0`
- Canonical pipeline output: `runs/<run_id>/...`
- Backward-compatibility export view: `json_jsonl/` (copy-only via `elis export-latest`)

## Canonical CLI

Primary commands:

```powershell
elis harvest <source> --search-config <path>
elis merge --inputs <harvest_outputs...>
elis dedup --input <appendix_a.json>
elis screen --input <appendix_a_deduped.json>
elis validate <schema_path> <data_path>
elis export-latest --run-id <run_id>
```

Optional sidecar workflow:

```powershell
elis agentic asta discover --query "..." --run-id <run_id>
elis agentic asta enrich --input <dedup_output> --run-id <run_id>
```

## Source Adapter Coverage in v2.0

Implemented adapters:

- `openalex`
- `crossref`
- `scopus`

Planned for later releases: Web of Science, IEEE Xplore, Semantic Scholar, CORE, Google Scholar, ScienceDirect.

## Quick Start

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"
```

Check command surface:

```powershell
elis --help
elis harvest --help
elis merge --help
elis dedup --help
elis screen --help
elis validate --help
```

## Repo Pointers

- Release plan: `docs/_active/RELEASE_PLAN_v2.0.md`
- Integration plan: `docs/_active/INTEGRATION_PLAN_V2.md`
- Harvest test plan: `docs/_active/HARVEST_TEST_PLAN.md`
- Post-release qualification plan: `docs/_active/POST_RELEASE_FUNCTIONAL_TEST_PLAN_v2.0.md`
- Workflow protocol: `AGENTS.md`
- Validation/audit policy: `AUDITS.md`
- Change history: `CHANGELOG.md`

## Pipeline Contract Notes

- `runs/<run_id>/` is authoritative.
- `json_jsonl/` is a compatibility export of the latest run.
- Stage outputs are expected to be deterministic where defined.
- Run manifests are sidecars (`*_manifest.json`) and must conform to `schemas/run_manifest.schema.json`.

## Legacy Scripts

Legacy script entrypoints are archived under `scripts/_archive/` and are retained for traceability.
Active workflows for `release/2.0` are expected to use `elis` CLI commands.

## License

MIT
