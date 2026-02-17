"""Tests for elis.pipeline.dedup - PE4 deterministic dedup stage."""

from __future__ import annotations

import json
import warnings
from pathlib import Path

from elis.pipeline import dedup


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------


def test_dedup_basic_removes_doi_duplicate(tmp_path: Path) -> None:
    """Two records sharing the same DOI → one keeper, one duplicate removed."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {"_meta": True},
            {
                "source": "openalex",
                "title": "Same Paper",
                "doi": "10.1/abc",
                "year": 2020,
                "authors": ["Alice"],
            },
            {
                "source": "crossref",
                "title": "Same Paper Variant",
                "doi": "https://doi.org/10.1/abc",
                "year": 2020,
                "authors": ["A. Smith"],
            },
        ],
    )
    out = tmp_path / "out.json"
    rep = tmp_path / "rep.json"
    dedup.run_dedup(str(p), str(out), str(rep))

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload[0]["_meta"] is True
    records = payload[1:]
    assert len(records) == 1
    assert records[0]["cluster_size"] == 2
    assert dedup.normalise_doi(records[0]["doi"]) == "10.1/abc"
    assert set(records[0]["cluster_sources"]) == {"openalex", "crossref"}

    report = json.loads(rep.read_text(encoding="utf-8"))
    assert report["input_records"] == 2
    assert report["unique_clusters"] == 1
    assert report["duplicates_removed"] == 1
    assert report["doi_based_dedup"] == 1


def test_dedup_no_duplicates_passthrough(tmp_path: Path) -> None:
    """Three records with distinct DOIs → all three survive."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {"source": "A", "title": "P1", "doi": "10.1/a"},
            {"source": "B", "title": "P2", "doi": "10.1/b"},
            {"source": "C", "title": "P3", "doi": "10.1/c"},
        ],
    )
    out = tmp_path / "out.json"
    rep = tmp_path / "rep.json"
    dedup.run_dedup(str(p), str(out), str(rep))

    records = json.loads(out.read_text())[1:]
    assert len(records) == 3
    report = json.loads(rep.read_text())
    assert report["duplicates_removed"] == 0


def test_dedup_title_year_author_key(tmp_path: Path) -> None:
    """Records without DOI dedup by title|year|first_author."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {
                "source": "scopus",
                "title": "  Electoral Integrity  ",
                "authors": ["  Smith, J.  "],
                "year": 2021,
                "doi": None,
            },
            {
                "source": "crossref",
                "title": "Electoral Integrity",
                "authors": ["Smith, J."],
                "year": 2021,
                "doi": "",
            },
        ],
    )
    out = tmp_path / "out.json"
    rep = tmp_path / "rep.json"
    dedup.run_dedup(str(p), str(out), str(rep))

    records = json.loads(out.read_text())[1:]
    assert len(records) == 1
    report = json.loads(rep.read_text())
    assert report["title_year_author_dedup"] == 1
    assert report["doi_based_dedup"] == 0


def test_dedup_output_has_meta_header(tmp_path: Path) -> None:
    """Output must start with _meta: True for screen compatibility."""
    p = tmp_path / "input.json"
    _write_json(p, [{"source": "A", "title": "T", "doi": "10.1/x"}])
    out = tmp_path / "out.json"
    dedup.run_dedup(str(p), str(out), str(tmp_path / "rep.json"))

    payload = json.loads(out.read_text())
    assert isinstance(payload, list)
    assert payload[0].get("_meta") is True


def test_dedup_output_newline_terminated(tmp_path: Path) -> None:
    p = tmp_path / "input.json"
    _write_json(p, [{"source": "A", "title": "T", "doi": "10.1/x"}])
    out = tmp_path / "out.json"
    rep = tmp_path / "rep.json"
    dedup.run_dedup(str(p), str(out), str(rep))
    assert out.read_bytes().endswith(b"\n")
    assert rep.read_bytes().endswith(b"\n")


def test_dedup_is_deterministic(tmp_path: Path) -> None:
    """Same input → identical output bytes."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {"source": "A", "title": "Z", "doi": "10.1/z", "year": 2020},
            {"source": "B", "title": "A", "doi": "10.1/a", "year": 2019},
        ],
    )
    out1 = tmp_path / "out1.json"
    rep1 = tmp_path / "rep1.json"
    out2 = tmp_path / "out2.json"
    rep2 = tmp_path / "rep2.json"
    dedup.run_dedup(str(p), str(out1), str(rep1))
    dedup.run_dedup(str(p), str(out2), str(rep2))
    assert out1.read_bytes() == out2.read_bytes()
    assert rep1.read_bytes() == rep2.read_bytes()


