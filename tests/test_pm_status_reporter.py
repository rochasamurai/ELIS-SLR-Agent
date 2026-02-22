"""Tests for scripts/pm_status_reporter.py (PE-OC-08)."""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

import pytest

from scripts.pm_status_reporter import (
    _engine_display,
    build_escalation_message,
    format_status_response,
    handle_escalate,
    load_registry,
    main,
    parse_active_registry,
)

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

_REGISTRY_CONTENT = """\
# Current PE Assignment

## Active PE Registry

| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |
|---|---|---|---|---|---|---|
| PE-OC-07 | openclaw-infra | prog-impl-codex | prog-val-claude | feature/pe-oc-07-gate-automation | merged | 2026-02-01 |
| PE-OC-08 | openclaw-infra | prog-impl-claude | prog-val-codex | feature/pe-oc-08-po-status-reporting | implementing | 2026-02-20 |
| PE-OC-09 | openclaw-infra | prog-impl-codex | prog-val-claude | feature/pe-oc-09-e2e-programs | gate-1-pending | 2026-02-21 |
"""


def _make_registry_file(tmp_path: Path, content: str = _REGISTRY_CONTENT) -> Path:
    p = tmp_path / "CURRENT_PE.md"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# parse_active_registry
# ---------------------------------------------------------------------------


def test_parse_active_registry_returns_rows() -> None:
    _, rows = parse_active_registry(_REGISTRY_CONTENT)
    assert rows is not None
    assert len(rows) == 3
    assert rows[0]["pe-id"] == "PE-OC-07"


def test_parse_active_registry_missing_section_returns_none() -> None:
    _, rows = parse_active_registry("# No registry here\n")
    assert rows is None


# ---------------------------------------------------------------------------
# _engine_display
# ---------------------------------------------------------------------------


def test_engine_display_codex() -> None:
    assert _engine_display("prog-impl-codex") == "CODEX"


def test_engine_display_claude() -> None:
    assert _engine_display("infra-val-claude") == "Claude Code"


def test_engine_display_unknown_passthrough() -> None:
    assert _engine_display("mystery-agent") == "mystery-agent"


# ---------------------------------------------------------------------------
# format_status_response (AC-1)
# ---------------------------------------------------------------------------


def test_status_format_excludes_merged() -> None:
    _, rows = parse_active_registry(_REGISTRY_CONTENT)
    result = format_status_response(rows, datetime.date(2026, 2, 22))
    assert "PE-OC-07" not in result
    assert "PE-OC-08" in result
    assert "PE-OC-09" in result


def test_status_format_hides_agent_ids() -> None:
    _, rows = parse_active_registry(_REGISTRY_CONTENT)
    result = format_status_response(rows, datetime.date(2026, 2, 22))
    assert "prog-impl-claude" not in result
    assert "prog-impl-codex" not in result
    assert "Claude Code" in result or "CODEX" in result


def test_status_format_contains_required_fields() -> None:
    _, rows = parse_active_registry(_REGISTRY_CONTENT)
    result = format_status_response(rows, datetime.date(2026, 2, 22))
    assert "Active PEs" in result
    assert "PEs active" in result
    assert "merged this week" in result


def test_status_format_active_count() -> None:
    _, rows = parse_active_registry(_REGISTRY_CONTENT)
    result = format_status_response(rows, datetime.date(2026, 2, 22))
    # 2 active PEs (PE-OC-08 implementing, PE-OC-09 gate-1-pending)
    assert "2 PEs active" in result


def test_status_format_merged_this_week_count() -> None:
    _, rows = parse_active_registry(_REGISTRY_CONTENT)
    # PE-OC-07 merged 2026-02-01, now is 2026-02-22 — 21 days ago → not this week
    result = format_status_response(rows, datetime.date(2026, 2, 22))
    assert "0 merged this week" in result


def test_status_format_merged_this_week_positive() -> None:
    content = """\
# Current PE Assignment

## Active PE Registry

| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |
|---|---|---|---|---|---|---|
| PE-OC-07 | openclaw-infra | prog-impl-codex | prog-val-claude | feature/x | merged | 2026-02-20 |
| PE-OC-08 | openclaw-infra | prog-impl-claude | prog-val-codex | feature/y | planning | 2026-02-22 |
"""
    _, rows = parse_active_registry(content)
    # 2026-02-22, PE-OC-07 merged 2026-02-20 (2 days ago) → within 7-day window
    result = format_status_response(rows, datetime.date(2026, 2, 22))
    assert "1 merged this week" in result


