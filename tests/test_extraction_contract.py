"""PE-SLR-07 extraction off-host contract tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from elis.extraction_offhost_contract import (
    ExtractionOffHostContract,
    ExtractionWorkflowEnvelope,
    assert_local_extraction_unsupported,
    build_extraction_evidence_bundle,
    persist_extraction_contract_artefacts,
)


def test_ac1_off_host_workflow_envelope_is_required() -> None:
    envelope = ExtractionWorkflowEnvelope(
        review_id="review-123",
        run_id="run-1",
        trigger_source="github-actions",
    )
    assert envelope.execution_surface == "off-host-workflow"
    assert envelope.local_execution_allowed is False


def test_ac1_rejects_non_off_host_execution_surface() -> None:
    with pytest.raises(ValueError, match="off-host workflow surfaces only"):
        ExtractionWorkflowEnvelope(
            review_id="review-123",
            run_id="run-1",
            trigger_source="github-actions",
            execution_surface="local",
        )


def test_ac1_rejects_local_execution_flag_true() -> None:
    with pytest.raises(ValueError, match="Local extraction execution is unsupported"):
        ExtractionWorkflowEnvelope(
            review_id="review-123",
            run_id="run-1",
            trigger_source="github-actions",
            local_execution_allowed=True,
        )


def test_ac2_contract_declares_input_output_schema_paths() -> None:
    contract = ExtractionOffHostContract(review_id="review-123")
    assert contract.input_schema_path().as_posix() == "schemas/appendix_b.schema.json"
    assert contract.output_schema_path().as_posix() == "schemas/appendix_c.schema.json"


def test_ac2_contract_declares_output_rows_path() -> None:
    contract = ExtractionOffHostContract(review_id="review-123")
    assert (
        contract.output_rows_path().as_posix()
        == "json_jsonl/ELIS_Appendix_C_DataExtraction_rows.json"
    )


def test_ac3_evidence_bundle_contains_audit_fields() -> None:
    envelope = ExtractionWorkflowEnvelope(
        review_id="review-777",
        run_id="run-777",
        trigger_source="github-actions",
    )
    contract = ExtractionOffHostContract(review_id="review-777")
    output_rows = [
        {"record_id": "r2", "title": "Beta"},
        {"record_id": "r1", "title": "Alpha"},
    ]
    bundle = build_extraction_evidence_bundle(
        envelope=envelope,
        contract=contract,
        output_rows=output_rows,
        commit_sha="abc1234",
        generated_at="2026-04-21T12:00:00Z",
    )
    assert bundle["review_id"] == "review-777"
    assert bundle["run_id"] == "run-777"
    assert bundle["output_record_count"] == 2
    assert bundle["output_record_ids"] == ["r1", "r2"]
    assert len(bundle["output_rows_sha256"]) == 64
    assert bundle["generated_at"] == "2026-04-21T12:00:00Z"


def test_ac3_bundle_digest_is_reproducible_for_same_payload() -> None:
    envelope = ExtractionWorkflowEnvelope(
        review_id="review-1",
        run_id="run-1",
        trigger_source="github-actions",
    )
    contract = ExtractionOffHostContract(review_id="review-1")
    rows = [{"record_id": "r1", "x": 1}, {"record_id": "r2", "x": 2}]

    b1 = build_extraction_evidence_bundle(
        envelope=envelope,
        contract=contract,
        output_rows=rows,
        commit_sha="deadbeef",
        generated_at="2026-04-21T00:00:00Z",
    )
    b2 = build_extraction_evidence_bundle(
        envelope=envelope,
        contract=contract,
        output_rows=rows,
        commit_sha="deadbeef",
        generated_at="2026-04-21T00:00:00Z",
    )
    assert b1["output_rows_sha256"] == b2["output_rows_sha256"]
    assert b1 == b2


def test_ac3_persisted_artefacts_are_written(tmp_path: Path) -> None:
    contract = ExtractionOffHostContract(review_id="r1", root=tmp_path)
    envelope = ExtractionWorkflowEnvelope(
        review_id="r1",
        run_id="run-9",
        trigger_source="github-actions",
    )
    bundle = persist_extraction_contract_artefacts(
        envelope=envelope,
        contract=contract,
        output_rows=[{"record_id": "rec-1"}],
        commit_sha="cafef00d",
        generated_at="2026-04-21T01:02:03Z",
    )

    assert contract.envelope_path().exists()
    assert contract.evidence_bundle_path().exists()

    persisted_envelope = json.loads(
        contract.envelope_path().read_text(encoding="utf-8")
    )
    persisted_bundle = json.loads(
        contract.evidence_bundle_path().read_text(encoding="utf-8")
    )
    assert persisted_envelope["execution_surface"] == "off-host-workflow"
    assert persisted_bundle["commit_sha"] == "cafef00d"
    assert persisted_bundle == bundle


def test_ac4_local_execution_is_explicitly_unsupported() -> None:
    with pytest.raises(RuntimeError, match="Local extraction execution is unsupported"):
        assert_local_extraction_unsupported()


def test_ac4_contract_paths_are_review_scoped(tmp_path: Path) -> None:
    contract = ExtractionOffHostContract(review_id="review-abc", root=tmp_path)
    assert contract.envelope_path() == (
        tmp_path / "review-abc" / "audit" / "extraction_workflow_envelope.json"
    )
    assert contract.evidence_bundle_path() == (
        tmp_path / "review-abc" / "audit" / "extraction_evidence_bundle.json"
    )
