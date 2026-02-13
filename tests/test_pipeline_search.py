"""Tests for elis.pipeline.search — helpers and CLI."""

from __future__ import annotations

import yaml

from elis.pipeline.search import (
    build_run_inputs,
    build_summary,
    lang_ok,
    main,
    normalize_title,
    stable_id,
    within_years,
)


# ── Helpers ──────────────────────────────────────────────────────────────────


class TestNormalizeTitle:
    def test_basic(self):
        assert normalize_title("Hello, World!") == "hello world"

    def test_extra_spaces(self):
        assert normalize_title("  lots   of   spaces  ") == "lots of spaces"

    def test_none(self):
        assert normalize_title(None) == ""

    def test_empty(self):
        assert normalize_title("") == ""


class TestStableId:
    def test_doi_preferred(self):
        assert stable_id("10.1234/abc", "Title", 2024) == "doi:10.1234/abc"

    def test_doi_normalised(self):
        assert stable_id("10.1234/ABC ", None, None) == "doi:10.1234/abc"

    def test_hash_fallback(self):
        sid = stable_id(None, "Some Title", 2024)
        assert sid.startswith("t:")
        assert len(sid) == 2 + 20  # "t:" + 20 hex chars

    def test_deterministic(self):
        a = stable_id(None, "Same Title", 2024)
        b = stable_id(None, "Same Title", 2024)
        assert a == b

    def test_different_years_differ(self):
        a = stable_id(None, "Same Title", 2023)
        b = stable_id(None, "Same Title", 2024)
        assert a != b


class TestWithinYears:
    def test_in_range(self):
        assert within_years(2020, 1990, 2025) is True

    def test_boundary_low(self):
        assert within_years(1990, 1990, 2025) is True

    def test_boundary_high(self):
        assert within_years(2025, 1990, 2025) is True

    def test_out_of_range(self):
        assert within_years(1989, 1990, 2025) is False

    def test_none(self):
        assert within_years(None, 1990, 2025) is False

    def test_string(self):
        assert within_years("2020", 1990, 2025) is False  # type: ignore[arg-type]


class TestLangOk:
    def test_allowed(self):
        assert lang_ok("en", ["en", "fr"]) is True

    def test_not_allowed(self):
        assert lang_ok("de", ["en", "fr"]) is False

    def test_none_language_passes(self):
        assert lang_ok(None, ["en"]) is True

    def test_empty_allowed_passes_all(self):
        assert lang_ok("de", []) is True

    def test_case_insensitive(self):
        assert lang_ok("EN", ["en"]) is True


class TestBuildSummary:
    def test_counts(self):
        records = [
            {"source": "crossref", "query_topic": "t1"},
            {"source": "crossref", "query_topic": "t1"},
            {"source": "arxiv", "query_topic": "t2"},
        ]
        summary = build_summary(records)
        assert summary["total"] == 3
        assert summary["per_source"]["crossref"] == 2
        assert summary["per_source"]["arxiv"] == 1
        assert summary["per_topic"]["t1"] == 2
        assert summary["per_topic"]["t2"] == 1

    def test_empty(self):
        summary = build_summary([])
        assert summary["total"] == 0
        assert summary["per_source"] == {}
        assert summary["per_topic"] == {}


class TestBuildRunInputs:
    def test_defaults(self):
        config = {
            "global": {
                "year_from": 1990,
                "year_to": 2025,
                "max_results_per_source": 50,
            },
            "topics": [
                {"id": "t1", "enabled": True, "include_preprints": False},
                {"id": "t2", "enabled": False},
            ],
        }
        ri = build_run_inputs(config)
        assert ri["year_from"] == 1990
        assert ri["year_to"] == 2025
        assert ri["topics_selected"] == ["t1"]
        assert ri["include_preprints_by_topic"]["t1"] is False


# ── CLI (main) ───────────────────────────────────────────────────────────────


class TestSearchMain:
    def test_missing_config(self, tmp_path):
        rc = main(["--config", str(tmp_path / "nonexistent.yml")])
        assert rc == 2

    def test_dry_run_with_minimal_config(self, tmp_path):
        """Dry-run with a config whose sources will be unreachable (no network)."""
        config = {
            "global": {
                "year_from": 2024,
                "year_to": 2024,
                "languages": ["en"],
                "max_results_per_source": 1,
                "job_result_cap": 1,
            },
            "topics": [
                {
                    "id": "test_topic",
                    "enabled": True,
                    "queries": ["test"],
                    "sources": [],
                }
            ],
        }
        cfg = tmp_path / "test_config.yml"
        cfg.write_text(yaml.dump(config), encoding="utf-8")
        rc = main(["--config", str(cfg), "--dry-run"])
        assert rc == 0
