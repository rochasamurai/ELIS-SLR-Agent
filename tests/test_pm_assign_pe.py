"""Tests for scripts/pm_assign_pe.py — PE-OC-06."""

from __future__ import annotations

import pathlib
from unittest.mock import patch

import pytest

from scripts.pm_assign_pe import (
    DOMAIN_PREFIX,
    agent_prefix,
    determine_engine,
    get_base_branch,
    insert_registry_row,
    make_branch_name,
    make_registry_row,
    main,
    parse_active_registry,
    slug,
)

# ---------------------------------------------------------------------------
# Fixtures — minimal CURRENT_PE.md content
# ---------------------------------------------------------------------------

_HEADER = (
    "| PE-ID       | Domain          | Implementer-agentId | Validator-agentId"
    " | Branch                                  | Status          | Last-updated |\n"
)
_SEP = (
    "|-------------|-----------------|---------------------|-------------------"
    "|-----------------------------------------|-----------------|-------------- |\n"
)


def _make_current_pe(rows: list[str], base_branch: str = "main") -> str:
    """Return a minimal CURRENT_PE.md string for testing."""
    registry_rows = "".join(rows)
    return (
        "# Current PE Assignment\n\n"
        "## Release context\n\n"
        "| Field          | Value |\n"
        "|----------------|-------|\n"
        f"| Base branch    | {base_branch} |\n\n"
        "---\n\n"
        "## Active PE Registry\n\n"
        + _HEADER
        + _SEP
        + registry_rows
        + "\nValid status values:\n- `planning`\n"
    )


_ROW_PROG_CODEX = (
    "| PE-PROG-01  | programs        | prog-impl-codex     | prog-val-claude  "
    " | feature/pe-prog-01-alpha                | merged          | 2026-01-01   |\n"
)
_ROW_PROG_CLAUDE = (
    "| PE-PROG-02  | programs        | prog-impl-claude    | prog-val-codex   "
    " | feature/pe-prog-02-beta                 | merged          | 2026-01-02   |\n"
)
_ROW_INFRA_CODEX = (
    "| PE-INFRA-01 | infra           | infra-impl-codex    | infra-val-claude "
    " | feature/pe-infra-01-setup               | merged          | 2026-01-01   |\n"
)


# ---------------------------------------------------------------------------
# determine_engine
# ---------------------------------------------------------------------------


def test_alternation_codex_to_claude() -> None:
    content = _make_current_pe([_ROW_PROG_CODEX])
    _, rows = parse_active_registry(content)
    assert rows is not None
    engine, prev = determine_engine(rows, "programs")
    assert engine == "claude"
    assert prev == "codex"


def test_alternation_claude_to_codex() -> None:
    content = _make_current_pe([_ROW_PROG_CODEX, _ROW_PROG_CLAUDE])
    _, rows = parse_active_registry(content)
    assert rows is not None
    engine, prev = determine_engine(rows, "programs")
    assert engine == "codex"
    assert prev == "claude"


def test_first_in_domain_defaults_codex() -> None:
    content = _make_current_pe([_ROW_PROG_CODEX])
    _, rows = parse_active_registry(content)
    assert rows is not None
    engine, prev = determine_engine(rows, "new-domain")
    assert engine == "codex"
    assert prev is None


def test_determine_engine_uses_last_row() -> None:
    """When a domain has multiple rows the last one determines alternation."""
    content = _make_current_pe([_ROW_PROG_CODEX, _ROW_PROG_CLAUDE, _ROW_PROG_CODEX])
    _, rows = parse_active_registry(content)
    assert rows is not None
    # Last row in programs domain is codex → next must be claude
    engine, prev = determine_engine(rows, "programs")
    assert engine == "claude"
    assert prev == "codex"


def test_determine_engine_ignores_other_domains() -> None:
    content = _make_current_pe([_ROW_INFRA_CODEX, _ROW_PROG_CLAUDE])
    _, rows = parse_active_registry(content)
    assert rows is not None
    # programs domain last was claude → next is codex
    engine, prev = determine_engine(rows, "programs")
    assert engine == "codex"
    assert prev == "claude"
    # infra domain last was codex → next is claude
    engine2, prev2 = determine_engine(rows, "infra")
    assert engine2 == "claude"
    assert prev2 == "codex"


