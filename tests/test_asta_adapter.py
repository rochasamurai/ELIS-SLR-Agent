"""Unit tests for ASTA MCP adapter."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from sources.asta_mcp.adapter import AstaMCPAdapter


def test_adapter_initialization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Adapter should initialize with defaults and create log directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ASTA_TOOL_KEY", "test-key")

    adapter = AstaMCPAdapter(evidence_window_end="2025-01-31")

    assert adapter.evidence_window_end == "2025-01-31"
    assert adapter.base_url == "https://asta-tools.allen.ai/mcp/v1"
    assert adapter.run_id
    assert adapter.log_dir.exists()
    assert adapter.stats["requests"] == 0


def test_adapter_warns_when_no_api_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Adapter should print warning when ASTA_TOOL_KEY is missing."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ASTA_TOOL_KEY", raising=False)

    _ = AstaMCPAdapter()
    captured = capsys.readouterr()

    assert "Warning: ASTA_TOOL_KEY not set" in captured.out


def test_extract_papers_from_mcp_parses_text_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Parser should extract records from MCP content payload."""
    monkeypatch.chdir(tmp_path)
    adapter = AstaMCPAdapter(run_id="test_run")

    response = {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    [{"title": "Paper A", "doi": "10.1/a"}, {"title": "Paper B"}]
                ),
            }
        ]
    }
    papers = adapter._extract_papers_from_mcp(response)
    assert len(papers) == 2
    assert papers[0]["title"] == "Paper A"


@patch("sources.asta_mcp.adapter.time.sleep")
@patch("sources.asta_mcp.adapter.requests.post")
def test_call_mcp_tool_retries_once_on_rate_limit(
    mock_post: Mock,
    mock_sleep: Mock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """429 response should increment stat and retry one time."""
    monkeypatch.chdir(tmp_path)
    adapter = AstaMCPAdapter(run_id="retry_test")

    first = Mock()
    first.status_code = 429
    first.raise_for_status.return_value = None
    first.headers = {"content-type": "application/json"}
    first.text = "{}"

    second = Mock()
    second.status_code = 200
    second.raise_for_status.return_value = None
    second.json.return_value = {"content": []}
    second.headers = {"content-type": "application/json"}
    second.text = "{}"

    mock_post.side_effect = [first, second]

    result = adapter._call_mcp_tool("tools/list", {})
    assert result == {"content": []}
    assert adapter.stats["requests"] == 1
    assert adapter.stats["rate_limit_hits"] == 1
    assert mock_post.call_count == 2
    mock_sleep.assert_called_once_with(5)
    assert (adapter.log_dir / "requests.jsonl").exists()
    assert (adapter.log_dir / "responses.jsonl").exists()


@patch("sources.asta_mcp.adapter.requests.post")
def test_call_mcp_tool_logs_errors(
    mock_post: Mock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """HTTP errors should increment error stats and create errors log."""
    monkeypatch.chdir(tmp_path)
    adapter = AstaMCPAdapter(run_id="error_test")

    response = Mock()
    response.status_code = 500
    response.raise_for_status.side_effect = requests.HTTPError("server exploded")
    mock_post.return_value = response

    with pytest.raises(requests.HTTPError):
        adapter._call_mcp_tool("tools/list", {})

    assert adapter.stats["errors"] == 1
    assert (adapter.log_dir / "errors.jsonl").exists()


def test_decode_sse_mcp_response(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """SSE response should be parsed from last data frame."""
    monkeypatch.chdir(tmp_path)
    adapter = AstaMCPAdapter(run_id="sse_test")

    response = Mock()
    response.headers = {"content-type": "text/event-stream"}
    response.text = (
        "event: message\n"
        'data: {"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"[]"}]}}\n'
    )

    payload = adapter._decode_mcp_response(response)
    assert payload["result"]["content"][0]["type"] == "text"


def test_normalize_paper_maps_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Paper normalization should map ASTA fields into ELIS schema fields."""
    monkeypatch.chdir(tmp_path)
    adapter = AstaMCPAdapter(run_id="normalize_test")

    sample = {
        "paperId": "abc123",
        "corpusId": 999,
        "title": "Sample Paper",
        "authors": [{"name": "Alice"}, {"name": "Bob"}],
        "year": 2024,
        "externalIds": {"DOI": "10.1/a", "ArXiv": "2101.00001"},
        "abstract": "Abstract text",
        "url": "https://example.org/paper",
        "venue": "Test Venue",
        "publicationDate": "2024-01-01",
        "fieldsOfStudy": ["Computer Science"],
        "isOpenAccess": True,
        "citationCount": 42,
        "tldr": {"text": "summary"},
    }

    normalized = adapter._normalize_paper(sample)
    assert normalized["source"] == "ASTA_MCP"
    assert normalized["asta_id"] == "abc123"
    assert normalized["corpus_id"] == 999
    assert normalized["title"] == "Sample Paper"
    assert normalized["authors"] == ["Alice", "Bob"]
    assert normalized["year"] == 2024
    assert normalized["doi"] == "10.1/a"
    assert normalized["arxiv_id"] == "2101.00001"
    assert normalized["abstract"] == "Abstract text"
    assert normalized["venue"] == "Test Venue"
    assert normalized["tldr"] == "summary"
    assert normalized["is_open_access"] is True
    assert normalized["citation_count"] == 42
    assert normalized["evidence_window"] == adapter.evidence_window_end
    assert isinstance(normalized["retrieved_at"], str)


def test_find_snippets_basic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Snippet search should parse and normalize snippet payload data."""
    monkeypatch.chdir(tmp_path)
    adapter = AstaMCPAdapter(run_id="snippet_test")
    payload = {
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "data": [
                                {
                                    "snippet": "snippet text",
                                    "paperId": "xyz",
                                    "title": "Paper",
                                    "year": 2024,
                                    "score": 0.95,
                                }
                            ]
                        }
                    ),
                }
            ]
        }
    }
    adapter._call_mcp_tool = Mock(return_value=payload)

    snippets = adapter.find_snippets("test query", limit=10)
    assert len(snippets) == 1
    assert snippets[0]["snippet_text"] == "snippet text"
    assert snippets[0]["snippet_source"] == "ASTA_MCP"


def test_get_paper_returns_normalized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """get_paper should return first paper normalized into ELIS schema."""
    monkeypatch.chdir(tmp_path)
    adapter = AstaMCPAdapter(run_id="get_paper_test")
    payload = {
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        [
                            {
                                "paperId": "abc123",
                                "title": "Sample Paper",
                                "authors": [{"name": "Alice"}],
                                "year": 2024,
                                "externalIds": {"DOI": "10.1/a"},
                            }
                        ]
                    ),
                }
            ]
        }
    }
    adapter._call_mcp_tool = Mock(return_value=payload)

    result = adapter.get_paper("DOI:10.1/a")
    assert result is not None
    assert result["source"] == "ASTA_MCP"
    assert "asta_id" in result


def test_get_paper_returns_none_on_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """get_paper should return None when tool response contains no papers."""
    monkeypatch.chdir(tmp_path)
    adapter = AstaMCPAdapter(run_id="get_paper_empty_test")
    adapter._call_mcp_tool = Mock(
        return_value={"result": {"content": [{"type": "text", "text": "[]"}]}}
    )

    result = adapter.get_paper("DOI:10.1/nonexistent")
    assert result is None
