"""Validate GitHub Actions control-plane wiring.

This check keeps development-agent coding entrypoints on the local-first
``elis-server`` runner while leaving GitHub-hosted workflows to CI and
orchestration duties.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = Path(".github/workflows")

LOCAL_AGENT_RUNNER_WORKFLOWS = {
    Path(".github/workflows/implementer-runner.yml"),
    Path(".github/workflows/validator-runner.yml"),
}

CI_WORKFLOWS = {
    Path(".github/workflows/ci.yml"),
    Path(".github/workflows/ci-gates.yml"),
}

AGENT_CODING_MARKERS = (
    "scripts/run_codex_agent.py",
    "scripts/run_claude_agent.py",
    "scripts.run_codex_validator",
    "scripts.run_claude_validator",
    "codex exec",
    "claude -p",
)

BOT_TOKEN_MARKERS = (
    "CODEX_BOT_TOKEN",
    "CLAUDE_BOT_TOKEN",
    "PM_BOT_TOKEN",
    "ELIS_APP_ID",
    "ELIS_APP_PRIVATE_KEY",
)

PORTABLE_GATE_MARKERS = (
    "python -m black --check",
    "python -m ruff check",
    "python -m pytest",
    "scripts/check_current_pe.py",
    "scripts/check_agent_scope.py",
    "scripts/check_review.py",
)


def _repo_path(path: Path) -> Path:
    return REPO_ROOT / path


def _read(path: Path) -> str:
    return _repo_path(path).read_text(encoding="utf-8")


def _workflow_paths() -> list[Path]:
    return sorted(
        path.relative_to(REPO_ROOT) for path in _repo_path(WORKFLOW_DIR).glob("*.yml")
    )


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def _uses_elis_server_runner(text: str) -> bool:
    return "self-hosted" in text and "elis-server" in text


def validate_control_plane_wiring() -> list[str]:
    """Return validation errors for the workflow control-plane boundary."""

    errors: list[str] = []
    for workflow in _workflow_paths():
        text = _read(workflow)
        invokes_agent_coding = _contains_any(text, AGENT_CODING_MARKERS)
        if not invokes_agent_coding:
            continue

        if workflow not in LOCAL_AGENT_RUNNER_WORKFLOWS:
            errors.append(
                f"{workflow.as_posix()} invokes an agent coding entrypoint outside "
                "the local agent runner workflows."
            )
        if not _uses_elis_server_runner(text):
            errors.append(
                f"{workflow.as_posix()} invokes an agent coding entrypoint without "
                "the self-hosted elis-server runner."
            )
        if "runs-on: ubuntu-latest" in text:
            errors.append(
                f"{workflow.as_posix()} invokes an agent coding entrypoint on "
                "ubuntu-latest."
            )

    for workflow in LOCAL_AGENT_RUNNER_WORKFLOWS:
        text = _read(workflow)
        if not _uses_elis_server_runner(text):
            errors.append(
                f"{workflow.as_posix()} must run on the self-hosted elis-server "
                "execution surface."
            )

    for workflow in CI_WORKFLOWS:
        text = _read(workflow)
        if _contains_any(text, BOT_TOKEN_MARKERS):
            errors.append(
                f"{workflow.as_posix()} is a CI workflow and must not reference "
                "bot/App credentials."
            )
        if _contains_any(text, AGENT_CODING_MARKERS):
            errors.append(
                f"{workflow.as_posix()} is a CI workflow and must not invoke "
                "agent coding entrypoints."
            )
        if not _contains_any(text, PORTABLE_GATE_MARKERS):
            errors.append(
                f"{workflow.as_posix()} should remain bounded to portable gates."
            )

    return errors


def main() -> int:
    errors = validate_control_plane_wiring()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Control-plane wiring OK — agent coding is local-first and CI is bounded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
