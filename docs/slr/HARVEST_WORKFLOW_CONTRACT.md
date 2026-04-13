# Harvest Workflow Contract

This document defines the canonical Harvest contract.  It was established in
`PE-SLR-01` and extended in `PE-SLR-02` with reliability and audit provisions.

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
fact, but it must not become the execution surface for Harvest acquisition.

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
    harvest_audit_log.jsonl
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

---

## Reliability contract (PE-SLR-02)

The following reliability invariants are introduced by `PE-SLR-02` and are
enforced by `elis/harvest_workflow.py`.

### Audit log (AC-1)

Every governed Harvest run that uses the Python-level reliability helpers MUST
write a structured audit log to:

```text
artifacts/harvest/<review_id>/evidence/harvest_audit_log.jsonl
```

Each line is a JSON object (keys sorted) with at minimum:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 string | UTC time of the attempt |
| `review_id` | string | Harvest review identifier |
| `source` | string | Data source name |
| `step` | string | Logical step label (e.g. `"fetch"`, `"write"`) |
| `status` | string | `"success"`, `"retry"`, or `"failure"` |
| `attempt` | integer | Attempt number (1-based) |
| `error` | string | Error message if `status` is `"retry"` or `"failure"` |

This log is sufficient for audit replay: a reader can reconstruct the
sequence of steps, their outcomes, and the first error for each failure.

### Failure diagnostics (AC-2)

When a harvest step fails after all retries, the error raised is
`HarvestStepError` (from `elis.harvest_workflow`).  Its string
representation is the operator-visible diagnostic:

```
[HARVEST FAILURE] review=<review_id> source=<source> step=<step> attempts=<N> cause=<exc>
```

This message is designed to be forwarded to operator channels (Discord,
CI step summaries, logs) without further transformation.

### Retry policy (AC-3)

The default retry policy is defined by `HarvestRetryPolicy`:

| Field | Default | Description |
|-------|---------|-------------|
| `max_attempts` | `3` | Total attempts including the first |
| `backoff_seconds` | `2.0` | Wait between retries in seconds |

The policy is a frozen dataclass and may be overridden per-call.  It is
passed explicitly to `run_with_retry()` so there are no hidden global
defaults.

### Output packaging (AC-4)

`package_harvest_output()` returns a deterministic, review-specific output
manifest.  Reproducibility guarantees:

- The `sources` list is always sorted.
- All path values are derived from `HarvestWorkflowContract` path methods.
- Calling this function twice with the same `sources` and `contract`
  produces byte-for-byte identical JSON output.
- The manifest is review-scoped: every path is under
  `artifacts/harvest/<review_id>/`.
