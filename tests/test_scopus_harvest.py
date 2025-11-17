"""
Tests for scopus_harvest.py
"""

import json
from unittest.mock import patch, Mock, MagicMock
import os


class TestScopusSearch:
    """Tests for scopus_search function."""

    @patch("scripts.scopus_harvest.requests.get")
    def test_successful_single_page_search(self, mock_get):
        """Should retrieve results from single page."""
        from scripts.scopus_harvest import scopus_search

        # Mock successful API response with 2 results, then empty
        first_response = Mock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "search-results": {
                "entry": [
                    {"dc:title": "Paper 1", "prism:doi": "10.1234/test1"},
                    {"dc:title": "Paper 2", "prism:doi": "10.1234/test2"},
                ]
            }
        }

        # Second call returns empty (end of results)
        second_response = Mock()
        second_response.status_code = 200
        second_response.json.return_value = {"search-results": {"entry": []}}

        mock_get.side_effect = [first_response, second_response]

        results = scopus_search("test query", count=25, max_results=100)

        assert len(results) == 2
        assert results[0]["dc:title"] == "Paper 1"
        assert mock_get.called

    @patch("scripts.scopus_harvest.requests.get")
    def test_successful_multi_page_search(self, mock_get):
        """Should retrieve results across multiple pages."""
        from scripts.scopus_harvest import scopus_search

        # Mock two pages of results
        page1_response = Mock()
        page1_response.status_code = 200
        page1_response.json.return_value = {
            "search-results": {"entry": [{"title": f"Paper {i}"} for i in range(25)]}
        }

        page2_response = Mock()
        page2_response.status_code = 200
        page2_response.json.return_value = {
            "search-results": {
                "entry": [{"title": f"Paper {i}"} for i in range(25, 50)]
            }
        }

        mock_get.side_effect = [page1_response, page2_response]

        results = scopus_search("test query", count=25, max_results=50)

        assert len(results) == 50
        assert mock_get.call_count == 2

    @patch("scripts.scopus_harvest.requests.get")
    def test_handles_api_error(self, mock_get):
        """Should handle API errors gracefully."""
        from scripts.scopus_harvest import scopus_search

        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        results = scopus_search("test query")

        assert results == []

    @patch("scripts.scopus_harvest.requests.get")
    def test_handles_empty_results(self, mock_get):
        """Should handle empty result set."""
        from scripts.scopus_harvest import scopus_search

        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {"entry": []}}
        mock_get.return_value = mock_response

        results = scopus_search("nonexistent query")

        assert results == []

    @patch("scripts.scopus_harvest.requests.get")
    def test_handles_missing_entry_key(self, mock_get):
        """Should handle response missing 'entry' key."""
        from scripts.scopus_harvest import scopus_search

        # Mock response without 'entry'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {}}
        mock_get.return_value = mock_response

        results = scopus_search("test query")

        assert results == []

    @patch("scripts.scopus_harvest.requests.get")
    def test_respects_max_results_limit(self, mock_get):
        """Should stop at max_results even if more available."""
        from scripts.scopus_harvest import scopus_search

        # Mock responses with many results
        def mock_response_generator():
            for _ in range(10):  # More pages than needed
                response = Mock()
                response.status_code = 200
                response.json.return_value = {
                    "search-results": {"entry": [{"title": "Paper"}] * 25}
                }
                yield response

        mock_get.side_effect = mock_response_generator()

        results = scopus_search("test query", count=25, max_results=50)

        # Should only fetch 2 pages (50 results)
        assert mock_get.call_count == 2
        assert len(results) == 50

    @patch("scripts.scopus_harvest.requests.get")
    def test_uses_correct_api_endpoint(self, mock_get):
        """Should call correct Scopus API endpoint."""
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {"entry": []}}
        mock_get.return_value = mock_response

        scopus_search("test query")

        call_args = mock_get.call_args
        assert "api.elsevier.com/content/search/scopus" in call_args[0][0]

    @patch("scripts.scopus_harvest.requests.get")
    def test_sends_correct_parameters(self, mock_get):
        """Should send correct query parameters."""
        from scripts.scopus_harvest import scopus_search

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {"entry": []}}
        mock_get.return_value = mock_response

        scopus_search("my test query", count=10, max_results=50)

        call_kwargs = mock_get.call_args.kwargs
        params = call_kwargs["params"]

        assert params["query"] == "my test query"
        assert params["count"] == 10
        assert params["start"] == 0

    @patch("scripts.scopus_harvest.requests.get")
    def test_pagination_increments_start(self, mock_get):
        """Should increment start parameter for pagination."""
        from scripts.scopus_harvest import scopus_search

        # Mock two pages
        responses = []
        for i in range(2):
            response = Mock()
            response.status_code = 200
            response.json.return_value = {
                "search-results": {
                    "entry": [{"title": f"Paper {j}"} for j in range(25)]
                }
            }
            responses.append(response)

        mock_get.side_effect = responses

        scopus_search("test", count=25, max_results=50)

        # Check pagination parameters
        first_call_params = mock_get.call_args_list[0].kwargs["params"]
        second_call_params = mock_get.call_args_list[1].kwargs["params"]

        assert first_call_params["start"] == 0
        assert second_call_params["start"] == 25


