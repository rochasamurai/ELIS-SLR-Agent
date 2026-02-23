#!/usr/bin/env python
"""OpenClaw doctor policy gate stub for PE-OC-15."""

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
    missing = []
    agents = config.get("agents", {}).get("list", [])
    if not isinstance(agents, list):
        return ["agents.list must be an array"]
    for agent in agents:
        exec_conf = agent.get("exec", {})
        ask = exec_conf.get("ask")
        if ask is not True:
            agent_id = agent.get("id", "<unknown>")
            missing.append(f"agent {agent_id} exec.ask is {ask!r}; must be true")
    return missing


def _validate_skills(config: dict) -> list[str]:
    hub = config.get("skills", {}).get("hub", {})
    auto_install = hub.get("autoInstall")
    if auto_install is True:
        return ["skills.hub.autoInstall must be false"]
    if auto_install is None:
        return ["skills.hub.autoInstall is missing"]
    if auto_install is not False:
        return [f"skills.hub.autoInstall is {auto_install!r}; must be false"]
    return []


def main() -> int:
    try:
        config = _load_config(pathlib.Path("openclaw/openclaw.json"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: Unable to load openclaw configuration — {exc}", file=sys.stderr)
        return 1

    errors = []
    errors.extend(_validate_agents(config))
    errors.extend(_validate_skills(config))

    if errors:
        print("FAIL: openclaw doctor stub validation failed", file=sys.stderr)
        for message in errors:
            print(f"- {message}", file=sys.stderr)
        return 1

    print("OK: openclaw doctor configuration meets expected policies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
