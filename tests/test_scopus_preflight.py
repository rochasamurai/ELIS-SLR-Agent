"""
Tests for scopus_preflight.py
"""

import pytest
import os
from unittest.mock import patch, Mock


class TestEnvironmentVariables:
    """Tests for environment variable handling."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_raises_error_when_api_key_missing(self):
        """Should raise error when SCOPUS_API_KEY is missing."""
        # Clear any existing imports
        import sys
        if 'scripts.scopus_preflight' in sys.modules:
            del sys.modules['scripts.scopus_preflight']
        
        with pytest.raises(EnvironmentError, match="Missing SCOPUS_API_KEY"):
            import scripts.scopus_preflight
    
    @patch.dict(os.environ, {'SCOPUS_API_KEY': 'test_key'}, clear=True)
    def test_raises_error_when_inst_token_missing(self):
        """Should raise error when SCOPUS_INST_TOKEN is missing."""
        import sys
        if 'scripts.scopus_preflight' in sys.modules:
            del sys.modules['scripts.scopus_preflight']
        
        with pytest.raises(EnvironmentError, match="Missing.*SCOPUS_INST_TOKEN"):
            import scripts.scopus_preflight
    
    @patch.dict(os.environ, {
        'SCOPUS_API_KEY': 'test_key_123',
        'SCOPUS_INST_TOKEN': 'test_token_456'
    })
    @patch('scripts.scopus_preflight.requests.get')
    def test_loads_successfully_with_both_credentials(self, mock_get):
        """Should load successfully when both credentials present."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {
                "entry": [{"title": "Test"}]
            }
        }
        mock_get.return_value = mock_response
        
        # Clear and reload module
        import sys
        if 'scripts.scopus_preflight' in sys.modules:
            del sys.modules['scripts.scopus_preflight']


class TestAPIRequest:
    """Tests for API request functionality."""
    
    @patch.dict(os.environ, {
        'SCOPUS_API_KEY': 'test_key',
        'SCOPUS_INST_TOKEN': 'test_token'
    })
    @patch('scripts.scopus_preflight.requests.get')
    def test_makes_request_to_scopus_api(self, mock_get):
        """Should make request to Scopus API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": [{"title": "Test"}]}
        }
        mock_get.return_value = mock_response
        
        # Clear and reload to trigger execution
        import sys
        if 'scripts.scopus_preflight' in sys.modules:
            del sys.modules['scripts.scopus_preflight']
        
        # Verify API was called
        assert mock_get.called
        call_args = mock_get.call_args
        assert "api.elsevier.com" in call_args[0][0]
    
    @patch.dict(os.environ, {
        'SCOPUS_API_KEY': 'my_key',
        'SCOPUS_INST_TOKEN': 'my_token'
    })
    @patch('scripts.scopus_preflight.requests.get')
    def test_includes_correct_headers(self, mock_get):
        """Should include API key and token in headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": [{"title": "Test"}]}
        }
        mock_get.return_value = mock_response
        
        import sys
        if 'scripts.scopus_preflight' in sys.modules:
            del sys.modules['scripts.scopus_preflight']
        
        # Check headers
        call_kwargs = mock_get.call_args.kwargs
        headers = call_kwargs['headers']
        
        assert headers['X-ELS-APIKey'] == 'my_key'
        assert headers['X-ELS-Insttoken'] == 'my_token'
        assert headers['Accept'] == 'application/json'
    
    @patch.dict(os.environ, {
        'SCOPUS_API_KEY': 'test_key',
        'SCOPUS_INST_TOKEN': 'test_token'
    })
    @patch('scripts.scopus_preflight.requests.get')
    def test_handles_successful_response(self, mock_get, capsys):
        """Should handle successful API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {
                "entry": [{"title": "Electoral Integrity Paper"}]
            }
        }
        mock_get.return_value = mock_response
        
        import sys
        if 'scripts.scopus_preflight' in sys.modules:
            del sys.modules['scripts.scopus_preflight']
        
        captured = capsys.readouterr()
        assert "Status Code: 200" in captured.out
        assert "Query OK" in captured.out
    
    @patch.dict(os.environ, {
        'SCOPUS_API_KEY': 'test_key',
        'SCOPUS_INST_TOKEN': 'test_token'
    })
    @patch('scripts.scopus_preflight.requests.get')
    def test_handles_api_error(self, mock_get, capsys):
        """Should handle API errors gracefully."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_get.return_value = mock_response
        
        import sys
        if 'scripts.scopus_preflight' in sys.modules:
            del sys.modules['scripts.scopus_preflight']
        
        captured = capsys.readouterr()
        assert "Status Code: 401" in captured.out
        assert "Error querying Scopus API" in captured.out
    
    @patch.dict(os.environ, {
        'SCOPUS_API_KEY': 'test_key',
        'SCOPUS_INST_TOKEN': 'test_token'
    })
    @patch('scripts.scopus_preflight.requests.get')
    def test_uses_correct_query_parameters(self, mock_get):
        """Should use correct query parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": []}
        }
        mock_get.return_value = mock_response
        
        import sys
        if 'scripts.scopus_preflight' in sys.modules:
            del sys.modules['scripts.scopus_preflight']
        
        call_kwargs = mock_get.call_args.kwargs
        params = call_kwargs['params']
        
        assert 'query' in params
        assert 'TITLE' in params['query']
        assert params['count'] == 1


class TestErrorHandling:
    """Tests for error handling."""
    
    @patch.dict(os.environ, {
        'SCOPUS_API_KEY': 'test_key',
        'SCOPUS_INST_TOKEN': 'test_token'
    })
    @patch('scripts.scopus_preflight.requests.get')
    def test_handles_json_decode_error(self, mock_get, capsys):
        """Should handle invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Not JSON"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        import sys
        if 'scripts.scopus_preflight' in sys.modules:
            del sys.modules['scripts.scopus_preflight']
        
        captured = capsys.readouterr()
        assert "Error querying Scopus API" in captured.out
    
    @patch.dict(os.environ, {
        'SCOPUS_API_KEY': 'test_key',
        'SCOPUS_INST_TOKEN': 'test_token'
    })
    @patch('scripts.scopus_preflight.requests.get')
    def test_handles_missing_entry_key(self, mock_get, capsys):
        """Should handle response missing expected keys."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {}  # Missing 'entry'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        import sys
        if 'scripts.scopus_preflight' in sys.modules:
            del sys.modules['scripts.scopus_preflight']
        
        captured = capsys.readouterr()
        # Should print error due to KeyError
        assert "Error querying Scopus API" in captured.out
        
