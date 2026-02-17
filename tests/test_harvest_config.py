"""Tests for harvest config resolution (elis.sources.config)."""

from __future__ import annotations

import textwrap

import pytest
import yaml

from elis.sources.config import (
    HarvestConfig,
    _get_legacy_max_results,
    _get_legacy_queries,
    _get_new_queries,
    _resolve_new_max_results,
    load_harvest_config,
)


# ---------------------------------------------------------------------------
# Fixtures — minimal config snippets
# ---------------------------------------------------------------------------

LEGACY_CONFIG = yaml.safe_load(
    textwrap.dedent(
        """\
    global:
      max_results_per_source: 500
    topics:
      - name: "Topic A"
        enabled: true
        sources: ["openalex", "crossref"]
        queries:
          - "electoral integrity"
          - "voting security"
      - name: "Topic B"
        enabled: false
        sources: ["openalex"]
        queries:
          - "disabled topic"
      - name: "Topic C"
        enabled: true
        sources: ["scopus"]
        queries:
          - "scopus only query"
    """
    )
)

NEW_CONFIG = yaml.safe_load(
    textwrap.dedent(
        """\
    query:
      boolean_string: '("electoral system" AND "integrity")'
      alternative_queries:
        - simplified: "electoral integrity strategies"
    databases:
      - name: "OpenAlex"
        enabled: true
        max_results:
          testing: 25
          pilot: 100
          production: 1000
        max_results_default: testing
      - name: "Scopus"
        enabled: true
        max_results:
          testing: 25
          pilot: 100
          production: 1000
        max_results_default: production
    """
    )
)


# ---------------------------------------------------------------------------
# Legacy config
# ---------------------------------------------------------------------------


class TestLegacyConfig:
    def test_extracts_enabled_queries(self) -> None:
        queries = _get_legacy_queries(LEGACY_CONFIG, "openalex")
        assert len(queries) == 2
        assert "electoral integrity" in queries

    def test_skips_disabled_topics(self) -> None:
        queries = _get_legacy_queries(LEGACY_CONFIG, "openalex")
        assert "disabled topic" not in queries

    def test_skips_other_sources(self) -> None:
        queries = _get_legacy_queries(LEGACY_CONFIG, "openalex")
        assert "scopus only query" not in queries

    def test_no_queries_for_missing_source(self) -> None:
        queries = _get_legacy_queries(LEGACY_CONFIG, "nonexistent")
        assert queries == []

    def test_max_results_from_global(self) -> None:
        assert _get_legacy_max_results(LEGACY_CONFIG) == 500

    def test_max_results_default(self) -> None:
        assert _get_legacy_max_results({}) == 1000


# ---------------------------------------------------------------------------
# New config
# ---------------------------------------------------------------------------


class TestNewConfig:
    def test_simplified_query_for_openalex(self) -> None:
        """OpenAlex should use the simplified alternative query."""
        queries = _get_new_queries(NEW_CONFIG, "openalex")
        assert queries == ["electoral integrity strategies"]

    def test_boolean_query_for_scopus(self) -> None:
        """Scopus should use the primary boolean string."""
        queries = _get_new_queries(NEW_CONFIG, "scopus")
        assert len(queries) == 1
        assert "electoral system" in queries[0]

    def test_no_queries_for_missing_db(self) -> None:
        queries = _get_new_queries(NEW_CONFIG, "nonexistent")
        assert queries == []

    def test_resolve_max_results_with_tier(self) -> None:
        assert _resolve_new_max_results(NEW_CONFIG, "openalex", "pilot") == 100

    def test_resolve_max_results_default_tier(self) -> None:
        """Without explicit tier, use max_results_default from db config."""
        assert _resolve_new_max_results(NEW_CONFIG, "openalex", None) == 25

    def test_resolve_max_results_unknown_tier_falls_back(self) -> None:
        """Unknown tier should fall back to default tier."""
        result = _resolve_new_max_results(NEW_CONFIG, "openalex", "nonexistent")
        assert result == 25  # Falls back to max_results_default=testing=25


# ---------------------------------------------------------------------------
# load_harvest_config integration
# ---------------------------------------------------------------------------


class TestLoadHarvestConfig:
    def test_new_config_mode(self, tmp_path) -> None:
        config_path = tmp_path / "search.yml"
        config_path.write_text(yaml.dump(NEW_CONFIG), encoding="utf-8")

        cfg = load_harvest_config(
            "openalex",
            search_config=str(config_path),
            tier="pilot",
        )
        assert isinstance(cfg, HarvestConfig)
        assert cfg.config_mode == "NEW"
        assert cfg.max_results == 100
        assert cfg.queries == ["electoral integrity strategies"]

    def test_max_results_override(self, tmp_path) -> None:
        config_path = tmp_path / "search.yml"
        config_path.write_text(yaml.dump(NEW_CONFIG), encoding="utf-8")

        cfg = load_harvest_config(
            "openalex",
            search_config=str(config_path),
            tier="pilot",
            max_results_override=42,
        )
        assert cfg.max_results == 42

    def test_output_override(self, tmp_path) -> None:
        config_path = tmp_path / "search.yml"
        config_path.write_text(yaml.dump(NEW_CONFIG), encoding="utf-8")

        cfg = load_harvest_config(
            "openalex",
            search_config=str(config_path),
            output="/tmp/custom.json",
        )
        assert cfg.output_path == "/tmp/custom.json"

    def test_legacy_mode_with_real_config(self) -> None:
        """If the legacy config file exists, load_harvest_config should work."""
        from pathlib import Path

        legacy = Path("config/elis_search_queries.yml")
        if not legacy.is_file():
            pytest.skip("Legacy config not found (expected in repo root)")

        cfg = load_harvest_config("openalex")
        assert cfg.config_mode == "LEGACY"
        assert cfg.max_results > 0
        assert len(cfg.queries) > 0
