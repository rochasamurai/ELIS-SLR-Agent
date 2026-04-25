from __future__ import annotations

import subprocess
import pytest

from scripts import implementer_runner_common as common


CURRENT_PE_BODY = """\
## Release context

| Field          | Value                        |
|----------------|------------------------------|
| Release        | ELIS 2-Agent Automation Plan |
| Base branch    | main                         |
| Plan file      | ELIS_2Agent_Automation_Plan_v2_0.md |
| Plan location  | repo root                    |

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

PLAN_BODY = """\
### PE-AUTO-04 · Implementer Agent Runner

| Field | Value |
|---|---|
| Domain | infra |

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | Runner fires upon detecting a change in `CURRENT_PE.md` with status `implementing` |
| AC-2 | Auth via secrets only |
| AC-3 | PR opened by the correct account |
| AC-4 | `HANDOFF.md` committed before the PR is converted to ready |
| AC-5 | Runner exits 1 when budget is exceeded |

---
"""


def test_parse_current_pe_extracts_runner_context(tmp_path):
    path = tmp_path / "CURRENT_PE.md"
    path.write_text(CURRENT_PE_BODY, encoding="utf-8")

    context = common.parse_current_pe(path)

    assert context.pe_id == "PE-AUTO-04"
    assert context.branch == "feature/pe-auto-04-impl-runner"
    assert context.status == "implementing"
    assert context.implementer_engine == "codex"
    assert context.validator_engine == "claude"


def test_acceptance_criteria_are_extracted(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(PLAN_BODY, encoding="utf-8")

    criteria = common.acceptance_criteria_for_pe(plan, "PE-AUTO-04")

    assert len(criteria) == 5
    assert criteria[0].startswith("Runner fires upon detecting")
    assert criteria[-1].startswith("Runner exits 1")


def test_build_prompt_contains_acceptance_criteria(tmp_path):
    repo = tmp_path
    (repo / "AGENTS.md").write_text("AGENTS BODY", encoding="utf-8")
    current_pe = repo / "CURRENT_PE.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan = repo / "ELIS_2Agent_Automation_Plan_v2_0.md"
    plan.write_text(PLAN_BODY, encoding="utf-8")

    prompt = common.build_prompt(
        engine="codex",
        repo_root=repo,
        current_pe_path=current_pe,
        plan_path=plan,
        pe_id="PE-AUTO-04",
    )

    assert "You are the ELIS CODEX Implementer runner for PE-AUTO-04." in prompt
    assert "AGENTS BODY" in prompt
    assert "=== ACTIVE PLAN ACCEPTANCE CRITERIA ===" in prompt
    assert "PR opened by the correct account" in prompt
    assert "Do not open, refresh, or ready the PR yourself." in prompt
    assert "open or refresh the draft PR" not in prompt


def test_budget_guard_fails_when_commit_limit_exceeded():
    with pytest.raises(common.RunnerError, match="Commit budget exceeded"):
        common.ensure_budget(
            21,
            20,
            started_at=100.0,
            now=101.0,
            timeout_seconds=100,
        )


def test_budget_guard_fails_when_timeout_exceeded():
    with pytest.raises(common.RunnerError, match="Runner timeout exceeded"):
        common.ensure_budget(
            1,
            20,
            started_at=100.0,
            now=1000.0,
            timeout_seconds=300,
        )


def test_expected_login_guard_detects_wrong_identity(monkeypatch):
    monkeypatch.setattr(common, "gh_login", lambda: "rochasamurai")

    with pytest.raises(common.RunnerError, match="expected 'elis-codex-bot'"):
        common.ensure_expected_login("codex")


def test_last_commit_touches_returns_true(monkeypatch):
    monkeypatch.setattr(
        common.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            args=["git", "show"],
            returncode=0,
            stdout="HANDOFF.md\nscripts/run_codex_agent.py\n",
            stderr="",
        ),
    )

    assert common.last_commit_touches("HANDOFF.md") is True


def test_last_commit_touches_returns_false(monkeypatch):
    monkeypatch.setattr(
        common.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            args=["git", "show"],
            returncode=0,
            stdout="scripts/run_codex_agent.py\n",
            stderr="",
        ),
    )

    assert common.last_commit_touches("HANDOFF.md") is False


def test_handoff_pr_guard_requires_clean_tree(monkeypatch):
    monkeypatch.setattr(common, "working_tree_clean", lambda: False)
    monkeypatch.setattr(common, "last_commit_touches", lambda _path: True)

    with pytest.raises(common.RunnerError, match="Working tree is dirty"):
        common.ensure_handoff_ready_for_pr()


def test_handoff_pr_guard_requires_handoff_in_last_commit(monkeypatch):
    monkeypatch.setattr(common, "working_tree_clean", lambda: True)
    monkeypatch.setattr(common, "last_commit_touches", lambda _path: False)

    with pytest.raises(common.RunnerError, match="HANDOFF.md is not part"):
        common.ensure_handoff_ready_for_pr()


def test_handoff_pr_guard_accepts_clean_tree_and_handoff_last(monkeypatch):
    monkeypatch.setattr(common, "working_tree_clean", lambda: True)
    monkeypatch.setattr(common, "last_commit_touches", lambda _path: True)

    common.ensure_handoff_ready_for_pr()


def test_run_implementer_checks_handoff_before_pr_operations(monkeypatch):
    events: list[str] = []
    inputs = common.RunnerInputs(
        pe_id="PE-AUTO-04",
        branch="feature/pe-auto-04-impl-runner",
        base_branch="main",
        plan_file="ELIS_2Agent_Automation_Plan_v2_0.md",
        engine="codex",
        max_commits=20,
        timeout_seconds=300,
    )
    context = common.CurrentPEContext(
        pe_id="PE-AUTO-04",
        branch="feature/pe-auto-04-impl-runner",
        base_branch="main",
        plan_file="ELIS_2Agent_Automation_Plan_v2_0.md",
        plan_location="repo root",
        status="implementing",
        implementer_agent="infra-impl-codex",
        validator_agent="infra-val-claude",
        implementer_engine="codex",
        validator_engine="claude",
    )

    monkeypatch.setattr(common, "parse_runner_inputs", lambda _argv, _engine: inputs)
    monkeypatch.setattr(common, "parse_current_pe", lambda _path: context)
    monkeypatch.setattr(common, "ensure_expected_login", lambda _engine: None)
    monkeypatch.setattr(common, "branch_commit_count", lambda _base: 0)
    monkeypatch.setattr(common, "build_prompt", lambda **_kwargs: "prompt")

    def fake_run_cli(*_args, **_kwargs):
        events.append("run_cli")

    def fake_handoff_guard():
        events.append("handoff_guard")

    def fake_create_pr(*_args):
        events.append("create_pr")

    def fake_ready(*_args):
        events.append("ready_pr")

    monkeypatch.setattr(common, "run_cli", fake_run_cli)
    monkeypatch.setattr(common, "ensure_handoff_ready_for_pr", fake_handoff_guard)
    monkeypatch.setattr(common, "create_draft_pr", fake_create_pr)
    monkeypatch.setattr(common, "mark_pr_ready", fake_ready)

    assert common.run_implementer(["runner"], engine="codex") == 0
    assert events == ["run_cli", "handoff_guard", "create_pr", "ready_pr"]


def test_runner_started_at_uses_epoch_env(monkeypatch):
    monkeypatch.setenv("RUNNER_STARTED_AT", "123.5")

    assert common.runner_started_at(now=999.0) == 123.5


def test_runner_started_at_accepts_iso8601(monkeypatch):
    monkeypatch.setenv("RUNNER_STARTED_AT", "2026-04-03T08:58:40Z")

    assert common.runner_started_at(now=999.0) == 1775206720.0


def test_runner_started_at_falls_back_when_invalid(monkeypatch):
    monkeypatch.setenv("RUNNER_STARTED_AT", "not-a-timestamp")

    assert common.runner_started_at(now=321.0) == 321.0
