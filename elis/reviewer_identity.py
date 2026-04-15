"""Reviewer identity mapping helpers for protected-branch workflows."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


MAP_PATH = Path("config/reviewer_identity_map.json")
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
    if not MAP_PATH.exists():
        raise ReviewerIdentityError(f"Identity map missing: {MAP_PATH}")
    try:
        data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReviewerIdentityError(f"Identity map is invalid JSON: {exc}") from exc
    agents = data.get("agents")
    if not isinstance(agents, dict):
        raise ReviewerIdentityError("Identity map must contain an 'agents' object.")
    return data


def entry_for_agent(agent_label: str) -> dict:
    data = _load_map()
    agents = data["agents"]
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