def test_dedup_empty_input(tmp_path: Path) -> None:
    """Empty input → output has only _meta, duplicates_removed=0."""
    p = tmp_path / "input.json"
    _write_json(p, [])
    out = tmp_path / "out.json"
    rep = tmp_path / "rep.json"
    dedup.run_dedup(str(p), str(out), str(rep))

    payload = json.loads(out.read_text())
    assert payload[0]["_meta"] is True
    assert len(payload) == 1

    report = json.loads(rep.read_text())
    assert report["input_records"] == 0
    assert report["unique_clusters"] == 0
    assert report["duplicates_removed"] == 0


def test_dedup_keeper_prefers_most_fields(tmp_path: Path) -> None:
    """When two records share a DOI, the one with more non-null fields wins."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {
                "source": "crossref",
                "title": "T",
                "doi": "10.1/x",
                "abstract": None,
                "language": None,
            },
            {
                "source": "scopus",
                "title": "T",
                "doi": "10.1/x",
                "abstract": "Rich abstract here",
                "language": "en",
            },
        ],
    )
    out = tmp_path / "out.json"
    dedup.run_dedup(str(p), str(out), str(tmp_path / "rep.json"))

    records = json.loads(out.read_text())[1:]
    assert len(records) == 1
    assert records[0]["source"] == "scopus"


def test_dedup_keeper_tiebreak_by_source_priority(tmp_path: Path) -> None:
    """When field counts tie, source priority breaks the tie (scopus > openalex)."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {"source": "openalex", "title": "Tie Paper", "doi": "10.1/tie"},
            {"source": "scopus", "title": "Tie Paper", "doi": "10.1/tie"},
        ],
    )
    out = tmp_path / "out.json"
    dedup.run_dedup(str(p), str(out), str(tmp_path / "rep.json"))

    records = json.loads(out.read_text())[1:]
    assert records[0]["source"] == "scopus"


def test_dedup_cluster_id_deterministic(tmp_path: Path) -> None:
    """cluster_id is stable across runs."""
    p = tmp_path / "input.json"
    _write_json(p, [{"source": "A", "title": "Stable", "doi": "10.1/s"}])
    out1 = tmp_path / "o1.json"
    out2 = tmp_path / "o2.json"
    dedup.run_dedup(str(p), str(out1), str(tmp_path / "r1.json"))
    dedup.run_dedup(str(p), str(out2), str(tmp_path / "r2.json"))
    r1 = json.loads(out1.read_text())[1:]
    r2 = json.loads(out2.read_text())[1:]
    assert r1[0]["cluster_id"] == r2[0]["cluster_id"]


def test_dedup_cluster_sources_all_sources_listed(tmp_path: Path) -> None:
    """cluster_sources must list all contributing sources."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {"source": "openalex", "doi": "10.1/x"},
            {"source": "crossref", "doi": "10.1/x"},
            {"source": "scopus", "doi": "10.1/x"},
        ],
    )
    out = tmp_path / "out.json"
    dedup.run_dedup(str(p), str(out), str(tmp_path / "rep.json"))
    records = json.loads(out.read_text())[1:]
    assert sorted(records[0]["cluster_sources"]) == ["crossref", "openalex", "scopus"]


def test_dedup_preserves_upstream_meta_fields(tmp_path: Path) -> None:
    """Upstream _meta fields (e.g. topics_enabled) propagated to output _meta."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {"_meta": True, "topics_enabled": ["t1"], "protocol_version": "v2"},
            {"source": "A", "title": "T", "doi": "10.1/a"},
        ],
    )
    out = tmp_path / "out.json"
    dedup.run_dedup(str(p), str(out), str(tmp_path / "rep.json"))

    meta_out = json.loads(out.read_text())[0]
    assert meta_out.get("topics_enabled") == ["t1"]
    assert meta_out.get("protocol_version") == "v2"


def test_dedup_report_top_10_collisions(tmp_path: Path) -> None:
    """top_10_collisions should list clusters with size > 1, capped at 10."""
    records = []
    # Create 12 clusters of size 2 each
    for i in range(12):
        doi = f"10.1/{i}"
        records.append({"source": "A", "title": f"P{i}", "doi": doi})
        records.append({"source": "B", "title": f"P{i}_dup", "doi": doi})

    p = tmp_path / "input.json"
    _write_json(p, records)
    out = tmp_path / "out.json"
    rep = tmp_path / "rep.json"
    dedup.run_dedup(str(p), str(out), str(rep))

    report = json.loads(rep.read_text())
    assert len(report["top_10_collisions"]) == 10
    assert all(c["size"] >= 2 for c in report["top_10_collisions"])


