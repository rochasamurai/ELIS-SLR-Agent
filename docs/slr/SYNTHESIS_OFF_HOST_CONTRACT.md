# Synthesis Off-Host Contract (`PE-SLR-08`)

## Purpose

Define the authoritative off-host workflow contract for synthesis and thematic
integration while preserving evidence traceability and explicit human oversight.

---

## AC-1 — Synthesis Remains Workflow-Governed and Off-Host

`SynthesisWorkflowEnvelope` is mandatory for every synthesis run:

- `execution_surface` must be `"off-host-workflow"`
- `local_execution_allowed` must be `False`
- `review_id`, `run_id`, and `trigger_source` must be present

Unsupported values fail at construction time.

---

## AC-2 — Cross-Study Reasoning Preserves Evidence Traceability

`SynthesisReasoningTrace` captures claim-to-evidence linkage:

| Field | Description |
|------|------|
| `claim_id` | Stable synthesis claim identifier |
| `supporting_record_ids` | Source record IDs supporting the claim |
| `evidence_refs` | Traceable evidence references (e.g. Appendix C rows) |
| `reasoning_summary` | Human-readable cross-study reasoning summary |

`build_synthesis_trace_bundle(...)` produces an auditable bundle including:

- sorted claim index
- canonical SHA-256 digest (`trace_sha256`) over trace payload
- commit SHA and generation timestamp
- execution envelope metadata

---

## AC-3 — Human-Review Checkpoints for High-Impact Outputs

`build_high_impact_checkpoints(findings)` creates mandatory
`HumanReviewCheckpoint` entries for findings with `impact_level` of:

- `high`
- `critical`

Each checkpoint requires reviewer sign-off (`reviewer_required=True`) and
starts as `status="pending"`.

---

## AC-4 — Migration Criteria Documented but Not Activated

`LocalMigrationCriteria` stores future migration preconditions.

`assert_local_migration_not_activated(criteria)` enforces that
`activation_requested` remains `False` in PE-SLR-08. Attempted activation raises
`RuntimeError`.

This keeps local migration criteria explicit and auditable without enabling
local synthesis execution.

---

## Artefact Contract

`SynthesisOffHostContract(review_id)` writes review-scoped audit artefacts:

| Artefact | Path |
|------|------|
| Workflow envelope | `artifacts/synthesis_offhost/<review_id>/audit/synthesis_workflow_envelope.json` |
| Trace bundle | `artifacts/synthesis_offhost/<review_id>/audit/synthesis_trace_bundle.json` |
| Human-review checkpoints | `artifacts/synthesis_offhost/<review_id>/audit/synthesis_human_review_checkpoints.json` |

Input traceability anchor:
- extraction input schema: `schemas/appendix_c.schema.json`

---

## Minimal Usage

```python
from elis.synthesis_offhost_contract import (
    SynthesisWorkflowEnvelope,
    SynthesisOffHostContract,
    SynthesisReasoningTrace,
    persist_synthesis_contract_artefacts,
)

envelope = SynthesisWorkflowEnvelope(
    review_id="review-2026-01",
    run_id="gh-run-789",
    trigger_source="github-actions",
)
contract = SynthesisOffHostContract(review_id="review-2026-01")
traces = [
    SynthesisReasoningTrace(
        claim_id="claim-001",
        supporting_record_ids=("rec-11", "rec-42"),
        evidence_refs=("appendix-c:row-11", "appendix-c:row-42"),
        reasoning_summary="Two independent studies converge on the same effect.",
    )
]
bundle = persist_synthesis_contract_artefacts(
    envelope=envelope,
    contract=contract,
    traces=traces,
    findings=[{"claim_id": "claim-001", "impact_level": "high"}],
    commit_sha="abc123def",
)
print(bundle["trace_sha256"])
```
