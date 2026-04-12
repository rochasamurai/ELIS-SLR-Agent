"""
Tests for PE-AUTO-13: Gate 2 re-trigger on bot review approval.

Asserts that auto-merge-on-pass.yml contains the required triggers
(pull_request_review and workflow_run) so Gate 2 re-evaluates when a
bot review approval or a gate-1 status arrives after the last push.
"""

import re
from pathlib import Path

import yaml

WORKFLOW_PATH = Path(".github/workflows/auto-merge-on-pass.yml")


def load_workflow() -> dict:
    with WORKFLOW_PATH.open() as f:
        wf = yaml.safe_load(f)
    # PyYAML (YAML 1.1) parses bare `on:` as the boolean True.
    # Normalise so tests can always use the string key "on".
    if True in wf and "on" not in wf:
        wf["on"] = wf.pop(True)
    return wf


def test_workflow_file_exists():
    assert WORKFLOW_PATH.exists(), f"Workflow file not found: {WORKFLOW_PATH}"


def test_push_trigger_preserved():
    """Existing push trigger must still be present — no regression."""
    wf = load_workflow()
    on = wf.get("on", {})
    assert "push" in on, "push trigger is missing — regression!"
    push = on["push"]
    branches = push.get("branches", [])
    assert "feature/**" in branches
    assert "chore/**" in branches
    assert "hotfix/**" in branches


def test_pull_request_review_trigger_present():
    """AC-1: pull_request_review trigger with type submitted must be present."""
    wf = load_workflow()
    on = wf.get("on", {})
    assert (
        "pull_request_review" in on
    ), "pull_request_review trigger is missing from auto-merge-on-pass.yml"
    prr = on["pull_request_review"]
    assert prr is not None
    types = prr.get("types", []) if isinstance(prr, dict) else []
    assert (
        "submitted" in types
    ), "pull_request_review trigger must include type 'submitted'"


def test_workflow_run_trigger_present():
    """AC-2: workflow_run trigger referencing Auto-assign Validator must be present."""
    wf = load_workflow()
    on = wf.get("on", {})
    assert (
        "workflow_run" in on
    ), "workflow_run trigger is missing from auto-merge-on-pass.yml"
    wr = on["workflow_run"]
    assert wr is not None
    workflows = wr.get("workflows", []) if isinstance(wr, dict) else []
    assert (
        "Auto-assign Validator" in workflows
    ), "workflow_run trigger must reference 'Auto-assign Validator'"


def test_workflow_run_trigger_on_completed():
    """workflow_run trigger must fire on completed type."""
    wf = load_workflow()
    wr = wf["on"]["workflow_run"]
    types = wr.get("types", [])
    assert "completed" in types, "workflow_run trigger must include type 'completed'"


def test_pull_request_review_scoped_to_tracked_branches():
    """AC-1: branch scope for pull_request_review is enforced via job if-condition."""
    raw = WORKFLOW_PATH.read_text()
    # The job-level if condition must reference all three branch prefixes.
    for prefix in ("feature/", "chore/", "hotfix/"):
        assert prefix in raw, (
            f"Branch prefix '{prefix}' not found in workflow — "
            "pull_request_review must be scoped to feature/**, chore/**, hotfix/**"
        )


def test_workflow_run_scoped_to_tracked_branches():
    """AC-2: branch scope for workflow_run is enforced via job if-condition."""
    raw = WORKFLOW_PATH.read_text()
    # Branch prefixes must appear in the if-condition (shared with PR-review block).
    assert (
        "workflow_run.head_branch" in raw or "workflow_run" in raw
    ), "workflow_run branch scoping not found in if-condition"
    for prefix in ("feature/", "chore/", "hotfix/"):
        assert prefix in raw, (
            f"Branch prefix '{prefix}' not found in workflow — "
            "workflow_run must be scoped to feature/**, chore/**, hotfix/**"
        )


def test_workflow_run_filters_on_success():
    """workflow_run must only proceed when the triggering run concluded successfully."""
    raw = WORKFLOW_PATH.read_text()
    assert (
        "conclusion == 'success'" in raw or 'conclusion == "success"' in raw
    ), "workflow_run job condition must check conclusion == 'success'"


def test_branch_name_resolution_step_present():
    """A step must resolve the correct head branch for all three trigger types."""
    wf = load_workflow()
    jobs = wf.get("jobs", {})
    gate2 = jobs.get("gate-2", {})
    steps = gate2.get("steps", [])
    step_names = [s.get("name", "") for s in steps]
    assert any("Resolve head branch" in name for name in step_names), (
        "Missing 'Resolve head branch' step — required to normalise BRANCH_NAME "
        "across push, pull_request_review, and workflow_run events"
    )


def test_resolve_step_is_first():
    """Resolve head branch must be the first step (before checkout)."""
    wf = load_workflow()
    steps = wf["jobs"]["gate-2"]["steps"]
    first_name = steps[0].get("name", "")
    assert (
        "Resolve head branch" in first_name
    ), f"First step must be 'Resolve head branch', got: '{first_name}'"


def test_checkout_uses_resolved_branch():
    """Checkout step must use the resolved BRANCH_NAME, not hard-coded GITHUB_REF."""
    wf = load_workflow()
    steps = wf["jobs"]["gate-2"]["steps"]
    checkout_steps = [
        s for s in steps if s.get("uses", "").startswith("actions/checkout")
    ]
    assert checkout_steps, "No checkout step found"
    checkout = checkout_steps[0]
    ref_val = checkout.get("with", {}).get("ref", "")
    assert (
        "BRANCH_NAME" in ref_val
    ), f"Checkout ref must use BRANCH_NAME, got: '{ref_val}'"


def test_no_duplicate_job_keys():
    """Regression guard (LL-03): no duplicate top-level job keys in the YAML."""
    raw = WORKFLOW_PATH.read_text()
    job_key_re = re.compile(r"^  (\w[\w-]*):", re.MULTILINE)
    keys = job_key_re.findall(raw)
    duplicates = [k for k in set(keys) if keys.count(k) > 1]
    assert not duplicates, f"Duplicate job keys detected: {duplicates}"
