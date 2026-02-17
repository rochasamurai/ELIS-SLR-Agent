"""Tests for the CrossRef source adapter."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import jsonschema
import pytest

from elis.sources.crossref import (
    CrossRefAdapter,
    transform_entry,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CROSSREF_ENTRY = {
    "DOI": "10.1234/test.002",
    "URL": "https://doi.org/10.1234/test.002",
    "title": ["Electoral Integrity and Democratic Governance"],
    "author": [
        {"given": "Alice", "family": "Smith"},
        {"given": "Bob", "family": "Jones"},
    ],
    "published-print": {"date-parts": [[2023, 6, 15]]},
    "abstract": "<jats:p>This study examines electoral integrity.</jats:p>",
    "type": "journal-article",
    "publisher": "Test Publisher",
    "is-referenced-by-count": 18,
}


def _load_harvester_schema() -> dict:
    schema_path = Path("schemas/appendix_a_harvester.schema.json")
    if not schema_path.exists():
        pytest.skip("Harvester schema not found")
    return json.loads(schema_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------


class TestTransformEntry:
    def test_basic_fields(self) -> None:
        record = transform_entry(SAMPLE_CROSSREF_ENTRY)
        assert record["source"] == "CrossRef"
        assert record["title"] == "Electoral Integrity and Democratic Governance"
        assert record["year"] == 2023
        assert record["doi"] == "10.1234/test.002"
        assert record["authors"] == ["Alice Smith", "Bob Jones"]
        assert record["citation_count"] == 18
        assert record["crossref_id"] == "10.1234/test.002"
        assert record["crossref_type"] == "journal-article"
        assert record["publisher"] == "Test Publisher"

    def test_title_from_array(self) -> None:
        """CrossRef returns title as a list — first element used."""
        entry = {**SAMPLE_CROSSREF_ENTRY, "title": ["First Title", "Subtitle"]}
        record = transform_entry(entry)
        assert record["title"] == "First Title"

    def test_empty_title_array(self) -> None:
        entry = {**SAMPLE_CROSSREF_ENTRY, "title": []}
        record = transform_entry(entry)
        assert record["title"] == ""

    def test_doi_uppercase_key(self) -> None:
        """CrossRef uses uppercase DOI key."""
        record = transform_entry(SAMPLE_CROSSREF_ENTRY)
        assert record["doi"] == "10.1234/test.002"

    def test_abstract_preserved(self) -> None:
        record = transform_entry(SAMPLE_CROSSREF_ENTRY)
        assert "electoral integrity" in record["abstract"]

    def test_url_from_entry(self) -> None:
        record = transform_entry(SAMPLE_CROSSREF_ENTRY)
        assert record["url"] == "https://doi.org/10.1234/test.002"

    def test_year_from_published_print(self) -> None:
        record = transform_entry(SAMPLE_CROSSREF_ENTRY)
        assert record["year"] == 2023

    def test_year_from_published_online_fallback(self) -> None:
        entry = {**SAMPLE_CROSSREF_ENTRY}
        del entry["published-print"]
        entry["published-online"] = {"date-parts": [[2022, 1]]}
        record = transform_entry(entry)
        assert record["year"] == 2022

    def test_year_none_when_no_date(self) -> None:
        entry = {**SAMPLE_CROSSREF_ENTRY}
        del entry["published-print"]
        record = transform_entry(entry)
        assert record["year"] is None

    def test_year_none_on_invalid_date_parts(self) -> None:
        entry = {**SAMPLE_CROSSREF_ENTRY, "published-print": {"date-parts": [[]]}}
        record = transform_entry(entry)
        assert record["year"] is None

    def test_year_none_on_non_numeric(self) -> None:
        entry = {
            **SAMPLE_CROSSREF_ENTRY,
            "published-print": {"date-parts": [["not_a_year"]]},
        }
        record = transform_entry(entry)
        assert record["year"] is None

    def test_missing_fields_handled(self) -> None:
        minimal = {"DOI": "10.0000/minimal"}
        record = transform_entry(minimal)
        assert record["source"] == "CrossRef"
        assert record["title"] == ""
        assert record["authors"] == []
        assert record["year"] is None
        assert record["doi"] == "10.0000/minimal"
        assert record["abstract"] == ""
        assert record["citation_count"] == 0

    def test_author_missing_given_name(self) -> None:
        entry = {**SAMPLE_CROSSREF_ENTRY, "author": [{"family": "Solo"}]}
        record = transform_entry(entry)
        assert record["authors"] == ["Solo"]

    def test_author_missing_family_excluded(self) -> None:
        entry = {**SAMPLE_CROSSREF_ENTRY, "author": [{"given": "NoFamily"}]}
        record = transform_entry(entry)
        assert record["authors"] == []

    def test_none_citation_count_becomes_zero(self) -> None:
        entry = {**SAMPLE_CROSSREF_ENTRY, "is-referenced-by-count": None}
        record = transform_entry(entry)
        assert record["citation_count"] == 0

    def test_schema_compliance(self) -> None:
        """Transformed record must pass appendix_a_harvester.schema.json."""
        schema = _load_harvester_schema()
        record = transform_entry(SAMPLE_CROSSREF_ENTRY)
        jsonschema.validate([record], schema)

    def test_raw_metadata_preserved(self) -> None:
        record = transform_entry(SAMPLE_CROSSREF_ENTRY)
        assert record["raw_metadata"] is SAMPLE_CROSSREF_ENTRY


# ---------------------------------------------------------------------------
# Adapter properties
# ---------------------------------------------------------------------------


class TestCrossRefAdapterProperties:
    def test_source_name(self) -> None:
        adapter = CrossRefAdapter()
        assert adapter.source_name == "crossref"

    def test_display_name(self) -> None:
        adapter = CrossRefAdapter()
        assert adapter.display_name == "CrossRef"


# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------


class TestCrossRefPreflight:
    def test_preflight_success(self) -> None:
        adapter = CrossRefAdapter()
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        with patch("elis.sources.crossref.ELISHttpClient") as MockClient:
            MockClient.return_value.get.return_value = mock_resp
            ok, msg = adapter.preflight()

        assert ok is True
        assert msg == "ok"

    def test_preflight_failure(self) -> None:
        adapter = CrossRefAdapter()

        with patch("elis.sources.crossref.ELISHttpClient") as MockClient:
            MockClient.return_value.get.side_effect = Exception("timeout")
            ok, msg = adapter.preflight()

        assert ok is False
        assert "timeout" in msg


# ---------------------------------------------------------------------------
# Harvest pagination
# ---------------------------------------------------------------------------


class TestCrossRefHarvest:
    def _make_api_response(self, items: list[dict], total: int) -> dict:
        return {
            "message": {
                "items": items,
                "total-results": total,
            }
        }

    def test_harvest_yields_records(self) -> None:
        adapter = CrossRefAdapter()
        entry = {**SAMPLE_CROSSREF_ENTRY}
        api_data = self._make_api_response([entry], total=1)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with patch("elis.sources.crossref.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp

            records = list(adapter.harvest(["test query"], max_results=10))

        assert len(records) == 1
        assert records[0]["source"] == "CrossRef"
        assert records[0]["title"] == "Electoral Integrity and Democratic Governance"

    def test_harvest_respects_max_results(self) -> None:
        adapter = CrossRefAdapter()
        entries = [
            {**SAMPLE_CROSSREF_ENTRY, "DOI": f"10.1234/{i}", "title": [f"Paper {i}"]}
            for i in range(5)
        ]
        api_data = self._make_api_response(entries, total=100)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with patch("elis.sources.crossref.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp

            records = list(adapter.harvest(["test"], max_results=3))

        assert len(records) == 3

    def test_harvest_stops_on_empty_items(self) -> None:
        adapter = CrossRefAdapter()
        api_data = self._make_api_response([], total=0)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with patch("elis.sources.crossref.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp

            records = list(adapter.harvest(["test"], max_results=10))

        assert records == []

    def test_harvest_stops_when_offset_exceeds_total(self) -> None:
        """When offset >= total-results, pagination should stop."""
        adapter = CrossRefAdapter()
        entries = [
            {**SAMPLE_CROSSREF_ENTRY, "DOI": f"10.1234/{i}", "title": [f"Paper {i}"]}
            for i in range(2)
        ]
        api_data = self._make_api_response(entries, total=2)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with patch("elis.sources.crossref.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp

            records = list(adapter.harvest(["test"], max_results=100))

        assert len(records) == 2
        # Only one API call needed since total=2 and we got 2 items
        assert mock_client.get.call_count == 1

    def test_harvest_multiple_queries(self) -> None:
        adapter = CrossRefAdapter()
        entry1 = {**SAMPLE_CROSSREF_ENTRY, "DOI": "10.1234/1", "title": ["Paper 1"]}
        entry2 = {**SAMPLE_CROSSREF_ENTRY, "DOI": "10.1234/2", "title": ["Paper 2"]}

        data1 = self._make_api_response([entry1], total=1)
        data2 = self._make_api_response([entry2], total=1)

        mock_resp1 = MagicMock()
        mock_resp1.status_code = 200
        mock_resp1.json.return_value = data1

        mock_resp2 = MagicMock()
        mock_resp2.status_code = 200
        mock_resp2.json.return_value = data2

        with patch("elis.sources.crossref.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.side_effect = [mock_resp1, mock_resp2]

            records = list(adapter.harvest(["query 1", "query 2"], max_results=10))

        assert len(records) == 2

    def test_harvest_handles_request_failure(self) -> None:
        adapter = CrossRefAdapter()

        with patch("elis.sources.crossref.ELISHttpClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.get.side_effect = Exception("network error")

            records = list(adapter.harvest(["test"], max_results=10))

        assert records == []

    def test_harvest_uses_mailto_when_set(self) -> None:
        adapter = CrossRefAdapter()
        api_data = self._make_api_response([], total=0)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with (
            patch("elis.sources.crossref.ELISHttpClient") as MockClient,
            patch.dict("os.environ", {"ELIS_CONTACT": "test@example.com"}),
        ):
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp

            list(adapter.harvest(["test"], max_results=10))

        call_kwargs = mock_client.get.call_args
        assert call_kwargs[1]["params"]["mailto"] == "test@example.com"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class TestCrossRefRegistry:
    def test_crossref_registered(self) -> None:
        from elis.sources import get_adapter

        adapter_cls = get_adapter("crossref")
        assert adapter_cls is CrossRefAdapter

    def test_crossref_in_available_sources(self) -> None:
        from elis.sources import available_sources

        assert "crossref" in available_sources()
