#!/usr/bin/env python3
"""Tests for scripts/po_dispatch.py — dry-run PO→PM safe-start helper."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "po_dispatch.py"


def _load():
    spec = importlib.util.spec_from_file_location("po_dispatch", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def test_build_packet_uses_the_approved_safe_start_sequence() -> None:
    packet = MODULE.build_packet(
        pe_id="PE-OPS-DISPATCH-WRAPPER-HARDENING-01",
        branch="feature/pe-ops-dispatch-wrapper-hardening-01",
        baseline="origin/main @ a486f05e8376afd227595b9f1ccad3f88369cf74",
        lane="Strict",
        implementer="infra-impl-b",
        validator="infra-val-a",
    )

    assert packet.phase == "Phase 1"
    assert packet.mode == "dry-run"
    assert len(packet.sequence_steps) == 6
    assert packet.sequence_steps[0].action == "Ask PM to create a dedicated PE thread"
    assert packet.sequence_steps[1].action == "Send /reset in that PE thread"
    assert packet.sequence_steps[2].action == "Require complete RESET_BINDING_ACK_FORMAT"
    assert packet.sequence_steps[5].action.startswith(
        "Remind that opening starts from current origin/main"
    )
    assert packet.hard_stops == MODULE.HARD_STOPS
    assert packet.phase_1_gates == MODULE.PHASE_1_GATES
    assert packet.request_templates["ack_required"].startswith("Require the full")


def test_render_contract_json_includes_ack_and_baseline_reminders() -> None:
    packet = MODULE.build_packet(
        pe_id="PE-OPS-DISPATCH-WRAPPER-HARDENING-01",
        branch="feature/pe-ops-dispatch-wrapper-hardening-01",
        baseline="origin/main @ a486f05e8376afd227595b9f1ccad3f88369cf74",
        lane="Strict",
        implementer="infra-impl-b",
        validator="infra-val-a",
    )

    payload = json.loads(MODULE.render_contract_json(packet))
    assert payload["pe_id"] == "PE-OPS-DISPATCH-WRAPPER-HARDENING-01"
    assert payload["sequence_steps"][2]["action"] == "Require complete RESET_BINDING_ACK_FORMAT"
    assert payload["request_templates"]["open_instruction"].startswith(
        "Only after a valid RESET_BINDING_ACK_FORMAT"
    )
    assert "CURRENT_PE.md must be plan-complete" in payload["request_templates"]["baseline_reminder"]


def test_validate_packet_rejects_non_strict_lane() -> None:
    packet = MODULE.build_packet(
        pe_id="PE-OPS-DISPATCH-WRAPPER-HARDENING-01",
        branch="feature/pe-ops-dispatch-wrapper-hardening-01",
        baseline="origin/main @ a486f05e8376afd227595b9f1ccad3f88369cf74",
        lane="Loose",
        implementer="infra-impl-b",
        validator="infra-val-a",
    )

    assert any("Lane must be 'Strict'" in item for item in MODULE.validate_packet(packet))


def test_dry_run_emits_phase_one_statement() -> None:
    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            "PE-OPS-DISPATCH-WRAPPER-HARDENING-01",
            "--branch",
            "feature/pe-ops-dispatch-wrapper-hardening-01",
            "--baseline",
            "origin/main @ a486f05e8376afd227595b9f1ccad3f88369cf74",
            "--lane",
            "Strict",
            "--implementer",
            "infra-impl-b",
            "--validator",
            "infra-val-a",
            "--mode",
            "dry-run",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PO DISPATCH HELPER" in result.stdout
    assert MODULE.PHASE_1_ONLY_STATEMENT in result.stdout
    assert "dedicated PE thread" in result.stdout
