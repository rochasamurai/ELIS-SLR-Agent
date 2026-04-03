from __future__ import annotations

from pathlib import Path

from scripts import dispatch_implementer_runner


CURRENT_PE_IMPLEMENTING = """\
## Release context

| Field          | Value                       |
|----------------|-----------------------------|
| Release        | ELIS 2-Agent Automation Plan |
| Base branch    | main                        |
| Plan file      | ELIS_2Agent_Automation_Plan_v2_0.md |
| Plan location  | repo root                   |

## Current PE

| Field   | Value                          |
|---------|--------------------------------|
| PE      | PE-AUTO-04                     |
| Branch  | feature/pe-auto-04-impl-runner |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |

## Active PE Registry

| PE-ID       | Domain | Implementer-agentId | Validator-agentId | Branch                          | Status       | Last-updated |
|-------------|--------|---------------------|-------------------|---------------------------------|--------------|--------------|
| PE-AUTO-03  | infra  | infra-impl-claude   | infra-val-codex   | feature/pe-auto-03              | merged       | 2026-04-03   |
| PE-AUTO-04  | infra  | infra-impl-codex    | infra-val-claude  | feature/pe-auto-04-impl-runner  | implementing | 2026-04-03   |
"""


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_dispatches_when_active_pe_is_implementing(tmp_path, monkeypatch):
    current_pe = tmp_path / "CURRENT_PE.md"
    output = tmp_path / "github_output.txt"
    _write(current_pe, CURRENT_PE_IMPLEMENTING)
    monkeypatch.setenv("CURRENT_PE_PATH", str(current_pe))
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    assert dispatch_implementer_runner.main() == 0

    text = output.read_text(encoding="utf-8")
    assert "should_dispatch=true" in text
    assert "engine=codex" in text
    assert "branch=feature/pe-auto-04-impl-runner" in text


def test_skips_when_active_pe_not_implementing(tmp_path, monkeypatch):
    current_pe = tmp_path / "CURRENT_PE.md"
    output = tmp_path / "github_output.txt"
    _write(
        current_pe,
        CURRENT_PE_IMPLEMENTING.replace("implementing", "planning", 1),
    )
    monkeypatch.setenv("CURRENT_PE_PATH", str(current_pe))
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    assert dispatch_implementer_runner.main() == 0
    assert "should_dispatch=false" in output.read_text(encoding="utf-8")
