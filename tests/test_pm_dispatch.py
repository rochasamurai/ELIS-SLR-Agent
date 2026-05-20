#!/usr/bin/env python3
"""Tests for scripts/pm_dispatch.py — current PE opening packet."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

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

ACTIVE_STATE = {
    "pe_id": "PE-OPS-CURRENT-PE-STATE-01",
    "objective": "Move canonical PE machine state out of CURRENT_PE.md into structured state. CURRENT_PE.md becomes a validated human-readable summary only.",
    "branch": "feature/pe-ops-current-pe-state-01",
    "baseline": "origin/main @ f686e92ac64f9d174d2cf64b781ce95312d7a090",
    "lane": "Strict",
    "implementer": "infra-impl-b",
    "validator": "infra-val-a",
    "current_state": "planning",
    "file_scope": [
        "CURRENT_PE.md",
        ".elis/state/current_pe.json",
        "schemas/current_pe.schema.json",
        "scripts/check_current_pe.py",
        "scripts/check_pe_opening_context.py",
        "scripts/pm_dispatch.py",
        "tests/test_check_current_pe.py",
        "tests/test_check_pe_opening_context.py",
        "tests/test_pm_dispatch.py",
        "tests/test_pm_dispatch_contract.py",
        "docs/governance/ELIS_Current_PE_State_Model.md",
        ".elis/pe/PE-OPS-CURRENT-PE-STATE-01/PE_TASK.md",
        ".elis/pe/PE-OPS-CURRENT-PE-STATE-01/HANDOFF.md",
    ],
    "runtime_bootstrap_allowlist": [
        "AGENTS.md",
        "TOOLS.md",
        "USER.md",
        "HEARTBEAT.md",
        "SOUL.md",
        "IDENTITY.md",
        ".openclaw/",
        "memory/",
        "skills/",
        "canvas/",
    ],
    "required_rules": [
        "PRESERVED_RUNTIME_BOOTSTRAP_FILES_ARE_NOT_DISPATCH_BLOCKERS_RULE",
        "NEW_PE_REQUIRES_FRESH_THREAD_AND_RESET_ACK_RULE",
        "DISPATCH_CONTRACT_MUST_USE_TARGET_AGENT_WORKSPACE_RULE",
        "FRESH_VALIDATOR_SUBAGENT_DISPATCH_RULE",
        "VALIDATOR_MUST_NOT_USE_PM_WORKTREE_RULE",
        "VALIDATION_PASS_REQUIRES_PRIOR_RESET_ACK_RULE",
        "TARGET_REF_AVAILABLE_BEFORE_AGENT_BINDING_RULE",
        "FIXED_AGENT_WORKTREE_READINESS_BEFORE_DISPATCH_RULE",
        "ROLE_CORRECT_GIT_AUTHOR_IDENTITY_RULE",
        "COMPLETE_BRANCH_FILE_SCOPE_EVIDENCE_RULE",
    ],
    "phase_1_gates": ["dry-run", "check", "generate"],
    "tests": [
        "tests/test_pm_dispatch.py",
        "tests/test_pm_dispatch_contract.py",
        "tests/test_po_dispatch.py",
    ],
    "rollback": "Revert only the approved scoped files to the accepted origin/main baseline and keep OpenClaw/Hermes configuration unchanged.",
    "hard_stops": [
        "do not create the branch here",
        "do not call Discord APIs",
        "do not send live messages",
        "do not call OpenClaw live dispatch actions",
        "do not mutate repo state outside approved scope",
        "do not alter CURRENT_PE.md outside approved scope",
        "do not change OpenClaw/Hermes config",
        "do not change auth or secret state",
        "do not restart services",
        "do not replace live dispatch behaviour",
        "do not push, open PRs, or merge without PO approval",
    ],
    "live_dispatch_statement": "Phase 1 only generates and checks dispatch contracts; it does not call live dispatch APIs or Discord APIs.",
    "runtime_bootstrap_policy": "Approved OpenClaw runtime/bootstrap files are non-blocking only when they are untracked or workspace-local, not staged, not part of the PE-approved file scope, not secret-bearing, not modified tracked repository files, not being committed, and not masking unsafe PE residue.",
}

CLOSEOUT_STATE = {
    "pe_id": "—",
    "objective": "PE-OPS-CURRENT-PE-STATE-01 is merged; no active PE remains.",
    "branch": "—",
    "baseline": "origin/main @ 26254d3556526ef9ef59f399f51d5a7c0e837c6a",
    "lane": "—",
    "implementer": "—",
    "validator": "—",
    "current_state": "plan-complete",
    "file_scope": ["CURRENT_PE.md", ".elis/state/current_pe.json"],
    "runtime_bootstrap_allowlist": [
        "AGENTS.md",
        "TOOLS.md",
        "USER.md",
        "HEARTBEAT.md",
        "SOUL.md",
        "IDENTITY.md",
        ".openclaw/",
        "memory/",
        "skills/",
        "canvas/",
    ],
    "required_rules": [],
    "phase_1_gates": [],
    "tests": [
        "tests/test_check_current_pe.py",
        "tests/test_check_pe_opening_context.py",
    ],
    "rollback": "Restore CURRENT_PE.md and .elis/state/current_pe.json to the merged closeout snapshot if needed.",
    "hard_stops": [
        "do not change runtime/config/auth/service files",
        "do not restart services",
        "do not resume PE-OPS-A2A-RUNTIME-01 yet",
    ],
    "live_dispatch_statement": "No active PE remains; the structured state is now a closeout snapshot.",
    "runtime_bootstrap_policy": "Approved OpenClaw runtime/bootstrap files remain non-blocking only when they are untracked or workspace-local, not staged, not part of the closeout scope, not secret-bearing, not modified tracked repository files, not being committed, and not masking unsafe residue.",
}

STATE_CASES = [ACTIVE_STATE, CLOSEOUT_STATE]


def _state_markdown(state: dict[str, object]) -> str:
    if state["current_state"] == "planning":
        return """# Current PE Assignment

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
"""

    return """# Current PE Assignment