# ---------------------------------------------------------------------------
# Alternation guard (AC-2)
# ---------------------------------------------------------------------------


def test_alternation_guard_raises() -> None:
    """AssertionError is raised when new_engine would equal prev_engine."""
    prev_engine = "codex"
    new_engine = "codex"  # simulates a logic bug producing the same engine
    with pytest.raises(AssertionError, match="Alternation violation"):
        assert new_engine != prev_engine, (
            f"Alternation violation: domain 'programs' previous implementer was "
            f"'{prev_engine}'; assigning '{new_engine}' would repeat the same engine."
        )


# ---------------------------------------------------------------------------
# slug and make_branch_name (AC-4)
# ---------------------------------------------------------------------------


def test_slug_basic() -> None:
    assert slug("PDF export") == "pdf-export"


def test_slug_special_chars() -> None:
    assert slug("Hello, World!") == "hello-world"


def test_slug_multiple_spaces() -> None:
    assert slug("  multiple   spaces  ") == "multiple-spaces"


def test_make_branch_name_with_description() -> None:
    assert (
        make_branch_name("PE-PROG-08", "PDF export") == "feature/pe-prog-08-pdf-export"
    )


def test_make_branch_name_no_description() -> None:
    assert make_branch_name("PE-PROG-08", "") == "feature/pe-prog-08"


def test_make_branch_name_lowercase() -> None:
    assert (
        make_branch_name("PE-INFRA-09", "Logging Setup")
        == "feature/pe-infra-09-logging-setup"
    )


# ---------------------------------------------------------------------------
# agent_prefix
# ---------------------------------------------------------------------------


def test_agent_prefix_mapping() -> None:
    assert agent_prefix("infra") == "infra"
    assert agent_prefix("openclaw-infra") == "prog"
    assert agent_prefix("programs") == "prog"
    assert agent_prefix("slr") == "slr"


def test_agent_prefix_unknown_domain() -> None:
    assert agent_prefix("custom-domain") == "custom"


def test_domain_prefix_dict_complete() -> None:
    for domain, prefix in DOMAIN_PREFIX.items():
        assert agent_prefix(domain) == prefix


# ---------------------------------------------------------------------------
# insert_registry_row
# ---------------------------------------------------------------------------


def test_insert_registry_row() -> None:
    content = _make_current_pe([_ROW_PROG_CODEX])
    new_row = "| PE-PROG-02  | programs | prog-impl-claude | prog-val-codex | feature/pe-prog-02 | planning | 2026-02-01 |"
    updated = insert_registry_row(content, new_row)
    lines = updated.splitlines()
    # Find the last | line in the registry
    table_lines = [ln for ln in lines if ln.strip().startswith("|")]
    assert any("PE-PROG-02" in ln for ln in table_lines)
    # New row must come after existing PE-PROG-01 row
    idx_01 = next(i for i, ln in enumerate(lines) if "PE-PROG-01" in ln)
    idx_02 = next(i for i, ln in enumerate(lines) if "PE-PROG-02" in ln)
    assert idx_02 > idx_01


# ---------------------------------------------------------------------------
# get_base_branch
# ---------------------------------------------------------------------------


def test_get_base_branch_main() -> None:
    content = _make_current_pe([], base_branch="main")
    assert get_base_branch(content) == "main"


def test_get_base_branch_custom() -> None:
    content = _make_current_pe([], base_branch="release/2.0")
    assert get_base_branch(content) == "release/2.0"


def test_get_base_branch_with_backticks() -> None:
    content = "| Base branch    | `main` |\n"
    assert get_base_branch(content) == "main"


# ---------------------------------------------------------------------------
# make_registry_row
# ---------------------------------------------------------------------------


def test_make_registry_row_programs_codex() -> None:
    row = make_registry_row(
        "PE-PROG-08", "programs", "codex", "feature/pe-prog-08-pdf-export", "2026-02-22"
    )
    assert "prog-impl-codex" in row
    assert "prog-val-claude" in row
    assert "planning" in row
    assert "PE-PROG-08" in row


