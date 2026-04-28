from __future__ import annotations

import json
from pathlib import Path

from elis.reviewer_identity import review_handle_for_engine, review_login_for_engine


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "openclaw" / "openclaw.json"
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "auto-assign-validator.yml"


def test_identity_map_contains_required_agent_rows() -> None:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    identities = data["agents"]["reviewerIdentities"]

    assert "CODEX" in identities
    assert "Claude Code" in identities
    assert "PM" in identities

    assert identities["CODEX"]["review_login"] == "elis-codex-bot"
    assert identities["Claude Code"]["review_login"] == "elis-claude-bot"
    assert identities["PM"]["review_login"] == "elis-pm-bot"


def test_runtime_lookup_is_data_driven() -> None:
    assert review_handle_for_engine("codex") == "@codex"
    assert review_handle_for_engine("claude") == "@claude-code"
    assert review_login_for_engine("codex") == "elis-codex-bot"
    assert review_login_for_engine("claude") == "elis-claude-bot"


def test_agents_requires_formal_review_not_comment_only() -> None:
    agents_text = AGENTS_PATH.read_text(encoding="utf-8")
    assert (
        "A comment-only PASS signal does not satisfy required-review branch"
        in agents_text
    )
    assert (
        "For PASS, plain PR comments are not sufficient on protected branches"
        in agents_text
    )


def test_identity_lookup_helpers_are_committed_for_assignment_workflows() -> None:
    resolver_text = (REPO_ROOT / "scripts" / "resolve_validator_handle.py").read_text(
        encoding="utf-8"
    )
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "review_handle_for_engine" in resolver_text
    assert "auto-assign-validator.yml" in WORKFLOW_PATH.as_posix()
    assert "validator-assignment" in workflow_text
