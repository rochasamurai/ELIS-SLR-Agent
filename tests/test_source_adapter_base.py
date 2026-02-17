"""Tests for the SourceAdapter ABC and adapter registry."""

from __future__ import annotations

import pytest

from elis.sources import available_sources, get_adapter
from elis.sources.base import SourceAdapter


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestRegistry:
    def test_openalex_registered(self) -> None:
        assert "openalex" in available_sources()

    def test_get_adapter_returns_class(self) -> None:
        cls = get_adapter("openalex")
        assert issubclass(cls, SourceAdapter)

    def test_get_adapter_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown source"):
            get_adapter("nonexistent_source")

    def test_available_sources_sorted(self) -> None:
        sources = available_sources()
        assert sources == sorted(sources)


# ---------------------------------------------------------------------------
# ABC contract tests
# ---------------------------------------------------------------------------


class TestSourceAdapterABC:
    def test_cannot_instantiate_abc(self) -> None:
        with pytest.raises(TypeError):
            SourceAdapter()  # type: ignore[abstract]

    def test_concrete_adapter_instantiates(self) -> None:
        cls = get_adapter("openalex")
        adapter = cls()
        assert adapter.source_name == "openalex"
        assert adapter.display_name == "OpenAlex"
