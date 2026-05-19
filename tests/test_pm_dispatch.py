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


def _write_scope_file(root: Path, rel: str, content: str = "placeholder\n") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_scoped_files(root: Path, include_runtime_noise: bool = True) -> None:
    _write_scope_file(
        root,
        "CURRENT_PE.md",
        """# Current PE Assignment

## Current PE

| Field   | Value |
|---------|-------|
| PE      | PE-OPS-DISPATCH-WRAPPER-HARDENING-01 |
| Branch  | feature/pe-ops-dispatch-wrapper-hardening-01 |

## Agent roles

| Agent | Role |
|-------|------|
| infra-impl-b | Implementer |
| infra-val-a | Validator |

Phase 1 dry-run/check/generate only.
""",
    )
    _write_scope_file(
        root,
        ".elis/pe/PE-OPS-DISPATCH-WRAPPER-HARDENING-01/PE_TASK.md",
        "Phase 1 dry-run / check / generate only.\n- scripts/pm_dispatch.py\n- scripts/po_dispatch.py\n",
    )
    _write_scope_file(
        root,
        ".elis/pe/PE-OPS-DISPATCH-WRAPPER-HARDENING-01/HANDOFF.md",
        "Summary\nFiles Changed\nAcceptance Criteria\nValidation Commands\n",
    )
    _write_scope_file(
        root,
        "docs/governance/ELIS_Dispatch_Wrapper_Hardening.md",
        "Approved dispatch wrapper hardening note.\n",
    )
    _write_scope_file(root, "scripts/pm_dispatch.py")
    _write_scope_file(root, "scripts/po_dispatch.py")
    _write_scope_file(root, "tests/test_pm_dispatch.py")
    _write_scope_file(root, "tests/test_pm_dispatch_contract.py")
    _write_scope_file(root, "tests/test_po_dispatch.py")

    if include_runtime_noise:
        _write_scope_file(root, "AGENTS.md")
        _write_scope_file(root, ".openclaw/workspace-state.json")
        _write_scope_file(root, "memory/runtime-note.md")


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)


def test_build_packet_uses_the_approved_phase_one_contract() -> None:
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
    assert packet.file_scope == MODULE.APPROVED_FILE_SCOPE
    assert packet.runtime_bootstrap_allowlist == MODULE.RUNTIME_BOOTSTRAP_ALLOWLIST
    assert packet.required_rules == MODULE.REQUIRED_RULES
    assert packet.phase_1_gates == MODULE.PHASE_1_GATES
    assert packet.tests == MODULE.EXPECTED_TESTS
    assert packet.live_dispatch_statement == MODULE.PHASE_1_ONLY_STATEMENT
    assert packet.runtime_bootstrap_policy == MODULE.RUNTIME_BOOTSTRAP_POLICY


def test_render_contract_json_includes_allowlist_and_required_rules() -> None:
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
    assert payload["runtime_bootstrap_allowlist"] == list(
        MODULE.RUNTIME_BOOTSTRAP_ALLOWLIST
    )
    assert payload["required_rules"] == list(MODULE.REQUIRED_RULES)
    assert payload["tests"] == list(MODULE.EXPECTED_TESTS)
    assert payload["live_dispatch_statement"] == MODULE.PHASE_1_ONLY_STATEMENT


def test_classify_workspace_line_allows_preserved_runtime_bootstrap_noise() -> None:
    finding = MODULE.classify_workspace_line("?? AGENTS.md")

    assert finding.category == "preserved-runtime-bootstrap"
    assert "allowed" in finding.reason.lower()


def test_classify_workspace_line_blocks_untracked_dirty_files_outside_scope() -> None:
    finding = MODULE.classify_workspace_line("?? notes/todo.txt")

    assert finding.category == "blocker"
    assert "outside approved scope" in finding.reason.lower()


def test_check_mode_passes_when_only_approved_scope_and_allowed_noise_exist(
    tmp_path: Path,
) -> None:
    _init_git_repo(tmp_path)
    _make_scoped_files(tmp_path, include_runtime_noise=True)

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
            "check",
            "--repo-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: Phase 1 packet is well-formed" in result.stdout
    assert "Phase 1 only generates and checks dispatch contracts" in result.stdout


def test_check_mode_fails_on_dirty_files_outside_scope(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    _make_scoped_files(tmp_path, include_runtime_noise=True)
    _write_scope_file(tmp_path, "notes/todo.txt")

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
            "check",
            "--repo-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=tmp_path,
    )

    assert result.returncode == 1, result.stdout + result.stderr
    assert "Dispatch blockers detected" in result.stdout
    assert "notes/todo.txt" in result.stdout


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
    assert MODULE.PHASE_1_ONLY_STATEMENT in result.stdout
    assert "PM DISPATCH OPENING PACKET" in result.stdout
