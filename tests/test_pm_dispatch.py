#!/usr/bin/env python3
"""Tests for scripts/pm_dispatch.py — deterministic PM opening packet wrapper."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pm_dispatch.py"


def _load():
    spec = importlib.util.spec_from_file_location("pm_dispatch", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def _make_scoped_files(root: Path) -> None:
    for rel in MODULE.APPROVED_FILE_SCOPE:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel == "CURRENT_PE.md":
            path.write_text(
                """# Current PE Assignment

| Field   | Value |
|---------|-------|
| PE      | PE-OPS-PM-DISPATCH-01 |
| Branch  | feature/pe-ops-pm-dispatch-01-deterministic-pm-dispatch-wrapper |

| Agent       | Role |
|-------------|------|
| infra-impl-b | Implementer |
| infra-val-a | Validator |
""",
                encoding="utf-8",
            )
        else:
            path.write_text(f"placeholder for {rel}\n", encoding="utf-8")


def test_build_packet_uses_approved_scope_and_phase_one_only() -> None:
    packet = MODULE.build_packet(
        pe_id="PE-OPS-PM-DISPATCH-01",
        branch="feature/pe-ops-pm-dispatch-01-deterministic-pm-dispatch-wrapper",
        baseline="origin/main @ a790d605b673aa42fec7f17c805d8c7ce88c4aa2",
        lane="Strict",
        implementer="infra-impl-b",
        validator="infra-val-a",
    )

    assert packet.phase == "Phase 1"
    assert packet.mode == "dry-run"
    assert packet.file_scope == MODULE.APPROVED_FILE_SCOPE
    assert packet.phase_1_gates == MODULE.PHASE_1_GATES
    assert packet.live_dispatch_statement == MODULE.LIVE_DISPATCH_STATEMENT


def test_validate_packet_rejects_wrong_lane() -> None:
    packet = MODULE.build_packet(
        pe_id="PE-OPS-PM-DISPATCH-01",
        branch="feature/pe-ops-pm-dispatch-01-deterministic-pm-dispatch-wrapper",
        baseline="origin/main @ a790d605b673aa42fec7f17c805d8c7ce88c4aa2",
        lane="Loose",
        implementer="infra-impl-b",
        validator="infra-val-a",
    )

    assert any("Lane must be 'Strict'" in item for item in MODULE.validate_packet(packet))


def test_render_contract_json_is_deterministic() -> None:
    packet = MODULE.build_packet(
        pe_id="PE-OPS-PM-DISPATCH-01",
        branch="feature/pe-ops-pm-dispatch-01-deterministic-pm-dispatch-wrapper",
        baseline="origin/main @ a790d605b673aa42fec7f17c805d8c7ce88c4aa2",
        lane="Strict",
        implementer="infra-impl-b",
        validator="infra-val-a",
    )

    payload = json.loads(MODULE.render_contract_json(packet))
    assert payload["pe_id"] == "PE-OPS-PM-DISPATCH-01"
    assert payload["file_scope"] == list(MODULE.APPROVED_FILE_SCOPE)
    assert payload["phase_1_gates"] == list(MODULE.PHASE_1_GATES)
    assert payload["live_dispatch_statement"] == MODULE.LIVE_DISPATCH_STATEMENT


def test_check_mode_passes_when_approved_files_exist(tmp_path: Path) -> None:
    _make_scoped_files(tmp_path)

    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            "PE-OPS-PM-DISPATCH-01",
            "--branch",
            "feature/pe-ops-pm-dispatch-01-deterministic-pm-dispatch-wrapper",
            "--baseline",
            "origin/main @ a790d605b673aa42fec7f17c805d8c7ce88c4aa2",
            "--lane",
            "Strict",
            "--implementer",
            "infra-impl-b",
            "--validator",
            "infra-val-a",
            "--mode",
            "check",
            "--repo-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: Phase 1 packet is well-formed and does not call live dispatch APIs." in result.stdout


def test_dry_run_emits_phase_one_statement() -> None:
    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            "PE-OPS-PM-DISPATCH-01",
            "--branch",
            "feature/pe-ops-pm-dispatch-01-deterministic-pm-dispatch-wrapper",
            "--baseline",
            "origin/main @ a790d605b673aa42fec7f17c805d8c7ce88c4aa2",
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
    assert MODULE.LIVE_DISPATCH_STATEMENT in result.stdout
    assert "PM DISPATCH OPENING PACKET" in result.stdout
