"""ELIS source adapter registry.

Adapters self-register via the ``@register`` decorator.  Import this
module to ensure all bundled adapters are loaded, then use
``get_adapter(name)`` to retrieve a class by its lowercase source key.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from elis.sources.base import SourceAdapter

_REGISTRY: dict[str, type[SourceAdapter]] = {}


def register(name: str):
    """Class decorator that registers an adapter under *name*."""

    def _decorator(cls: type[SourceAdapter]) -> type[SourceAdapter]:
        _REGISTRY[name] = cls
        return cls

    return _decorator


def get_adapter(name: str) -> type[SourceAdapter]:
    """Return the adapter **class** registered under *name*.

    Raises ``ValueError`` if *name* is not registered.
    """
    _ensure_loaded()
    if name not in _REGISTRY:
        raise ValueError(f"Unknown source: {name!r}. Available: {sorted(_REGISTRY)}")
    return _REGISTRY[name]


def available_sources() -> list[str]:
    """Return sorted list of registered source names."""
    _ensure_loaded()
    return sorted(_REGISTRY)


# ------------------------------------------------------------------
# Lazy import to trigger registration decorators
# ------------------------------------------------------------------

_loaded = False


def _ensure_loaded() -> None:
    global _loaded  # noqa: PLW0603
    if _loaded:
        return
    # Import adapter modules so their @register decorators execute.
    import elis.sources.crossref  # noqa: F401
    import elis.sources.openalex  # noqa: F401

    _loaded = True
