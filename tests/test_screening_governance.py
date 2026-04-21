"""PE-SLR-04 screening governance tests."""

from __future__ import annotations

import pytest

from elis.screening_governance import (
    CapacityPolicy,
    ScreeningDecision,
    DEFAULT_CAPACITY_POLICY,
    enforce_capacity,
    generate_audit_bundle,
    is_borderline,
    surface_borderline_cases,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _decision(
    record_id: str = "r1",
    source_id: str = "s1",
    title: str = "A title",
    decision: str = "included",
    rationale: str = "relevant to topic",
    decided_at: str = "2026-04-21T00:00:00Z",
    reviewer: str = "automated",
) -> ScreeningDecision:
    return ScreeningDecision(
        record_id=record_id,
        source_id=source_id,
        title=title,
        decision=decision,
        rationale=rationale,
        decided_at=decided_at,
        reviewer=reviewer,
    )


# ---------------------------------------------------------------------------
# AC-1: provenance and rationale fields
# ---------------------------------------------------------------------------


def test_decision_preserves_all_provenance_fields() -> None:
    d = _decision(record_id="r42", source_id="doi:10.1/x", title="Test paper")
    assert d.record_id == "r42"
    assert d.source_id == "doi:10.1/x"
    assert d.title == "Test paper"
    assert d.decided_at == "2026-04-21T00:00:00Z"
    assert d.reviewer == "automated"


def test_decision_requires_non_empty_rationale() -> None:
    with pytest.raises(ValueError, match="rationale"):
        _decision(rationale="")


def test_decision_requires_non_empty_record_id() -> None:
    with pytest.raises(ValueError, match="record_id"):
        _decision(record_id="")


def test_decision_requires_non_empty_source_id() -> None:
    with pytest.raises(ValueError, match="source_id"):
        _decision(source_id="")


def test_decision_rejects_invalid_decision_value() -> None:
    with pytest.raises(ValueError, match="decision must be one of"):
        _decision(decision="maybe")


# ---------------------------------------------------------------------------
# AC-2: borderline / discrepant case detection
# ---------------------------------------------------------------------------


def test_is_borderline_by_decision_field() -> None:
    assert is_borderline(_decision(decision="borderline", rationale="review required"))


def test_is_borderline_by_rationale_marker() -> None:
    assert is_borderline(
        _decision(decision="included", rationale="uncertain relevance")
    )


def test_is_not_borderline_for_clear_inclusion() -> None:
    assert not is_borderline(
        _decision(decision="included", rationale="directly relevant")
    )


def test_surface_borderline_cases_filters_correctly() -> None:
    decisions = [
        _decision(record_id="r1", decision="included", rationale="clear match"),
        _decision(record_id="r2", decision="borderline", rationale="ambiguous scope"),
        _decision(record_id="r3", decision="excluded", rationale="out of scope"),
        _decision(
            record_id="r4", decision="included", rationale="uncertain methodology"
        ),
    ]
    borderline = surface_borderline_cases(decisions)
    ids = {d.record_id for d in borderline}
    assert ids == {"r2", "r4"}


def test_surface_borderline_cases_empty_input() -> None:
    assert surface_borderline_cases([]) == []


# ---------------------------------------------------------------------------
# AC-3: reproducible audit bundle
# ---------------------------------------------------------------------------


def test_audit_bundle_contains_required_fields() -> None:
    decisions = [
        _decision(record_id="r1", decision="included"),
        _decision(record_id="r2", decision="excluded", rationale="off-topic"),
        _decision(record_id="r3", decision="borderline", rationale="borderline case"),
    ]
    bundle = generate_audit_bundle("review-001", decisions)

    assert bundle["schema_version"] == "1.0"
    assert bundle["review_id"] == "review-001"
    assert bundle["stage"] == "screening-governance"
    assert bundle["record_total"] == 3
    assert bundle["decision_counts"]["included"] == 1
    assert bundle["decision_counts"]["excluded"] == 1
    assert bundle["decision_counts"]["borderline"] == 1
    assert bundle["borderline_count"] == 1
    assert bundle["borderline_ids"] == ["r3"]
    assert "generated_at" in bundle


def test_audit_bundle_borderline_ids_are_sorted() -> None:
    decisions = [
        _decision(record_id="zz", decision="borderline", rationale="borderline"),
        _decision(record_id="aa", decision="borderline", rationale="borderline"),
    ]
    bundle = generate_audit_bundle("r", decisions)
    assert bundle["borderline_ids"] == ["aa", "zz"]


def test_audit_bundle_includes_capacity_policy() -> None:
    bundle = generate_audit_bundle(
        "r", [], policy=CapacityPolicy(max_records_per_run=50)
    )
    assert bundle["capacity_policy"]["max_records_per_run"] == 50


def test_audit_bundle_empty_decisions() -> None:
    bundle = generate_audit_bundle("empty-review", [])
    assert bundle["record_total"] == 0
    assert bundle["borderline_count"] == 0
    assert bundle["decision_counts"] == {}


# ---------------------------------------------------------------------------
# AC-4: capacity policy
# ---------------------------------------------------------------------------


def test_default_capacity_policy_values() -> None:
    p = DEFAULT_CAPACITY_POLICY
    assert p.max_records_per_run == 100
    assert p.max_records_per_batch == 500
    assert p.max_concurrent_runs == 1
    assert p.min_seconds_between_runs == 0


def test_enforce_capacity_truncates_to_policy_limit() -> None:
    records = list(range(200))
    policy = CapacityPolicy(max_records_per_run=10)
    result = enforce_capacity(records, policy)
    assert len(result) == 10
    assert result == list(range(10))


def test_enforce_capacity_returns_all_when_under_limit() -> None:
    records = list(range(5))
    result = enforce_capacity(records)
    assert result == records


def test_capacity_policy_rejects_zero_max_records() -> None:
    with pytest.raises(ValueError, match="max_records_per_run must be positive"):
        CapacityPolicy(max_records_per_run=0)


def test_capacity_policy_rejects_negative_min_seconds() -> None:
    with pytest.raises(
        ValueError, match="min_seconds_between_runs must be non-negative"
    ):
        CapacityPolicy(min_seconds_between_runs=-1)
