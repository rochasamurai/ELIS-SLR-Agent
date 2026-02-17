"""Tests for elis.pipeline.screen — screening logic and CLI."""

from __future__ import annotations

import json
import os

import pytest

from elis.pipeline.screen import (
    build_summary,
    is_preprint,
    lang_allowed,
    main,
    screen_records,
    within_years,
)


# ── Helpers ──────────────────────────────────────────────────────────────────


class TestIsPreprint:
    def test_arxiv_source(self):
        assert is_preprint({"source": "arxiv"}) is True

    def test_arxiv_venue(self):
        assert is_preprint({"venue": "arXiv"}) is True

    def test_preprint_doc_type(self):
        assert is_preprint({"doc_type": "preprint"}) is True

    def test_journal_article(self):
        assert is_preprint({"source": "crossref", "venue": "Nature"}) is False

    def test_empty(self):
        assert is_preprint({}) is False


class TestLangAllowed:
    def test_allowed(self):
        assert lang_allowed("en", ["en", "fr"], False) is True

    def test_blocked(self):
        assert lang_allowed("de", ["en", "fr"], False) is False

    def test_unknown_blocked(self):
        assert lang_allowed(None, ["en"], False) is False

    def test_unknown_allowed(self):
        assert lang_allowed(None, ["en"], True) is True


class TestWithinYears:
    def test_in_range(self):
        assert within_years(2020, 1990, 2025) is True

    def test_out(self):
        assert within_years(1980, 1990, 2025) is False

    def test_none(self):
        assert within_years(None, 1990, 2025) is False


# ── Screening core ───────────────────────────────────────────────────────────


class TestScreenRecords:
    @pytest.fixture()
    def sample_records(self):
        return [
            {
                "id": "r1",
                "year": 2020,
                "language": "en",
                "source": "crossref",
                "query_topic": "t1",
            },
            {
                "id": "r2",
                "year": 1980,
                "language": "en",
                "source": "crossref",
                "query_topic": "t1",
            },
            {
                "id": "r3",
                "year": 2020,
                "language": None,
                "source": "arxiv",
                "query_topic": "t1",
            },
            {
                "id": "r4",
                "year": 2020,
                "language": "de",
                "source": "crossref",
                "query_topic": "t1",
            },
        ]

    def test_basic_screening(self, sample_records):
        included, excluded = screen_records(
            sample_records,
            year_from=1990,
            year_to=2025,
            languages=["en"],
            allow_unknown_language=False,
            enforce_preprint_policy=False,
            include_preprints_by_topic={},
        )
        # r1 included; r2 out_of_year; r3 language_unknown; r4 language_blocked
        assert len(included) == 1
        assert included[0]["id"] == "r1"
        assert excluded["out_of_year"] == 1
        assert excluded["language_unknown"] == 1
        assert excluded["language_blocked"] == 1

    def test_allow_unknown_language(self, sample_records):
        included, excluded = screen_records(
            sample_records,
            year_from=1990,
            year_to=2025,
            languages=["en"],
            allow_unknown_language=True,
            enforce_preprint_policy=False,
            include_preprints_by_topic={},
        )
        ids = {r["id"] for r in included}
        assert "r1" in ids
        assert "r3" in ids  # unknown language now allowed

    def test_preprint_policy(self, sample_records):
        included, excluded = screen_records(
            sample_records,
            year_from=1990,
            year_to=2025,
            languages=["en", "de"],
            allow_unknown_language=True,
            enforce_preprint_policy=True,
            include_preprints_by_topic={"t1": False},
        )
        ids = {r["id"] for r in included}
        # r3 is arxiv (preprint) and t1 forbids preprints
        assert "r3" not in ids
        assert excluded.get("preprint_blocked", 0) >= 1


class TestBuildSummary:
    def test_counts(self):
        records = [
            {"source": "crossref", "query_topic": "t1"},
            {"source": "arxiv", "query_topic": "t2"},
        ]
        s = build_summary(records)
        assert s["total"] == 2
        assert s["per_source"]["crossref"] == 1
        assert s["per_topic"]["t2"] == 1


# ── CLI (main) ───────────────────────────────────────────────────────────────


class TestScreenMain:
    @pytest.fixture()
    def appendix_a_file(self, tmp_path):
        """Write a minimal valid Appendix A file and return its path."""
        data = [
            {
                "_meta": True,
                "protocol_version": "ELIS 2025 (MVP)",
                "global": {
                    "year_from": 2020,
                    "year_to": 2024,
                    "languages": ["en"],
                },
                "topics_enabled": ["t1"],
                "run_inputs": {"include_preprints_by_topic": {"t1": True}},
            },
            {
                "id": "doi:10.1/a",
                "title": "Paper A",
                "year": 2022,
                "language": "en",
                "source": "crossref",
                "query_topic": "t1",
                "query_string": "test",
                "retrieved_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "doi:10.1/b",
                "title": "Paper B",
                "year": 1980,
                "language": "en",
                "source": "crossref",
                "query_topic": "t1",
                "query_string": "test",
                "retrieved_at": "2024-01-01T00:00:00Z",
            },
        ]
        fp = tmp_path / "appendix_a.json"
        fp.write_text(json.dumps(data), encoding="utf-8")
        return str(fp)

    def test_dry_run(self, appendix_a_file, tmp_path):
        out = str(tmp_path / "appendix_b.json")
        rc = main(["--input", appendix_a_file, "--output", out, "--dry-run"])
        assert rc == 0
        assert not os.path.exists(out)  # dry-run should not write

    def test_write_output(self, appendix_a_file, tmp_path):
        out = str(tmp_path / "appendix_b.json")
        rc = main(["--input", appendix_a_file, "--output", out])
        assert rc == 0
        assert os.path.isfile(out)

        data = json.loads(open(out, encoding="utf-8").read())
        assert isinstance(data, list)
        assert data[0].get("_meta") is True
        # Only Paper A passes (Paper B year 1980 < 2020)
        records = [r for r in data if not r.get("_meta")]
        assert len(records) == 1
        assert records[0]["id"] == "doi:10.1/a"
