"""Scopus source adapter for the ELIS adapter layer.

Ported from ``scripts/scopus_harvest.py``.  Scopus uses offset-based
pagination, requires ``SCOPUS_API_KEY`` + ``SCOPUS_INST_TOKEN`` env vars,
wraps queries in ``TITLE-ABS-KEY()``, and returns the first author only
via ``dc:creator``.
"""

from __future__ import annotations

import logging
import os
from typing import Iterator

from elis.sources import register
from elis.sources.base import SourceAdapter
from elis.sources.http_client import ELISHttpClient

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.elsevier.com/content/search/scopus"
_COUNT_PER_PAGE = 25  # API maximum


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def _get_auth_headers() -> dict[str, str]:
    """Build Scopus API auth headers from environment variables.

    Raises ``EnvironmentError`` if credentials are missing.
    """
    api_key = os.getenv("SCOPUS_API_KEY")
    inst_token = os.getenv("SCOPUS_INST_TOKEN")
    if not api_key or not inst_token:
        raise EnvironmentError(
            "Missing SCOPUS_API_KEY or SCOPUS_INST_TOKEN environment variables"
        )
    return {
        "X-ELS-APIKey": api_key,
        "X-ELS-Insttoken": inst_token,
        "Accept": "application/json",
    }


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------


def transform_entry(entry: dict) -> dict:
    """Transform a raw Scopus search result into the harvester schema.

    Handles:
    - ``dc:identifier`` with ``SCOPUS_ID:`` prefix stripping
    - ``dc:creator`` as single-author string → list
    - Year from ``prism:coverDate`` (``YYYY-MM-DD``)
    - DOI from ``prism:doi``
    - Abstract from ``dc:description``
    """
    # Scopus ID — strip SCOPUS_ID: prefix
    dc_identifier = entry.get("dc:identifier", "") or ""
    scopus_id = dc_identifier.replace("SCOPUS_ID:", "") if dc_identifier else ""

    # Authors — Scopus search API returns dc:creator as string (first author only)
    creator = entry.get("dc:creator", "") or ""
    authors = [creator] if creator else []

    # Year from prism:coverDate (e.g. "2026-01-01")
    year: int | None = None
    cover_date = entry.get("prism:coverDate", "") or ""
    if cover_date and len(cover_date) >= 4:
        try:
            year = int(cover_date[:4])
        except (ValueError, TypeError):
            year = None

    # Citation count
    citation_count = entry.get("citedby-count")
    if citation_count is not None:
        try:
            citation_count = int(citation_count)
        except (ValueError, TypeError):
            citation_count = 0
    else:
        citation_count = 0

    return {
        "source": "Scopus",
        "title": entry.get("dc:title", "") or "",
        "authors": authors,
        "year": year,
        "doi": entry.get("prism:doi", "") or "",
        "abstract": entry.get("dc:description", "") or "",
        "url": entry.get("prism:url", "") or "",
        "scopus_id": scopus_id,
        "citation_count": citation_count,
        "raw_metadata": entry,
    }


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


@register("scopus")
class ScopusAdapter(SourceAdapter):
    """Adapter for the Elsevier Scopus API."""

    @property
    def source_name(self) -> str:
        return "scopus"

    @property
    def display_name(self) -> str:
        return "Scopus"

    def preflight(self) -> tuple[bool, str]:
        """Check that Scopus API credentials are set and the API is reachable."""
        try:
            headers = _get_auth_headers()
        except EnvironmentError as exc:
            return False, str(exc)

        client = self._make_client()
        try:
            resp = client.get(
                _BASE_URL,
                params={"query": "TITLE-ABS-KEY(test)", "count": 1},
                headers=headers,
            )
            if resp.status_code == 200:
                return True, "ok"
            return False, f"HTTP {resp.status_code}"  # pragma: no cover
        except Exception as exc:
            return False, str(exc)

    def harvest(self, queries: list[str], max_results: int) -> Iterator[dict]:
        """Yield normalised records from Scopus for *queries*."""
        try:
            headers = _get_auth_headers()
        except EnvironmentError:
            logger.warning("[Scopus] Missing credentials — skipping harvest")
            return

        client = self._make_client()
        for query in queries:
            yield from self._search(client, query, max_results, headers)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_client() -> ELISHttpClient:
        return ELISHttpClient("Scopus", delay_seconds=0.5)

    @staticmethod
    def _search(
        client: ELISHttpClient,
        query: str,
        max_results: int,
        headers: dict[str, str],
    ) -> Iterator[dict]:
        """Page through Scopus results via offset and yield records."""
        start = 0
        fetched = 0

        while fetched < max_results:
            count = min(_COUNT_PER_PAGE, max_results - fetched)
            params: dict[str, object] = {
                "query": query,
                "count": count,
                "start": start,
            }

            try:
                resp = client.get(_BASE_URL, params=params, headers=headers)
            except Exception:
                logger.warning("[Scopus] Request failed — stopping pagination")
                return

            data = resp.json()
            entries = data.get("search-results", {}).get("entry", [])
            if not entries:
                return

            for entry in entries:
                yield transform_entry(entry)
                fetched += 1
                if fetched >= max_results:
                    return

            start += len(entries)

            # Check total available
            total_str = data.get("search-results", {}).get(
                "opensearch:totalResults", "0"
            )
            try:
                total = int(total_str)
            except (ValueError, TypeError):
                total = 0
            if start >= total:
                return

            client.polite_wait()
