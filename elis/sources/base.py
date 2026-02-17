"""SourceAdapter abstract base class for the ELIS adapter layer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator


class SourceAdapter(ABC):
    """Abstract base for all ELIS harvest source adapters.

    Adapters are pure record generators — ``harvest()`` yields normalised
    dicts that conform to ``schemas/appendix_a_harvester.schema.json``.
    Output writing and cross-query deduplication are handled by the CLI
    layer, not the adapter.
    """

    @abstractmethod
    def preflight(self) -> tuple[bool, str]:
        """Quick connectivity / credential check.

        Returns ``(True, "ok")`` on success or ``(False, "<reason>")``
        on failure.
        """

    @abstractmethod
    def harvest(self, queries: list[str], max_results: int) -> Iterator[dict]:
        """Yield normalised records for *queries*, up to *max_results* total.

        Each yielded dict must contain at least the fields required by
        ``schemas/appendix_a_harvester.schema.json``:
        ``source``, ``title``, ``authors``, ``year``.
        """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Lowercase source identifier, e.g. ``'openalex'``."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable display name, e.g. ``'OpenAlex'``."""