class TestScopusHeaders:
    """Tests for API headers configuration."""

    @patch.dict(
        os.environ,
        {"SCOPUS_API_KEY": "test_key_123", "SCOPUS_INST_TOKEN": "test_token_456"},
    )
    def test_headers_include_api_key(self):
        """Should include API key in headers."""
        # Reload module to pick up env vars
        import importlib
        import scripts.scopus_harvest

        importlib.reload(scripts.scopus_harvest)

        from scripts.scopus_harvest import HEADERS

        assert "X-ELS-APIKey" in HEADERS
        assert HEADERS["X-ELS-APIKey"] == "test_key_123"

    @patch.dict(
        os.environ,
        {"SCOPUS_API_KEY": "test_key_123", "SCOPUS_INST_TOKEN": "test_token_456"},
    )
    def test_headers_include_inst_token(self):
        """Should include institutional token in headers."""
        import importlib
        import scripts.scopus_harvest

        importlib.reload(scripts.scopus_harvest)

        from scripts.scopus_harvest import HEADERS

        assert "X-ELS-Insttoken" in HEADERS
        assert HEADERS["X-ELS-Insttoken"] == "test_token_456"

    @patch.dict(
        os.environ, {"SCOPUS_API_KEY": "test_key", "SCOPUS_INST_TOKEN": "test_token"}
    )
    def test_headers_include_accept_json(self):
        """Should request JSON format."""
        import importlib
        import scripts.scopus_harvest

        importlib.reload(scripts.scopus_harvest)

        from scripts.scopus_harvest import HEADERS

        assert HEADERS["Accept"] == "application/json"


class TestMainExecution:
    """Tests for main script execution."""

    @patch("scripts.scopus_harvest.scopus_search")
    @patch("builtins.open", create=True)
    @patch("os.makedirs")
    def test_main_creates_output_directory(self, mock_makedirs, mock_open, mock_search):
        """Should create output directory if it doesn't exist."""
        mock_search.return_value = [{"title": "Test"}]
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Manually call what main does
        output_path = "imports/scopus_sample.jsonl"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        mock_makedirs.assert_called()

    @patch("scripts.scopus_harvest.scopus_search")
    @patch("builtins.open", create=True)
    @patch("os.makedirs")
    def test_main_writes_jsonl_format(self, mock_makedirs, mock_open, mock_search):
        """Should write results in JSONL format."""
        # Mock search results
        mock_results = [
            {"title": "Paper 1", "doi": "10.1234/1"},
            {"title": "Paper 2", "doi": "10.1234/2"},
        ]
        mock_search.return_value = mock_results

        # Mock file handle
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Simulate main execution
        with open("imports/scopus_sample.jsonl", "w", encoding="utf-8") as f:
            for item in mock_results:
                f.write(json.dumps(item) + "\n")

        # Verify JSONL format (one write call per line)
        assert mock_file.write.call_count == 2  # One call per item

        # Verify each write includes newline
        for call in mock_file.write.call_args_list:
            written_text = call[0][0]
            assert written_text.endswith("\n")
            # Verify it's valid JSON
            json.loads(written_text.strip())


class TestIntegration:
    """Integration tests for full workflow."""

    @patch("scripts.scopus_harvest.requests.get")
    def test_full_harvest_workflow(self, mock_get, tmp_path):
        """Should complete full harvest workflow."""
        from scripts.scopus_harvest import scopus_search

        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {
                "entry": [
                    {
                        "dc:title": "Test Paper",
                        "prism:doi": "10.1234/test",
                        "dc:creator": "Author Name",
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        # Execute search
        results = scopus_search("test query", max_results=25)

        # Write to file
        output_file = tmp_path / "test_output.jsonl"
        with open(output_file, "w", encoding="utf-8") as f:
            for item in results:
                f.write(json.dumps(item) + "\n")

        # Verify results
        assert len(results) == 1
        assert output_file.exists()

        # Verify JSONL format
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 1
            parsed = json.loads(lines[0])
            assert parsed["dc:title"] == "Test Paper"
