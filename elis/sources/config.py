"""Harvest configuration resolution for the ELIS adapter layer.

Supports two config modes:
1. NEW: --search-config <yaml> with optional --tier (testing/pilot/benchmark/production/exhaustive)
2. LEGACY: config/elis_search_queries.yml (backwards compatible)

Priority: --search-config + --tier > --search-config (default tier) >
          config/elis_search_queries.yml (legacy). --max-results always overrides.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Tier values (centralised)
# ---------------------------------------------------------------------------

TIERS: dict[str, int] = {
    "testing": 25,
    "pilot": 100,
    "benchmark": 500,
    "production": 1000,
    "exhaustive": 99999,
}


# ---------------------------------------------------------------------------
# HarvestConfig — result of config resolution
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HarvestConfig:
    """Resolved harvest configuration for a single source run."""

    queries: list[str]
    max_results: int
    config_mode: str  # "NEW" or "LEGACY"
    output_path: str


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dict."""
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_source_config() -> dict[str, Any]:
    """Load config/sources.yml from the repo root."""
    candidates = [
        Path("config/sources.yml"),
        Path(__file__).resolve().parents[2] / "config" / "sources.yml",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return load_yaml(candidate)
    return {}


# ---------------------------------------------------------------------------
# Legacy config helpers
# ---------------------------------------------------------------------------

# Source name mapping: adapter source_name -> legacy config key(s)
_LEGACY_SOURCE_NAMES: dict[str, list[str]] = {
    "openalex": ["openalex"],
    "crossref": ["crossref"],
    "scopus": ["scopus"],
    "semanticscholar": ["semantic_scholar", "semanticscholar"],
    "ieee": ["ieee_xplore", "ieee"],
    "core": ["core"],
    "wos": ["web_of_science", "wos"],
    "sciencedirect": ["sciencedirect"],
    "google_scholar": ["google_scholar"],
}


def _get_legacy_queries(config: dict[str, Any], source_name: str) -> list[str]:
    """Extract queries for *source_name* from legacy config topics."""
    known_keys = _LEGACY_SOURCE_NAMES.get(source_name, [source_name])
    queries: list[str] = []
    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue
        sources = [s.lower() for s in topic.get("sources", [])]
        if not any(k in sources for k in known_keys):
            continue
        for q in topic.get("queries", []):
            stripped = q.strip()
            if stripped:
                queries.append(stripped)
    return queries


def _get_legacy_max_results(config: dict[str, Any]) -> int:
    """Return max_results from legacy global config."""
    return int(config.get("global", {}).get("max_results_per_source", 1000))


# ---------------------------------------------------------------------------
# New config helpers
# ---------------------------------------------------------------------------

# Display name mapping: adapter source_name -> search config database name(s)
_NEW_DB_NAMES: dict[str, list[str]] = {
    "openalex": ["OpenAlex", "openalex"],
    "crossref": ["CrossRef", "crossref"],
    "scopus": ["Scopus", "scopus"],
    "semanticscholar": ["Semantic Scholar", "semanticscholar"],
    "ieee": ["IEEE Xplore", "ieee", "IEEE"],
    "core": ["CORE", "core"],
    "wos": ["Web of Science", "wos", "WoS"],
    "sciencedirect": ["ScienceDirect", "sciencedirect"],
    "google_scholar": ["Google Scholar", "google_scholar"],
}


def _find_db_config(config: dict[str, Any], source_name: str) -> dict[str, Any] | None:
    """Find the database block matching *source_name* in a new-format config.

    Returns ``None`` when the database entry is missing **or** when
    ``enabled`` is explicitly set to ``False``.
    """
    known_names = _NEW_DB_NAMES.get(source_name, [source_name])
    for db in config.get("databases", []):
        db_name = db.get("name", "")
        if db_name in known_names or db_name.lower() in known_names:
            if db.get("enabled", True) is False:
                return None
            return db
    return None


def _get_new_queries(config: dict[str, Any], source_name: str) -> list[str]:
    """Extract queries from a new-format search config for *source_name*.

    Uses the simplified alternative query for sources with limited boolean
    support, otherwise the primary boolean_string.
    """
    db_config = _find_db_config(config, source_name)
    if db_config is None:
        return []

    query_section = config.get("query", {})

    # Check for simplified alternative query for this source
    if source_name in ("openalex", "crossref", "google_scholar"):
        for alt in query_section.get("alternative_queries", []):
            if isinstance(alt, dict) and "simplified" in alt:
                simplified = alt["simplified"].strip()
                if simplified:
                    return [simplified]

    # Use primary boolean string
    boolean_string = query_section.get("boolean_string", "").strip()
    if boolean_string:
        # OpenAlex default.search doesn't support quoted phrases — strip quotes
        # when falling back to the boolean string so behaviour matches legacy.
        if source_name in ("openalex",):
            boolean_string = boolean_string.replace('"', "")
        return [boolean_string]

    return []


def _resolve_new_max_results(
    config: dict[str, Any], source_name: str, tier: str | None
) -> int:
    """Resolve max_results from a new-format config for *source_name*."""
    db_config = _find_db_config(config, source_name)
    if db_config is None:
        return 1000

    max_results_config = db_config.get("max_results")

    if isinstance(max_results_config, dict):
        effective_tier = tier or db_config.get("max_results_default", "testing")
        result = max_results_config.get(effective_tier)
        if result is not None:
            return int(result)
        # Fallback to default tier
        default_tier = db_config.get("max_results_default", "testing")
        result = max_results_config.get(default_tier)
        if result is not None:
            return int(result)
        return 1000

    if max_results_config is not None:
        return int(max_results_config)

    return 1000


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

DEFAULT_OUTPUT = os.path.join("json_jsonl", "ELIS_Appendix_A_Search_rows.json")


def load_harvest_config(
    source_name: str,
    search_config: str | None = None,
    tier: str | None = None,
    max_results_override: int | None = None,
    output: str | None = None,
) -> HarvestConfig:
    """Resolve harvest configuration for *source_name*.

    Priority:
      --search-config + --tier  >  --search-config (default tier)  >
      config/elis_search_queries.yml (legacy).
      --max-results always overrides.
    """
    output_path = output or DEFAULT_OUTPUT

    if search_config:
        config = load_yaml(search_config)
        queries = _get_new_queries(config, source_name)
        max_results = _resolve_new_max_results(config, source_name, tier)
        config_mode = "NEW"
    else:
        legacy_path = Path("config/elis_search_queries.yml")
        if not legacy_path.is_file():
            # Try relative to package root
            legacy_path = (
                Path(__file__).resolve().parents[2]
                / "config"
                / "elis_search_queries.yml"
            )
        config = load_yaml(legacy_path) if legacy_path.is_file() else {}
        queries = _get_legacy_queries(config, source_name)
        max_results = _get_legacy_max_results(config)
        config_mode = "LEGACY"

    if max_results_override is not None:
        max_results = max_results_override

    return HarvestConfig(
        queries=queries,
        max_results=max_results,
        config_mode=config_mode,
        output_path=output_path,
    )
