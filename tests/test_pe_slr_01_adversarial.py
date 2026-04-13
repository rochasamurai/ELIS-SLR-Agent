"""Adversarial tests for PE-SLR-01 harvest contract."""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import jsonschema
from elis.harvest_contract import (
    HarvestWorkflowContract,
    build_harvest_evidence,
    write_harvest_evidence,
)


@pytest.fixture
def evidence_schema():
    return json.loads(
        Path("schemas/harvest_evidence.schema.json").read_text(encoding="utf-8")
    )


def test_contract_with_empty_review_id():
    contract = HarvestWorkflowContract(review_id="")
    # Should still generate paths, but review_id in payload will fail schema
    assert contract.bundle_root() == Path("artifacts/harvest")


def test_evidence_payload_missing_required_fields(evidence_schema):
    payload = {"schema_version": "1.0", "review_id": "test"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=payload, schema=evidence_schema)


def test_evidence_payload_invalid_schema_version(evidence_schema):
    contract = HarvestWorkflowContract(review_id="test")
    payload = build_harvest_evidence(
        review_id="test",
        search_config="cfg.yml",
        tier="test",
        sources=["openalex"],
        contract=contract,
    )
    payload["schema_version"] = "2.0"  # Const is "1.0"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=payload, schema=evidence_schema)


def test_evidence_payload_empty_sources(evidence_schema):
    contract = HarvestWorkflowContract(review_id="test")
    payload = build_harvest_evidence(
        review_id="test",
        search_config="cfg.yml",
        tier="test",
        sources=[],  # minItems: 1
        contract=contract,
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=payload, schema=evidence_schema)


def test_evidence_payload_empty_review_id(evidence_schema):
    contract = HarvestWorkflowContract(review_id="")
    payload = build_harvest_evidence(
        review_id="",  # minLength: 1
        search_config="cfg.yml",
        tier="test",
        sources=["openalex"],
        contract=contract,
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=payload, schema=evidence_schema)


def test_write_harvest_evidence_creates_directories(tmp_path):
    contract = HarvestWorkflowContract(review_id="new-review", root=tmp_path)
    evidence_path = write_harvest_evidence(
        review_id="new-review",
        search_config="cfg.yml",
        tier="test",
        sources=["openalex"],
        contract=contract,
    )
    assert evidence_path.exists()
    assert evidence_path.parent.name == "evidence"
    assert evidence_path.parent.parent.name == "new-review"
