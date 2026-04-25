from __future__ import annotations

from pathlib import Path

from elis.workflow_state_machine import (
    IMPLEMENTER_DISPATCH_STATE,
    LOCAL_AGENT_EXECUTION_SURFACE,
    VALIDATOR_DISPATCH_SOURCE_STATE,
    VALIDATOR_DISPATCH_TARGET_STATE,
    implementer_dispatch_allowed,
    validator_dispatch_allowed,
)
from scripts.check_control_plane_wiring import validate_control_plane_wiring

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_control_plane_wiring_check_passes_for_repository() -> None:
    assert validate_control_plane_wiring() == []


def test_agent_coding_workflows_are_local_first() -> None:
    for workflow in [
        ".github/workflows/implementer-runner.yml",
        ".github/workflows/validator-runner.yml",
    ]:
        text = _read(workflow)
        assert "self-hosted" in text
        assert LOCAL_AGENT_EXECUTION_SURFACE in text
        assert "runs-on: ubuntu-latest" not in text


def test_github_hosted_workflows_do_not_invoke_development_agent_entrypoints() -> None:
    forbidden = (
        "scripts/run_codex_agent.py",
        "scripts/run_claude_agent.py",
        "scripts.run_codex_validator",
        "scripts.run_claude_validator",
        "codex exec",
        "claude -p",
    )
    allowed = {
        ".github/workflows/implementer-runner.yml",
        ".github/workflows/validator-runner.yml",
    }

    for path in (REPO_ROOT / ".github/workflows").glob("*.yml"):
        repo_path = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if repo_path in allowed:
            continue
        assert "runs-on: ubuntu-latest" not in text or not any(
            marker in text for marker in forbidden
        )


def test_dispatch_guards_use_canonical_state_machine_states() -> None:
    assert implementer_dispatch_allowed(IMPLEMENTER_DISPATCH_STATE) is True
    assert implementer_dispatch_allowed(VALIDATOR_DISPATCH_SOURCE_STATE) is False
    assert validator_dispatch_allowed(VALIDATOR_DISPATCH_SOURCE_STATE) is True
    assert validator_dispatch_allowed("implementing") is False
    assert VALIDATOR_DISPATCH_TARGET_STATE == "validating"


def test_auto_assign_validator_uses_model_agnostic_handle_resolver() -> None:
    text = _read(".github/workflows/auto-assign-validator.yml")
    assert "python scripts/resolve_validator_handle.py" in text
    assert "if 'codex' in validator_agent" not in text
    assert "elif 'gemini' in validator_agent" not in text
