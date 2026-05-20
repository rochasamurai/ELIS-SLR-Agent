#!/usr/bin/env python3
"""Tests for scripts/pm_dispatch.py — current PE opening packet."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pm_dispatch.py"
STATE_PATH = Path(__file__).resolve().parents[1] / ".elis" / "state" / "current_pe.json"


def _load():
    spec = importlib.util.spec_from_file_location("pm_dispatch", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = _load()
CURRENT_STATE = json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _write_scope_file(root: Path, rel: str, content: str = "placeholder\n") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_scoped_files(root: Path, include_runtime_noise: bool = True) -> None:
    _write_scope_file(
        root,
        "CURRENT_PE.md",
        """# Current PE Assignment

## Release context

| Field          | Value                               |
|----------------|-------------------------------------|
| Release        | ELIS SLR Agent — Multi-Agent Implementation Plan · v2.0.1 |
| Base branch    | main                                |
| Plan file      | ELIS_MultiAgent_Implementation_Plan_v2_0.md |
| Plan location  | repo root                           |

## Current PE

| Field   | Value |
|---------|-------|
| PE      | PE-OPS-CURRENT-PE-STATE-01 |
| Branch  | feature/pe-ops-current-pe-state-01 |

> **planning / awaiting implementer dispatch.**

## Agent roles

| Agent | Role |
|-------|------|
| infra-impl-b | Implementer |
| infra-val-a | Validator |

## Active PE Registry

