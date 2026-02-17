"""Tests for the OpenAlex source adapter."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import jsonschema
import pytest

from elis.sources.openalex import (
    OpenAlexAdapter,
    _reconstruct_abstract,
    transform_entry,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_OPENALEX_ENTRY = {
    "id": "https://openalex.org/W12345",
    "doi": "https://doi.org/10.1234/test.001",
    "title": "Electoral Integrity Strategies",
    "publication_year": 2023,
    "authorships": [
        {"author": {"display_name": "Alice Smith", "id": "A1"}},
        {"author": {"display_name": "Bob Jones", "id": "A2"}},
    ],
    "abstract_inverted_index": {
        "Electoral": [0],
        "integrity": [1],
        "is": [2],
        "important": [3],
        "for": [4],
        "democracy": [5],
    },
    "cited_by_count": 42,
}


def _load_harvester_schema() -> dict:
    schema_path = Path("schemas/appendix_a_harvester.schema.json")
    if not schema_path.exists():
        pytest.skip("Harvester schema not found")
    return json.loads(schema_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Abstract reconstruction
# ---------------------------------------------------------------------------


class TestReconstructAbstract:
    def test_empty_index(self) -> None:
        assert _reconstruct_abstract({}) == ""

    def test_single_word(self) -> None:
        assert _reconstruct_abstract({"hello": [0]}) == "hello"

    def test_multi_word_ordered(self) -> None:
        result = _reconstruct_abstract({"a": [0], "b": [1], "c": [2]})
        assert result == "a b c"

    def test_word_at_multiple_positions(self) -> None:
        result = _reconstruct_abstract({"the": [0, 2], "cat": [1]})
        assert result == "the cat the"


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------


class TestTransformEntry:
    def test_basic_fields(self) -> None:
        record = transform_entry(SAMPLE_OPENALEX_ENTRY)
        assert record["source"] == "OpenAlex"
        assert record["title"] == "Electoral Integrity Strategies"
        assert record["year"] == 2023
        assert record["doi"] == "10.1234/test.001"
        assert record["authors"] == ["Alice Smith", "Bob Jones"]
        assert record["citation_count"] == 42
        assert record["openalex_id"] == "https://openalex.org/W12345"

    def test_doi_prefix_stripped(self) -> None:
        record = transform_entry(SAMPLE_OPENALEX_ENTRY)
        assert not record["doi"].startswith("https://doi.org/")

    def test_abstract_reconstructed(self) -> None:
        record = transform_entry(SAMPLE_OPENALEX_ENTRY)
        assert record["abstract"] == "Electoral integrity is important for democracy"

    def test_missing_fields_handled(self) -> None:
        minimal = {"id": "W1"}
        record = transform_entry(minimal)
        assert record["source"] == "OpenAlex"
        assert record["title"] == ""
        assert record["authors"] == []
        assert record["year"] is None
        assert record["doi"] == ""
        assert record["abstract"] == ""
        assert record["citation_count"] == 0

    def test_none_year_stays_none(self) -> None:
        entry = {**SAMPLE_OPENALEX_ENTRY, "publication_year": None}
        record = transform_entry(entry)
        assert record["year"] is None

    def test_invalid_year_becomes_none(self) -> None:
        entry = {**SAMPLE_OPENALEX_ENTRY, "publication_year": "not_a_year"}
        record = transform_entry(entry)
        assert record["year"] is None

    def test_none_citation_count_becomes_zero(self) -> None:
        entry = {**SAMPLE_OPENALEX_ENTRY, "cited_by_count": None}
        record = transform_entry(entry)
        assert record["citation_count"] == 0

    def test_schema_compliance(self) -> None:
        """Transformed record must pass appendix_a_harvester.schema.json."""
        schema = _load_harvester_schema()
        record = transform_entry(SAMPLE_OPENALEX_ENTRY)
        jsonschema.validate([record], schema)

    def test_raw_metadata_preserved(self) -> None:
        record = transform_entry(SAMPLE_OPENALEX_ENTRY)
        assert record["raw_metadata"] is SAMPLE_OPENALEX_ENTRY


# ---------------------------------------------------------------------------
# Adapter properties
# ---------------------------------------------------------------------------


class TestOpenAlexAdapterProperties:
    def test_source_name(self) -> None:
        adapter = OpenAlexAdapter()
        assert adapter.source_name == "openalex"

    def test_display_name(self) -> None:
        adapter = OpenAlexAdapter()
        assert adapter.display_name == "OpenAlex"


# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------


class TestOpenAlexPreflight:
    def test_preflight_success(self) -> None:
        adapter = OpenAlexAdapter()
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        with patch("elis.sources.openalex.ELISHttpClient") as MockClient:
            MockClient.return_value.get.return_value = mock_resp
            ok, msg = adapter.preflight()

        assert ok is True
        assert msg == "ok"

    def test_preflight_failure(self) -> None:
        adapter = OpenAlexAdapter()

        with patch("elis.sources.openalex.ELISHttpClient") as MockClient:
            MockClient.return_value.get.side_effect = Exception("timeout")
            ok, msg = adapter.preflight()

        assert ok is False
        assert "timeout" in msg


# ---------------------------------------------------------------------------
# Harvest pagination
# ---------------------------------------------------------------------------


class TestOpenAlexHarvest:
    def _make_api_response(self, works: list[dict], total: int) -> dict:
        return {
            "results": works,
            "meta": {"count": total},
        }

    def test_harvest_yields_records(self) -> None:
        adapter = OpenAlexAdapter()
        entry = {**SAMPLE_OPENALEX_ENTRY}
        api_data = self._make_api_response([entry], total=1)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with patch("elis.sources.openalex.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp

            records = list(adapter.harvest(["test query"], max_results=10))

        assert len(records) == 1
        assert records[0]["source"] == "OpenAlex"
        assert records[0]["title"] == "Electoral Integrity Strategies"

    def test_harvest_respects_max_results(self) -> None:
        adapter = OpenAlexAdapter()
        entries = [
            {**SAMPLE_OPENALEX_ENTRY, "id": f"W{i}", "title": f"Paper {i}"}
            for i in range(5)
        ]
        api_data = self._make_api_response(entries, total=100)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with patch("elis.sources.openalex.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp

            records = list(adapter.harvest(["test"], max_results=3))

        assert len(records) == 3

    def test_harvest_stops_on_empty_page(self) -> None:
        adapter = OpenAlexAdapter()
        api_data = self._make_api_response([], total=0)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with patch("elis.sources.openalex.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp

            records = list(adapter.harvest(["test"], max_results=10))

        assert records == []

    def test_harvest_multiple_queries(self) -> None:
        adapter = OpenAlexAdapter()
        entry1 = {**SAMPLE_OPENALEX_ENTRY, "id": "W1", "title": "Paper 1"}
        entry2 = {**SAMPLE_OPENALEX_ENTRY, "id": "W2", "title": "Paper 2"}

        data1 = self._make_api_response([entry1], total=1)
        data2 = self._make_api_response([entry2], total=1)

        mock_resp1 = MagicMock()
        mock_resp1.status_code = 200
        mock_resp1.json.return_value = data1

        mock_resp2 = MagicMock()
        mock_resp2.status_code = 200
        mock_resp2.json.return_value = data2

        with patch("elis.sources.openalex.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.side_effect = [mock_resp1, mock_resp2]

            records = list(adapter.harvest(["query 1", "query 2"], max_results=10))

        assert len(records) == 2

    def test_harvest_handles_request_failure(self) -> None:
        adapter = OpenAlexAdapter()

        with patch("elis.sources.openalex.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.side_effect = Exception("network error")

            records = list(adapter.harvest(["test"], max_results=10))

        assert records == []
