"""ASTA MCP adapter for ELIS SLR Agent.

Policy: ASTA proposes, ELIS decides.
ASTA is used for discovery/evidence support, not as a canonical source.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


class AstaMCPAdapter:
    """Client for the ASTA MCP endpoint with audit logging."""

    def __init__(
        self,
        evidence_window_end: str = "2025-01-31",
        run_id: str | None = None,
        base_url: str = "https://asta-tools.allen.ai/mcp/v1",
    ) -> None:
        self.base_url = base_url
        self.evidence_window_end = evidence_window_end
        self.api_key = os.getenv("ASTA_TOOL_KEY")

        if not self.api_key:
            print("Warning: ASTA_TOOL_KEY not set. Running without API key.")

        self.headers = {"Content-Type": "application/json"}
        # Streamable HTTP MCP servers may require both JSON and SSE accept types.
        self.headers["Accept"] = "application/json, text/event-stream"
        self.headers["MCP-Protocol-Version"] = "2025-03-26"
        if self.api_key:
            self.headers["x-api-key"] = self.api_key

        self.run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.log_dir = Path("runs") / self.run_id / "asta"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.stats: dict[str, int] = {
            "requests": 0,
            "errors": 0,
            "rate_limit_hits": 0,
        }

    def _call_mcp_tool(
        self, tool_name: str, arguments: dict[str, Any], timeout: int = 30
    ) -> dict[str, Any]:
        """Call one ASTA MCP tool with retry-once behavior for HTTP 429."""
        payload = {
            "jsonrpc": "2.0",
            "id": self.stats["requests"] + 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        self._log_request(tool_name, payload)
        self.stats["requests"] += 1

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=timeout,
            )

            if response.status_code == 429:
                self.stats["rate_limit_hits"] += 1
                time.sleep(5)
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=timeout,
                )

            response.raise_for_status()
            result = self._decode_mcp_response(response)
            self._raise_if_mcp_error(result, tool_name)
            self._log_response(tool_name, result)
            return result

        except requests.RequestException as exc:
            self.stats["errors"] += 1
            self._log_error(tool_name, str(exc))
            raise
        except ValueError as exc:
            self.stats["errors"] += 1
            self._log_error(tool_name, str(exc))
            raise

    def search_candidates(
        self, query: str, limit: int = 100, venues: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Discovery mode search for candidate papers."""
        arguments: dict[str, Any] = {
            "keyword": query,
            "fields": (
                "title,abstract,authors,year,url,venue,"
                "fieldsOfStudy,isOpenAccess,journal,publicationDate"
            ),
            "limit": limit,
            "publication_date_range": f"2000-01-01:{self.evidence_window_end}",
        }
        if venues:
            arguments["venues"] = ",".join(venues)

        result = self._call_mcp_tool("search_papers_by_relevance", arguments)
        papers = self._extract_papers_from_mcp(result)
        self._log_normalized("search_candidates", papers)
        return papers

    def _decode_mcp_response(self, response: requests.Response) -> dict[str, Any]:
        """Decode JSON or SSE response into a single MCP JSON object."""
        raw_ct = ""
        if hasattr(response, "headers") and hasattr(response.headers, "get"):
            raw_ct = response.headers.get("content-type") or ""
        content_type = str(raw_ct).lower()
        text = (
            response.text
            if isinstance(response.text, str)
            else str(response.text or "")
        )

        if "application/json" in content_type:
            return response.json()

        if "text/event-stream" in content_type or text.lstrip().startswith("event:"):
            data_lines = []
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("data: "):
                    data_lines.append(line[6:])
            if not data_lines:
                raise ValueError("MCP SSE response missing data payload")
            # Last data frame is the terminal message for this non-streaming usage.
            return json.loads(data_lines[-1])

        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(
            f"Unsupported MCP response format: content-type={content_type!r}"
        )

    def _raise_if_mcp_error(self, payload: dict[str, Any], tool_name: str) -> None:
        """Raise ValueError when MCP returns semantic error payload."""
        if "error" in payload:
            raise ValueError(f"MCP error for {tool_name}: {payload['error']}")

        result = payload.get("result", {})
        if not isinstance(result, dict):
            return
        if result.get("isError"):
            content = result.get("content", [])
            message = ""
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, dict):
                    message = str(first.get("text", "")).strip()
            if not message:
                message = "Unknown MCP tool error"
            raise ValueError(f"MCP tool error for {tool_name}: {message}")

    def _extract_papers_from_mcp(
        self, mcp_response: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Extract paper records from MCP content payload."""
        papers: list[dict[str, Any]] = []
        # JSON-RPC shape: {"result": {"content": [...]}}
        content = mcp_response.get("content")
        if content is None:
            result_obj = mcp_response.get("result", {})
            if isinstance(result_obj, dict):
                content = result_obj.get("content", [])
        if content is None:
            content = []
        if not isinstance(content, list):
            return papers

        for item in content:
            if not isinstance(item, dict) or item.get("type") != "text":
                continue
            text = item.get("text", "")
            if not isinstance(text, str):
                continue
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, list):
                papers.extend([p for p in parsed if isinstance(p, dict)])
            elif isinstance(parsed, dict):
                data = parsed.get("data")
                if isinstance(data, list):
                    papers.extend([p for p in data if isinstance(p, dict)])
                else:
                    papers.append(parsed)
        return papers

    def _normalize_paper(self, asta_paper: dict[str, Any]) -> dict[str, Any]:
        """Normalize one raw ASTA/Semantic Scholar paper into ELIS schema."""
        raw_authors = asta_paper.get("authors", [])
        authors: list[str] = []
        if isinstance(raw_authors, list):
            for author in raw_authors:
                if isinstance(author, dict):
                    name = author.get("name")
                    if isinstance(name, str) and name.strip():
                        authors.append(name.strip())
                elif isinstance(author, str) and author.strip():
                    authors.append(author.strip())

        external_ids = asta_paper.get("externalIds", {})
        doi = None
        arxiv_id = None
        if isinstance(external_ids, dict):
            doi = external_ids.get("DOI")
            arxiv_id = external_ids.get("ArXiv")

        tldr = asta_paper.get("tldr")
        tldr_text = tldr.get("text") if isinstance(tldr, dict) else None

        return {
            "source": "ASTA_MCP",
            "asta_id": asta_paper.get("paperId"),
            "corpus_id": asta_paper.get("corpusId"),
            "title": asta_paper.get("title", ""),
            "authors": authors,
            "year": asta_paper.get("year"),
            "doi": doi,
            "arxiv_id": arxiv_id,
            "abstract": asta_paper.get("abstract", ""),
            "url": asta_paper.get("url", ""),
            "venue": asta_paper.get("venue", ""),
            "publication_date": asta_paper.get("publicationDate"),
            "fields_of_study": asta_paper.get("fieldsOfStudy", []),
            "is_open_access": asta_paper.get("isOpenAccess", False),
            "citation_count": asta_paper.get("citationCount", 0),
            "tldr": tldr_text,
            "retrieved_at": self._utc_now(),
            "evidence_window": self.evidence_window_end,
        }

    def _extract_snippets_from_mcp(
        self, mcp_response: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Extract snippet records from MCP content payload."""
        snippets: list[dict[str, Any]] = []
        content = mcp_response.get("content")
        if content is None:
            result_obj = mcp_response.get("result", {})
            if isinstance(result_obj, dict):
                content = result_obj.get("content", [])
        if content is None or not isinstance(content, list):
            return snippets

        for item in content:
            if not isinstance(item, dict) or item.get("type") != "text":
                continue
            text = item.get("text", "")
            if not isinstance(text, str):
                continue
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, list):
                snippets.extend([s for s in parsed if isinstance(s, dict)])
            elif isinstance(parsed, dict):
                data = parsed.get("data")
                if isinstance(data, list):
                    snippets.extend([s for s in data if isinstance(s, dict)])
                else:
                    snippets.append(parsed)
        return snippets

    def _normalize_snippet(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Normalize one raw snippet record into ELIS evidence shape."""
        return {
            "snippet_text": raw.get("snippet") or raw.get("text", ""),
            "paper_id": raw.get("paperId") or raw.get("paper_id", ""),
            "paper_title": raw.get("title", ""),
            "paper_year": raw.get("year"),
            "paper_doi": raw.get("doi"),
            "score": raw.get("score", 0.0),
            "snippet_source": "ASTA_MCP",
            "retrieved_at": self._utc_now(),
        }

    def find_snippets(
        self,
        query: str,
        paper_ids: list[str] | None = None,
        venues: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Run evidence-mode snippet search and return normalized snippets."""
        arguments: dict[str, Any] = {
            "query": query,
            "limit": min(limit, 250),
            "inserted_before": self.evidence_window_end,
        }
        if paper_ids:
            arguments["paper_ids"] = ",".join(paper_ids[:100])
        if venues:
            arguments["venues"] = ",".join(venues)

        result = self._call_mcp_tool("snippet_search", arguments, timeout=60)
        raw_snippets = self._extract_snippets_from_mcp(result)
        snippets = [self._normalize_snippet(raw) for raw in raw_snippets]
        self._log_normalized("find_snippets", snippets)
        return snippets

    def get_paper(self, paper_id: str) -> dict[str, Any] | None:
        """Fetch and normalize full metadata for a single paper by id."""
        arguments = {
            "paper_id": paper_id,
            "fields": (
                "title,abstract,authors,year,doi,url,venue,publicationDate,"
                "references,citations,fieldsOfStudy,isOpenAccess,citationCount,tldr"
            ),
        }

        try:
            result = self._call_mcp_tool("get_papers", arguments, timeout=15)
        except requests.HTTPError as exc:
            response = getattr(exc, "response", None)
            if response is not None and getattr(response, "status_code", None) == 404:
                return None
            raise

        papers = self._extract_papers_from_mcp(result)
        if not papers:
            return None

        normalized = self._normalize_paper(papers[0])
        self._log_normalized("get_paper", [normalized])
        return normalized

    def _log_request(self, operation: str, payload: dict[str, Any]) -> None:
        self._append_jsonl(
            self.log_dir / "requests.jsonl",
            {"timestamp": self._utc_now(), "operation": operation, "payload": payload},
        )

    def _log_response(self, operation: str, response: dict[str, Any]) -> None:
        self._append_jsonl(
            self.log_dir / "responses.jsonl",
            {
                "timestamp": self._utc_now(),
                "operation": operation,
                "response": response,
            },
        )

    def _log_normalized(self, operation: str, records: list[dict[str, Any]]) -> None:
        self._append_jsonl(
            self.log_dir / "normalized_records.jsonl",
            {
                "timestamp": self._utc_now(),
                "operation": operation,
                "count": len(records),
                "records": records,
            },
        )

    def _log_error(self, operation: str, error: str) -> None:
        self._append_jsonl(
            self.log_dir / "errors.jsonl",
            {"timestamp": self._utc_now(), "operation": operation, "error": error},
        )

    def _append_jsonl(self, path: Path, row: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def get_stats(self) -> dict[str, int]:
        """Return a copy of request/error/rate-limit counters."""
        return dict(self.stats)

    def __repr__(self) -> str:
        return f"AstaMCPAdapter(window={self.evidence_window_end}, run={self.run_id})"
