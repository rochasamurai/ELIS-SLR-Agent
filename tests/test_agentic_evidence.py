"""Tests for PE5 evidence span validation."""

from __future__ import annotations

from elis.agentic.evidence import validate_evidence_spans


def test_validate_evidence_spans_marks_valid_and_invalid() -> None:
    record = {
        "title": "Electoral Integrity and Blockchain Voting",
        "abstract": "This study evaluates auditability and transparency.",
    }
    spans = ["blockchain voting", "missing phrase", "auditability"]
    result = validate_evidence_spans(record, spans)

    assert result[0]["valid"] is True
    assert result[1]["valid"] is False
    assert result[2]["valid"] is True


def test_validate_evidence_spans_handles_empty_values() -> None:
    record = {"title": None, "abstract": None}
    result = validate_evidence_spans(record, ["", "x"])
    assert result == [{"text": "", "valid": False}, {"text": "x", "valid": False}]
