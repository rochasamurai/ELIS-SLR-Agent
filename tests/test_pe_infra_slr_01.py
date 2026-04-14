"""tests/test_pe_infra_slr_01.py — PE-INFRA-SLR-01 acceptance-criteria tests.

Validates the Role-Based Agent Surface Normalisation introduced in AGENTS.md §14
and implemented in ``elis/role_surface.py``.

AC-3: Update tests to validate role-based naming.
"""

from __future__ import annotations

import pytest

from elis.role_surface import (
    ENGINE_SUFFIXES,
    SURFACE_ROLE_MAP,
    is_structured_surface,
    role_from_surface,
)


# ---------------------------------------------------------------------------
# Mapping completeness
# ---------------------------------------------------------------------------


class TestSurfaceRoleMap:
    """SURFACE_ROLE_MAP must cover all canonical surfaces from AGENTS.md §14.2."""

    EXPECTED_SURFACES = [
        "infra-impl-claude",
        "infra-impl-codex",
        "infra-val-claude",
        "infra-val-codex",
        "prog-impl-claude",
        "prog-impl-codex",
        "prog-val-claude",
        "prog-val-codex",
        "slr-impl-claude",
        "slr-impl-codex",
        "slr-val-claude",
        "slr-val-codex",
    ]

    def test_all_canonical_surfaces_present(self):
        for surface in self.EXPECTED_SURFACES:
            assert (
                surface in SURFACE_ROLE_MAP
            ), f"Surface {surface!r} missing from SURFACE_ROLE_MAP"

    def test_no_extra_surfaces(self):
        assert set(SURFACE_ROLE_MAP.keys()) == set(
            self.EXPECTED_SURFACES
        ), "SURFACE_ROLE_MAP contains unexpected surfaces"

    @pytest.mark.parametrize(
        "surface,expected_role",
        [
            ("infra-impl-claude", "infra-impl"),
            ("infra-impl-codex", "infra-impl"),
            ("infra-val-claude", "infra-val"),
            ("infra-val-codex", "infra-val"),
            ("prog-impl-claude", "prog-impl"),
            ("prog-impl-codex", "prog-impl"),
            ("prog-val-claude", "prog-val"),
            ("prog-val-codex", "prog-val"),
            ("slr-impl-claude", "slr-impl"),
            ("slr-impl-codex", "slr-impl"),
            ("slr-val-claude", "slr-val"),
            ("slr-val-codex", "slr-val"),
        ],
    )
    def test_explicit_mapping_values(self, surface: str, expected_role: str):
        assert SURFACE_ROLE_MAP[surface] == expected_role


# ---------------------------------------------------------------------------
# role_from_surface
# ---------------------------------------------------------------------------


class TestRoleFromSurface:
    """role_from_surface resolves surface names to role names."""

    @pytest.mark.parametrize(
        "surface,expected_role",
        [
            ("infra-impl-claude", "infra-impl"),
            ("infra-val-codex", "infra-val"),
            ("prog-impl-codex", "prog-impl"),
            ("prog-val-claude", "prog-val"),
            ("slr-impl-claude", "slr-impl"),
            ("slr-val-codex", "slr-val"),
        ],
    )
    def test_known_surfaces(self, surface: str, expected_role: str):
        assert role_from_surface(surface) == expected_role

    def test_fallback_for_unknown_structured_surface(self):
        """Unlisted but structured surfaces fall back to the derivation rule."""
        assert role_from_surface("slr-val-gemini") == "slr-val"

    def test_unstructured_surface_raises(self):
        """One-off surfaces without an engine suffix raise ValueError."""
        with pytest.raises(ValueError, match="gemini-cli"):
            role_from_surface("gemini-cli")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            role_from_surface("")

    def test_single_token_raises(self):
        with pytest.raises(ValueError):
            role_from_surface("infra")

    def test_same_role_for_both_engines(self):
        """Both engine variants of a surface map to the same role."""
        for prefix in (
            "infra-impl",
            "infra-val",
            "prog-impl",
            "prog-val",
            "slr-impl",
            "slr-val",
        ):
            role_claude = role_from_surface(f"{prefix}-claude")
            role_codex = role_from_surface(f"{prefix}-codex")
            assert role_claude == role_codex == prefix


# ---------------------------------------------------------------------------
# is_structured_surface
# ---------------------------------------------------------------------------


class TestIsStructuredSurface:
    @pytest.mark.parametrize(
        "surface,expected",
        [
            ("infra-impl-claude", True),
            ("infra-val-codex", True),
            ("slr-val-gemini", True),
            ("gemini-cli", False),
            ("codex", False),
            ("", False),
            ("infra-impl", False),
        ],
    )
    def test_structured_detection(self, surface: str, expected: bool):
        assert is_structured_surface(surface) == expected


# ---------------------------------------------------------------------------
# Engine suffixes
# ---------------------------------------------------------------------------


class TestEngineSuffixes:
    def test_canonical_engines_present(self):
        assert "claude" in ENGINE_SUFFIXES
        assert "codex" in ENGINE_SUFFIXES
        assert "gemini" in ENGINE_SUFFIXES

    def test_no_provider_specific_terms_in_role_names(self):
        """Role names must not contain engine suffixes."""
        for role in SURFACE_ROLE_MAP.values():
            parts = role.split("-")
            for engine in ENGINE_SUFFIXES:
                assert (
                    engine not in parts
                ), f"Role name {role!r} contains engine suffix {engine!r}"


# ---------------------------------------------------------------------------
# AGENTS.md section presence (AC-1)
# ---------------------------------------------------------------------------


class TestAgentsMdSection:
    """AGENTS.md must contain the Role-Based Agent Surface Normalisation section."""

    def test_section_14_present(self, tmp_path):
        agents_path = "AGENTS.md"
        content = open(agents_path, encoding="utf-8").read()
        assert (
            "## 14) Role-Based Agent Surface Normalisation" in content
        ), "AGENTS.md is missing §14 Role-Based Agent Surface Normalisation"

    def test_mapping_table_present(self):
        content = open("AGENTS.md", encoding="utf-8").read()
        assert (
            "SURFACE_ROLE_MAP" in content or "14.2" in content
        ), "AGENTS.md §14.2 mapping table not found"

    def test_governance_rules_present(self):
        content = open("AGENTS.md", encoding="utf-8").read()
        assert "14.4" in content, "AGENTS.md §14.4 governance rules not found"
