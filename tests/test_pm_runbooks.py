from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs" / "openclaw"
DEPLOY_SCRIPT = REPO_ROOT / "scripts" / "deploy_openclaw_workspaces.sh"


def read_doc(name: str) -> str:
    return (DOCS_ROOT / name).read_text(encoding="utf-8")


def test_pm_e2e_validation_runbook_exists_and_covers_required_commands() -> None:
    text = read_doc("PM_E2E_VALIDATION_RUNBOOK.md")
    required_fragments = [
        "Who are you?",
        "What are the current PEs?",
        "git -C /opt/elis/repo worktree list",
        "openclaw approvals get --gateway",
        "openclaw channels status --probe",
        "PLAN_CURRENT.md",
        "25 entries per message",
    ]
    for fragment in required_fragments:
        assert fragment in text


def test_native_operations_restore_runbook_exists_and_covers_restore_flow() -> None:
    text = read_doc("NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md")
    required_fragments = [
        "bash scripts/deploy_openclaw_workspaces.sh",
        "systemctl --user restart openclaw-gateway",
        "openclaw doctor",
        "openclaw approvals get --gateway",
        "PM_SESSION_RESET.md",
        "PM_E2E_VALIDATION_RUNBOOK.md",
        "CURRENT_PE.md",
    ]
    for fragment in required_fragments:
        assert fragment in text


def test_existing_docs_reference_new_runbooks() -> None:
    deployment = read_doc("DEPLOYMENT.md")
    native_install = read_doc("NATIVE_INSTALL.md")
    pm_rules = read_doc("PM_AGENT_RULES.md")
    pm_reset = read_doc("PM_SESSION_RESET.md")

    assert "PM_E2E_VALIDATION_RUNBOOK.md" in deployment
    assert "NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md" in deployment
    assert "NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md" in native_install
    assert "PM_E2E_VALIDATION_RUNBOOK.md" in pm_rules
    assert "PM_E2E_VALIDATION_RUNBOOK.md" in pm_reset


def test_deploy_script_recreates_pm_docs_dir_after_sync() -> None:
    text = DEPLOY_SCRIPT.read_text(encoding="utf-8")

    assert "rsync -av --delete" in text
    assert 'mkdir -p "$TARGET_PM_DOCS"' in text
    assert 'ln -sfn "$REPO_ROOT/$PLAN_FILE" "$TARGET_PM_DOCS/PLAN_CURRENT.md"' in text
