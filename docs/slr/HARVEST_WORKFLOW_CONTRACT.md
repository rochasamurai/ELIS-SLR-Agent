# Harvest Workflow Contract

This document defines the canonical Harvest contract for `PE-SLR-01`.

## Canonical entrypoint

Harvest is workflow-governed. The canonical dispatch entrypoint is:

- `.github/workflows/elis-agent-search.yml`

This workflow is the approved route for a governed Harvest run that produces
Appendix A artefacts for review work.

`elis-search-preflight.yml` remains a smoke test only. It is not the canonical
Harvest run entrypoint.

## Governance boundary

Harvest search, export, and source API traffic stays off `elis-server`
local-agent execution.

The following actions are workflow-only for the current architecture:

- `elis harvest ...`
- direct external source API harvest calls
- workflow-managed export and evidence bundling

`elis-server` may inspect committed artefacts and workflow outputs after the
fact, but it must not become the execution surface for Harvest acquisition in
`PE-SLR-01`.

## Storage contract

Each governed Harvest run is review-scoped under:

```text
artifacts/harvest/<review_id>/
  raw/
    crossref.json
    crossref_manifest.json
    openalex.json
    openalex_manifest.json
    scopus.json
    scopus_manifest.json
  canonical/
    ELIS_Appendix_A_Search_rows.json
    ELIS_Appendix_A_Search_rows_manifest.json
    merge_report.json
  evidence/
    harvest_evidence.json
```

The workflow also publishes the canonical Appendix A output back to:

```text
json_jsonl/ELIS_Appendix_A_Search_rows.json
json_jsonl/ELIS_Appendix_A_Search_rows_manifest.json
```

That publication path is for repository-facing downstream use. The
review-scoped `artifacts/harvest/<review_id>/...` tree is the stable Harvest
storage contract for workflow evidence.

## Schemas

Harvest outputs and evidence are governed by committed schemas:

- `schemas/appendix_a_harvester.schema.json` for per-source raw Harvest output
- `schemas/appendix_a.schema.json` for canonical Appendix A output
- `schemas/run_manifest.schema.json` for all Harvest manifest sidecars
- `schemas/harvest_evidence.schema.json` for the representative evidence bundle

## Representative run requirements

A representative Harvest run is valid only if it:

- is started through `.github/workflows/elis-agent-search.yml`
- writes per-source outputs and manifest sidecars into `artifacts/harvest/<review_id>/raw/`
- writes canonical Appendix A, its manifest, and `merge_report.json` into `artifacts/harvest/<review_id>/canonical/`
- writes `harvest_evidence.json` into `artifacts/harvest/<review_id>/evidence/`
- uploads the review-scoped Harvest bundle as a GitHub Actions artefact

## Current source set

`PE-SLR-01` formalises the currently governed Harvest sources used by the
workflow:

- Crossref
- OpenAlex
- Scopus

Expanding the governed source set is a later PE concern and must preserve this
workflow and storage contract.