def test_status_format_no_active_pes() -> None:
    content = """\
# Current PE Assignment

## Active PE Registry

| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |
|---|---|---|---|---|---|---|
| PE-OC-07 | openclaw-infra | prog-impl-codex | prog-val-claude | feature/x | merged | 2026-02-20 |
"""
    _, rows = parse_active_registry(content)
    result = format_status_response(rows, datetime.date(2026, 2, 22))
    assert "no active PEs" in result
    assert "0 PEs active" in result


# ---------------------------------------------------------------------------
# build_escalation_message
# ---------------------------------------------------------------------------


def test_build_escalation_message_format() -> None:
    msg = build_escalation_message(
        pe_id="PE-OC-08",
        blocker="Test blocker",
        status="implementing",
        iteration_count=2,
        options=[("Option one", "trade-off one"), ("Option two", "trade-off two")],
        recommendation="A — rationale",
    )
    assert "PE-OC-08" in msg
    assert "Test blocker" in msg
    assert "implementing" in msg
    assert "Iteration count: 2" in msg
    assert "A. Option one" in msg
    assert "B. Option two" in msg
    assert "PM recommendation: A — rationale" in msg


# ---------------------------------------------------------------------------
# handle_escalate (AC-5)
# ---------------------------------------------------------------------------


def test_handle_escalate_known_pe() -> None:
    _, rows = parse_active_registry(_REGISTRY_CONTENT)
    result = handle_escalate("PE-OC-08", rows)
    assert "PE-OC-08" in result
    assert "implementing" in result
    assert "PM recommendation" in result


def test_handle_escalate_unknown_pe() -> None:
    _, rows = parse_active_registry(_REGISTRY_CONTENT)
    result = handle_escalate("PE-OC-99", rows)
    assert "PE-OC-99" in result
    assert "not found" in result.lower()


def test_handle_escalate_case_insensitive() -> None:
    _, rows = parse_active_registry(_REGISTRY_CONTENT)
    result = handle_escalate("pe-oc-08", rows)
    assert "PE-OC-08" in result


# ---------------------------------------------------------------------------
# load_registry
# ---------------------------------------------------------------------------


def test_load_registry_returns_rows(tmp_path: Path) -> None:
    p = _make_registry_file(tmp_path)
    rows = load_registry(p)
    assert len(rows) == 3


def test_load_registry_bad_file_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text("no registry here", encoding="utf-8")
    with pytest.raises(ValueError):
        load_registry(bad)


# ---------------------------------------------------------------------------
# main() CLI (AC-1, AC-5)
# ---------------------------------------------------------------------------


def test_main_status_command(tmp_path: Path, capsys) -> None:
    p = _make_registry_file(tmp_path)
    old_argv = sys.argv
    sys.argv = ["pm_status_reporter.py", "--command", "status", "--registry", str(p)]
    try:
        rc = main()
    finally:
        sys.argv = old_argv
    assert rc == 0
    out = capsys.readouterr().out
    assert "Active PEs" in out
    assert "PE-OC-08" in out


def test_main_escalate_command(tmp_path: Path, capsys) -> None:
    p = _make_registry_file(tmp_path)
    old_argv = sys.argv
    sys.argv = [
        "pm_status_reporter.py",
        "--command",
        "escalate",
        "--pe-id",
        "PE-OC-08",
        "--registry",
        str(p),
    ]
    try:
        rc = main()
    finally:
        sys.argv = old_argv
    assert rc == 0
    out = capsys.readouterr().out
    assert "PE-OC-08" in out
    assert "PM recommendation" in out


def test_main_escalate_missing_pe_id_returns_1(tmp_path: Path, capsys) -> None:
    p = _make_registry_file(tmp_path)
    old_argv = sys.argv
    sys.argv = [
        "pm_status_reporter.py",
        "--command",
        "escalate",
        "--registry",
        str(p),
    ]
    try:
        rc = main()
    finally:
        sys.argv = old_argv
    assert rc == 1


def test_main_invalid_registry_returns_1(tmp_path: Path, capsys) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text("nothing here", encoding="utf-8")
    old_argv = sys.argv
    sys.argv = ["pm_status_reporter.py", "--command", "status", "--registry", str(bad)]
    try:
        rc = main()
    finally:
        sys.argv = old_argv
    assert rc == 1
    assert "ERROR" in capsys.readouterr().out
