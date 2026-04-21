"""PE-SLR-06 local support analysis tests."""

from __future__ import annotations

import pytest

from elis.local_support_analysis import (
    BibliometricCluster,
    CapacityReport,
    DiscrepancyReport,
    cluster_by_title_similarity,
    detect_discrepancies,
    measure_capacity_impact,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _rec(record_id: str, title: str) -> dict:
    return {"record_id": record_id, "title": title}


# ---------------------------------------------------------------------------
# AC-1: Bibliometric clustering on bounded local datasets
# ---------------------------------------------------------------------------


def test_cluster_groups_similar_titles() -> None:
    records = [
        _rec("r1", "Machine learning in electoral systems"),
        _rec("r2", "Machine learning for electoral systems review"),
        _rec("r3", "Completely unrelated zoology paper"),
    ]
    clusters = cluster_by_title_similarity(records, threshold=0.4)
    for c in clusters:
        if "r1" in c.record_ids:
            assert "r2" in c.record_ids


def test_cluster_separates_dissimilar_titles() -> None:
    records = [
        _rec("r1", "quantum physics optics laser"),
        _rec("r2", "sociological study migration patterns"),
    ]
    clusters = cluster_by_title_similarity(records, threshold=0.5)
    for c in clusters:
        assert len(c.record_ids) == 1


def test_cluster_bounded_by_max_records() -> None:
    records = [_rec(f"r{i}", f"unique title number {i}") for i in range(200)]
    clusters = cluster_by_title_similarity(records, max_records=10)
    all_ids = {r for c in clusters for r in c.record_ids}
    assert all(int(r[1:]) < 10 for r in all_ids)


def test_cluster_advisory_only_flag() -> None:
    clusters = cluster_by_title_similarity([_rec("r1", "A title about science")])
    assert all(c.advisory_only for c in clusters)


def test_cluster_rejects_non_advisory() -> None:
    with pytest.raises(ValueError, match="advisory_only must be True"):
        BibliometricCluster(
            cluster_id="c1",
            record_ids=("r1",),
            representative_title="T",
            similarity_basis="test",
            advisory_only=False,
        )


def test_cluster_rejects_empty_record_ids() -> None:
    with pytest.raises(ValueError, match="record_ids must not be empty"):
        BibliometricCluster(
            cluster_id="c1",
            record_ids=(),
            representative_title="T",
            similarity_basis="test",
        )


def test_cluster_empty_input_returns_empty() -> None:
    assert cluster_by_title_similarity([]) == []


def test_cluster_deterministic_for_same_input() -> None:
    records = [_rec(f"r{i}", f"systematic review biology study {i}") for i in range(6)]
    c1 = cluster_by_title_similarity(records, threshold=0.3)
    c2 = cluster_by_title_similarity(records, threshold=0.3)
    assert [c.record_ids for c in c1] == [c.record_ids for c in c2]


def test_cluster_all_records_covered() -> None:
    records = [_rec(f"r{i}", f"title {i} about research") for i in range(5)]
    clusters = cluster_by_title_similarity(records, threshold=0.9)
    all_ids = {r for c in clusters for r in c.record_ids}
    assert all_ids == {r["record_id"] for r in records}


# ---------------------------------------------------------------------------
# AC-2: Discrepancy outputs stored as advisory artefacts only
# ---------------------------------------------------------------------------


def test_discrepancy_report_advisory_only() -> None:
    report = detect_discrepancies([_rec("r1", "A title"), _rec("r2", "B title")])
    assert report.advisory_only is True
    assert report.disclaimer != ""


def test_discrepancy_detects_near_duplicates() -> None:
    records = [
        _rec("r1", "Systematic review artificial intelligence healthcare"),
        _rec("r2", "Systematic review artificial intelligence healthcare applications"),
        _rec("r3", "An entirely different paper about medieval history"),
    ]
    report = detect_discrepancies(records, similarity_threshold=0.5)
    pairs = {frozenset(p) for p in report.potential_duplicates}
    assert frozenset({"r1", "r2"}) in pairs


def test_discrepancy_no_duplicates_empty_pairs() -> None:
    records = [
        _rec("r1", "quantum physics optics laser"),
        _rec("r2", "sociological migration patterns"),
    ]
    report = detect_discrepancies(records, similarity_threshold=0.9)
    assert report.conflict_count == 0
    assert report.potential_duplicates == ()


def test_discrepancy_bounded_by_max_records() -> None:
    records = [_rec(f"r{i}", "same title systematic review study") for i in range(200)]
    report = detect_discrepancies(records, max_records=10)
    all_ids = {r for pair in report.potential_duplicates for r in pair}
    assert all(int(r[1:]) < 10 for r in all_ids)


def test_discrepancy_pairs_are_sorted() -> None:
    records = [
        _rec("zz", "identical title systematic review study"),
        _rec("aa", "identical title systematic review study"),
    ]
    report = detect_discrepancies(records, similarity_threshold=0.5)
    if report.potential_duplicates:
        a, b = report.potential_duplicates[0]
        assert a <= b


# ---------------------------------------------------------------------------
# AC-3: Runtime safeguard prevents final-decision use
# ---------------------------------------------------------------------------


def test_discrepancy_rejects_non_advisory() -> None:
    with pytest.raises(ValueError, match="advisory_only must be True"):
        DiscrepancyReport(
            report_id="r",
            potential_duplicates=(),
            conflict_count=0,
            generated_at="2026-04-21T00:00:00Z",
            advisory_only=False,
        )


def test_discrepancy_as_final_decision_raises() -> None:
    report = detect_discrepancies([_rec("r1", "some title")])
    with pytest.raises(TypeError, match="cannot be used as a final review decision"):
        report.as_final_decision()


def test_cluster_advisory_disclaimer_consistent() -> None:
    report = detect_discrepancies([_rec("r1", "a title")])
    assert "advisory" in report.disclaimer.lower()


# ---------------------------------------------------------------------------
# AC-4: Capacity impact measured and documented
# ---------------------------------------------------------------------------


def test_measure_capacity_returns_report() -> None:
    records = [_rec(f"r{i}", f"unique title {i}") for i in range(20)]
    result, report = measure_capacity_impact(
        cluster_by_title_similarity, records, max_records=10
    )
    assert isinstance(report, CapacityReport)
    assert report.record_count == 10
    assert report.max_records_used == 10
    assert report.elapsed_seconds >= 0
    assert report.operation == "cluster_by_title_similarity"


def test_measure_capacity_elapsed_non_negative() -> None:
    records = [_rec("r1", "a title")]
    _, report = measure_capacity_impact(cluster_by_title_similarity, records)
    assert report.elapsed_seconds >= 0


def test_measure_capacity_result_matches_direct_call() -> None:
    records = [_rec(f"r{i}", f"title {i} science study") for i in range(5)]
    result, _ = measure_capacity_impact(
        cluster_by_title_similarity, records, max_records=5, threshold=0.3
    )
    direct = cluster_by_title_similarity(records[:5], threshold=0.3)
    assert [c.record_ids for c in result] == [c.record_ids for c in direct]


def test_measure_capacity_uses_max_records_bound() -> None:
    records = [_rec(f"r{i}", f"different title {i}") for i in range(100)]
    _, report = measure_capacity_impact(
        cluster_by_title_similarity, records, max_records=15
    )
    assert report.record_count == 15
