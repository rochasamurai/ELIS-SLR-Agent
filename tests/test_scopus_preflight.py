"""
Tests for scopus_preflight.py
"""

import os
from unittest.mock import patch, Mock
import pytest


class TestEnvironmentVariables:
    """Test environment variable validation."""

    @patch.dict(os.environ, {}, clear=True)
    def test_raises_error_when_api_key_missing(self):
        """Should raise error when SCOPUS_API_KEY is missing."""
        from scripts.scopus_preflight import check_environment

        with pytest.raises(EnvironmentError, match="Missing SCOPUS_API_KEY"):
            check_environment()

    @patch.dict(os.environ, {"SCOPUS_API_KEY": "test_key"}, clear=True)
    def test_raises_error_when_inst_token_missing(self):
        """Should raise error when SCOPUS_INST_TOKEN is missing."""
        from scripts.scopus_preflight import check_environment

        with pytest.raises(EnvironmentError, match="Missing.*SCOPUS_INST_TOKEN"):
            check_environment()

    @patch.dict(
        os.environ, {"SCOPUS_API_KEY": "test_key", "SCOPUS_INST_TOKEN": "test_token"}
    )
    def test_loads_successfully_with_both_credentials(self):
        """Should load successfully when both credentials are present."""
        from scripts.scopus_preflight import check_environment

        # Should not raise
        api_key, inst_token = check_environment()
        assert api_key == "test_key"
        assert inst_token == "test_token"


class TestAPIRequest:
    """Test API request functionality."""

    @patch.dict(
        os.environ, {"SCOPUS_API_KEY": "test_key", "SCOPUS_INST_TOKEN": "test_token"}
    )
    @patch("requests.get")
    def test_makes_request_to_scopus_api(self, mock_get):
        """Should make request to Scopus API."""
        from scripts.scopus_preflight import test_scopus_connection

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": [{"title": "Test"}]}
        }
        mock_get.return_value = mock_response

        test_scopus_connection()

        # Verify API was called
        assert mock_get.called

    @patch.dict(
        os.environ, {"SCOPUS_API_KEY": "my_key", "SCOPUS_INST_TOKEN": "my_token"}
    )
    @patch("requests.get")
    def test_includes_correct_headers(self, mock_get):
        """Should include API key and token in headers."""
        from scripts.scopus_preflight import test_scopus_connection

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": [{"title": "Test"}]}
        }
        mock_get.return_value = mock_response

        test_scopus_connection()

        # Check headers
        call_kwargs = mock_get.call_args.kwargs
        headers = call_kwargs["headers"]
        assert headers["X-ELS-APIKey"] == "my_key"
        assert headers["X-ELS-Insttoken"] == "my_token"

    @patch.dict(
        os.environ, {"SCOPUS_API_KEY": "test_key", "SCOPUS_INST_TOKEN": "test_token"}
    )
    @patch("requests.get")
    def test_handles_successful_response(self, mock_get, capsys):
        """Should handle successful API response."""
        from scripts.scopus_preflight import test_scopus_connection

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": [{"title": "Electoral Integrity Paper"}]}
        }
        mock_get.return_value = mock_response

        test_scopus_connection()

        captured = capsys.readouterr()
        assert "Status Code: 200" in captured.out
        assert "Query OK" in captured.out

    @patch.dict(
        os.environ, {"SCOPUS_API_KEY": "test_key", "SCOPUS_INST_TOKEN": "test_token"}
    )
    @patch("requests.get")
    def test_handles_api_error(self, mock_get, capsys):
        """Should handle API errors gracefully."""
        from scripts.scopus_preflight import test_scopus_connection

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_get.return_value = mock_response

        test_scopus_connection()

        captured = capsys.readouterr()
        assert "Status Code: 401" in captured.out
        assert "Error querying Scopus API" in captured.out

    @patch.dict(
        os.environ, {"SCOPUS_API_KEY": "test_key", "SCOPUS_INST_TOKEN": "test_token"}
    )
    @patch("requests.get")
    def test_uses_correct_query_parameters(self, mock_get):
        """Should use correct query parameters."""
        from scripts.scopus_preflight import test_scopus_connection

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {"entry": []}}
        mock_get.return_value = mock_response

        test_scopus_connection()

        call_kwargs = mock_get.call_args.kwargs
        params = call_kwargs["params"]
        assert "query" in params
        assert params["query"] == "TITLE(electoral integrity)"
        assert params["count"] == 1


class TestErrorHandling:
    """Test error handling scenarios."""

    @patch.dict(
        os.environ, {"SCOPUS_API_KEY": "test_key", "SCOPUS_INST_TOKEN": "test_token"}
    )
    @patch("requests.get")
    def test_handles_json_decode_error(self, mock_get, capsys):
        """Should handle JSON decode errors."""
        from scripts.scopus_preflight import test_scopus_connection

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Not JSON"
        mock_get.return_value = mock_response

        test_scopus_connection()

        captured = capsys.readouterr()
        assert "Error querying Scopus API" in captured.out

    @patch.dict(
        os.environ, {"SCOPUS_API_KEY": "test_key", "SCOPUS_INST_TOKEN": "test_token"}
    )
    @patch("requests.get")
    def test_handles_missing_entry_key(self, mock_get, capsys):
        """Should handle missing 'entry' key in response."""
        from scripts.scopus_preflight import test_scopus_connection

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {}}
        mock_get.return_value = mock_response

        test_scopus_connection()

        captured = capsys.readouterr()
        assert "Error querying Scopus API" in captured.out
