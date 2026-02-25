#!/usr/bin/env python
"""OpenClaw doctor policy gate — validates openclaw.json against current schema (v2026.2+)."""

from __future__ import annotations

import json
import pathlib
import sys


def _load_config(path: pathlib.Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _validate_agents(config: dict) -> list[str]:
    errors = []
    agents = config.get("agents", {}).get("list", [])
    if not isinstance(agents, list):
        return ["agents.list must be an array"]
    if not agents:
        return ["agents.list must be non-empty"]
    for agent in agents:
        agent_id = agent.get("id", "<unknown>")
        if not agent.get("workspace"):
            errors.append(f"agent {agent_id} missing workspace")
        if not agent.get("model"):
            errors.append(f"agent {agent_id} missing model")
    return errors


def _validate_telegram_plugin(config: dict) -> list[str]:
    enabled = (
        config.get("plugins", {}).get("entries", {}).get("telegram", {}).get("enabled")
    )
    if enabled is not True:
        return [f"plugins.entries.telegram.enabled is {enabled!r}; must be true"]
    return []


def _validate_bindings(config: dict) -> list[str]:
    bindings = config.get("bindings", [])
    if not isinstance(bindings, list) or not bindings:
        return [
            "bindings must be a non-empty array with at least a telegram pm binding"
        ]
    for b in bindings:
        if b.get("agentId") == "pm" and b.get("match", {}).get("channel") == "telegram":
            return []
    return ["bindings must include a telegram binding for the pm agent"]


def main() -> int:
    try:
        config = _load_config(pathlib.Path("openclaw/openclaw.json"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: Unable to load openclaw configuration — {exc}", file=sys.stderr)
        return 1

    errors = []
    errors.extend(_validate_agents(config))
    errors.extend(_validate_telegram_plugin(config))
    errors.extend(_validate_bindings(config))

    if errors:
        print("FAIL: openclaw doctor stub validation failed", file=sys.stderr)
        for message in errors:
            print(f"- {message}", file=sys.stderr)
        return 1

    print("OK: openclaw doctor configuration meets expected policies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
