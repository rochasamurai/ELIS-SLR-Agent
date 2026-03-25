"""Unit tests for scripts/check_openclaw_config_sync.py."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

from scripts.check_openclaw_config_sync import (
    _declared_agent_ids,
    _live_agent_ids,
    main,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_SAMPLE_CONFIG = {
    "version": "0.3",
    "agents": {
        "list": [
            {
                "id": "pm",
                "workspace": "workspace-pm",
                "model": "openai/gpt-5.1-codex",
                "exec": {"ask": True},
            },
            {
                "id": "harvest-impl-codex",
                "workspace": "workspace-slr-harvest",
                "model": "openai/gpt-5.1-codex",
                "exec": {"ask": True},
            },
            {
                "id": "harvest-val-claude",
                "workspace": "workspace-slr-harvest",
                "model": "anthropic/claude-sonnet-4-6",
                "exec": {"ask": True},
            },
        ]
    },
}

_AGENTS_LIST_OUTPUT_IN_SYNC = """\
Agents:
- pm
  Workspace: workspace-pm
  Model: openai/gpt-5.1-codex
- harvest-impl-codex
  Workspace: workspace-slr-harvest
  Model: openai/gpt-5.1-codex
- harvest-val-claude
  Workspace: workspace-slr-harvest
  Model: anthropic/claude-sonnet-4-6
"""

_AGENTS_LIST_OUTPUT_MISSING = """\
Agents:
- pm
  Workspace: workspace-pm
  Model: openai/gpt-5.1-codex
"""


# ---------------------------------------------------------------------------
# _declared_agent_ids
# ---------------------------------------------------------------------------


def test_declared_agent_ids(tmp_path):
    cfg = tmp_path / "openclaw.json"
    cfg.write_text(json.dumps(_SAMPLE_CONFIG), encoding="utf-8")
    ids = _declared_agent_ids(cfg)
    assert ids == ["pm", "harvest-impl-codex", "harvest-val-claude"]


# ---------------------------------------------------------------------------
# _live_agent_ids
# ---------------------------------------------------------------------------


def _mock_run_success(output: str):
    result = MagicMock()
    result.returncode = 0
    result.stdout = output
    return result


def test_live_agent_ids_in_sync():
    with patch("scripts.check_openclaw_config_sync.subprocess.run") as mock_run:
        mock_run.return_value = _mock_run_success(_AGENTS_LIST_OUTPUT_IN_SYNC)
        ids = _live_agent_ids("openclaw")
    assert ids == ["pm", "harvest-impl-codex", "harvest-val-claude"]


def test_live_agent_ids_docker_not_found():
    with patch(
        "scripts.check_openclaw_config_sync.subprocess.run",
        side_effect=FileNotFoundError("docker not found"),
    ):
        ids = _live_agent_ids("openclaw")
    assert ids is None


def test_live_agent_ids_container_not_running():
    result = MagicMock()
    result.returncode = 1
    result.stdout = ""
    with patch(
        "scripts.check_openclaw_config_sync.subprocess.run", return_value=result
    ):
        ids = _live_agent_ids("openclaw")
    assert ids is None


def test_live_agent_ids_timeout():
    with patch(
        "scripts.check_openclaw_config_sync.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="docker", timeout=10),
    ):
        ids = _live_agent_ids("openclaw")
    assert ids is None


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def _write_config(tmp_path, data):
    cfg_dir = tmp_path / "openclaw"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg = cfg_dir / "openclaw.json"
    cfg.write_text(json.dumps(data), encoding="utf-8")
    return tmp_path


def test_main_in_sync(tmp_path, monkeypatch):
    _write_config(tmp_path, _SAMPLE_CONFIG)
    monkeypatch.setattr(
        "scripts.check_openclaw_config_sync.CONFIG_PATH",
        tmp_path / "openclaw" / "openclaw.json",
    )
    with patch("scripts.check_openclaw_config_sync.subprocess.run") as mock_run:
        mock_run.return_value = _mock_run_success(_AGENTS_LIST_OUTPUT_IN_SYNC)
        rc = main()
    assert rc == 0


def test_main_missing_agents(tmp_path, monkeypatch):
    _write_config(tmp_path, _SAMPLE_CONFIG)
    monkeypatch.setattr(
        "scripts.check_openclaw_config_sync.CONFIG_PATH",
        tmp_path / "openclaw" / "openclaw.json",
    )
    with patch("scripts.check_openclaw_config_sync.subprocess.run") as mock_run:
        mock_run.return_value = _mock_run_success(_AGENTS_LIST_OUTPUT_MISSING)
        rc = main()
    assert rc == 1


def test_main_docker_unreachable(tmp_path, monkeypatch):
    _write_config(tmp_path, _SAMPLE_CONFIG)
    monkeypatch.setattr(
        "scripts.check_openclaw_config_sync.CONFIG_PATH",
        tmp_path / "openclaw" / "openclaw.json",
    )
    with patch(
        "scripts.check_openclaw_config_sync.subprocess.run",
        side_effect=FileNotFoundError("docker not found"),
    ):
        rc = main()
    assert rc == 0


def test_main_config_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "scripts.check_openclaw_config_sync.CONFIG_PATH",
        tmp_path / "openclaw" / "openclaw.json",
    )
    rc = main()
    assert rc == 1