| PE-ID       | Domain          | Implementer-agentId  | Validator-agentId  | Branch                                            | Status          | Last-updated |
|-------------|-----------------|----------------------|--------------------|---------------------------------------------------|-----------------|--------------|
| PE-OPS-CURRENT-PE-STATE-01 | ops | infra-impl-b | infra-val-a | feature/pe-ops-current-pe-state-01 | planning | 2026-05-19 |
""",
    )
    _write_scope_file(
        root,
        ".elis/state/current_pe.json",
        json.dumps(CURRENT_STATE, indent=2) + "\n",
    )
    _write_scope_file(
        root,
        ".elis/pe/PE-OPS-CURRENT-PE-STATE-01/PE_TASK.md",
        "Move canonical PE machine state out of CURRENT_PE.md into structured state.\n",
    )
    _write_scope_file(
        root,
        ".elis/pe/PE-OPS-CURRENT-PE-STATE-01/HANDOFF.md",
        "Summary\nFiles Changed\nAcceptance Criteria\n",
    )
    _write_scope_file(
        root,
        "docs/governance/ELIS_Current_PE_State_Model.md",
        "Current PE state model contract.\n",
    )
    _write_scope_file(root, "scripts/pm_dispatch.py")
    _write_scope_file(root, "tests/test_pm_dispatch.py")
    _write_scope_file(root, "tests/test_pm_dispatch_contract.py")
    _write_scope_file(root, "scripts/check_current_pe.py")
    _write_scope_file(root, "scripts/check_pe_opening_context.py")
    _write_scope_file(root, "tests/test_check_current_pe.py")
    _write_scope_file(root, "tests/test_check_pe_opening_context.py")
    _write_scope_file(root, "schemas/current_pe.schema.json")

    if include_runtime_noise:
        _write_scope_file(root, "AGENTS.md")
        _write_scope_file(root, ".openclaw/workspace-state.json")
        _write_scope_file(root, "memory/runtime-note.md")


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)


def test_build_packet_uses_the_current_pe_state() -> None:
    packet = MODULE.build_packet(
        state=CURRENT_STATE,
        pe_id="PE-OPS-CURRENT-PE-STATE-01",
        branch="feature/pe-ops-current-pe-state-01",
        baseline="origin/main @ f686e92ac64f9d174d2cf64b781ce95312d7a090",
        lane="Strict",
        implementer="infra-impl-b",
        validator="infra-val-a",
    )

    assert packet.phase == "planning"
    assert packet.mode == "dry-run"
    assert packet.objective == CURRENT_STATE["objective"]
    assert packet.file_scope == tuple(CURRENT_STATE["file_scope"])
    assert packet.runtime_bootstrap_allowlist == tuple(
        CURRENT_STATE["runtime_bootstrap_allowlist"]
    )
    assert packet.required_rules == tuple(CURRENT_STATE["required_rules"])
    assert packet.phase_1_gates == tuple(CURRENT_STATE["phase_1_gates"])
    assert packet.tests == tuple(CURRENT_STATE["tests"])
    assert packet.live_dispatch_statement == CURRENT_STATE["live_dispatch_statement"]
    assert packet.runtime_bootstrap_policy == CURRENT_STATE["runtime_bootstrap_policy"]


def test_render_contract_json_includes_current_state() -> None:
    packet = MODULE.build_packet(
        state=CURRENT_STATE,
        pe_id="PE-OPS-CURRENT-PE-STATE-01",
        branch="feature/pe-ops-current-pe-state-01",
        baseline="origin/main @ f686e92ac64f9d174d2cf64b781ce95312d7a090",
        lane="Strict",
        implementer="infra-impl-b",
        validator="infra-val-a",
    )

    payload = json.loads(MODULE.render_contract_json(packet))
    assert payload["pe_id"] == "PE-OPS-CURRENT-PE-STATE-01"
    assert payload["branch"] == "feature/pe-ops-current-pe-state-01"
    assert payload["objective"] == CURRENT_STATE["objective"]
    assert payload["runtime_bootstrap_allowlist"] == list(
        CURRENT_STATE["runtime_bootstrap_allowlist"]
    )
    assert payload["required_rules"] == list(CURRENT_STATE["required_rules"])
    assert payload["tests"] == list(CURRENT_STATE["tests"])


def test_classify_workspace_line_allows_preserved_runtime_bootstrap_noise() -> None:
    finding = MODULE.classify_workspace_line("?? AGENTS.md")

    assert finding.category == "preserved-runtime-bootstrap"
    assert "allowed" in finding.reason.lower()


def test_classify_workspace_line_blocks_untracked_dirty_files_outside_scope() -> None:
    finding = MODULE.classify_workspace_line("?? notes/todo.txt")

    assert finding.category == "blocker"
    assert "outside approved scope" in finding.reason.lower()


def test_check_mode_passes_when_only_current_scope_and_allowed_noise_exist(
    tmp_path: Path,
) -> None:
    _init_git_repo(tmp_path)
    _make_scoped_files(tmp_path, include_runtime_noise=True)

    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            "PE-OPS-CURRENT-PE-STATE-01",
            "--branch",
            "feature/pe-ops-current-pe-state-01",
            "--baseline",
            "origin/main @ f686e92ac64f9d174d2cf64b781ce95312d7a090",
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
    assert "PASS: Current PE packet is well-formed" in result.stdout
    assert "Phase 1 only generates and checks dispatch contracts" in result.stdout


def test_check_mode_fails_on_dirty_files_outside_scope(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    _make_scoped_files(tmp_path, include_runtime_noise=True)
    _write_scope_file(tmp_path, "notes/todo.txt")

    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            "PE-OPS-CURRENT-PE-STATE-01",
            "--branch",
            "feature/pe-ops-current-pe-state-01",
            "--baseline",
            "origin/main @ f686e92ac64f9d174d2cf64b781ce95312d7a090",
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


def test_generate_emits_current_state_json() -> None:
    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            "PE-OPS-CURRENT-PE-STATE-01",
            "--branch",
            "feature/pe-ops-current-pe-state-01",
            "--baseline",
            "origin/main @ f686e92ac64f9d174d2cf64b781ce95312d7a090",
            "--lane",
            "Strict",
            "--implementer",
            "infra-impl-b",
            "--validator",
            "infra-val-a",
            "--mode",
            "generate",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["pe_id"] == "PE-OPS-CURRENT-PE-STATE-01"
    assert payload["branch"] == "feature/pe-ops-current-pe-state-01"
    assert payload["objective"] == CURRENT_STATE["objective"]
