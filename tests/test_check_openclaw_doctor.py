from __future__ import annotations

import json

from scripts import check_openclaw_doctor as doctor
from scripts import check_openclaw_security as security


def _valid_config() -> dict:
    return {
        "agents": {
            "list": [
                {
                    "id": "pm",
                    "workspace": "/home/samurai/openclaw/workspace-pm",
                    "model": "openai/gpt-5-mini",
                },
                {
                    "id": "prog-impl-codex",
                    "workspace": "/home/samurai/openclaw/workspace-prog-impl",
                    "model": "openai/gpt-5.1-codex",
                },
            ]
        },
        "bindings": [
            {"agentId": "pm", "match": {"channel": "telegram"}},
            {"agentId": "pm", "match": {"channel": "discord"}},
        ],
        "plugins": {
            "entries": {
                "telegram": {"enabled": True},
                "discord": {"enabled": True},
            }
        },
    }


def test_validate_agents_accepts_canonical_host_paths():
    assert doctor._validate_agents(_valid_config()) == []


def test_validate_agents_rejects_container_only_path():
    config = _valid_config()
    config["agents"]["list"][1]["workspace"] = "/app/workspaces/workspace-prog-impl"
    errors = doctor._validate_agents(config)
    assert any("container-only workspace path" in err for err in errors)


def test_validate_bindings_requires_both_pm_channels():
    config = _valid_config()
    config["bindings"] = [{"agentId": "pm", "match": {"channel": "telegram"}}]
    errors = doctor._validate_bindings(config)
    assert "bindings must include a discord binding for the pm agent" in errors


def test_security_check_rejects_noncanonical_workspace(tmp_path):
    config = _valid_config()
    config["agents"]["list"][0]["workspace"] = "workspace-pm"
    path = tmp_path / "openclaw.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    errors = security.check_openclaw_config(path)
    assert any("canonical host path" in err for err in errors)
