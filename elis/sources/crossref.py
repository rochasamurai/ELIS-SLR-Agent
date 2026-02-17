"""CrossRef source adapter for the ELIS adapter layer.

Ported from ``scripts/crossref_harvest.py``.  CrossRef uses offset-based
pagination, optional polite-pool via ``ELIS_CONTACT`` env var, returns
titles as single-element arrays, and uses an uppercase ``DOI`` key.
"""

from __future__ import annotations

import logging
import os
from typing import Iterator

from elis.sources import register
from elis.sources.base import SourceAdapter
from elis.sources.http_client import ELISHttpClient

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.crossref.org/works"
_ROWS_PER_REQUEST = 1000  # API maximum


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------


def transform_entry(entry: dict) -> dict:
    """Transform a raw CrossRef work record into the harvester schema.

    Handles:
    - Title as array → take first element
    - DOI from uppercase ``DOI`` key
    - Authors from ``given`` + ``family`` fields
    - Year from ``published-print`` or ``published-online`` date-parts
    - Abstract as plain string (may contain JATS XML tags)
    """
    # Title — CrossRef returns as a list
    title_list = entry.get("title", [])
    title = title_list[0] if title_list else ""

    # Authors
    authors = [
        f"{a.get('given', '')} {a.get('family', '')}".strip()
        for a in entry.get("author", [])
        if a.get("family")
    ]

    # Year — prefer published-print, fall back to published-online
    year: int | None = None
    published = entry.get("published-print") or entry.get("published-online")
    if published:
        date_parts = published.get("date-parts", [[]])
        if date_parts and date_parts[0]:
            try:
                year = int(date_parts[0][0])
            except (ValueError, TypeError):
                year = None

    # Abstract
    abstract = entry.get("abstract", "") or ""

    # Citation count — CrossRef uses "is-referenced-by-count"
    citation_count = entry.get("is-referenced-by-count")
    if citation_count is None:
        citation_count = 0

    return {
        "source": "CrossRef",
        "title": title or "",
        "authors": authors,
        "year": year,
        "doi": entry.get("DOI", "") or "",
        "abstract": abstract,
        "url": entry.get("URL", "") or "",
        "crossref_id": entry.get("DOI", "") or "",
        "crossref_type": entry.get("type", "") or "",
        "publisher": entry.get("publisher", "") or "",
        "citation_count": citation_count,
        "raw_metadata": entry,
    }


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


@register("crossref")
class CrossRefAdapter(SourceAdapter):
    """Adapter for the CrossRef API (``https://api.crossref.org``)."""

    @property
    def source_name(self) -> str:
        return "crossref"

    @property
    def display_name(self) -> str:
        return "CrossRef"

    def preflight(self) -> tuple[bool, str]:
        """Check that the CrossRef API is reachable."""
        client = self._make_client()
        try:
            resp = client.get(
                _BASE_URL,
                params={"query": "test", "rows": 1},
            )
            if resp.status_code == 200:
                return True, "ok"
            return False, f"HTTP {resp.status_code}"  # pragma: no cover
        except Exception as exc:
            return False, str(exc)

    def harvest(self, queries: list[str], max_results: int) -> Iterator[dict]:
        """Yield normalised records from CrossRef for *queries*."""
        client = self._make_client()
        mailto = os.getenv("ELIS_CONTACT")

        for query in queries:
            yield from self._search(client, query, max_results, mailto)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_client() -> ELISHttpClient:
        return ELISHttpClient("CrossRef", delay_seconds=0.5)

    @staticmethod
    def _search(
        client: ELISHttpClient,
        query: str,
        max_results: int,
        mailto: str | None,
    ) -> Iterator[dict]:
        """Page through CrossRef results via offset and yield records."""
        offset = 0
        fetched = 0

        while fetched < max_results:
            rows = min(_ROWS_PER_REQUEST, max_results - fetched)
            params: dict[str, object] = {
                "query": query,
                "rows": rows,
                "offset": offset,
            }
            if mailto:
                params["mailto"] = mailto

            try:
                resp = client.get(_BASE_URL, params=params)
            except Exception:
                logger.warning("[CrossRef] Request failed — stopping pagination")
                return

            data = resp.json()
            message = data.get("message", {})
            items = message.get("items", [])
            if not items:
                return

            for entry in items:
                yield transform_entry(entry)
                fetched += 1
                if fetched >= max_results:
                    return

            offset += len(items)

            # Check if we've exhausted available results
            total = message.get("total-results", 0)
            if offset >= total:
                return

            client.polite_wait()
