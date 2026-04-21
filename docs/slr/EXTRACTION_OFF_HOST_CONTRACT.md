# Extraction Off-Host Contract (`PE-SLR-07`)

## Purpose

Define the authoritative extraction execution contract for the current hybrid
SLR architecture:

- Extraction is workflow-governed and off-host.
- Local extraction execution is explicitly unsupported on current hardware.
- Inputs/outputs and evidence bundle requirements are auditable and reproducible.

---

## AC-1 — Extraction Remains Workflow-Governed and Off-Host

`ExtractionWorkflowEnvelope` is the required execution envelope.

Required fields:

| Field | Rule |
|------|------|
| `execution_surface` | Must be `"off-host-workflow"` |
| `local_execution_allowed` | Must be `False` |
| `review_id`, `run_id`, `trigger_source` | Must be non-blank |

Construction fails for unsupported values.

---

## AC-2 — Schema and Evidence Requirements

`ExtractionOffHostContract` is the path contract.

| Contract path | Value |
|------|------|
| Input schema | `schemas/appendix_b.schema.json` |
| Output schema | `schemas/appendix_c.schema.json` |
| Output rows | `json_jsonl/ELIS_Appendix_C_DataExtraction_rows.json` |
| Envelope artefact | `artifacts/extraction_offhost/<review_id>/audit/extraction_workflow_envelope.json` |
| Evidence bundle artefact | `artifacts/extraction_offhost/<review_id>/audit/extraction_evidence_bundle.json` |

---

## AC-3 — Auditable and Reproducible Output Evidence

`build_extraction_evidence_bundle(...)` produces a deterministic bundle containing:

- run identity (`review_id`, `run_id`, `trigger_source`)
- execution controls (`execution_surface`, `local_execution_allowed`)
- schema/output paths
- output record count and sorted `output_record_ids`
- content digest `output_rows_sha256`
- source commit SHA and generation timestamp

For identical inputs (including `generated_at`), the bundle and digest are identical.

`persist_extraction_contract_artefacts(...)` writes both envelope and bundle as JSON
artefacts under the review-scoped audit directory.

---

## AC-4 — Local Execution Explicitly Unsupported

`assert_local_extraction_unsupported()` always raises:

- `RuntimeError("Local extraction execution is unsupported on current hardware...")`

This is a deliberate hard block to prevent accidental local migration.

---

## Usage Example

```python
from elis.extraction_offhost_contract import (
    ExtractionOffHostContract,
    ExtractionWorkflowEnvelope,
    persist_extraction_contract_artefacts,
)

envelope = ExtractionWorkflowEnvelope(
    review_id="review-2026-001",
    run_id="gh-run-123456",
    trigger_source="github-actions",
)
contract = ExtractionOffHostContract(review_id="review-2026-001")

bundle = persist_extraction_contract_artefacts(
    envelope=envelope,
    contract=contract,
    output_rows=[{"record_id": "rec-001"}, {"record_id": "rec-002"}],
    commit_sha="abc123def456",
)
print(bundle["output_rows_sha256"])
```
