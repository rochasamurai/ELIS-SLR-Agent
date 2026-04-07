"""Tests for validator_runner_common.py — PE-AUTO-05."""

from __future__ import annotations

import subprocess

import pytest

from scripts import validator_runner_common as common

CURRENT_PE_BODY = """\
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

| PE-ID       | Domain | Implementer-agentId | Validator-agentId | Branch                               | Status       | Last-updated |
|-------------|--------|---------------------|-------------------|--------------------------------------|--------------|--------------|
| PE-AUTO-04  | infra  | infra-impl-codex    | infra-val-claude  | feature/pe-auto-04-impl-runner       | merged       | 2026-04-03   |
| PE-AUTO-05  | infra  | infra-impl-claude   | infra-val-codex   | feature/pe-auto-05-validator-runner  | implementing | 2026-04-03   |
"""

PLAN_BODY = """\
### PE-AUTO-05 · Validator Agent Runner

| Field | Value |
|---|---|
| Domain | infra |

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | Validator triggers automatically after Gate 1 comment |
| AC-2 | REVIEW_PE*.md committed on the branch with verbatim evidence |
| AC-3 | Formal GitHub Review posted by the opposite account |
| AC-4 | Gate 2 reads the verdict and auto-merges on PASS |
| AC-5 | On FAIL: Implementer receives fix assignment via PR comment from elis-pm-bot |

---
"""

REVIEW_PASS = """\
# REVIEW_PE_AUTO_05.md

### Verdict

PASS

### Gate results

```
pytest: 640 passed
```

### Scope

```
A  scripts/validator_runner_common.py
```

### Required fixes

None.

### Evidence

```
python scripts/check_review.py
REVIEW evidence check PASS
```
"""

REVIEW_FAIL = REVIEW_PASS.replace("PASS\n", "FAIL\n").replace(
    "None.", "- AC-3 not satisfied."
)


# ---------------------------------------------------------------------------
# review_file_name
# ---------------------------------------------------------------------------


def test_review_file_name_hyphen_to_underscore():
    assert common.review_file_name("PE-AUTO-05") == "REVIEW_PE_AUTO_05.md"


def test_review_file_name_other_domain():
    assert common.review_file_name("PE-MS-01") == "REVIEW_PE_MS_01.md"


# ---------------------------------------------------------------------------
# read_verdict
# ---------------------------------------------------------------------------


def test_read_verdict_pass(tmp_path):
    (tmp_path / "REVIEW_PE_AUTO_05.md").write_text(REVIEW_PASS, encoding="utf-8")
    assert common.read_verdict(tmp_path, "PE-AUTO-05") == "PASS"


def test_read_verdict_fail(tmp_path):
    (tmp_path / "REVIEW_PE_AUTO_05.md").write_text(REVIEW_FAIL, encoding="utf-8")
    assert common.read_verdict(tmp_path, "PE-AUTO-05") == "FAIL"


def test_read_verdict_not_found(tmp_path):
    assert common.read_verdict(tmp_path, "PE-AUTO-05") == "NOT_FOUND"


# ---------------------------------------------------------------------------
# build_validator_prompt
# ---------------------------------------------------------------------------


def test_build_validator_prompt_contains_required_elements(tmp_path):
    (tmp_path / "AGENTS.md").write_text("AGENTS BODY", encoding="utf-8")
    current_pe = tmp_path / "CURRENT_PE.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan = tmp_path / "ELIS_2Agent_Automation_Plan_v2_0.md"
    plan.write_text(PLAN_BODY, encoding="utf-8")

    prompt = common.build_validator_prompt(
        engine="codex",
        repo_root=tmp_path,
        current_pe_path=current_pe,
        plan_path=plan,
        pe_id="PE-AUTO-05",
        pr_number="312",
    )

    assert "You are the ELIS CODEX Validator runner for PE-AUTO-05." in prompt
    assert "REVIEW_PE_AUTO_05.md" in prompt
    assert "gh pr review 312" in prompt
    assert "Validator triggers automatically" in prompt
    assert "AGENTS BODY" in prompt


