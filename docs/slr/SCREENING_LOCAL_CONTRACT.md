# Screening Local Contract (`PE-SLR-03`)

## Purpose

Define the local-first screening contract for bounded ASReview pilot runs on
`elis-server`, with review-scoped storage, schema-bound outputs, and auditable
pilot artefacts.

## Contract Summary

- Runtime target: `elis-server`
- Stage: local screening pilot (`PE-SLR-03`)
- Review-scoped root: `artifacts/screening/<review_id>/`
- Runtime-state exclusion: screening artefacts must not be stored under
  `.openclaw/`, `.claude/`, `.codex/`, or `.config/`

## Required Paths

For each `review_id`, the contract writes:

- `artifacts/screening/<review_id>/input/ELIS_Appendix_A_Search_rows.json`
- `artifacts/screening/<review_id>/output/ELIS_Appendix_B_Screening_rows.json`
- `artifacts/screening/<review_id>/audit/screening_pilot_report.json`
- `artifacts/screening/<review_id>/audit/screening_pilot_manifest.json`

## Schema Binding

- Input schema reference: `schemas/appendix_a.schema.json`
- Output schema reference: `schemas/appendix_b.schema.json`

Pilot report and manifest must include both schema references and explicit
record-cap metadata for traceable bounded execution.

## ASReview Runtime Check (`elis-server`)

Run either command:

```bash
asreview --version
python -c "import asreview; print(asreview.__version__)"
```

At least one command must succeed for AC-1 compliance.

## Bounded Pilot Run

Run a bounded pilot by calling `run_bounded_screening_pilot(...)` from
`elis.screening_local_contract` with:

- `review_id` set
- a real Appendix A input path
- `record_cap` set to a finite bound (for example `100`)

The pilot is successful when:

- run completes without exception
- output/report/manifest files are written in the review-scoped contract paths
- report confirms `stored_outside_runtime_state = true`

CLI runner:

```bash
python scripts/run_screening_local_pilot.py \
  --review-id review-001 \
  --appendix-a json_jsonl/ELIS_Appendix_A_Search_rows.json \
  --record-cap 100
```
