"""Tests for elis.pipeline.merge - PE3 canonical merge stage."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from elis.pipeline import merge
from elis.pipeline.screen import main as screen_main


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_merge_normalises_records_and_writes_report(tmp_path: Path) -> None:
    in_a = tmp_path / "openalex.json"
    in_b = tmp_path / "crossref.jsonl"
    out = tmp_path / "appendix_a.json"
    report = tmp_path / "merge_report.json"

    _write_json(
        in_a,
        [
            {
                "source": "OpenAlex",
                "title": "  A   Study   ",
                "authors": ["  Alice  ", " Bob "],
                "year": "2024",
                "doi": "https://doi.org/10.1000/ABC",
                "query_topic": "topic-z",
                "query_string": '"alpha"',
            }
        ],
    )
    _write_jsonl(
        in_b,
        [
            {
                "source": "CrossRef",
                "title": "B study",
                "authors": [" Carol "],
                "year": 2023,
                "doi": "DOI:10.1000/XYZ",
                "query_topic": "topic-a",
                "query_string": '"beta"',
            }
        ],
    )

    merge.run_merge([str(in_a), str(in_b)], str(out), str(report))

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload[0]["_meta"] is True
    rows = payload[1:]
    assert len(rows) == 2

    first = rows[0]
    assert first["source"] == "crossref"
    assert first["title"] == "B study"
    assert first["doi"] == "10.1000/xyz"
    assert first["authors"] == ["Carol"]
    assert first["year"] == 2023
    assert first["id"].startswith(("doi:", "t:"))
    assert first["source_file"] == "crossref.jsonl"

    second = rows[1]
    assert second["source"] == "openalex"
    assert second["title"] == "A Study"
    assert second["doi"] == "10.1000/abc"
    assert second["authors"] == ["Alice", "Bob"]
    assert second["year"] == 2024

    rep = json.loads(report.read_text(encoding="utf-8"))
    assert rep["total_records"] == 2
    assert rep["per_source_counts"] == {"crossref": 1, "openalex": 1}
    assert rep["doi_coverage_pct"] == 100.0
    assert rep["input_files"] == [str(in_a), str(in_b)]


def test_merge_is_deterministic_for_same_inputs(tmp_path: Path) -> None:
    input_file = tmp_path / "input.json"
    _write_json(
        input_file,
        [
            {
                "source": "OpenAlex",
                "title": "Zeta",
                "authors": ["A"],
                "year": 2025,
                "doi": "https://doi.org/10.1/zeta",
            },
            {
                "source": "CrossRef",
                "title": "Alpha",
                "authors": ["B"],
                "year": 2020,
                "doi": "",
            },
        ],
    )

    out1 = tmp_path / "out1.json"
    rep1 = tmp_path / "rep1.json"
    out2 = tmp_path / "out2.json"
    rep2 = tmp_path / "rep2.json"

    merge.run_merge([str(input_file)], str(out1), str(rep1))
    merge.run_merge([str(input_file)], str(out2), str(rep2))

    assert out1.read_bytes() == out2.read_bytes()
    assert rep1.read_bytes() == rep2.read_bytes()


def test_merge_output_validates_and_is_screen_compatible(tmp_path: Path) -> None:
    input_file = tmp_path / "input.json"
    _write_json(
        input_file,
        [
            {
                "source": "CrossRef",
                "title": "Screenable Paper",
                "authors": ["Eve"],
                "year": 2021,
                "doi": "10.1/screen",
                "query_topic": "t1",
                "query_string": "test query",
                "language": "en",
            }
        ],
    )

    out = tmp_path / "appendix_a.json"
    report = tmp_path / "merge_report.json"
    merge.run_merge([str(input_file)], str(out), str(report))

    schema = json.loads(
        Path("schemas/appendix_a.schema.json").read_text(encoding="utf-8")
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(data))
    assert errors == []

    appendix_b = tmp_path / "appendix_b.json"
    rc = screen_main(["--input", str(out), "--output", str(appendix_b)])
    assert rc == 0
    assert appendix_b.exists()


# ---------------------------------------------------------------------------
# Adversarial tests — PE3 validator (Claude Code)
# ---------------------------------------------------------------------------


class TestNormaliseDoi:
    def test_https_prefix_stripped(self) -> None:
        assert merge.normalise_doi("https://doi.org/10.1/FOO") == "10.1/foo"

    def test_http_prefix_stripped(self) -> None:
        assert merge.normalise_doi("http://doi.org/10.1/FOO") == "10.1/foo"

    def test_doi_colon_prefix_stripped(self) -> None:
        assert merge.normalise_doi("doi:10.1/FOO") == "10.1/foo"

    def test_no_prefix_lowercased(self) -> None:
        assert merge.normalise_doi("10.1/FOO") == "10.1/foo"

    def test_empty_string_returns_empty(self) -> None:
        assert merge.normalise_doi("") == ""

    def test_none_returns_empty(self) -> None:
        assert merge.normalise_doi(None) == ""

    def test_only_prefix_no_suffix(self) -> None:
        assert merge.normalise_doi("https://doi.org/") == ""

    def test_all_four_variants_normalise_to_same_value(self) -> None:
        variants = [
            "https://doi.org/10.1/abc",
            "http://doi.org/10.1/abc",
            "doi:10.1/abc",
            "10.1/abc",
        ]
        results = {merge.normalise_doi(v) for v in variants}
        assert results == {"10.1/abc"}


class TestNormaliseYear:
    def test_int_passthrough(self) -> None:
        assert merge.normalise_year(2024) == 2024

    def test_string_parsed(self) -> None:
        assert merge.normalise_year("2021") == 2021

    def test_none_returns_none(self) -> None:
        assert merge.normalise_year(None) is None

    def test_empty_string_returns_none(self) -> None:
        assert merge.normalise_year("") is None

    def test_non_numeric_string_returns_none(self) -> None:
        assert merge.normalise_year("bad") is None

    def test_float_truncated(self) -> None:
        assert merge.normalise_year(2024.9) == 2024


class TestMergeAdversarial:
    def test_meta_entry_skipped_in_json_array(self, tmp_path: Path) -> None:
        """_meta header in a JSON array input must not appear in output records."""
        p = tmp_path / "input.json"
        p.write_text(
            json.dumps(
                [{"_meta": True, "record_count": 1}, {"source": "A", "title": "Real"}]
            ),
            encoding="utf-8",
        )
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        rows = json.loads(out.read_text())[1:]
        assert len(rows) == 1
        assert rows[0]["title"] == "Real"

    def test_meta_line_skipped_in_jsonl(self, tmp_path: Path) -> None:
        """_meta line in JSONL input must be skipped."""
        p = tmp_path / "input.jsonl"
        p.write_text(
            json.dumps({"_meta": True})
            + "\n"
            + json.dumps({"source": "B", "title": "JSONL"})
            + "\n",
            encoding="utf-8",
        )
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        rows = json.loads(out.read_text())[1:]
        assert len(rows) == 1

    def test_empty_json_array_produces_zero_records(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.json"
        p.write_text("[]", encoding="utf-8")
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        payload = json.loads(out.read_text())
        assert payload[0]["_meta"] is True
        assert len(payload) == 1  # only _meta header
        report = json.loads(rep.read_text())
        assert report["total_records"] == 0

    def test_sort_order_by_source_topic_title(self, tmp_path: Path) -> None:
        """Records must be sorted (source, query_topic, title, year)."""
        p = tmp_path / "input.json"
        p.write_text(
            json.dumps(
                [
                    {"source": "Z", "title": "B", "year": 2020, "query_topic": "t1"},
                    {"source": "A", "title": "C", "year": 2020, "query_topic": "t2"},
                    {"source": "A", "title": "A", "year": 2020, "query_topic": "t1"},
                    {"source": "A", "title": "B", "year": 2020, "query_topic": "t1"},
                ]
            ),
            encoding="utf-8",
        )
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        rows = json.loads(out.read_text())[1:]
        keys = [(r["source"], r["query_topic"], r["title"]) for r in rows]
        assert keys == [
            ("a", "t1", "A"),
            ("a", "t1", "B"),
            ("a", "t2", "C"),
            ("z", "t1", "B"),
        ]

    def test_stable_id_uses_doi_prefix_when_present(self, tmp_path: Path) -> None:
        p = tmp_path / "input.json"
        p.write_text(
            json.dumps([{"source": "A", "title": "T", "doi": "10.1/abc"}]),
            encoding="utf-8",
        )
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        rows = json.loads(out.read_text())[1:]
        assert rows[0]["id"].startswith("doi:")
        assert rows[0]["_stable_id"].startswith("doi:")

    def test_stable_id_uses_hash_prefix_when_no_doi(self, tmp_path: Path) -> None:
        p = tmp_path / "input.json"
        p.write_text(
            json.dumps([{"source": "A", "title": "No DOI paper", "doi": None}]),
            encoding="utf-8",
        )
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        rows = json.loads(out.read_text())[1:]
        assert rows[0]["id"].startswith("t:")

    def test_merge_position_monotonically_increases_across_files(
        self, tmp_path: Path
    ) -> None:
        pa = tmp_path / "a.json"
        pb = tmp_path / "b.json"
        pa.write_text(
            json.dumps(
                [{"source": "S", "title": "R1"}, {"source": "S", "title": "R2"}]
            ),
            encoding="utf-8",
        )
        pb.write_text(json.dumps([{"source": "S", "title": "R3"}]), encoding="utf-8")
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(pa), str(pb)], str(out), str(rep))
        rows = json.loads(out.read_text())[1:]
        positions = sorted(r["merge_position"] for r in rows)
        assert positions == [1, 2, 3]
        assert len(set(positions)) == 3  # all unique

    def test_authors_whitespace_normalised_and_blank_dropped(
        self, tmp_path: Path
    ) -> None:
        p = tmp_path / "input.json"
        p.write_text(
            json.dumps(
                [
                    {
                        "source": "A",
                        "title": "T",
                        "authors": ["  Alice   Bob  ", "  ", " Carol "],
                    }
                ]
            ),
            encoding="utf-8",
        )
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        rows = json.loads(out.read_text())[1:]
        assert rows[0]["authors"] == ["Alice Bob", "Carol"]

    def test_source_file_provenance_set_to_filename(self, tmp_path: Path) -> None:
        p = tmp_path / "scopus_2024.json"
        p.write_text(json.dumps([{"source": "Scopus", "title": "T"}]), encoding="utf-8")
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        rows = json.loads(out.read_text())[1:]
        assert rows[0]["source_file"] == "scopus_2024.json"

    def test_year_variants_cast_correctly(self, tmp_path: Path) -> None:
        p = tmp_path / "input.json"
        p.write_text(
            json.dumps(
                [
                    {"source": "A", "title": "Y1", "year": "2024"},
                    {"source": "A", "title": "Y2", "year": 2023},
                    {"source": "A", "title": "Y3", "year": None},
                    {"source": "A", "title": "Y4", "year": "bad"},
                    {"source": "A", "title": "Y5", "year": ""},
                ]
            ),
            encoding="utf-8",
        )
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        rows = json.loads(out.read_text())[1:]
        by_title = {r["title"]: r["year"] for r in rows}
        assert by_title["Y1"] == 2024
        assert by_title["Y2"] == 2023
        assert by_title["Y3"] is None
        assert by_title["Y4"] is None
        assert by_title["Y5"] is None

    def test_doi_coverage_pct_computed_correctly(self, tmp_path: Path) -> None:
        p = tmp_path / "input.json"
        p.write_text(
            json.dumps(
                [
                    {"source": "A", "title": "T1", "doi": "10.1/a"},
                    {"source": "A", "title": "T2", "doi": None},
                    {"source": "A", "title": "T3", "doi": "10.1/c"},
                    {"source": "A", "title": "T4", "doi": None},
                ]
            ),
            encoding="utf-8",
        )
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        report = json.loads(rep.read_text())
        assert report["doi_coverage_pct"] == 50.0

    def test_output_newline_terminated(self, tmp_path: Path) -> None:
        """Output files must end with a newline (determinism requirement)."""
        p = tmp_path / "input.json"
        p.write_text(json.dumps([{"source": "A", "title": "T"}]), encoding="utf-8")
        out = tmp_path / "out.json"
        rep = tmp_path / "rep.json"
        merge.run_merge([str(p)], str(out), str(rep))
        assert out.read_bytes().endswith(b"\n")
        assert rep.read_bytes().endswith(b"\n")
