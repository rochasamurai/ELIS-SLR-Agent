"""role_surface.py — Role-Based Agent Surface Normalisation helpers.

Implements the surface-to-role mapping defined in AGENTS.md §14.
A *workflow surface name* (agentId) encodes both the role and the slot,
e.g. ``infra-impl-a``. The *role name* is the provider-neutral part,
e.g. ``infra-impl``.

Usage::

    from elis.role_surface import role_from_surface, SURFACE_ROLE_MAP

    role_from_surface("infra-val-a")  # -> "infra-val"
    role_from_surface("prog-impl-b")  # -> "prog-impl"
"""

from __future__ import annotations

from elis.agent_id import canonical_agent_id, is_structured_agent_id, role_from_agent_id

# Canonical mapping of workflow surface names to role names.
# Source of truth: AGENTS.md §14.2.
SURFACE_ROLE_MAP: dict[str, str] = {
    "infra-impl-a": "infra-impl",
    "infra-impl-b": "infra-impl",
    "infra-val-a": "infra-val",
    "infra-val-b": "infra-val",
    "prog-impl-a": "prog-impl",
    "prog-impl-b": "prog-impl",
    "prog-val-a": "prog-val",
    "prog-val-b": "prog-val",
    "slr-impl-a": "slr-impl",
    "slr-impl-b": "slr-impl",
    "slr-val-a": "slr-val",
    "slr-val-b": "slr-val",
}

SLOT_SUFFIXES: frozenset[str] = frozenset({"a", "b", "c"})
ENGINE_SUFFIXES = SLOT_SUFFIXES


def role_from_surface(surface: str) -> str:
    """Return the role name for *surface*.

    Uses the explicit mapping table first. For structured surfaces not yet
    listed in the table, falls back to stripping the trailing slot suffix
    (AGENTS.md §14.3). Legacy model-coupled identifiers are normalised through
    the compatibility map before role derivation.

    Raises ``ValueError`` for unrecognised or unstructured surfaces (e.g.
    ``gemini-cli``).
    """
    canonical = canonical_agent_id(surface)
    if canonical in SURFACE_ROLE_MAP:
        return SURFACE_ROLE_MAP[canonical]
    try:
        return role_from_agent_id(canonical)
    except ValueError as exc:
        raise ValueError(
            f"Cannot derive role from surface name {surface!r}. "
            "One-off surfaces such as 'gemini-cli' have no structured role mapping."
        ) from exc


def is_structured_surface(surface: str) -> bool:
    """Return True if *surface* follows the ``<role>-<slot>`` convention."""
    return is_structured_agent_id(surface)
