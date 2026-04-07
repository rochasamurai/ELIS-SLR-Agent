"""Tests for scripts/check_role_registration.py — PM-CHORE skip fix."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_role_registration.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_role_registration", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load()

# Minimal CURRENT_PE.md that includes a PM-CHORE row with '—' agent IDs.
VALID_WITH_PM_CHORE = """\
## Release context

| Field          | Value                                |
|----------------|--------------------------------------|
| Release        | ELIS 2-Agent Automation Plan         |
| Base branch    | main                                 |
| Plan file      | ELIS_2Agent_Automation_Plan_v2_0.md  |
| Plan location  | repo root                            |

## Current PE

| Field   | Value                               |
|---------|-------------------------------------|
| PE      | PE-AUTO-05                          |
| Branch  | feature/pe-auto-05-validator-runner |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| Claude Code | Implementer |
| CODEX       | Validator   |

## Active PE Registry

| PE-ID       | Domain       | Implementer-agentId | Validator-agentId | Branch                               | Status | Last-updated |
|-------------|--------------|---------------------|-------------------|--------------------------------------|--------|--------------|
| PM-CHORE-01 | housekeeping | —                   | —                 | main (direct)                        | merged | 2026-03-03   |
| PE-AUTO-05  | infra        | infra-impl-claude   | infra-val-codex   | feature/pe-auto-05-validator-runner  | implementing | 2026-04-03 |
"""

INVALID_PM_CHORE_NOT_MERGED = """\
## Release context

| Field          | Value                                |
|----------------|--------------------------------------|
| Release        | ELIS 2-Agent Automation Plan         |
| Base branch    | main                                 |
| Plan file      | ELIS_2Agent_Automation_Plan_v2_0.md  |
| Plan location  | repo root                            |

## Current PE

| Field   | Value                               |
|---------|-------------------------------------|
| PE      | PE-AUTO-05                          |
| Branch  | feature/pe-auto-05-validator-runner |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| Claude Code | Implementer |
| CODEX       | Validator   |

## Active PE Registry

| PE-ID       | Domain       | Implementer-agentId | Validator-agentId | Branch        | Status       | Last-updated |
|-------------|--------------|---------------------|-------------------|---------------|--------------|--------------|
| PM-CHORE-99 | housekeeping | —                   | —                 | main (direct) | implementing | 2026-04-01   |
"""


def test_pm_chore_row_with_dash_agent_ids_passes(tmp_path, monkeypatch):
    """PM-CHORE rows with '—' agent IDs must not cause a failure when merged."""
    pe_file = tmp_path / "CURRENT_PE.md"
    pe_file.write_text(VALID_WITH_PM_CHORE, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(pe_file))
    assert MODULE.main() == 0


def test_pm_chore_row_not_merged_fails(tmp_path, monkeypatch):
    """PM-CHORE rows with '—' agent IDs and non-merged status must fail."""
    pe_file = tmp_path / "CURRENT_PE.md"
    pe_file.write_text(INVALID_PM_CHORE_NOT_MERGED, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(pe_file))
    assert MODULE.main() == 1
