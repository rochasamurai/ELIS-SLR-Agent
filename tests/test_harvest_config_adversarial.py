"""Adversarial tests for harvest config behavior parity."""

from __future__ import annotations

from elis.sources.config import _get_new_queries


def test_openalex_boolean_fallback_strips_quotes_when_no_simplified_query() -> None:
    """OpenAlex fallback query should remove quotes to match legacy behavior."""
    config = {
        "query": {
            "boolean_string": '"electoral integrity" AND election',
            "alternative_queries": [],
        },
        "databases": [{"name": "OpenAlex", "enabled": True}],
    }

    queries = _get_new_queries(config, "openalex")
    assert queries == ["electoral integrity AND election"]


def test_disabled_openalex_database_yields_no_queries() -> None:
    """Disabled DB entries should not produce runnable queries."""
    config = {
        "query": {"boolean_string": "electoral integrity", "alternative_queries": []},
        "databases": [{"name": "OpenAlex", "enabled": False}],
    }

    queries = _get_new_queries(config, "openalex")
    assert queries == []
