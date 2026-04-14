"""role_surface.py — Role-Based Agent Surface Normalisation helpers.

Implements the surface-to-role mapping defined in AGENTS.md §14.
A *workflow surface name* (agentId) encodes both the role and the engine,
e.g. ``infra-impl-claude``.  The *role name* is the provider-neutral part,
e.g. ``infra-impl``.

Usage::

    from elis.role_surface import role_from_surface, SURFACE_ROLE_MAP

    role_from_surface("infra-val-codex")   # -> "infra-val"
    role_from_surface("prog-impl-claude")  # -> "prog-impl"
"""

from __future__ import annotations

# Canonical mapping of workflow surface names to role names.
# Source of truth: AGENTS.md §14.2.
SURFACE_ROLE_MAP: dict[str, str] = {
    "infra-impl-claude": "infra-impl",
    "infra-impl-codex": "infra-impl",
    "infra-val-claude": "infra-val",
    "infra-val-codex": "infra-val",
    "prog-impl-claude": "prog-impl",
    "prog-impl-codex": "prog-impl",
    "prog-val-claude": "prog-val",
    "prog-val-codex": "prog-val",
    "slr-impl-claude": "slr-impl",
    "slr-impl-codex": "slr-impl",
    "slr-val-claude": "slr-val",
    "slr-val-codex": "slr-val",
}

# Known engine suffixes.
ENGINE_SUFFIXES: frozenset[str] = frozenset({"claude", "codex", "gemini"})


def role_from_surface(surface: str) -> str:
    """Return the role name for *surface*.

    Uses the explicit mapping table first.  For structured surfaces not yet
    listed in the table, falls back to stripping the trailing engine suffix
    (AGENTS.md §14.3).

    Raises ``ValueError`` for unrecognised or unstructured surfaces (e.g.
    ``gemini-cli``).
    """
    if surface in SURFACE_ROLE_MAP:
        return SURFACE_ROLE_MAP[surface]

    parts = surface.split("-")
    if len(parts) >= 2 and parts[-1] in ENGINE_SUFFIXES:
        return "-".join(parts[:-1])

    raise ValueError(
        f"Cannot derive role from surface name {surface!r}. "
        "One-off surfaces such as 'gemini-cli' have no structured role mapping."
    )


def is_structured_surface(surface: str) -> bool:
    """Return True if *surface* follows the ``<role>-<engine>`` convention."""
    parts = surface.split("-")
    return len(parts) >= 2 and parts[-1] in ENGINE_SUFFIXES
