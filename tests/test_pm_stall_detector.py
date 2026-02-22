"""Tests for scripts/pm_stall_detector.py (PE-OC-08)."""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

import pytest

from scripts.pm_stall_detector import (
    build_escalation_message,
    build_iteration_escalation,
    build_stall_escalation,
    count_validator_iterations,
    detect_iteration_breaches,
    detect_stalls,
    main,
    parse_active_registry,
    run_detection,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime.datetime(2026, 2, 22, 12, 0, 0, tzinfo=datetime.timezone.utc)
_THRESHOLD_HOURS = 48


def _make_registry(rows_md: str, tmp_path: Path) -> Path:
    content = (
        "# Current PE\n\n"
        "## Active PE Registry\n\n"
        "| PE-ID | Domain | Implementer-agentId | Validator-agentId |"
        " Branch | Status | Last-updated |\n"
        "|---|---|---|---|---|---|---|\n" + rows_md
    )
    p = tmp_path / "CURRENT_PE.md"
    p.write_text(content, encoding="utf-8")
    return p


def _row(pe_id: str, status: str, last_updated: str) -> str:
    return (
        f"| {pe_id} | openclaw-infra | prog-impl-claude | prog-val-codex |"
        f" feature/x | {status} | {last_updated} |\n"
    )


# ---------------------------------------------------------------------------
# detect_stalls (AC-2)
# ---------------------------------------------------------------------------


def test_detect_stall_over_threshold() -> None:
    # last updated 2026-02-19 → end-of-day 2026-02-19T23:59:59Z is ~60h before
    # 2026-02-22T12:00:00Z → stalled (age_hours > 48)
    _, rows = parse_active_registry(
        "# x\n\n## Active PE Registry\n\n"
        "| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |\n"
        "|---|---|---|---|---|---|---|\n"
        "| PE-OC-08 | openclaw-infra | prog-impl-claude | prog-val-codex | feature/x | implementing | 2026-02-19 |\n"
    )
    stalled = detect_stalls(rows, _NOW, _THRESHOLD_HOURS)
    assert len(stalled) == 1
    assert stalled[0]["pe-id"] == "PE-OC-08"


def test_no_stall_within_threshold() -> None:
    # last updated 2026-02-22 → 12 hours before now → not stalled
    _, rows = parse_active_registry(
        "# x\n\n## Active PE Registry\n\n"
        "| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |\n"
        "|---|---|---|---|---|---|---|\n"
        "| PE-OC-08 | openclaw-infra | prog-impl-claude | prog-val-codex | feature/x | implementing | 2026-02-22 |\n"
    )
    stalled = detect_stalls(rows, _NOW, _THRESHOLD_HOURS)
    assert stalled == []


def test_detect_stall_exactly_at_threshold_not_stalled() -> None:
    # last updated 2026-02-21 → end-of-day 2026-02-21T23:59:59Z is ~12h before
    # 2026-02-22T12:00:00Z → NOT stalled (age ≈ 12h, well under 48h threshold)
    now = datetime.datetime(2026, 2, 22, 12, 0, 0, tzinfo=datetime.timezone.utc)
    _, rows = parse_active_registry(
        "# x\n\n## Active PE Registry\n\n"
        "| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |\n"
        "|---|---|---|---|---|---|---|\n"
        "| PE-OC-09 | openclaw-infra | prog-impl-codex | prog-val-claude | feature/y | gate-1-pending | 2026-02-21 |\n"
    )
    stalled = detect_stalls(rows, now, _THRESHOLD_HOURS)
    assert stalled == []


def test_merged_rows_not_stalled() -> None:
    _, rows = parse_active_registry(
        "# x\n\n## Active PE Registry\n\n"
        "| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |\n"
        "|---|---|---|---|---|---|---|\n"
        "| PE-OC-07 | openclaw-infra | prog-impl-codex | prog-val-claude | feature/x | merged | 2026-01-01 |\n"
    )
    stalled = detect_stalls(rows, _NOW, _THRESHOLD_HOURS)
    assert stalled == []


def test_multiple_stalls_detected() -> None:
    _, rows = parse_active_registry(
        "# x\n\n## Active PE Registry\n\n"
        "| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |\n"
        "|---|---|---|---|---|---|---|\n"
        "| PE-OC-08 | openclaw-infra | prog-impl-claude | prog-val-codex | feature/a | implementing | 2026-02-19 |\n"
        "| PE-OC-09 | openclaw-infra | prog-impl-codex | prog-val-claude | feature/b | validating | 2026-02-18 |\n"
    )
    stalled = detect_stalls(rows, _NOW, _THRESHOLD_HOURS)
    assert len(stalled) == 2


# ---------------------------------------------------------------------------
# count_validator_iterations (AC-3)
# ---------------------------------------------------------------------------

_REVIEW_CONTENT_2_ROUNDS = """\
# REVIEW_PE_OC_08.md

## Round History

| Round | Verdict | Key Findings | Date |
|---|---|---|---|
| r1 | PASS | NB-1 | 2026-02-22 |
| r2 | PASS | resolved | 2026-02-22 |
"""

_REVIEW_CONTENT_3_ROUNDS = """\
# REVIEW_PE_OC_08.md

## Round History

| Round | Verdict | Key Findings | Date |
|---|---|---|---|
| r1 | FAIL | B-1 | 2026-02-20 |
| r2 | FAIL | B-2 | 2026-02-21 |
| r3 | PASS | resolved | 2026-02-22 |
"""


def test_count_iterations_no_review_file(tmp_path: Path) -> None:
    assert count_validator_iterations("PE-OC-99", tmp_path) == 0


def test_count_iterations_two_rounds(tmp_path: Path) -> None:
    review = tmp_path / "REVIEW_PE_OC_08.md"
    review.write_text(_REVIEW_CONTENT_2_ROUNDS, encoding="utf-8")
    assert count_validator_iterations("PE-OC-08", tmp_path) == 2


def test_count_iterations_three_rounds(tmp_path: Path) -> None:
    review = tmp_path / "REVIEW_PE_OC_08.md"
    review.write_text(_REVIEW_CONTENT_3_ROUNDS, encoding="utf-8")
    assert count_validator_iterations("PE-OC-08", tmp_path) == 3


# ---------------------------------------------------------------------------
# detect_iteration_breaches (AC-3)
# ---------------------------------------------------------------------------


def test_iteration_breach_above_threshold(tmp_path: Path) -> None:
    review = tmp_path / "REVIEW_PE_OC_08.md"
    review.write_text(_REVIEW_CONTENT_3_ROUNDS, encoding="utf-8")

    _, rows = parse_active_registry(
        "# x\n\n## Active PE Registry\n\n"
        "| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |\n"
        "|---|---|---|---|---|---|---|\n"
        "| PE-OC-08 | openclaw-infra | prog-impl-claude | prog-val-codex | feature/x | validating | 2026-02-22 |\n"
    )
    breaches = detect_iteration_breaches(rows, tmp_path, threshold=2)
    assert len(breaches) == 1
    assert breaches[0][0]["pe-id"] == "PE-OC-08"
    assert breaches[0][1] == 3


def test_no_iteration_breach_at_threshold(tmp_path: Path) -> None:
    review = tmp_path / "REVIEW_PE_OC_08.md"
    review.write_text(_REVIEW_CONTENT_2_ROUNDS, encoding="utf-8")

    _, rows = parse_active_registry(
        "# x\n\n## Active PE Registry\n\n"
        "| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |\n"
        "|---|---|---|---|---|---|---|\n"
        "| PE-OC-08 | openclaw-infra | prog-impl-claude | prog-val-codex | feature/x | validating | 2026-02-22 |\n"
    )
    # threshold=2: count must be > 2 → 2 rounds → no breach
    breaches = detect_iteration_breaches(rows, tmp_path, threshold=2)
    assert breaches == []


def test_merged_pe_excluded_from_breach_check(tmp_path: Path) -> None:
    review = tmp_path / "REVIEW_PE_OC_08.md"
    review.write_text(_REVIEW_CONTENT_3_ROUNDS, encoding="utf-8")

    _, rows = parse_active_registry(
        "# x\n\n## Active PE Registry\n\n"
        "| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |\n"
        "|---|---|---|---|---|---|---|\n"
        "| PE-OC-08 | openclaw-infra | prog-impl-claude | prog-val-codex | feature/x | merged | 2026-02-22 |\n"
    )
    breaches = detect_iteration_breaches(rows, tmp_path, threshold=2)
    assert breaches == []


# ---------------------------------------------------------------------------
# build_escalation_message (AC-4)
# ---------------------------------------------------------------------------


def test_build_escalation_contains_required_fields() -> None:
    msg = build_escalation_message(
        pe_id="PE-OC-08",
        blocker="Test stall",
        status="implementing",
        iteration_count=1,
        options=[("Fix it", "fast"), ("Defer it", "safe")],
        recommendation="A — fastest",
    )
    assert "PE-OC-08" in msg
    assert "Test stall" in msg
    assert "implementing" in msg
    assert "Iteration count: 1" in msg
    assert "A. Fix it" in msg
    assert "B. Defer it" in msg
    assert "PM recommendation: A — fastest" in msg


def test_build_stall_escalation_message(tmp_path: Path) -> None:
    row = {"pe-id": "PE-OC-08", "status": "implementing", "last-updated": "2026-02-20"}
    msg = build_stall_escalation(row, 72.0)
    assert "PE-OC-08" in msg
    assert "72" in msg
    assert "PM recommendation" in msg


def test_build_iteration_escalation_message() -> None:
    row = {"pe-id": "PE-OC-08", "status": "validating", "last-updated": "2026-02-22"}
    msg = build_iteration_escalation(row, 3)
    assert "PE-OC-08" in msg
    assert "Iteration count: 3" in msg
    assert "PM recommendation" in msg
    # Must have at least 2 resolution options (AC-3)
    assert "A." in msg
    assert "B." in msg


# ---------------------------------------------------------------------------
# run_detection
# ---------------------------------------------------------------------------


def test_run_detection_no_issues(tmp_path: Path) -> None:
    p = _make_registry(_row("PE-OC-08", "implementing", "2026-02-22"), tmp_path)
    messages = run_detection(p, tmp_path, threshold_hours=48, now=_NOW)
    assert messages == []


def test_run_detection_stall_found(tmp_path: Path) -> None:
    p = _make_registry(_row("PE-OC-08", "implementing", "2026-02-19"), tmp_path)
    messages = run_detection(p, tmp_path, threshold_hours=48, now=_NOW)
    assert len(messages) == 1
    assert "PE-OC-08" in messages[0]


def test_run_detection_iteration_breach(tmp_path: Path) -> None:
    p = _make_registry(_row("PE-OC-08", "validating", "2026-02-22"), tmp_path)
    review = tmp_path / "REVIEW_PE_OC_08.md"
    review.write_text(_REVIEW_CONTENT_3_ROUNDS, encoding="utf-8")
    messages = run_detection(
        p, tmp_path, threshold_hours=48, iteration_threshold=2, now=_NOW
    )
    assert len(messages) == 1
    assert "Iteration count: 3" in messages[0]


def test_run_detection_invalid_registry_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text("nothing here", encoding="utf-8")
    with pytest.raises(ValueError):
        run_detection(bad, tmp_path, now=_NOW)


# ---------------------------------------------------------------------------
# main() CLI
# ---------------------------------------------------------------------------


def test_main_no_stalls(tmp_path: Path, capsys) -> None:
    p = _make_registry(_row("PE-OC-08", "implementing", "2026-02-22"), tmp_path)
    old_argv = sys.argv
    sys.argv = [
        "pm_stall_detector.py",
        "--registry",
        str(p),
        "--repo-root",
        str(tmp_path),
    ]
    try:
        rc = main()
    finally:
        sys.argv = old_argv
    assert rc == 0
    assert "No stalls" in capsys.readouterr().out


def test_main_stall_detected(tmp_path: Path, capsys) -> None:
    p = _make_registry(_row("PE-OC-08", "implementing", "2026-02-19"), tmp_path)
    old_argv = sys.argv
    sys.argv = [
        "pm_stall_detector.py",
        "--registry",
        str(p),
        "--repo-root",
        str(tmp_path),
    ]
    try:
        rc = main()
    finally:
        sys.argv = old_argv
    assert rc == 0
    assert "PE-OC-08" in capsys.readouterr().out


def test_main_invalid_registry_returns_1(tmp_path: Path, capsys) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text("no registry here", encoding="utf-8")
    old_argv = sys.argv
    sys.argv = [
        "pm_stall_detector.py",
        "--registry",
        str(bad),
        "--repo-root",
        str(tmp_path),
    ]
    try:
        rc = main()
    finally:
        sys.argv = old_argv
    assert rc == 1
    assert "ERROR" in capsys.readouterr().out


def test_main_output_file(tmp_path: Path, capsys) -> None:
    p = _make_registry(_row("PE-OC-08", "implementing", "2026-02-19"), tmp_path)
    out_file = tmp_path / "out.json"
    old_argv = sys.argv
    sys.argv = [
        "pm_stall_detector.py",
        "--registry",
        str(p),
        "--repo-root",
        str(tmp_path),
        "--output",
        str(out_file),
    ]
    try:
        rc = main()
    finally:
        sys.argv = old_argv
    assert rc == 0
    assert out_file.exists()
    import json

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 1
