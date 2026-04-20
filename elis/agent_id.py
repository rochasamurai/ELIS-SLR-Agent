"""Helpers for model-agnostic ELIS agent identifiers.

The canonical naming rule is ``<domain>-<role>-<slot>`` where ``slot`` maps to
an engine in a committed registry. Legacy model-coupled identifiers remain
accepted only through the explicit compatibility map.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_MAP_PATH = (
    Path(__file__).resolve().parents[1] / "config" / "agent_id_migration_map.json"
)
ONE_OFF_AGENT_ENGINES: dict[str, str] = {"gemini-cli": "gemini"}


@lru_cache(maxsize=1)
def _policy() -> dict:
    return json.loads(_MAP_PATH.read_text(encoding="utf-8"))


def naming_rule() -> str:
    return str(_policy()["naming_rule"])


def provider_tokens() -> frozenset[str]:
    return frozenset(str(token) for token in _policy()["provider_tokens"])


def slot_to_engine() -> dict[str, str]:
    return {
        slot: str(meta["engine"]) for slot, meta in dict(_policy()["slots"]).items()
    }


def engine_to_slot() -> dict[str, str]:
    return {engine: slot for slot, engine in slot_to_engine().items()}


def legacy_to_canonical_map() -> dict[str, str]:
    return dict(_policy()["legacy_to_canonical"])


def canonical_to_legacy_map() -> dict[str, str]:
    return {new: old for old, new in legacy_to_canonical_map().items()}


def canonical_agent_id(agent_id: str) -> str:
    return legacy_to_canonical_map().get(agent_id, agent_id)


def is_structured_agent_id(agent_id: str) -> bool:
    canonical = canonical_agent_id(agent_id)
    parts = canonical.split("-")
    return len(parts) >= 3 and parts[-1] in slot_to_engine()


def role_from_agent_id(agent_id: str) -> str:
    canonical = canonical_agent_id(agent_id)
    parts = canonical.split("-")
    if len(parts) >= 3 and parts[-1] in slot_to_engine():
        return "-".join(parts[:-1])
    raise ValueError(f"Cannot derive role from agent id {agent_id!r}.")


def engine_from_agent_id(agent_id: str) -> str:
    if agent_id in ONE_OFF_AGENT_ENGINES:
        return ONE_OFF_AGENT_ENGINES[agent_id]
    canonical = canonical_agent_id(agent_id)
    parts = canonical.split("-")
    if len(parts) >= 3 and parts[-1] in slot_to_engine():
        return slot_to_engine()[parts[-1]]
    raise ValueError(f"Cannot infer engine from agent id {agent_id!r}.")


def canonical_surface(role_name: str, engine: str) -> str:
    slot = engine_to_slot().get(engine)
    if slot is None:
        raise ValueError(f"No slot is registered for engine {engine!r}.")
    return f"{role_name}-{slot}"


def contains_provider_token(value: str) -> bool:
    lowered = value.lower()
    return any(token in lowered.split("-") for token in provider_tokens())
