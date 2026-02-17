"""Tests for the Scopus source adapter."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import jsonschema
import pytest

from elis.sources.scopus import (
    ScopusAdapter,
    _get_auth_headers,
    transform_entry,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_SCOPUS_ENTRY = {
    "dc:identifier": "SCOPUS_ID:85012345678",
    "dc:title": "Electoral Integrity and Voter Confidence",
    "dc:creator": "Smith A.",
    "prism:coverDate": "2023-06-15",
    "prism:doi": "10.1016/j.test.2023.001",
    "dc:description": "This study examines voter confidence in elections.",
    "prism:url": "https://api.elsevier.com/content/abstract/scopus_id/85012345678",
    "citedby-count": "25",
}


def _load_harvester_schema() -> dict:
    schema_path = Path("schemas/appendix_a_harvester.schema.json")
    if not schema_path.exists():
        pytest.skip("Harvester schema not found")
    return json.loads(schema_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class TestAuthHeaders:
    def test_returns_headers_when_env_set(self) -> None:
        with patch.dict(
            "os.environ",
            {"SCOPUS_API_KEY": "key123", "SCOPUS_INST_TOKEN": "token456"},
        ):
            headers = _get_auth_headers()
        assert headers["X-ELS-APIKey"] == "key123"
        assert headers["X-ELS-Insttoken"] == "token456"
        assert headers["Accept"] == "application/json"

    def test_raises_when_api_key_missing(self) -> None:
        with patch.dict("os.environ", {"SCOPUS_INST_TOKEN": "token"}, clear=True):
            with pytest.raises(EnvironmentError, match="SCOPUS_API_KEY"):
                _get_auth_headers()

    def test_raises_when_inst_token_missing(self) -> None:
        with patch.dict("os.environ", {"SCOPUS_API_KEY": "key"}, clear=True):
            with pytest.raises(EnvironmentError, match="SCOPUS_INST_TOKEN"):
                _get_auth_headers()

    def test_raises_when_both_missing(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError):
                _get_auth_headers()


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------


class TestTransformEntry:
    def test_basic_fields(self) -> None:
        record = transform_entry(SAMPLE_SCOPUS_ENTRY)
        assert record["source"] == "Scopus"
        assert record["title"] == "Electoral Integrity and Voter Confidence"
        assert record["year"] == 2023
        assert record["doi"] == "10.1016/j.test.2023.001"
        assert record["authors"] == ["Smith A."]
        assert record["scopus_id"] == "85012345678"
        assert record["citation_count"] == 25

    def test_scopus_id_prefix_stripped(self) -> None:
        record = transform_entry(SAMPLE_SCOPUS_ENTRY)
        assert not record["scopus_id"].startswith("SCOPUS_ID:")

    def test_abstract_from_description(self) -> None:
        record = transform_entry(SAMPLE_SCOPUS_ENTRY)
        assert "voter confidence" in record["abstract"]

    def test_year_from_cover_date(self) -> None:
        record = transform_entry(SAMPLE_SCOPUS_ENTRY)
        assert record["year"] == 2023

    def test_year_none_when_no_date(self) -> None:
        entry = {**SAMPLE_SCOPUS_ENTRY}
        del entry["prism:coverDate"]
        record = transform_entry(entry)
        assert record["year"] is None

    def test_year_none_on_short_date(self) -> None:
        entry = {**SAMPLE_SCOPUS_ENTRY, "prism:coverDate": "20"}
        record = transform_entry(entry)
        assert record["year"] is None

    def test_year_none_on_non_numeric_date(self) -> None:
        entry = {**SAMPLE_SCOPUS_ENTRY, "prism:coverDate": "XXXX-01-01"}
        record = transform_entry(entry)
        assert record["year"] is None

    def test_missing_fields_handled(self) -> None:
        minimal: dict = {}
        record = transform_entry(minimal)
        assert record["source"] == "Scopus"
        assert record["title"] == ""
        assert record["authors"] == []
        assert record["year"] is None
        assert record["doi"] == ""
        assert record["abstract"] == ""
        assert record["scopus_id"] == ""
        assert record["citation_count"] == 0

    def test_creator_empty_string_gives_empty_authors(self) -> None:
        entry = {**SAMPLE_SCOPUS_ENTRY, "dc:creator": ""}
        record = transform_entry(entry)
        assert record["authors"] == []

    def test_creator_none_gives_empty_authors(self) -> None:
        entry = {**SAMPLE_SCOPUS_ENTRY, "dc:creator": None}
        record = transform_entry(entry)
        assert record["authors"] == []

    def test_none_citation_count_becomes_zero(self) -> None:
        entry = {**SAMPLE_SCOPUS_ENTRY}
        del entry["citedby-count"]
        record = transform_entry(entry)
        assert record["citation_count"] == 0

    def test_non_numeric_citation_count_becomes_zero(self) -> None:
        entry = {**SAMPLE_SCOPUS_ENTRY, "citedby-count": "N/A"}
        record = transform_entry(entry)
        assert record["citation_count"] == 0

    def test_schema_compliance(self) -> None:
        """Transformed record must pass appendix_a_harvester.schema.json."""
        schema = _load_harvester_schema()
        record = transform_entry(SAMPLE_SCOPUS_ENTRY)
        jsonschema.validate([record], schema)

    def test_raw_metadata_preserved(self) -> None:
        record = transform_entry(SAMPLE_SCOPUS_ENTRY)
        assert record["raw_metadata"] is SAMPLE_SCOPUS_ENTRY


# ---------------------------------------------------------------------------
# Adapter properties
# ---------------------------------------------------------------------------


class TestScopusAdapterProperties:
    def test_source_name(self) -> None:
        adapter = ScopusAdapter()
        assert adapter.source_name == "scopus"

    def test_display_name(self) -> None:
        adapter = ScopusAdapter()
        assert adapter.display_name == "Scopus"


# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------


class TestScopusPreflight:
    def test_preflight_success(self) -> None:
        adapter = ScopusAdapter()
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        with (
            patch("elis.sources.scopus._get_auth_headers", return_value={"h": "v"}),
            patch("elis.sources.scopus.ELISHttpClient") as MockClient,
        ):
            MockClient.return_value.get.return_value = mock_resp
            ok, msg = adapter.preflight()

        assert ok is True
        assert msg == "ok"

    def test_preflight_failure_no_credentials(self) -> None:
        adapter = ScopusAdapter()

        with patch(
            "elis.sources.scopus._get_auth_headers",
            side_effect=EnvironmentError("Missing SCOPUS_API_KEY"),
        ):
            ok, msg = adapter.preflight()

        assert ok is False
        assert "SCOPUS_API_KEY" in msg

    def test_preflight_failure_network(self) -> None:
        adapter = ScopusAdapter()

        with (
            patch("elis.sources.scopus._get_auth_headers", return_value={"h": "v"}),
            patch("elis.sources.scopus.ELISHttpClient") as MockClient,
        ):
            MockClient.return_value.get.side_effect = Exception("timeout")
            ok, msg = adapter.preflight()

        assert ok is False
        assert "timeout" in msg


# ---------------------------------------------------------------------------
# Harvest pagination
# ---------------------------------------------------------------------------


class TestScopusHarvest:
    def _make_api_response(self, entries: list[dict], total: int) -> dict:
        return {
            "search-results": {
                "entry": entries,
                "opensearch:totalResults": str(total),
            }
        }

    def test_harvest_yields_records(self) -> None:
        adapter = ScopusAdapter()
        entry = {**SAMPLE_SCOPUS_ENTRY}
        api_data = self._make_api_response([entry], total=1)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with (
            patch("elis.sources.scopus._get_auth_headers", return_value={"h": "v"}),
            patch("elis.sources.scopus.ELISHttpClient") as MockClient,
        ):
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp
            records = list(adapter.harvest(["test query"], max_results=10))

        assert len(records) == 1
        assert records[0]["source"] == "Scopus"
        assert records[0]["title"] == "Electoral Integrity and Voter Confidence"

    def test_harvest_respects_max_results(self) -> None:
        adapter = ScopusAdapter()
        entries = [
            {
                **SAMPLE_SCOPUS_ENTRY,
                "dc:identifier": f"SCOPUS_ID:{i}",
                "dc:title": f"Paper {i}",
            }
            for i in range(5)
        ]
        api_data = self._make_api_response(entries, total=100)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with (
            patch("elis.sources.scopus._get_auth_headers", return_value={"h": "v"}),
            patch("elis.sources.scopus.ELISHttpClient") as MockClient,
        ):
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp
            records = list(adapter.harvest(["test"], max_results=3))

        assert len(records) == 3

    def test_harvest_stops_on_empty_entries(self) -> None:
        adapter = ScopusAdapter()
        api_data = self._make_api_response([], total=0)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with (
            patch("elis.sources.scopus._get_auth_headers", return_value={"h": "v"}),
            patch("elis.sources.scopus.ELISHttpClient") as MockClient,
        ):
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp
            records = list(adapter.harvest(["test"], max_results=10))

        assert records == []

    def test_harvest_stops_when_offset_exceeds_total(self) -> None:
        adapter = ScopusAdapter()
        entries = [
            {
                **SAMPLE_SCOPUS_ENTRY,
                "dc:identifier": f"SCOPUS_ID:{i}",
                "dc:title": f"Paper {i}",
            }
            for i in range(2)
        ]
        api_data = self._make_api_response(entries, total=2)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        with (
            patch("elis.sources.scopus._get_auth_headers", return_value={"h": "v"}),
            patch("elis.sources.scopus.ELISHttpClient") as MockClient,
        ):
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp
            records = list(adapter.harvest(["test"], max_results=100))

        assert len(records) == 2
        assert mock_client.get.call_count == 1

    def test_harvest_multiple_queries(self) -> None:
        adapter = ScopusAdapter()
        entry1 = {
            **SAMPLE_SCOPUS_ENTRY,
            "dc:identifier": "SCOPUS_ID:1",
            "dc:title": "Paper 1",
        }
        entry2 = {
            **SAMPLE_SCOPUS_ENTRY,
            "dc:identifier": "SCOPUS_ID:2",
            "dc:title": "Paper 2",
        }

        data1 = self._make_api_response([entry1], total=1)
        data2 = self._make_api_response([entry2], total=1)

        mock_resp1 = MagicMock()
        mock_resp1.status_code = 200
        mock_resp1.json.return_value = data1

        mock_resp2 = MagicMock()
        mock_resp2.status_code = 200
        mock_resp2.json.return_value = data2

        with (
            patch("elis.sources.scopus._get_auth_headers", return_value={"h": "v"}),
            patch("elis.sources.scopus.ELISHttpClient") as MockClient,
        ):
            mock_client = MockClient.return_value
            mock_client.get.side_effect = [mock_resp1, mock_resp2]
            records = list(adapter.harvest(["q1", "q2"], max_results=10))

        assert len(records) == 2

    def test_harvest_handles_request_failure(self) -> None:
        adapter = ScopusAdapter()

        with (
            patch("elis.sources.scopus._get_auth_headers", return_value={"h": "v"}),
            patch("elis.sources.scopus.ELISHttpClient") as MockClient,
        ):
            mock_client = MockClient.return_value
            mock_client.get.side_effect = Exception("network error")
            records = list(adapter.harvest(["test"], max_results=10))

        assert records == []

    def test_harvest_skips_when_no_credentials(self) -> None:
        adapter = ScopusAdapter()

        with patch(
            "elis.sources.scopus._get_auth_headers",
            side_effect=EnvironmentError("Missing creds"),
        ):
            records = list(adapter.harvest(["test"], max_results=10))

        assert records == []

    def test_harvest_passes_auth_headers(self) -> None:
        adapter = ScopusAdapter()
        api_data = self._make_api_response([], total=0)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data

        fake_headers = {
            "X-ELS-APIKey": "k",
            "X-ELS-Insttoken": "t",
            "Accept": "application/json",
        }

        with (
            patch("elis.sources.scopus._get_auth_headers", return_value=fake_headers),
            patch("elis.sources.scopus.ELISHttpClient") as MockClient,
        ):
            mock_client = MockClient.return_value
            mock_client.get.return_value = mock_resp
            list(adapter.harvest(["test"], max_results=10))

        call_kwargs = mock_client.get.call_args
        assert call_kwargs[1]["headers"] == fake_headers


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class TestScopusRegistry:
    def test_scopus_registered(self) -> None:
        from elis.sources import get_adapter

        adapter_cls = get_adapter("scopus")
        assert adapter_cls is ScopusAdapter

    def test_scopus_in_available_sources(self) -> None:
        from elis.sources import available_sources

        assert "scopus" in available_sources()