# ---------------------------------------------------------------------------
# parse_validator_inputs
# ---------------------------------------------------------------------------


def test_parse_validator_inputs_all_required():
    inputs = common.parse_validator_inputs(
        [
            "run_codex_validator.py",
            "--pe-id",
            "PE-AUTO-05",
            "--branch",
            "feature/pe-auto-05-validator-runner",
            "--plan",
            "ELIS_2Agent_Automation_Plan_v2_0.md",
            "--pr-number",
            "312",
        ],
        engine="codex",
    )
    assert inputs.pe_id == "PE-AUTO-05"
    assert inputs.branch == "feature/pe-auto-05-validator-runner"
    assert inputs.pr_number == "312"
    assert inputs.base_branch == "main"  # default


def test_parse_validator_inputs_missing_pr_number_fails():
    with pytest.raises(common.RunnerError, match="pr.number"):
        common.parse_validator_inputs(
            [
                "run_codex_validator.py",
                "--pe-id",
                "PE-AUTO-05",
                "--branch",
                "feature/pe-auto-05-validator-runner",
                "--plan",
                "ELIS_2Agent_Automation_Plan_v2_0.md",
            ],
            engine="codex",
        )


# ---------------------------------------------------------------------------
# post_fail_assignment
# ---------------------------------------------------------------------------


def test_post_fail_assignment_calls_gh_codex(monkeypatch):
    calls = []

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(common.subprocess, "run", fake_run)
    common.post_fail_assignment("312", "codex")

    assert any("gh" in c[0] for c in calls)
    assert "@codex" in " ".join(calls[0][calls[0].index("--body") + 1 :])


def test_post_fail_assignment_calls_gh_claude(monkeypatch):
    calls = []

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(common.subprocess, "run", fake_run)
    common.post_fail_assignment("312", "claude")

    body_arg = calls[0][calls[0].index("--body") + 1]
    assert "@claude-code" in body_arg


def test_post_fail_assignment_raises_on_gh_error(monkeypatch):
    def fake_run(cmd, **_kwargs):
        return subprocess.CompletedProcess(
            cmd, 1, stdout="", stderr="gh: authentication failed"
        )

    monkeypatch.setattr(common.subprocess, "run", fake_run)
    with pytest.raises(common.RunnerError, match="authentication failed"):
        common.post_fail_assignment("312", "codex")


# ---------------------------------------------------------------------------
# verify_review_committed
# ---------------------------------------------------------------------------


def test_verify_review_committed_passes_when_file_in_log(monkeypatch):
    monkeypatch.setattr(
        common.subprocess,
        "run",
        lambda *_a, **_kw: subprocess.CompletedProcess(
            [], 0, stdout="REVIEW_PE_AUTO_05.md\nsome_other.py\n", stderr=""
        ),
    )
    common.verify_review_committed("PE-AUTO-05", "main")  # must not raise


def test_verify_review_committed_fails_when_file_absent(monkeypatch):
    monkeypatch.setattr(
        common.subprocess,
        "run",
        lambda *_a, **_kw: subprocess.CompletedProcess(
            [], 0, stdout="scripts/other.py\n", stderr=""
        ),
    )
    with pytest.raises(common.RunnerError, match="not found in commits"):
        common.verify_review_committed("PE-AUTO-05", "main")


# ---------------------------------------------------------------------------
# verify_formal_review_posted
# ---------------------------------------------------------------------------


def test_verify_formal_review_posted_passes_with_review(monkeypatch):
    monkeypatch.setattr(
        common.subprocess,
        "run",
        lambda *_a, **_kw: subprocess.CompletedProcess(
            [],
            0,
            stdout='{"reviews": [{"state": "APPROVED", "author": {"login": "elis-codex-bot"}}]}',
            stderr="",
        ),
    )
    common.verify_formal_review_posted("312")  # must not raise


