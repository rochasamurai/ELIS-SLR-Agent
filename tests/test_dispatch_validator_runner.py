"""Tests for dispatch_validator_runner.py — PE-AUTO-05."""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import dispatch_validator_runner

CURRENT_PE_BODY_READY = """\
## Release context

| Field          | Value                        |
|----------------|------------------------------|
| Release        | ELIS 2-Agent Automation Plan |
| Base branch    | main                         |
| Plan file      | ELIS_2Agent_Automation_Plan_v2_0.md |
| Plan location  | repo root                    |

## Current PE

| Field   | Value                              |
|---------|------------------------------------|
| PE      | PE-AUTO-05                         |
| Branch  | feature/pe-auto-05-validator-runner |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| Claude Code | Implementer |
| CODEX       | Validator   |

## Active PE Registry

| PE-ID       | Domain | Implementer-agentId | Validator-agentId | Branch                               | Status          | Last-updated |
|-------------|--------|---------------------|-------------------|--------------------------------------|-----------------|--------------|
| PE-AUTO-04  | infra  | infra-impl-codex    | infra-val-claude  | feature/pe-auto-04-impl-runner       | merged          | 2026-04-03   |
| PE-AUTO-05  | infra  | infra-impl-claude   | infra-val-codex   | feature/pe-auto-05-validator-runner  | gate-1-pending  | 2026-04-03   |
"""

CURRENT_PE_BODY_IMPLEMENTING = CURRENT_PE_BODY_READY.replace(
    "gate-1-pending", "implementing"
)

HANDOFF_BODY = """\
# HANDOFF — PE-AUTO-05

## Status Packet

### 6.1
- Example evidence

### 6.2
- Example evidence

### 6.3
- Example evidence

### 6.4
- Example evidence

### 6.5
- Example evidence

## Summary

Done.

## Files Changed

- scripts/example.py

## Acceptance Criteria

- AC-1 satisfied

## Validation Commands

- pytest -q
"""


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _fake_gh_pr_view(branch: str):
    """Return a fake subprocess.run that responds to gh pr view with the given branch."""

    def fake_run(cmd, **_kwargs):
        if "gh" in cmd and "pr" in cmd and "view" in cmd:
            return subprocess.CompletedProcess(
                cmd, 0, stdout=f'{{"headRefName": "{branch}"}}', stderr=""
            )
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    return fake_run


def test_dispatches_when_pr_branch_matches_and_pe_ready(tmp_path, monkeypatch):
    current_pe = tmp_path / "CURRENT_PE.md"
    handoff = tmp_path / "HANDOFF.md"
    output = tmp_path / "github_output.txt"
    _write(current_pe, CURRENT_PE_BODY_READY)
    _write(handoff, HANDOFF_BODY)
    monkeypatch.setenv("CURRENT_PE_PATH", str(current_pe))
    monkeypatch.setenv("HANDOFF_PATH", str(handoff))
    monkeypatch.setenv("PR_NUMBER", "312")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setattr(
        dispatch_validator_runner.subprocess,
        "run",
        _fake_gh_pr_view("feature/pe-auto-05-validator-runner"),
    )

    assert dispatch_validator_runner.main() == 0

    text = output.read_text(encoding="utf-8")
    assert "should_dispatch=true" in text
    assert "engine=codex" in text
    assert "pr_number=312" in text


def test_rejects_when_pe_still_implementing(tmp_path, monkeypatch):
    current_pe = tmp_path / "CURRENT_PE.md"
    handoff = tmp_path / "HANDOFF.md"
    _write(current_pe, CURRENT_PE_BODY_IMPLEMENTING)
    _write(handoff, HANDOFF_BODY)
    monkeypatch.setenv("CURRENT_PE_PATH", str(current_pe))
    monkeypatch.setenv("HANDOFF_PATH", str(handoff))
    monkeypatch.setenv("PR_NUMBER", "312")
    monkeypatch.setattr(
        dispatch_validator_runner.subprocess,
        "run",
        _fake_gh_pr_view("feature/pe-auto-05-validator-runner"),
    )

    assert dispatch_validator_runner.main() == 1


def test_rejects_when_handoff_is_incomplete(tmp_path, monkeypatch):
    current_pe = tmp_path / "CURRENT_PE.md"
    handoff = tmp_path / "HANDOFF.md"
    _write(current_pe, CURRENT_PE_BODY_READY)
    _write(handoff, "# HANDOFF\n")
    monkeypatch.setenv("CURRENT_PE_PATH", str(current_pe))
    monkeypatch.setenv("HANDOFF_PATH", str(handoff))
    monkeypatch.setenv("PR_NUMBER", "312")
    monkeypatch.setattr(
        dispatch_validator_runner.subprocess,
        "run",
        _fake_gh_pr_view("feature/pe-auto-05-validator-runner"),
    )

    assert dispatch_validator_runner.main() == 1


def test_skips_when_pr_branch_does_not_match(tmp_path, monkeypatch):
    current_pe = tmp_path / "CURRENT_PE.md"
    handoff = tmp_path / "HANDOFF.md"
    output = tmp_path / "github_output.txt"
    _write(current_pe, CURRENT_PE_BODY_READY)
    _write(handoff, HANDOFF_BODY)
    monkeypatch.setenv("CURRENT_PE_PATH", str(current_pe))
    monkeypatch.setenv("HANDOFF_PATH", str(handoff))
    monkeypatch.setenv("PR_NUMBER", "299")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setattr(
        dispatch_validator_runner.subprocess,
        "run",
        _fake_gh_pr_view("feature/pe-auto-04-impl-runner"),  # old branch
    )

    assert dispatch_validator_runner.main() == 0
    assert "should_dispatch=false" in output.read_text(encoding="utf-8")


def test_fails_when_pr_number_not_set(tmp_path, monkeypatch):
    current_pe = tmp_path / "CURRENT_PE.md"
    handoff = tmp_path / "HANDOFF.md"
    _write(current_pe, CURRENT_PE_BODY_READY)
    _write(handoff, HANDOFF_BODY)
    monkeypatch.setenv("CURRENT_PE_PATH", str(current_pe))
    monkeypatch.setenv("HANDOFF_PATH", str(handoff))
    monkeypatch.delenv("PR_NUMBER", raising=False)

    assert dispatch_validator_runner.main() == 1