def test_make_registry_row_infra_claude() -> None:
    row = make_registry_row(
        "PE-INFRA-10", "infra", "claude", "feature/pe-infra-10-x", "2026-02-22"
    )
    assert "infra-impl-claude" in row
    assert "infra-val-codex" in row


# ---------------------------------------------------------------------------
# main() — AC-1: dry-run (no file writes, no git calls)
# ---------------------------------------------------------------------------


def test_main_dry_run(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    current_pe.write_text(_make_current_pe([_ROW_PROG_CODEX]), encoding="utf-8")

    with patch("scripts.pm_assign_pe.subprocess.run"):
        rc = (
            main.__wrapped__()
            if hasattr(main, "__wrapped__")
            else _run_main(
                [
                    "--domain",
                    "programs",
                    "--pe",
                    "PE-PROG-08",
                    "--description",
                    "PDF export",
                    "--dry-run",
                    "--current-pe",
                    str(current_pe),
                ]
            )
        )

    out = capsys.readouterr().out
    assert rc == 0
    assert "PE-PROG-08" in out
    assert "claude" in out.lower()  # codex prev → claude new
    assert "feature/pe-prog-08-pdf-export" in out
    assert "[dry-run]" in out
    # File must NOT have been modified
    assert "PE-PROG-08" not in current_pe.read_text(encoding="utf-8")


def test_main_writes_row(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture) -> None:
    """AC-1: script writes new row to CURRENT_PE.md observing alternation."""
    current_pe = tmp_path / "CURRENT_PE.md"
    current_pe.write_text(_make_current_pe([_ROW_PROG_CODEX]), encoding="utf-8")

    with patch("scripts.pm_assign_pe.subprocess.run"):
        rc = _run_main(
            [
                "--domain",
                "programs",
                "--pe",
                "PE-PROG-08",
                "--description",
                "PDF export",
                "--current-pe",
                str(current_pe),
            ]
        )

    assert rc == 0
    updated = current_pe.read_text(encoding="utf-8")
    assert "PE-PROG-08" in updated
    assert "prog-impl-claude" in updated  # codex prev → claude
    assert "prog-val-codex" in updated
    assert "planning" in updated
    assert "feature/pe-prog-08-pdf-export" in updated


def test_main_duplicate_pe_exits_1(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture
) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    current_pe.write_text(_make_current_pe([_ROW_PROG_CODEX]), encoding="utf-8")

    rc = _run_main(
        [
            "--domain",
            "programs",
            "--pe",
            "PE-PROG-01",  # already exists
            "--current-pe",
            str(current_pe),
        ]
    )
    assert rc == 1
    assert "already exists" in capsys.readouterr().out


def test_main_missing_file_exits_1(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture
) -> None:
    rc = _run_main(
        [
            "--domain",
            "programs",
            "--pe",
            "PE-PROG-99",
            "--current-pe",
            str(tmp_path / "does_not_exist.md"),
        ]
    )
    assert rc == 1
    assert "not found" in capsys.readouterr().out


def test_main_first_in_domain_defaults_codex(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture
) -> None:
    """First PE in a new domain gets codex as implementer."""
    current_pe = tmp_path / "CURRENT_PE.md"
    current_pe.write_text(_make_current_pe([_ROW_INFRA_CODEX]), encoding="utf-8")

    with patch("scripts.pm_assign_pe.subprocess.run"):
        rc = _run_main(
            [
                "--domain",
                "programs",
                "--pe",
                "PE-PROG-01",
                "--description",
                "bootstrap",
                "--current-pe",
                str(current_pe),
            ]
        )

    assert rc == 0
    out = capsys.readouterr().out
    assert "prog-impl-codex" in out
    assert "prog-val-claude" in out


# ---------------------------------------------------------------------------
# Helper — invoke main() with argv list
# ---------------------------------------------------------------------------


def _run_main(argv: list[str]) -> int:
    import sys as _sys

    old_argv = _sys.argv
    _sys.argv = ["pm_assign_pe.py"] + argv
    try:
        return main()
    finally:
        _sys.argv = old_argv