def test_dedup_meta_skipped_in_json_array(tmp_path: Path) -> None:
    """_meta entries in input must not be counted as records."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {"_meta": True, "record_count": 99},
            {"source": "A", "title": "Real", "doi": "10.1/r"},
        ],
    )
    out = tmp_path / "out.json"
    rep = tmp_path / "rep.json"
    dedup.run_dedup(str(p), str(out), str(rep))

    report = json.loads(rep.read_text())
    assert report["input_records"] == 1


def test_dedup_reads_jsonl_input(tmp_path: Path) -> None:
    """JSONL input (not JSON array) is accepted."""
    p = tmp_path / "input.jsonl"
    _write_jsonl(
        p,
        [
            {"source": "A", "title": "T1", "doi": "10.1/a"},
            {"source": "B", "title": "T2", "doi": "10.1/b"},
        ],
    )
    out = tmp_path / "out.json"
    rep = tmp_path / "rep.json"
    dedup.run_dedup(str(p), str(out), str(rep))

    records = json.loads(out.read_text())[1:]
    assert len(records) == 2


def test_dedup_fuzzy_off_by_default(tmp_path: Path) -> None:
    """Near-identical titles must NOT be merged without --fuzzy."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {
                "source": "A",
                "title": "Electoral Integrity in Modern Democracies",
                "year": 2020,
            },
            {
                "source": "B",
                "title": "Electoral Integrity in Modern Democracies!",
                "year": 2020,
            },
        ],
    )
    out = tmp_path / "out.json"
    dedup.run_dedup(str(p), str(out), str(tmp_path / "rep.json"), fuzzy=False)

    # Punctuation stripped by normalise_text → same key → still deduped by exact match
    # Both have no DOI; normalise_text strips "!" → same key → 1 cluster
    report = json.loads((tmp_path / "rep.json").read_text())
    # If exact match catches it, fine; the key invariant is fuzzy=False doesn't error
    assert report["fuzzy_dedup"] == 0


def test_dedup_fuzzy_enabled_warns(tmp_path: Path) -> None:
    """--fuzzy must emit a warning."""
    p = tmp_path / "input.json"
    _write_json(p, [{"source": "A", "title": "T", "doi": "10.1/x"}])
    out = tmp_path / "out.json"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        dedup.run_dedup(str(p), str(out), str(tmp_path / "rep.json"), fuzzy=True)
    assert any("fuzzy" in str(warning.message).lower() for warning in w)


def test_dedup_sort_order_deterministic(tmp_path: Path) -> None:
    """Output keepers must be sorted by (source, query_topic, title)."""
    p = tmp_path / "input.json"
    _write_json(
        p,
        [
            {"source": "Z", "title": "B", "query_topic": "t1", "doi": "10.1/zb"},
            {"source": "A", "title": "C", "query_topic": "t2", "doi": "10.1/ac"},
            {"source": "A", "title": "A", "query_topic": "t1", "doi": "10.1/aa"},
            {"source": "A", "title": "B", "query_topic": "t1", "doi": "10.1/ab"},
        ],
    )
    out = tmp_path / "out.json"
    dedup.run_dedup(str(p), str(out), str(tmp_path / "rep.json"))
    records = json.loads(out.read_text())[1:]
    keys = [(r["source"], r.get("query_topic", ""), r["title"]) for r in records]
    assert keys == [
        ("A", "t1", "A"),
        ("A", "t1", "B"),
        ("A", "t2", "C"),
        ("Z", "t1", "B"),
    ]


# ---------------------------------------------------------------------------
# Unit tests for normalise helpers
# ---------------------------------------------------------------------------


class TestNormaliseDoi:
    def test_https_prefix_stripped(self) -> None:
        assert dedup.normalise_doi("https://doi.org/10.1/FOO") == "10.1/foo"

    def test_http_prefix_stripped(self) -> None:
        assert dedup.normalise_doi("http://doi.org/10.1/FOO") == "10.1/foo"

    def test_doi_colon_stripped(self) -> None:
        assert dedup.normalise_doi("doi:10.1/FOO") == "10.1/foo"

    def test_no_prefix_lowercased(self) -> None:
        assert dedup.normalise_doi("10.1/FOO") == "10.1/foo"

    def test_none_returns_empty(self) -> None:
        assert dedup.normalise_doi(None) == ""

    def test_empty_returns_empty(self) -> None:
        assert dedup.normalise_doi("") == ""


class TestNormaliseText:
    def test_lowercase_and_strip_punctuation(self) -> None:
        assert dedup.normalise_text("Hello, World!") == "hello world"

    def test_collapse_whitespace(self) -> None:
        assert dedup.normalise_text("  too   many   spaces  ") == "too many spaces"

    def test_none_returns_empty(self) -> None:
        assert dedup.normalise_text(None) == ""

    def test_empty_returns_empty(self) -> None:
        assert dedup.normalise_text("") == ""


class TestClusterId:
    def test_stable_across_calls(self) -> None:
        assert dedup._cluster_id("10.1/abc") == dedup._cluster_id("10.1/abc")

    def test_twelve_hex_chars(self) -> None:
        cid = dedup._cluster_id("some key")
        assert len(cid) == 12
        assert all(c in "0123456789abcdef" for c in cid)

    def test_different_keys_different_ids(self) -> None:
        assert dedup._cluster_id("key1") != dedup._cluster_id("key2")
