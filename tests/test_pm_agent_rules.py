from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PM_AGENTS_PATH = REPO_ROOT / "openclaw" / "workspaces" / "workspace-pm" / "AGENTS.md"
PM_SKILLS_PATH = REPO_ROOT / "openclaw" / "workspaces" / "workspace-pm" / "SKILLS.md"

# Paths to governance docs that should encode the new rules
GOVERNANCE_DOCS = [
    REPO_ROOT
    / "docs"
    / "governance"
    / "ELIS_Agent_Dispatch_Binding_and_Validation_Rules.md",
    REPO_ROOT / "docs" / "governance" / "ELIS_PE_Dispatch_Checklist.md",
    REPO_ROOT / "docs" / "governance" / "ELIS_PE_Operating_Protocol.md",
]


def test_pm_rules_live_in_workspace_pm_agents() -> None:
    assert (
        PM_AGENTS_PATH.exists()
    ), f"Missing PM rules source of truth: {PM_AGENTS_PATH}"


def test_pm_rules_source_defines_prompt_source_order() -> None:
    text = PM_AGENTS_PATH.read_text(encoding="utf-8")
    assert "Prompt Source Order" in text
    assert "AGENTS.md" in text
    assert "MEMORY.md" in text


def test_pm_rules_source_defines_status_transition_guard() -> None:
    text = PM_AGENTS_PATH.read_text(encoding="utf-8")
    assert "Status Transition Guard" in text
    assert "implementing → validating" in text
    assert "validating → gate-2-pending" in text
    assert "gate-2-pending → merged" in text


def test_pm_skills_live_in_workspace_pm() -> None:
    assert PM_SKILLS_PATH.exists(), f"Missing PM skills file: {PM_SKILLS_PATH}"


def test_pm_skills_defines_opening_context_guard() -> None:
    """PM SKILLS.md should reference PE opening context checks."""
    text = PM_SKILLS_PATH.read_text(encoding="utf-8")
    assert "opening context" in text.lower() or "opening" in text.lower()


def test_pm_skills_defines_dispatch_binding_guard() -> None:
    """PM SKILLS.md should reference dispatch binding preconditions."""
    text = PM_SKILLS_PATH.read_text(encoding="utf-8")
    assert "binding" in text.lower() or "bound" in text.lower()


def test_pm_skills_defines_failure_class() -> None:
    """PM SKILLS.md should reference failure class taxonomy."""
    text = PM_SKILLS_PATH.read_text(encoding="utf-8")
    assert "failure class" in text.lower() or "FAILURE" in text


def test_pm_skills_defines_pm_no_write_rule() -> None:
    """PM SKILLS.md should reference the PM no-write rule."""
    text = PM_SKILLS_PATH.read_text(encoding="utf-8")
    assert "write" in text.lower()


def test_governance_docs_encode_review_on_final_branch_rule() -> None:
    """Governance docs should encode the LATEST_VALIDATOR_REVIEW_MUST_BE_ON_FINAL_PR_BRANCH_RULE."""
    rule_phrases = [
        "REVIEW_MUST_BE_ON_FINAL_PR_BRANCH",
        "REVIEW_NOT_ON_BRANCH",
        "REVIEW.md must be committed",
        "final validated branch HEAD",
    ]
    for doc in GOVERNANCE_DOCS:
        text = doc.read_text(encoding="utf-8")
        assert any(
            phrase in text for phrase in rule_phrases
        ), f"{doc.name} missing REVIEW-on-final-branch rule: none of {rule_phrases} found"


def test_governance_docs_encode_execution_owner_rule() -> None:
    """Governance docs should encode the AUTHORISED_EXECUTION_OWNER_FOR_BRANCH_INTEGRATION_RULE."""
    rule_phrases = [
        "AUTHORISED_EXECUTION_OWNER_FOR_BRANCH_INTEGRATION",
        "execution owner",
        "PM must not execute merges, pushes, PR actions",
        "PM coordinates only",
    ]
    for doc in GOVERNANCE_DOCS:
        text = doc.read_text(encoding="utf-8")
        assert any(
            phrase in text for phrase in rule_phrases
        ), f"{doc.name} missing execution owner rule: none of {rule_phrases} found"


def test_governance_docs_encode_pm_no_git_write() -> None:
    """Governance docs should explicitly forbid PM from git operations."""
    git_phrases = ["git push", "git merge", "git rebase", "history rewrite"]
    for doc in GOVERNANCE_DOCS:
        text = doc.read_text(encoding="utf-8")
        assert any(
            phrase in text for phrase in git_phrases
        ), f"{doc.name} missing git operation prohibition: none of {git_phrases} found"


def test_review_template_has_final_branch_head_field() -> None:
    """REVIEW.template.md should have a field for the final validated branch HEAD."""
    template_path = REPO_ROOT / "docs" / "templates" / "REVIEW.template.md"
    text = template_path.read_text(encoding="utf-8")
    assert "final validated branch HEAD" in text


def test_check_validation_readiness_has_review_on_branch_check() -> None:
    """check_validation_readiness.py should have the REVIEW committed check."""
    script_path = REPO_ROOT / "scripts" / "check_validation_readiness.py"
    text = script_path.read_text(encoding="utf-8")
    assert "REVIEW_NOT_ON_BRANCH" in text


def test_infra_val_agents_has_final_branch_rule() -> None:
    """Infra-val AGENTS.md should encode the review-on-final-branch rule."""
    path = REPO_ROOT / "openclaw" / "workspaces" / "workspace-infra-val" / "AGENTS.md"
    text = path.read_text(encoding="utf-8")
    assert "REVIEW_MUST_BE_ON_FINAL_PR_BRANCH" in text


def test_infra_val_agents_has_execution_owner_rule() -> None:
    """Infra-val AGENTS.md should encode the execution owner rule."""
    path = REPO_ROOT / "openclaw" / "workspaces" / "workspace-infra-val" / "AGENTS.md"
    text = path.read_text(encoding="utf-8")
    assert "AUTHORISED_EXECUTION_OWNER_FOR_BRANCH_INTEGRATION" in text
