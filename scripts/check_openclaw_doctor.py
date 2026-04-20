#!/usr/bin/env python
"""OpenClaw doctor policy gate — validates openclaw.json against current schema (v2026.2+)."""

from __future__ import annotations

import json
import pathlib
import sys

REQUIRED_SLR_PHASE_IDS = {
    "harvest-impl-a",
    "harvest-val-b",
    "screen-impl-b",
    "screen-val-a",
    "extract-impl-a",
    "extract-val-b",
    "synth-impl-b",
    "synth-val-a",
    "prisma-impl-b",
    "prisma-val-a",
}
LEGACY_SLR_IDS = {
    "slr-impl-codex",
    "slr-impl-claude",
    "slr-val-codex",
    "slr-val-claude",
    "slr-impl-a",
    "slr-impl-b",
    "slr-val-a",
    "slr-val-b",
}


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
    agent_ids = {agent.get("id") for agent in agents}
    if "pm" not in agent_ids:
        errors.append("agents.list must include the pm agent")
    missing_phase_ids = sorted(REQUIRED_SLR_PHASE_IDS - agent_ids)
    if missing_phase_ids:
        errors.append(
            "agents.list missing phase-specialized SLR IDs: "
            + ", ".join(missing_phase_ids)
        )
    stale_ids = sorted(LEGACY_SLR_IDS & agent_ids)
    if stale_ids:
        errors.append(
            "agents.list still includes legacy generic SLR IDs: " + ", ".join(stale_ids)
        )
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
