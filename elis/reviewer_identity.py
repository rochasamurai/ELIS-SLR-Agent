"""Reviewer identity mapping helpers for protected-branch workflows."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


CONFIG_PATH = Path("openclaw/openclaw.json")
ENGINE_TO_AGENT = {
    "codex": "CODEX",
    "claude": "Claude Code",
    "pm": "PM",
    "gemini": "Gemini CLI",
}


class ReviewerIdentityError(ValueError):
    """Raised when reviewer identity mapping is missing or invalid."""


@lru_cache(maxsize=1)
def _load_map() -> dict:
    if not CONFIG_PATH.exists():
        raise ReviewerIdentityError(f"Identity config missing: {CONFIG_PATH}")
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReviewerIdentityError(f"Identity config is invalid JSON: {exc}") from exc

    agents = data.get("agents")
    if not isinstance(agents, dict):
        raise ReviewerIdentityError("Identity config must contain an 'agents' object.")

    identities = agents.get("reviewerIdentities")
    if not isinstance(identities, dict):
        raise ReviewerIdentityError(
            "Identity config must contain 'agents.reviewerIdentities'."
        )
    return identities


def entry_for_agent(agent_label: str) -> dict:
    agents = _load_map()
    if agent_label not in agents:
        raise ReviewerIdentityError(f"Agent '{agent_label}' is not in identity map.")
    entry = agents[agent_label]
    if not isinstance(entry, dict):
        raise ReviewerIdentityError(
            f"Agent entry for '{agent_label}' must be an object."
        )
    return entry


def entry_for_engine(engine: str) -> dict:
    label = ENGINE_TO_AGENT.get(engine)
    if label is None:
        raise ReviewerIdentityError(f"Unknown engine '{engine}'.")
    return entry_for_agent(label)


def review_handle_for_engine(engine: str) -> str:
    handle = str(entry_for_engine(engine).get("review_handle", "")).strip()
    if not handle.startswith("@"):
        raise ReviewerIdentityError(f"Missing review handle for engine '{engine}'.")
    return handle


def review_login_for_engine(engine: str) -> str:
    login = str(entry_for_engine(engine).get("review_login", "")).strip()
    if not login:
        raise ReviewerIdentityError(f"Missing review login for engine '{engine}'.")
    return login
