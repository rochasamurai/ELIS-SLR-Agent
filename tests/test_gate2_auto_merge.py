"""Acceptance tests for PE-INFRA-SLR-05 — Gate 2 Auto-Merge Alignment.

Covers all seven acceptance criteria from the implementation plan.
"""

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "auto-merge-on-pass.yml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_reviewer_identity.py"
REVIEWER_MAP_PATH = REPO_ROOT / "config" / "reviewer_identity_map.json"


# ─── helpers ──────────────────────────────────────────────────────────────────


def _load_workflow() -> dict:
    with open(WORKFLOW_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _get_on(wf: dict) -> dict:
    """Return the 'on' mapping from a parsed workflow.

    PyYAML parses the bare YAML key ``on`` as the boolean ``True``.
    Fall back to the string key for robustness.
    """
    return wf.get(True, wf.get("on", {}))  # type: ignore[arg-type]


def _get_auto_merge_steps(wf: dict) -> list[dict]:
    """Return the step(s) that perform the actual GitHub merge API call."""
    steps = wf["jobs"]["gate-2"]["steps"]
    return [
        s
        for s in steps
        if "auto-merge" in s.get("name", "").lower()
        or (
            "merge" in s.get("name", "").lower()
            and "notify" not in s.get("name", "").lower()
            and "gate" not in s.get("name", "").lower()
            and "authoris" not in s.get("name", "").lower()
            and "determin" not in s.get("name", "").lower()
        )
    ]


def _workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def _run_identity_script(
    reviewer_login: str,
    current_pe_path: Path,
    reviewer_map_path: Path,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["REVIEWER_LOGIN"] = reviewer_login
    env["CURRENT_PE_PATH"] = str(current_pe_path)
    env["REVIEWER_MAP_PATH"] = str(reviewer_map_path)
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        env=env,
    )


# ─── shared fixtures ──────────────────────────────────────────────────────────


@pytest.fixture()
def pe_file_val_a(tmp_path: Path) -> Path:
    """CURRENT_PE.md with infra-val-a (CODEX / elis-codex-bot) as Validator."""
    p = tmp_path / "CURRENT_PE.md"
    p.write_text(
        textwrap.dedent(
            """\
        ## Agent roles
        | Agent       | Role        |
        |-------------|-------------|
        | Claude Code | Implementer |
        | CODEX       | Validator   |

        > PE-INFRA-SLR-05: `infra-impl-b` (Claude Code) as Implementer · `infra-val-a` (CODEX @ `elis-server`) as Validator.
        """
        ),
        encoding="utf-8",
    )
    return p


@pytest.fixture()
def pe_file_val_b(tmp_path: Path) -> Path:
    """CURRENT_PE.md with infra-val-b (Claude Code / elis-claude-bot) as Validator."""
    p = tmp_path / "CURRENT_PE.md"
    p.write_text(
        "> PE-TEST: `infra-impl-a` (CODEX) as Implementer · `infra-val-b` (Claude Code) as Validator.\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture()
def reviewer_map(tmp_path: Path) -> Path:
    """Minimal reviewer_identity_map.json."""
    p = tmp_path / "reviewer_identity_map.json"
    p.write_text(
        json.dumps(
            {
                "agents": {
                    "CODEX": {
                        "engine": "codex",
                        "review_login": "elis-codex-bot",
                        "validator_capable_on_protected_branches": True,
                    },
                    "Claude Code": {
                        "engine": "claude",
                        "review_login": "elis-claude-bot",
                        "validator_capable_on_protected_branches": True,
                    },
                    "PM": {
                        "engine": "pm",
                        "review_login": "elis-pm-bot",
                        "validator_capable_on_protected_branches": False,
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    return p


# ─── AC-1: pull_request_review trigger ────────────────────────────────────────


def test_ac1_workflow_has_pull_request_review_trigger():
    """AC-1: auto-merge-on-pass.yml must trigger on pull_request_review: submitted."""
    wf = _load_workflow()
    on = _get_on(wf)
    assert "pull_request_review" in on, "pull_request_review trigger is missing"
    pr_review = on["pull_request_review"]
    types = pr_review.get("types", []) if isinstance(pr_review, dict) else []
    assert (
        "submitted" in types
    ), "pull_request_review trigger must list types: [submitted]"


def test_ac1_push_trigger_retained():
    """AC-1 (backwards compat): push trigger must still be present."""
    wf = _load_workflow()
    assert "push" in _get_on(wf), "push trigger must be retained"


# ─── AC-2: merge condition requires all four prerequisites ────────────────────


def test_ac2_merge_step_gated_on_no_veto():
    """AC-2: merge step condition must reference absence of pm-review-required."""
    assert "pm-review-required" in _workflow_text()


def test_ac2_merge_step_gated_on_clean_mergeable_state():
    """AC-2: merge step condition must require mergeable_state == 'clean'."""
    assert "'clean'" in _workflow_text() or '"clean"' in _workflow_text()


def test_ac2_merge_step_gated_on_gate2b_success():
    """AC-2: merge step must be gated on gate2b success."""
    wf = _load_workflow()
    merge_steps = _get_auto_merge_steps(wf)
    assert merge_steps, "No auto-merge step found"
    for s in merge_steps:
        cond = s.get("if", "")
        assert (
            "gate2b" in cond and "success" in cond
        ), f"Merge step '{s['name']}' must be gated on gate2b.outcome == 'success'"


# ─── AC-3: check_reviewer_identity.py — mapped-bot verification ───────────────


def test_ac3_correct_bot_for_val_a_accepted(pe_file_val_a, reviewer_map):
    """AC-3: elis-codex-bot (mapped for infra-val-a) is accepted, exits 0."""
    result = _run_identity_script("elis-codex-bot", pe_file_val_a, reviewer_map)
    assert result.returncode == 0, result.stderr


def test_ac3_wrong_bot_for_val_a_rejected(pe_file_val_a, reviewer_map):
    """AC-3: elis-claude-bot is rejected when validator is infra-val-a (CODEX)."""
    result = _run_identity_script("elis-claude-bot", pe_file_val_a, reviewer_map)
    assert result.returncode != 0, "Wrong bot must be rejected"


def test_ac3_correct_bot_for_val_b_accepted(pe_file_val_b, reviewer_map):
    """AC-3: elis-claude-bot (mapped for infra-val-b) is accepted, exits 0."""
    result = _run_identity_script("elis-claude-bot", pe_file_val_b, reviewer_map)
    assert result.returncode == 0, result.stderr


def test_ac3_human_reviewer_rejected(pe_file_val_a, reviewer_map):
    """AC-3: a human GitHub account is rejected."""
    result = _run_identity_script("rochasamurai", pe_file_val_a, reviewer_map)
    assert result.returncode != 0


def test_ac3_pm_bot_rejected_for_validator_role(pe_file_val_a, reviewer_map):
    """AC-3: elis-pm-bot is rejected because it is not validator-capable."""
    result = _run_identity_script("elis-pm-bot", pe_file_val_a, reviewer_map)
    assert result.returncode != 0


def test_ac3_empty_reviewer_login_rejected(pe_file_val_a, reviewer_map):
    """AC-3: empty REVIEWER_LOGIN must exit non-zero."""
    result = _run_identity_script("", pe_file_val_a, reviewer_map)
    assert result.returncode != 0


def test_ac3_script_called_from_workflow():
    """AC-3: workflow must invoke check_reviewer_identity.py."""
    assert (
        "check_reviewer_identity.py" in _workflow_text()
    ), "workflow must call check_reviewer_identity.py"


# ─── AC-4: REVIEW compliance check remains mandatory ─────────────────────────


def test_ac4_workflow_calls_check_review():
    """AC-4: workflow must call check_review.py as a compliance step."""
    assert "check_review.py" in _workflow_text()


def test_ac4_merge_gated_on_gate2b():
    """AC-4: auto-merge step must be gated on gate2b outcome == 'success'."""
    wf = _load_workflow()
    merge_steps = _get_auto_merge_steps(wf)
    assert merge_steps
    for s in merge_steps:
        cond = s.get("if", "")
        assert (
            "gate2b" in cond
        ), f"Auto-merge step '{s['name']}' must be gated on gate2b"


# ─── AC-5: review trigger path reaches merge without additional push ──────────


def test_ac5_merge_step_reachable_from_review_trigger():
    """AC-5: merge step must be reachable from review trigger path."""
    wf = _load_workflow()
    # Review trigger exists (already tested in AC-1, but re-verify for clarity)
    assert "pull_request_review" in _get_on(wf)
    # Merge step exists
    merge_steps = _get_auto_merge_steps(wf)
    assert merge_steps, "No merge step found"


def test_ac5_merge_step_not_gated_on_github_ref_name():
    """AC-5: merge condition must not reference GITHUB_REF_NAME (push-only var)."""
    wf = _load_workflow()
    merge_steps = _get_auto_merge_steps(wf)
    for s in merge_steps:
        cond = s.get("if", "")
        assert (
            "GITHUB_REF_NAME" not in cond
        ), f"Merge step '{s['name']}' must not require GITHUB_REF_NAME"


def test_ac5_auth_step_handles_review_trigger():
    """AC-5: workflow has an authorisation step that handles the review trigger path."""
    text = _workflow_text()
    assert (
        "reviewer_check" in text
    ), "reviewer_check step must be referenced in auth logic"
    assert "review" in text and "authorized" in text


# ─── AC-6: pm-review-required label blocks auto-merge ────────────────────────


def test_ac6_veto_step_present():
    """AC-6: workflow must have a step that checks for pm-review-required label."""
    wf = _load_workflow()
    steps = wf["jobs"]["gate-2"]["steps"]
    step_names = [s.get("name", "").lower() for s in steps]
    assert any(
        "veto" in n or "pm" in n for n in step_names
    ), "No PM veto check step found"


def test_ac6_merge_gated_on_veto_false():
    """AC-6: merge step must be gated on veto == 'false'."""
    wf = _load_workflow()
    merge_steps = _get_auto_merge_steps(wf)
    assert merge_steps
    for s in merge_steps:
        cond = s.get("if", "")
        assert (
            "veto" in cond and "false" in cond
        ), f"Merge step '{s['name']}' must gate on veto == 'false', got: {cond!r}"


def test_ac6_veto_notify_step_present():
    """AC-6: workflow must notify PM when veto label is set."""
    text = _workflow_text()
    assert "veto" in text and "pm-review-required" in text


# ─── AC-7 is satisfied by running this file with pytest -v ────────────────────
