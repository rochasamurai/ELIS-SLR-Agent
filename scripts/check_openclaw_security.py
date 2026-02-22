#!/usr/bin/env python
"""Security audit helper for the OpenClaw PM environment (PE-OC-11)."""

from __future__ import annotations

import json
import os
import pathlib
import sys
from typing import List

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCKER_COMPOSE = REPO_ROOT / "docker-compose.yml"
OPENCLAW_CONFIG = REPO_ROOT / "openclaw" / "openclaw.json"
AGENT_IGNORE = REPO_ROOT / ".agentignore"


def _expand_path(value: str) -> pathlib.Path:
    expanded = os.path.expandvars(os.path.expanduser(value))
    return pathlib.Path(expanded)


def check_docker_volumes(compose_path: pathlib.Path) -> List[str]:
    content = compose_path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    services = data.get("services", {})
    violations: List[str] = []
    for name, cfg in services.items():
        volumes = cfg.get("volumes", [])
        for entry in volumes:
            if not isinstance(entry, str) or ":" not in entry:
                continue
            host_path = entry.split(":", 1)[0]
            host_path_norm = _expand_path(host_path)
            if REPO_ROOT in host_path_norm.parents or host_path_norm == REPO_ROOT:
                violations.append(
                    f"{name} mounts {host_path} → exposes repository path"
                )
            if host_path.strip().startswith("."):
                violations.append(
                    f"{name} mounts relative path {host_path} → avoid repo exposure"
                )
        ports = cfg.get("ports", [])
        for port in ports:
            if isinstance(port, str) and not port.strip().startswith("127.0.0.1"):
                violations.append(
                    f"{name} exposes port {port} without localhost binding"
                )
    return violations


def check_agentignore(ignore_path: pathlib.Path) -> List[str]:
    if not ignore_path.exists():
        return ["`.agentignore` is missing"]
    lines = [line.strip() for line in ignore_path.read_text().splitlines()]
    required_prefixes = ["openclaw/workspaces", "openclaw/openclaw.json"]
    missing = []
    for prefix in required_prefixes:
        if not any(line.startswith(prefix) for line in lines):
            missing.append(prefix)
    return [f".agentignore missing pattern for {prefix}" for prefix in missing]


def check_openclaw_config(config_path: pathlib.Path) -> List[str]:
    if not config_path.exists():
        return ["openclaw configuration not found"]
    data = json.loads(config_path.read_text(encoding="utf-8"))
    errors: List[str] = []
    skills = data.get("skills", {}).get("hub", {})
    if skills.get("autoInstall") is not False:
        errors.append("openclaw.skills.hub.autoInstall must be false")
    for agent in data.get("agents", {}).get("list", []):
        exec_cfg = agent.get("exec", {})
        if exec_cfg.get("ask") is not True:
            errors.append(f"agent {agent.get('id')} missing exec.ask:true")
    return errors


def print_report():
    print("Checking docker-compose volume hygiene...")
    volume_issues = check_docker_volumes(DOCKER_COMPOSE)
    if volume_issues:
        raise SystemExit("\n".join(volume_issues))
    print("Docker volumes do not expose the repository.")

    print("Ensuring .agentignore covers openclaw workspaces…")
    ignore_issues = check_agentignore(AGENT_IGNORE)
    if ignore_issues:
        raise SystemExit("\n".join(ignore_issues))
    print(".agentignore includes openclaw workspace protections.")

    print("Validating openclaw JSON security settings…")
    config_issues = check_openclaw_config(OPENCLAW_CONFIG)
    if config_issues:
        raise SystemExit("\n".join(config_issues))
    print("openclaw.json enforces exec.ask and disables skill auto-install.")

    print("openclaw security checks passed.")


if __name__ == "__main__":
    try:
        print_report()
    except SystemExit:
        sys.exit(1)
