"""Tests for scripts/check_current_pe.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_current_pe.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_current_pe", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load()


VALID_CURRENT_PE = """\
# Current PE Assignment

## Release context

| Field          | Value                               |
|----------------|-------------------------------------|
| Release        | ELIS 2-Agent Automation Plan        |
| Base branch    | main                                |
| Plan file      | ELIS_2Agent_Automation_Plan_v2_0.md |
| Plan location  | repo root                           |

## Current PE

| Field   | Value                                         |
|---------|-----------------------------------------------|
| PE      | PE-AUTO-02                                    |
| Branch  | feature/pe-auto-02-current-pe-ci-validation   |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |

## Active PE Registry

| PE-ID       | Domain | Implementer-agentId | Validator-agentId | Branch                                       | Status        | Last-updated |
|-------------|--------|---------------------|-------------------|----------------------------------------------|---------------|--------------|
| PE-AUTO-01  | infra  | infra-impl-claude   | infra-val-codex   | feature/pe-auto-01-bot-accounts-pats         | merged        | 2026-03-28   |
| PE-AUTO-02  | infra  | infra-impl-codex    | infra-val-claude  | feature/pe-auto-02-current-pe-ci-validation  | implementing  | 2026-03-28   |
"""


def _write_current_pe(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "CURRENT_PE.md"
    path.write_text(content, encoding="utf-8")
    return path


def test_main_accepts_valid_current_pe(tmp_path, monkeypatch, capsys):
    path = _write_current_pe(tmp_path, VALID_CURRENT_PE)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 0
    assert "CURRENT_PE.md OK" in capsys.readouterr().out


def test_blank_release_field_fails(tmp_path, monkeypatch):
    content = VALID_CURRENT_PE.replace(
        "| Plan file      | ELIS_2Agent_Automation_Plan_v2_0.md |",
        "| Plan file      |                                     |",
    )
    path = _write_current_pe(tmp_path, content)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 1


def test_invalid_pe_format_fails(tmp_path, monkeypatch):
    content = VALID_CURRENT_PE.replace("PE-AUTO-02", "PE-auto-02", 1)
    path = _write_current_pe(tmp_path, content)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 1


def test_invalid_branch_format_fails(tmp_path, monkeypatch):
    content = VALID_CURRENT_PE.replace(
        "feature/pe-auto-02-current-pe-ci-validation",
        "bugfix/current-pe",
        1,
    )
    path = _write_current_pe(tmp_path, content)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 1


def test_active_pe_status_must_be_planning_or_implementing(tmp_path, monkeypatch):
    content = VALID_CURRENT_PE.replace(
        "| PE-AUTO-02  | infra  | infra-impl-codex    | infra-val-claude  | feature/pe-auto-02-current-pe-ci-validation  | implementing  | 2026-03-28   |",
        "| PE-AUTO-02  | infra  | infra-impl-codex    | infra-val-claude  | feature/pe-auto-02-current-pe-ci-validation  | validating    | 2026-03-28   |",
    )
    path = _write_current_pe(tmp_path, content)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 1


def test_alternation_rule_violation_fails(tmp_path, monkeypatch):
    content = VALID_CURRENT_PE.replace(
        "| PE-AUTO-02  | infra  | infra-impl-codex    | infra-val-claude  | feature/pe-auto-02-current-pe-ci-validation  | implementing  | 2026-03-28   |",
        "| PE-AUTO-02  | infra  | infra-impl-claude   | infra-val-codex   | feature/pe-auto-02-current-pe-ci-validation  | implementing  | 2026-03-28   |",
    )
    path = _write_current_pe(tmp_path, content)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 1


def test_same_engine_roles_fail(tmp_path, monkeypatch):
    content = VALID_CURRENT_PE.replace(
        "| PE-AUTO-02  | infra  | infra-impl-codex    | infra-val-claude  | feature/pe-auto-02-current-pe-ci-validation  | implementing  | 2026-03-28   |",
        "| PE-AUTO-02  | infra  | infra-impl-codex    | infra-val-codex   | feature/pe-auto-02-current-pe-ci-validation  | implementing  | 2026-03-28   |",
    )
    path = _write_current_pe(tmp_path, content)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 1


def test_missing_registry_row_for_current_pe_fails(tmp_path, monkeypatch):
    content = VALID_CURRENT_PE.replace(
        "| PE-AUTO-02  | infra  | infra-impl-codex    | infra-val-claude  | feature/pe-auto-02-current-pe-ci-validation  | implementing  | 2026-03-28   |\n",
        "",
    )
    path = _write_current_pe(tmp_path, content)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 1


def test_branch_mismatch_between_current_and_registry_fails(tmp_path, monkeypatch):
    content = VALID_CURRENT_PE.replace(
        "feature/pe-auto-02-current-pe-ci-validation  | implementing",
        "feature/pe-auto-02-wrong-branch             | implementing",
    )
    path = _write_current_pe(tmp_path, content)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 1


def test_agent_roles_table_must_match_registry_engines(tmp_path, monkeypatch):
    content = VALID_CURRENT_PE.replace(
        "| CODEX       | Implementer |",
        "| CODEX       | Validator   |",
    )
    content = content.replace(
        "| Claude Code | Validator   |",
        "| Claude Code | Implementer |",
    )
    path = _write_current_pe(tmp_path, content)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 1


def test_plan_complete_mode_is_valid(tmp_path, monkeypatch, capsys):
    content = (
        VALID_CURRENT_PE.replace(
            "| PE      | PE-AUTO-02                                    |",
            "| PE      | —                                             |",
        )
        .replace(
            "| Branch  | feature/pe-auto-02-current-pe-ci-validation   |",
            "| Branch  | —                                             |",
        )
        .replace(
            "| CODEX       | Implementer |",
            "| CODEX       | —           |",
        )
        .replace(
            "| Claude Code | Validator   |",
            "| Claude Code | —           |",
        )
        .replace(
            "## Agent roles\n",
            "## Agent roles\n\n> **Plan complete.** All PEs are merged.\n\n",
        )
    )
    path = _write_current_pe(tmp_path, content)
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert MODULE.main() == 0
    assert "plan-complete mode" in capsys.readouterr().out