def test_verify_formal_review_posted_fails_with_no_reviews(monkeypatch):
    monkeypatch.setattr(
        common.subprocess,
        "run",
        lambda *_a, **_kw: subprocess.CompletedProcess(
            [], 0, stdout='{"reviews": []}', stderr=""
        ),
    )
    with pytest.raises(common.RunnerError, match="No formal GitHub review"):
        common.verify_formal_review_posted("312")


def test_verify_formal_review_posted_passes_with_correct_login(monkeypatch):
    monkeypatch.setattr(
        common.subprocess,
        "run",
        lambda *_a, **_kw: subprocess.CompletedProcess(
            [],
            0,
            stdout='{"reviews": [{"state": "APPROVED", "author": {"login": "elis-codex-bot"}}]}',
            stderr="",
        ),
    )
    common.verify_formal_review_posted(
        "312", expected_login="elis-codex-bot"
    )  # must not raise


def test_verify_formal_review_posted_fails_with_wrong_login(monkeypatch):
    monkeypatch.setattr(
        common.subprocess,
        "run",
        lambda *_a, **_kw: subprocess.CompletedProcess(
            [],
            0,
            stdout='{"reviews": [{"state": "APPROVED", "author": {"login": "some-other-bot"}}]}',
            stderr="",
        ),
    )
    with pytest.raises(common.RunnerError, match="wrong identity"):
        common.verify_formal_review_posted("312", expected_login="elis-codex-bot")


# ---------------------------------------------------------------------------
# run_validator — engine mismatch guard
# ---------------------------------------------------------------------------


def test_run_validator_rejects_wrong_engine(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "CURRENT_PE.md").write_text(CURRENT_PE_BODY, encoding="utf-8")
    (tmp_path / "ELIS_2Agent_Automation_Plan_v2_0.md").write_text(
        PLAN_BODY, encoding="utf-8"
    )

    # Validator engine in CURRENT_PE_BODY is 'codex' — passing 'claude' must fail.
    rc = common.run_validator(
        [
            "run_claude_validator.py",
            "--pe-id",
            "PE-AUTO-05",
            "--branch",
            "feature/pe-auto-05-validator-runner",
            "--plan",
            "ELIS_2Agent_Automation_Plan_v2_0.md",
            "--pr-number",
            "312",
        ],
        engine="claude",
    )
    assert rc == 1


def test_run_validator_enforces_expected_reviewer_login(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "AGENTS.md").write_text("AGENTS BODY", encoding="utf-8")
    (tmp_path / "CURRENT_PE.md").write_text(CURRENT_PE_BODY, encoding="utf-8")
    (tmp_path / "ELIS_2Agent_Automation_Plan_v2_0.md").write_text(
        PLAN_BODY, encoding="utf-8"
    )

    captured: dict[str, str] = {}

    monkeypatch.setattr(common, "ensure_expected_login", lambda _engine: None)
    monkeypatch.setattr(common, "run_cli", lambda _engine, _prompt: None)
    monkeypatch.setattr(
        common, "verify_review_committed", lambda _pe_id, _base_branch: None
    )

    def fake_verify_formal_review_posted(
        pr_number: str, expected_login: str | None = None
    ):
        captured["pr_number"] = pr_number
        captured["expected_login"] = expected_login or ""

    monkeypatch.setattr(
        common, "verify_formal_review_posted", fake_verify_formal_review_posted
    )
    monkeypatch.setattr(common, "read_verdict", lambda _repo_root, _pe_id: "PASS")

    rc = common.run_validator(
        [
            "run_codex_validator.py",
            "--pe-id",
            "PE-AUTO-05",
            "--branch",
            "feature/pe-auto-05-validator-runner",
            "--plan",
            "ELIS_2Agent_Automation_Plan_v2_0.md",
            "--pr-number",
            "312",
            "--base-branch",
            "main",
        ],
        engine="codex",
    )

    assert rc == 0
    assert captured["pr_number"] == "312"
    assert captured["expected_login"] == "elis-codex-bot"