> Maintained by PM. Update ALL fields at the start of every new PE or release.
> Both agents read this file as Step 0. It is the only file that needs editing
> when switching release lines.

---

## Release context

| Field          | Value                                                          |
|----------------|----------------------------------------------------------------|
| Release        | ELIS SLR Agent — Multi-Agent Implementation Plan · v2.0.1     |
| Base branch    | main                                                           |
| Plan file      | ELIS_MultiAgent_Implementation_Plan_v2_0.md                   |
| Plan location  | repo root                                                      |

---

## Current PE

| Field   | Value |
|---------|-------|
| PE      | — |
| Branch  | — |

> **plan-complete / no active PE. `PE-OPS-CURRENT-PE-STATE-01` merged on `origin/main`.**

## Agent roles

| Agent | Role |
|-------|------|
| — | — |
| — | — |

> no active PE roles.


---

## Active PE Registry

| PE-ID       | Domain          | Implementer-agentId  | Validator-agentId  | Branch                                            | Status          | Last-updated |
|-------------|-----------------|----------------------|--------------------|---------------------------------------------------|-----------------|--------------|
| PE-OPS-CURRENT-PE-STATE-01 | ops | infra-impl-b | infra-val-a | feature/pe-ops-current-pe-state-01 | merged | 2026-05-20 |
"""


def _write_scope_file(root: Path, rel: str, content: str = "placeholder\n") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_scoped_files(
    root: Path,
    *,
    state: dict[str, object],
    include_runtime_noise: bool = True,
) -> None:
    _write_scope_file(root, "CURRENT_PE.md", _state_markdown(state))
    _write_scope_file(
        root, ".elis/state/current_pe.json", json.dumps(state, indent=2) + "\n"
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


@pytest.mark.parametrize("state", STATE_CASES)
def test_build_packet_uses_the_current_pe_state(state: dict[str, object]) -> None:
    packet = MODULE.build_packet(
        state=state,
        pe_id=str(state["pe_id"]),
        branch=str(state["branch"]),
        baseline=str(state["baseline"]),
        lane=str(state["lane"]),
        implementer=str(state["implementer"]),
        validator=str(state["validator"]),
    )

    assert packet.phase == str(state["current_state"])
    assert packet.mode == "dry-run"
    assert packet.objective == state["objective"]
    assert packet.file_scope == tuple(state["file_scope"])
    assert packet.runtime_bootstrap_allowlist == tuple(
        state["runtime_bootstrap_allowlist"]
    )
    assert packet.required_rules == tuple(state["required_rules"])
    assert packet.phase_1_gates == tuple(state["phase_1_gates"])
    assert packet.tests == tuple(state["tests"])
    assert packet.live_dispatch_statement == state["live_dispatch_statement"]
    assert packet.runtime_bootstrap_policy == state["runtime_bootstrap_policy"]


@pytest.mark.parametrize("state", STATE_CASES)
def test_render_contract_json_includes_current_state(state: dict[str, object]) -> None:
    packet = MODULE.build_packet(
        state=state,
        pe_id=str(state["pe_id"]),
        branch=str(state["branch"]),
        baseline=str(state["baseline"]),
        lane=str(state["lane"]),
        implementer=str(state["implementer"]),
        validator=str(state["validator"]),
    )

    payload = json.loads(MODULE.render_contract_json(packet))
    assert payload["pe_id"] == state["pe_id"]
    assert payload["branch"] == state["branch"]
    assert payload["objective"] == state["objective"]
    assert payload["runtime_bootstrap_allowlist"] == list(
        state["runtime_bootstrap_allowlist"]
    )
    assert payload["required_rules"] == list(state["required_rules"])
    assert payload["tests"] == list(state["tests"])


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
    _make_scoped_files(tmp_path, state=ACTIVE_STATE, include_runtime_noise=True)

    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            str(ACTIVE_STATE["pe_id"]),
            "--branch",
            str(ACTIVE_STATE["branch"]),
            "--baseline",
            str(ACTIVE_STATE["baseline"]),
            "--lane",
            str(ACTIVE_STATE["lane"]),
            "--implementer",
            str(ACTIVE_STATE["implementer"]),
            "--validator",
            str(ACTIVE_STATE["validator"]),
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
    _make_scoped_files(tmp_path, state=ACTIVE_STATE, include_runtime_noise=True)
    _write_scope_file(tmp_path, "notes/todo.txt")

    result = subprocess.run(
        [
            str(SCRIPT),
            "--pe-id",
            str(ACTIVE_STATE["pe_id"]),
            "--branch",
            str(ACTIVE_STATE["branch"]),
            "--baseline",
            str(ACTIVE_STATE["baseline"]),
            "--lane",
            str(ACTIVE_STATE["lane"]),
            "--implementer",
            str(ACTIVE_STATE["implementer"]),
            "--validator",
            str(ACTIVE_STATE["validator"]),
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
            str(ACTIVE_STATE["pe_id"]),
            "--branch",
            str(ACTIVE_STATE["branch"]),
            "--baseline",
            str(ACTIVE_STATE["baseline"]),
            "--lane",
            str(ACTIVE_STATE["lane"]),
            "--implementer",
            str(ACTIVE_STATE["implementer"]),
            "--validator",
            str(ACTIVE_STATE["validator"]),
            "--mode",
            "generate",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["pe_id"] == ACTIVE_STATE["pe_id"]
    assert payload["branch"] == ACTIVE_STATE["branch"]
    assert payload["objective"] == ACTIVE_STATE["objective"]
