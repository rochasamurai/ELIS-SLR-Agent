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
    if not any(agent.get("id") == "pm" for agent in agents):
        errors.append("agents.list must include the pm agent")
    for agent in agents:
        agent_id = agent.get("id", "<unknown>")
        workspace = agent.get("workspace")
        if not workspace:
            errors.append(f"agent {agent_id} missing workspace")
        elif "/app/" in workspace:
            errors.append(
                f"agent {agent_id} uses container-only workspace path {workspace}"
            )
        elif not workspace.startswith("/home/samurai/openclaw/"):
            errors.append(
                f"agent {agent_id} workspace {workspace!r} must use canonical host path"
            )
        if not agent.get("model"):
            errors.append(f"agent {agent_id} missing model")
    return errors


def _validate_plugins(config: dict) -> list[str]:
    entries = config.get("plugins", {}).get("entries", {})
    errors = []
    for name in ("telegram", "discord"):
        enabled = entries.get(name, {}).get("enabled")
        if enabled is not True:
            errors.append(
                f"plugins.entries.{name}.enabled is {enabled!r}; must be true"
            )
    return errors


def _validate_bindings(config: dict) -> list[str]:
    bindings = config.get("bindings", [])
    if not isinstance(bindings, list) or not bindings:
        return ["bindings must be a non-empty array with pm channel bindings"]
    seen = set()
    for binding in bindings:
        if binding.get("agentId") == "pm":
            channel = binding.get("match", {}).get("channel")
            if channel:
                seen.add(channel)
    errors = []
    for channel in ("telegram", "discord"):
        if channel not in seen:
            errors.append(f"bindings must include a {channel} binding for the pm agent")
    return errors


def main() -> int:
    try:
        config = _load_config(pathlib.Path("openclaw/openclaw.json"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: Unable to load openclaw configuration — {exc}", file=sys.stderr)
        return 1

    errors = []
    errors.extend(_validate_agents(config))
    errors.extend(_validate_plugins(config))
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
