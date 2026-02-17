"""Tests for ELISHttpClient retry, backoff, and secret-safe logging."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest
import requests

from elis.sources.http_client import ELISHttpClient, _sanitise_params


# ---------------------------------------------------------------------------
# Sanitisation
# ---------------------------------------------------------------------------


class TestSanitiseParams:
    def test_masks_apikey(self) -> None:
        result = _sanitise_params({"apiKey": "secret123", "query": "test"})
        assert result["apiKey"] == "***"
        assert result["query"] == "test"

    def test_masks_token(self) -> None:
        result = _sanitise_params({"token": "abc", "insttoken": "xyz"})
        assert result["token"] == "***"
        assert result["insttoken"] == "***"

    def test_empty_params(self) -> None:
        assert _sanitise_params(None) == {}
        assert _sanitise_params({}) == {}


# ---------------------------------------------------------------------------
# Successful requests
# ---------------------------------------------------------------------------


class TestGetSuccess:
    def test_returns_response_on_200(self) -> None:
        client = ELISHttpClient("test", delay_seconds=0, max_retries=2)
        mock_resp = MagicMock(spec=requests.Response)
        mock_resp.status_code = 200

        with patch.object(client._session, "get", return_value=mock_resp):
            resp = client.get("http://example.com")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Retry behaviour
# ---------------------------------------------------------------------------


class TestRetryBehaviour:
    def test_retries_on_429(self) -> None:
        """429 should trigger retry, then succeed on the second attempt."""
        client = ELISHttpClient(
            "test", delay_seconds=0, max_retries=3, backoff_base=0.01
        )

        resp_429 = MagicMock(spec=requests.Response)
        resp_429.status_code = 429
        resp_200 = MagicMock(spec=requests.Response)
        resp_200.status_code = 200

        with patch.object(client._session, "get", side_effect=[resp_429, resp_200]):
            resp = client.get("http://example.com")
        assert resp.status_code == 200

    def test_retries_on_500(self) -> None:
        """5xx should trigger retry."""
        client = ELISHttpClient(
            "test", delay_seconds=0, max_retries=3, backoff_base=0.01
        )

        resp_500 = MagicMock(spec=requests.Response)
        resp_500.status_code = 500
        resp_200 = MagicMock(spec=requests.Response)
        resp_200.status_code = 200

        with patch.object(client._session, "get", side_effect=[resp_500, resp_200]):
            resp = client.get("http://example.com")
        assert resp.status_code == 200

    def test_no_retry_on_404(self) -> None:
        """4xx (non-429) should raise immediately, no retry."""
        client = ELISHttpClient("test", delay_seconds=0, max_retries=3)

        resp_404 = MagicMock(spec=requests.Response)
        resp_404.status_code = 404
        resp_404.raise_for_status.side_effect = requests.exceptions.HTTPError("404")

        with patch.object(client._session, "get", return_value=resp_404):
            with pytest.raises(requests.exceptions.HTTPError):
                client.get("http://example.com")

    def test_max_retries_exceeded(self) -> None:
        """After exhausting retries, raise_for_status should be called."""
        client = ELISHttpClient(
            "test", delay_seconds=0, max_retries=2, backoff_base=0.01
        )

        resp_429 = MagicMock(spec=requests.Response)
        resp_429.status_code = 429
        resp_429.raise_for_status.side_effect = requests.exceptions.HTTPError("429")

        with patch.object(
            client._session,
            "get",
            return_value=resp_429,
        ):
            with pytest.raises(requests.exceptions.HTTPError):
                client.get("http://example.com")

    def test_request_exception_propagates(self) -> None:
        """Network errors should propagate immediately."""
        client = ELISHttpClient("test", delay_seconds=0)

        with patch.object(
            client._session,
            "get",
            side_effect=requests.exceptions.ConnectionError("fail"),
        ):
            with pytest.raises(requests.exceptions.ConnectionError):
                client.get("http://example.com")


# ---------------------------------------------------------------------------
# Logging safety
# ---------------------------------------------------------------------------


class TestLoggingSafety:
    def test_retry_log_does_not_contain_secrets(self, caplog) -> None:
        """Log messages from retries must not leak sensitive params."""
        client = ELISHttpClient(
            "test", delay_seconds=0, max_retries=1, backoff_base=0.01
        )

        resp_429 = MagicMock(spec=requests.Response)
        resp_429.status_code = 429
        resp_429.raise_for_status.side_effect = requests.exceptions.HTTPError("429")

        with patch.object(client._session, "get", return_value=resp_429):
            with caplog.at_level(logging.WARNING):
                with pytest.raises(requests.exceptions.HTTPError):
                    client.get(
                        "http://example.com",
                        params={"apiKey": "SECRET_VALUE"},
                    )

        # The params dict is not logged by the retry path, but the
        # sanitise function would mask it if it were.  Just verify no
        # "SECRET_VALUE" appears anywhere in logs.
        for record in caplog.records:
            assert "SECRET_VALUE" not in record.getMessage()


# ---------------------------------------------------------------------------
# Polite wait
# ---------------------------------------------------------------------------


class TestPoliteWait:
    def test_polite_wait_calls_sleep(self) -> None:
        client = ELISHttpClient("test", delay_seconds=0.25)
        with patch("elis.sources.http_client.time.sleep") as mock_sleep:
            client.polite_wait()
        mock_sleep.assert_called_once_with(0.25)

    def test_polite_wait_zero_noop(self) -> None:
        client = ELISHttpClient("test", delay_seconds=0)
        with patch("elis.sources.http_client.time.sleep") as mock_sleep:
            client.polite_wait()
        mock_sleep.assert_not_called()
