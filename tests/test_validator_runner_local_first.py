"""Tests for check_validator_runner_local_first.py — PE-SLR-12."""

from __future__ import annotations

from pathlib import Path

from scripts.check_validator_runner_local_first import (
    ARCHIVE_PREFIX,
    REQUIRED_REVIEW_SECTIONS,
    validate_validator_runner_local_first,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

CURRENT_PE_BODY = """\
## Release context

| Field          | Value                       |
|----------------|-----------------------------|
| Release        | ELIS SLR Agent              |
| Base branch    | main                        |
| Plan file      | ELIS_MultiAgent_Implementation_Plan_v1_9.md |
| Plan location  | repo root                   |

## Current PE

| Field   | Value |
|---------|-------|
| PE      | PE-SLR-12 |
| Branch  | feature/pe-slr-12-validator-runner-evidence-contract |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| Claude Code | Implementer |
| CODEX       | Validator   |

## Active PE Registry

| PE-ID     | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |
|-----------|--------|---------------------|-------------------|--------|--------|--------------|
| PE-SLR-12 | slr    | prog-impl-b         | prog-val-a        | feature/pe-slr-12-validator-runner-evidence-contract | implementing | 2026-04-25 |
"""

PLAN_BODY = """\
### PE-SLR-12 · Validator Runner and Evidence Contract

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Validator does not self-start and only runs after explicit PM authorisation. |
| AC-2 | The validator writes to `docs/reviews/archive/REVIEW_PE<N>.md`. |
| AC-3 | The review file contains the required sections and at least one fenced evidence block. |
| AC-4 | `scripts/check_review.py` passes against the archived review file. |
| AC-5 | The formal verdict and review evidence remain aligned with the branch state. |

---
"""


def test_validator_runner_local_first_check_passes_with_active_context(tmp_path):
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text(PLAN_BODY, encoding="utf-8")

    assert (
        validate_validator_runner_local_first(
            repo_root=REPO_ROOT,
            current_pe_path=current_pe,
            plan_path=plan,
        )
        == []
    )


def test_validator_runner_check_reports_missing_plan_section(tmp_path):
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text("# Wrong plan\n", encoding="utf-8")

    errors = validate_validator_runner_local_first(
        repo_root=REPO_ROOT,
        current_pe_path=current_pe,
        plan_path=plan,
    )

    assert any("Could not find plan section for PE-SLR-12" in e for e in errors)


def test_validator_runner_check_detects_missing_runner_workflow(tmp_path):
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text(PLAN_BODY, encoding="utf-8")

    # Point to a repo_root that has no workflows
    errors = validate_validator_runner_local_first(
        repo_root=tmp_path,
        current_pe_path=current_pe,
        plan_path=plan,
    )

    assert any("validator-runner.yml" in e and "missing" in e for e in errors)


def test_validator_runner_workflow_runs_on_elis_server(tmp_path):
    """Verify real workflow uses self-hosted elis-server (AC-1)."""
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text(PLAN_BODY, encoding="utf-8")

    errors = validate_validator_runner_local_first(
        repo_root=REPO_ROOT,
        current_pe_path=current_pe,
        plan_path=plan,
    )

    assert not any(
        "elis-server" in e for e in errors
    ), "Expected no elis-server error; got: " + str(errors)


def test_dispatch_script_enforces_pm_authorisation(tmp_path):
    """Verify dispatch script has evidence-backed state machine guard (AC-1)."""
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text(PLAN_BODY, encoding="utf-8")

    errors = validate_validator_runner_local_first(
        repo_root=REPO_ROOT,
        current_pe_path=current_pe,
        plan_path=plan,
    )

    assert not any(
        "authorisation guard" in e for e in errors
    ), "Expected no authorisation-guard error; got: " + str(errors)


def test_validator_prompt_references_archive_path(tmp_path):
    """Verify built prompt instructs agent to write to archive path (AC-2)."""
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text(PLAN_BODY, encoding="utf-8")

    errors = validate_validator_runner_local_first(
        repo_root=REPO_ROOT,
        current_pe_path=current_pe,
        plan_path=plan,
    )

    assert not any(
        ARCHIVE_PREFIX in e for e in errors
    ), "Expected no archive-path error; got: " + str(errors)


def test_validator_prompt_includes_all_required_sections(tmp_path):
    """Verify prompt lists every required REVIEW section (AC-3)."""
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text(PLAN_BODY, encoding="utf-8")

    errors = validate_validator_runner_local_first(
        repo_root=REPO_ROOT,
        current_pe_path=current_pe,
        plan_path=plan,
    )

    for section in REQUIRED_REVIEW_SECTIONS:
        assert not any(
            section in e for e in errors
        ), f"Expected no error about section '{section}'; got: {errors}"


def test_validator_prompt_includes_check_review_verification(tmp_path):
    """Verify prompt instructs agent to run check_review.py (AC-4)."""
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text(PLAN_BODY, encoding="utf-8")

    errors = validate_validator_runner_local_first(
        repo_root=REPO_ROOT,
        current_pe_path=current_pe,
        plan_path=plan,
    )

    assert not any(
        "check_review.py" in e for e in errors
    ), "Expected no check_review.py error; got: " + str(errors)


def test_run_validator_post_run_alignment_checks_ordered(tmp_path):
    """Verify verify_review_committed → verify_formal_review_posted → read_verdict (AC-5)."""
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text(PLAN_BODY, encoding="utf-8")

    errors = validate_validator_runner_local_first(
        repo_root=REPO_ROOT,
        current_pe_path=current_pe,
        plan_path=plan,
    )

    assert not any(
        "verify_review_committed" in e for e in errors
    ), "Expected no ordering error; got: " + str(errors)
    assert not any(
        "verify_formal_review_posted" in e for e in errors
    ), "Expected no ordering error; got: " + str(errors)
    assert not any(
        "read_verdict" in e for e in errors
    ), "Expected no ordering error; got: " + str(errors)
