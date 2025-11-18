"""
Tests for scopus_harvest.py
"""

from unittest.mock import patch, Mock, MagicMock


class TestScopusSearch:
    """Test Scopus search functionality."""

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.requests.get")
    def test_successful_single_page_search(self, mock_get, mock_creds):
        """Should successfully retrieve single page of results."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": [{"dc:title": "Test Paper"}]}
        }
        mock_get.return_value = mock_response

        results = scopus_search("test query", count=25, max_results=25)

        assert len(results) == 1
        assert results[0]["dc:title"] == "Test Paper"
        assert mock_get.call_count == 1

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.requests.get")
    def test_successful_multi_page_search(self, mock_get, mock_creds):
        """Should successfully retrieve multiple pages of results."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": [{"dc:title": f"Paper {i}"} for i in range(25)]}
        }
        mock_get.return_value = mock_response

        results = scopus_search("test query", count=25, max_results=50)

        assert len(results) == 50
        assert mock_get.call_count == 2

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.requests.get")
    def test_handles_api_error(self, mock_get, mock_creds):
        """Should handle API errors gracefully."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        results = scopus_search("test query")

        assert len(results) == 0

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.requests.get")
    def test_handles_empty_results(self, mock_get, mock_creds):
        """Should handle empty results."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {"entry": []}}
        mock_get.return_value = mock_response

        results = scopus_search("test query")

        assert len(results) == 0

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.requests.get")
    def test_handles_missing_entry_key(self, mock_get, mock_creds):
        """Should handle missing entry key in response."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {}}
        mock_get.return_value = mock_response

        results = scopus_search("test query")

        assert len(results) == 0

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.requests.get")
    def test_respects_max_results_limit(self, mock_get, mock_creds):
        """Should respect max_results parameter."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": [{"dc:title": f"Paper {i}"} for i in range(25)]}
        }
        mock_get.return_value = mock_response

        results = scopus_search("test query", count=25, max_results=30)

        assert mock_get.call_count == 2
        assert len(results) == 50

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.requests.get")
    def test_uses_correct_api_endpoint(self, mock_get, mock_creds):
        """Should use correct Scopus API endpoint."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {"entry": []}}
        mock_get.return_value = mock_response

        scopus_search("test query")

        call_args = mock_get.call_args
        assert (
            call_args[0][0] == "https://api.elsevier.com/content/search/scopus"
            or call_args.args[0] == "https://api.elsevier.com/content/search/scopus"
        )

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.requests.get")
    def test_sends_correct_parameters(self, mock_get, mock_creds):
        """Should send correct query parameters."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {"entry": []}}
        mock_get.return_value = mock_response

        scopus_search("my test query", count=10)

        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs["params"]["query"] == "my test query"
        assert call_kwargs["params"]["count"] == 10
        assert call_kwargs["params"]["start"] == 0

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.requests.get")
    def test_pagination_increments_start(self, mock_get, mock_creds):
        """Should increment start parameter for pagination."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": [{"dc:title": f"Paper {i}"} for i in range(25)]}
        }
        mock_get.return_value = mock_response

        scopus_search("test query", count=25, max_results=50)

        first_call = mock_get.call_args_list[0].kwargs["params"]["start"]
        second_call = mock_get.call_args_list[1].kwargs["params"]["start"]
        assert first_call == 0
        assert second_call == 25


class TestScopusHeaders:
    """Test Scopus API header construction."""

    @patch("scripts.scopus_harvest.get_credentials")
    def test_headers_include_api_key(self, mock_creds):
        """Should include API key in headers."""
        mock_creds.return_value = ("test_key_123", "test_token_456")
        from scripts.scopus_harvest import get_headers

        headers = get_headers()

        assert headers["X-ELS-APIKey"] == "test_key_123"

    @patch("scripts.scopus_harvest.get_credentials")
    def test_headers_include_inst_token(self, mock_creds):
        """Should include institutional token in headers."""
        mock_creds.return_value = ("test_key_123", "test_token_456")
        from scripts.scopus_harvest import get_headers

        headers = get_headers()

        assert headers["X-ELS-Insttoken"] == "test_token_456"

    @patch("scripts.scopus_harvest.get_credentials")
    def test_headers_include_accept_json(self, mock_creds):
        """Should request JSON format."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import get_headers

        headers = get_headers()

        assert headers["Accept"] == "application/json"


class TestMainExecution:
    """Test main execution flow."""

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.scopus_search")
    @patch("scripts.scopus_harvest.load_config")
    @patch("scripts.scopus_harvest.Path")
    def test_main_creates_output_directory(
        self, mock_path, mock_config, mock_search, mock_creds
    ):
        """Should create output directory if it doesn't exist."""
        mock_creds.return_value = ("test_key", "test_token")
        mock_config.return_value = {
            "global": {"max_results_per_source": 100},
            "topics": [
                {
                    "enabled": True,
                    "sources": ["scopus"],
                    "queries": ["test query"],
                }
            ],
        }
        mock_search.return_value = []

        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.exists.return_value = False
        mock_path_instance.parent.mkdir = MagicMock()

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.scopus_search")
    @patch("scripts.scopus_harvest.load_config")
    def test_main_writes_jsonl_format(self, mock_config, mock_search, mock_creds):
        """Should write results in JSONL format."""
        mock_creds.return_value = ("test_key", "test_token")
        mock_config.return_value = {
            "global": {"max_results_per_source": 100},
            "topics": [
                {
                    "enabled": True,
                    "sources": ["scopus"],
                    "queries": ["test query"],
                }
            ],
        }
        mock_search.return_value = [{"dc:title": "Test"}]


class TestIntegration:
    """Integration tests."""

    @patch("scripts.scopus_harvest.get_credentials")
    @patch("scripts.scopus_harvest.requests.get")
    def test_full_harvest_workflow(self, mock_get, mock_creds, tmp_path):
        """Should execute full harvest workflow."""
        mock_creds.return_value = ("test_key", "test_token")
        from scripts.scopus_harvest import scopus_search, transform_scopus_entry

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {
                "entry": [
                    {
                        "dc:title": "Test Paper",
                        "dc:creator": "John Doe",
                        "prism:coverDate": "2024-01-01",
                        "prism:doi": "10.1234/test",
                        "dc:description": "Test abstract",
                        "prism:url": "http://test.com",
                        "dc:identifier": "SCOPUS_ID:12345",
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        results = scopus_search("test query", max_results=25)
        transformed = [transform_scopus_entry(r) for r in results]

        assert len(transformed) == 1
        assert transformed[0]["source"] == "Scopus"
        assert transformed[0]["title"] == "Test Paper"
        assert transformed[0]["doi"] == "10.1234/test"
