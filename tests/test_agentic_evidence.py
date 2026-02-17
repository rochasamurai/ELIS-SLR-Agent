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


# ---------------------------------------------------------------------------
# Adversarial tests (Validator-added)
# ---------------------------------------------------------------------------


def test_validate_spans_case_insensitive() -> None:
    """Case-insensitive matching: upper-case span found in lower-case title."""
    record = {"title": "blockchain voting systems", "abstract": ""}
    result = validate_evidence_spans(record, ["BLOCKCHAIN VOTING"])
    assert result[0]["valid"] is True


def test_validate_spans_empty_span_list() -> None:
    """Empty span list returns empty validated list (no error)."""
    record = {"title": "Some Paper", "abstract": "Some abstract."}
    assert validate_evidence_spans(record, []) == []


def test_validate_spans_span_equals_title() -> None:
    """Span exactly equal to title is valid."""
    title = "Electoral Integrity"
    record = {"title": title, "abstract": ""}
    result = validate_evidence_spans(record, [title])
    assert result[0]["valid"] is True


def test_validate_spans_found_in_abstract_only() -> None:
    """Span not in title but found in abstract is still valid."""
    record = {"title": "A Generic Title", "abstract": "Specific term here."}
    result = validate_evidence_spans(record, ["specific term here"])
    assert result[0]["valid"] is True


def test_validate_spans_found_in_title_only_no_abstract() -> None:
    """Record missing abstract key: span found in title is still valid."""
    record = {"title": "Auditability in elections"}
    result = validate_evidence_spans(record, ["auditability"])
    assert result[0]["valid"] is True


def test_validate_spans_invalid_flagged_not_removed() -> None:
    """Output length equals input length — invalid spans are flagged, not dropped."""
    record = {"title": "Some paper", "abstract": "Some abstract."}
    spans = ["not here", "also missing", "not here either"]
    result = validate_evidence_spans(record, spans)
    assert len(result) == 3
    assert all(s["valid"] is False for s in result)


def test_validate_spans_none_span_is_invalid() -> None:
    """None span (coerced to '') is treated as invalid."""
    record = {"title": "Valid title", "abstract": "Valid abstract."}
    result = validate_evidence_spans(record, [None])  # type: ignore[list-item]
    assert result[0]["valid"] is False
    assert result[0]["text"] == ""


def test_validate_spans_returns_text_key() -> None:
    """Each result dict carries a 'text' key with the original span string."""
    record = {"title": "Alpha Beta", "abstract": ""}
    result = validate_evidence_spans(record, ["alpha"])
    assert "text" in result[0]
    assert result[0]["text"] == "alpha"
