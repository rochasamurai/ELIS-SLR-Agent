from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
VISIBILITY_PATH = REPO_ROOT / "config" / "openclaw" / "pm_dispatch_settings.json"
EVIDENCE_PATH = REPO_ROOT / "docs" / "openclaw" / "PM_CROSS_AGENT_DISPATCH_EVIDENCE.md"


def test_dispatch_visibility_is_all_in_tracked_config() -> None:
    config = json.loads(VISIBILITY_PATH.read_text(encoding="utf-8"))
    assert config["tools"]["sessions"]["visibility"] == "all"


def test_pm_to_validator_dispatch_ack_evidence_is_committed() -> None:
    text = EVIDENCE_PATH.read_text(encoding="utf-8")
    assert "sessions_send" in text
    assert "ACK" in text
    assert "forbidden" not in text.lower()


def test_agents_gate_1_defaults_to_pm_direct_dispatch_with_fallback() -> None:
    text = AGENTS_PATH.read_text(encoding="utf-8")
    assert "Default path: PM dispatches the validator assignment directly" in text
    assert "PO relay is a last-resort fallback only" in text
