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

VALID_WITH_GEMINI_VALIDATOR = """\
## Release context

| Field          | Value                                |
|----------------|--------------------------------------|
| Release        | ELIS Hybrid SLR Execution Plan       |
| Base branch    | main                                 |
| Plan file      | ELIS_MultiAgent_Implementation_Plan_v1_8_1.md |
| Plan location  | repo root                            |

## Current PE

| Field   | Value                                 |
|---------|---------------------------------------|
| PE      | PE-SLR-01                             |
| Branch  | feature/pe-slr-01-harvest-workflow-contract |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Gemini CLI  | Validator   |

## Active PE Registry

| PE-ID       | Domain       | Implementer-agentId | Validator-agentId | Branch                                      | Status          | Last-updated |
|-------------|--------------|---------------------|-------------------|---------------------------------------------|-----------------|--------------|
| PE-SLR-01   | slr          | prog-impl-codex     | gemini-cli        | feature/pe-slr-01-harvest-workflow-contract | gate-2-pending  | 2026-04-13   |
"""

INVALID_GEMINI_ROLE_MISMATCH = """\
## Release context

| Field          | Value                                |
|----------------|--------------------------------------|
| Release        | ELIS Hybrid SLR Execution Plan       |
| Base branch    | main                                 |
| Plan file      | ELIS_MultiAgent_Implementation_Plan_v1_8_1.md |
| Plan location  | repo root                            |

## Current PE

| Field   | Value                                 |
|---------|---------------------------------------|
| PE      | PE-SLR-01                             |
| Branch  | feature/pe-slr-01-harvest-workflow-contract |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Validator   |
| Gemini CLI  | Implementer |

## Active PE Registry

| PE-ID       | Domain       | Implementer-agentId | Validator-agentId | Branch                                      | Status          | Last-updated |
|-------------|--------------|---------------------|-------------------|---------------------------------------------|-----------------|--------------|
| PE-SLR-01   | slr          | prog-impl-codex     | gemini-cli        | feature/pe-slr-01-harvest-workflow-contract | gate-2-pending  | 2026-04-13   |
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


def test_gemini_validator_role_registration_passes(tmp_path, monkeypatch):
    pe_file = tmp_path / "CURRENT_PE.md"
    pe_file.write_text(VALID_WITH_GEMINI_VALIDATOR, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(pe_file))
    assert MODULE.main() == 0


def test_role_table_must_match_registry_engines(tmp_path, monkeypatch):
    pe_file = tmp_path / "CURRENT_PE.md"
    pe_file.write_text(INVALID_GEMINI_ROLE_MISMATCH, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(pe_file))
    assert MODULE.main() == 1


VALID_WITH_SUPERSEDED_SAME_DOMAIN = """\
## Release context

| Field          | Value                                          |
|----------------|------------------------------------------------|
| Release        | ELIS Hybrid SLR Execution Plan · v1.8.2        |
| Base branch    | main                                           |
| Plan file      | ELIS_MultiAgent_Implementation_Plan_v1_8_2.md  |
| Plan location  | repo root                                      |

## Current PE

| Field   | Value                                                           |
|---------|-----------------------------------------------------------------|
| PE      | PE-INFRA-SLR-01                                                 |
| Branch  | feature/pe-infra-slr-01-role-based-agent-surface-normalisation  |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| Claude Code | Implementer |
| CODEX       | Validator   |

## Active PE Registry

| PE-ID           | Domain | Implementer-agentId | Validator-agentId | Branch                                                          | Status       | Last-updated |
|-----------------|--------|---------------------|-------------------|-----------------------------------------------------------------|--------------|--------------|
| PE-AUTO-13      | infra  | infra-impl-claude   | infra-val-codex   | feature/pe-auto-13-gate2-retrigger                              | superseded   | 2026-04-12   |
| PE-INFRA-SLR-01 | infra  | infra-impl-claude   | infra-val-codex   | feature/pe-infra-slr-01-role-based-agent-surface-normalisation  | implementing | 2026-04-14   |
"""


def test_superseded_row_excluded_from_alternation_check(tmp_path, monkeypatch):
    """Superseded rows must not participate in the consecutive-engine alternation check."""
    pe_file = tmp_path / "CURRENT_PE.md"
    pe_file.write_text(VALID_WITH_SUPERSEDED_SAME_DOMAIN, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(pe_file))
    assert MODULE.main() == 0
