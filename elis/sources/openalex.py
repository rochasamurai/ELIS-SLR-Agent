"""OpenAlex source adapter for the ELIS adapter layer.

Ported from ``scripts/openalex_harvest.py``.  OpenAlex uses page-based
pagination, optional polite-pool via ``ELIS_CONTACT`` env var, and stores
abstracts as inverted indices that must be reconstructed.
"""

from __future__ import annotations

import logging
import os
from typing import Iterator

from elis.sources import register
from elis.sources.base import SourceAdapter
from elis.sources.http_client import ELISHttpClient

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.openalex.org/works"
_PER_PAGE = 200  # API maximum


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------


def _reconstruct_abstract(inverted_index: dict[str, list[int]]) -> str:
    """Reconstruct plain-text abstract from OpenAlex inverted index."""
    if not inverted_index:
        return ""
    words: dict[int, str] = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words[i] for i in sorted(words))


def transform_entry(entry: dict) -> dict:
    """Transform a raw OpenAlex work record into the harvester schema.

    Handles:
    - DOI prefix stripping (``https://doi.org/…``)
    - Abstract inverted-index reconstruction
    - Authors from ``authorships`` array
    - Year as ``int | None``
    - Citation count defaulting to ``0``
    """
    # Authors
    authors = [
        a.get("author", {}).get("display_name", "")
        for a in entry.get("authorships", [])
        if a.get("author", {}).get("display_name")
    ]

    # Year
    year_raw = entry.get("publication_year")
    year: int | None = None
    if year_raw is not None:
        try:
            year = int(year_raw)
        except (ValueError, TypeError):
            year = None

    # DOI — strip URL prefix
    doi = entry.get("doi", "") or ""
    for prefix in ("https://doi.org/", "http://doi.org/"):
        if doi.startswith(prefix):
            doi = doi[len(prefix) :]
            break

    # Abstract
    abstract = _reconstruct_abstract(entry.get("abstract_inverted_index") or {})

    # Citation count — always int
    citation_count = entry.get("cited_by_count")
    if citation_count is None:
        citation_count = 0

    return {
        "source": "OpenAlex",
        "title": entry.get("title", "") or "",
        "authors": authors,
        "year": year,
        "doi": doi,
        "abstract": abstract,
        "url": entry.get("doi", "") or entry.get("id", "") or "",
        "openalex_id": entry.get("id", "") or "",
        "citation_count": citation_count,
        "raw_metadata": entry,
    }


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


@register("openalex")
class OpenAlexAdapter(SourceAdapter):
    """Adapter for the OpenAlex API (``https://api.openalex.org``)."""

    @property
    def source_name(self) -> str:
        return "openalex"

    @property
    def display_name(self) -> str:
        return "OpenAlex"

    def preflight(self) -> tuple[bool, str]:
        """Check that the OpenAlex API is reachable."""
        client = self._make_client()
        try:
            resp = client.get(
                _BASE_URL,
                params={"filter": "default.search:test", "per_page": 1},
            )
            if resp.status_code == 200:
                return True, "ok"
            return False, f"HTTP {resp.status_code}"  # pragma: no cover
        except Exception as exc:
            return False, str(exc)

    def harvest(self, queries: list[str], max_results: int) -> Iterator[dict]:
        """Yield normalised records from OpenAlex for *queries*."""
        client = self._make_client()
        mailto = os.getenv("ELIS_CONTACT")

        for query in queries:
            yield from self._search(client, query, max_results, mailto)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_client() -> ELISHttpClient:
        return ELISHttpClient("OpenAlex", delay_seconds=0.1)

    @staticmethod
    def _search(
        client: ELISHttpClient,
        query: str,
        max_results: int,
        mailto: str | None,
    ) -> Iterator[dict]:
        """Page through OpenAlex results and yield transformed records."""
        page = 1
        fetched = 0

        while fetched < max_results:
            per_page = min(_PER_PAGE, max_results - fetched)
            params: dict[str, object] = {
                "filter": f"default.search:{query}",
                "per_page": per_page,
                "page": page,
            }
            if mailto:
                params["mailto"] = mailto

            try:
                resp = client.get(_BASE_URL, params=params)
            except Exception:
                logger.warning("[OpenAlex] Request failed — stopping pagination")
                return

            data = resp.json()
            works = data.get("results", [])
            if not works:
                return

            for entry in works:
                yield transform_entry(entry)
                fetched += 1
                if fetched >= max_results:
                    return

            # Check total available
            total = data.get("meta", {}).get("count", 0)
            if fetched >= total:
                return

            page += 1
            client.polite_wait()
