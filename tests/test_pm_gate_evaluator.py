"""Tests for scripts/pm_gate_evaluator.py (PE-OC-07)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.pm_gate_evaluator import (
    PM_REVIEW_REQUIRED,
    build_po_message,
    evaluate_gate,
    evaluate_gate_1,
    evaluate_gate_2,
    main,
)


def test_gate_1_pass_assigns_validator() -> None:
    result = evaluate_gate_1(
        {
            "pe_id": "PE-OC-07",
            "ci_green": True,
            "handoff_present": True,
            "status_packet_complete": True,
        },
        "@claude-code",
    )
    assert result["decision"] == "pass"
    assert result["ready"] is True
    assert result["registry_status"] == "validating"
    assert result["actions"]["assign_validator"] is True
    assert "@claude-code" in result["actions"]["post_comment"]


def test_gate_1_fail_reports_missing_conditions() -> None:
    result = evaluate_gate_1(
        {
            "pe_id": "PE-OC-07",
            "ci_green": False,
            "handoff_present": True,
            "status_packet_complete": False,
        },
        "@claude-code",
    )
    assert result["decision"] == "fail"
    assert result["ready"] is False
    assert result["registry_status"] == "gate-1-pending"
    assert "ci_green" in result["missing_conditions"]
    assert "status_packet_complete" in result["missing_conditions"]


def test_gate_2_pass_merges_when_ci_green() -> None:
    result = evaluate_gate_2(
        {
            "pe_id": "PE-OC-07",
            "review_verdict": "PASS",
            "ci_green": True,
            "labels": [],
        }
    )
    assert result["decision"] == "pass"
    assert result["ready"] is True
    assert result["registry_status"] == "merged"
    assert result["actions"]["merge_pr"] is True


def test_gate_2_escalates_on_pm_review_required_label() -> None:
    result = evaluate_gate_2(
        {
            "pe_id": "PE-OC-07",
            "review_verdict": "PASS",
            "ci_green": True,
            "labels": [PM_REVIEW_REQUIRED],
        }
    )
    assert result["decision"] == "escalate"
    assert result["ready"] is False
    assert result["actions"]["merge_pr"] is False
    assert result["actions"]["escalate_to_po"] is True


def test_gate_2_waits_for_ci_when_verdict_pass_but_ci_not_green() -> None:
    result = evaluate_gate_2(
        {
            "pe_id": "PE-OC-07",
            "review_verdict": "PASS",
            "ci_green": False,
            "labels": [],
        }
    )
    assert result["decision"] == "wait"
    assert result["registry_status"] == "gate-2-pending"
    assert result["actions"]["merge_pr"] is False


def test_gate_2_fail_verdict_returns_implementing_status() -> None:
    result = evaluate_gate_2(
        {
            "pe_id": "PE-OC-07",
            "review_verdict": "FAIL",
            "ci_green": True,
            "labels": [],
        }
    )
    assert result["decision"] == "fail"
    assert result["registry_status"] == "implementing"
    assert result["actions"]["escalate_to_po"] is True


def test_dispatch_by_gate_routes_to_gate_1() -> None:
    result = evaluate_gate(
        "gate-1",
        {
            "pe_id": "PE-OC-07",
            "ci_green": True,
            "handoff_present": True,
            "status_packet_complete": True,
        },
    )
    assert result["gate"] == "gate-1"
    assert result["decision"] == "pass"


def test_po_message_contains_gate_and_status() -> None:
    msg = build_po_message("PE-OC-07", "gate-2", "pass", "merged")
    assert "PE-OC-07" in msg
    assert "gate-2 PASS" in msg
    assert "merged" in msg


def test_main_reads_event_file_and_prints_json(tmp_path: Path, capsys) -> None:
    payload = {
        "pe_id": "PE-OC-07",
        "ci_green": True,
        "handoff_present": True,
        "status_packet_complete": True,
    }
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(payload), encoding="utf-8")

    import sys as _sys

    old_argv = _sys.argv
    _sys.argv = [
        "pm_gate_evaluator.py",
        "--gate",
        "gate-1",
        "--event-file",
        str(event_file),
    ]
    try:
        rc = main()
    finally:
        _sys.argv = old_argv

    assert rc == 0
    out = capsys.readouterr().out
    assert '"decision": "pass"' in out
    assert '"registry_status": "validating"' in out


def test_main_invalid_json_returns_1(tmp_path: Path, capsys) -> None:
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not-json", encoding="utf-8")

    import sys as _sys

    old_argv = _sys.argv
    _sys.argv = [
        "pm_gate_evaluator.py",
        "--gate",
        "gate-1",
        "--event-file",
        str(bad_file),
    ]
    try:
        rc = main()
    finally:
        _sys.argv = old_argv

    assert rc == 1
    assert "ERROR:" in capsys.readouterr().out
