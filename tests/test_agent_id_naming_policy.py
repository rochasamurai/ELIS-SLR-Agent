from __future__ import annotations

import json
from pathlib import Path

from elis.agent_id import (
    canonical_surface,
    contains_provider_token,
    engine_from_agent_id,
    legacy_to_canonical_map,
    naming_rule,
)
from scripts.check_current_pe import _engine as current_pe_engine
from scripts.check_agent_id_naming_policy import policy_violations
from scripts.check_parallel_eligibility import _engine as parallel_engine
from scripts.check_role_registration import extract_engine as registry_engine
from scripts.plan_loader import _engine as plan_loader_engine
from scripts.pm_assign_pe import make_registry_row


def test_naming_rule_is_committed() -> None:
    assert naming_rule() == "<domain>-<role>-<slot>"


def test_migration_map_covers_active_surfaces() -> None:
    mapping = legacy_to_canonical_map()
    assert mapping["infra-impl-codex"] == "infra-impl-a"
    assert mapping["infra-val-claude"] == "infra-val-b"
    assert mapping["prog-impl-codex"] == "prog-impl-a"
    assert mapping["slr-val-claude"] == "slr-val-b"
    assert mapping["harvest-impl-codex"] == "harvest-impl-a"


def test_canonical_ids_are_not_model_coupled() -> None:
    for canonical in legacy_to_canonical_map().values():
        assert not contains_provider_token(canonical)


def test_engine_resolution_accepts_legacy_and_new_ids() -> None:
    assert engine_from_agent_id("infra-impl-codex") == "codex"
    assert engine_from_agent_id("infra-impl-a") == "codex"
    assert engine_from_agent_id("infra-val-claude") == "claude"
    assert engine_from_agent_id("infra-val-b") == "claude"


def test_dispatch_and_validation_helpers_accept_new_ids() -> None:
    assert current_pe_engine("infra-impl-a") == "codex"
    assert parallel_engine("infra-impl-b") == "claude"
    assert registry_engine("prog-val-a") == "codex"
    assert plan_loader_engine("prog-val-b") == "claude"


def test_pm_assignment_writes_new_slot_based_ids() -> None:
    row = make_registry_row(
        "PE-INFRA-SLR-04",
        "infra",
        "codex",
        "feature/pe-infra-slr-04-model-agnostic-agent-naming-governance",
        "2026-04-19",
    )
    assert "infra-impl-a" in row
    assert "infra-val-b" in row


def test_canonical_surface_uses_slot_registry() -> None:
    assert canonical_surface("prog-impl", "codex") == "prog-impl-a"
    assert canonical_surface("prog-val", "claude") == "prog-val-b"


def test_current_pe_uses_new_active_ids() -> None:
    text = Path("CURRENT_PE.md").read_text(encoding="utf-8")
    assert "infra-impl-a" in text
    assert "infra-val-b" in text


def test_plan_uses_new_active_ids() -> None:
    text = Path("ELIS_MultiAgent_Implementation_Plan_v1_8_3.md").read_text(
        encoding="utf-8"
    )
    assert "Implementer | `infra-impl-a` |" in text
    assert "Validator | `infra-val-b` |" in text
    assert "Implementer | `infra-impl-b` |" in text
    assert "Validator | `infra-val-a` |" in text


def test_openclaw_runtime_config_uses_new_ids() -> None:
    data = json.loads(
        Path("docs/openclaw/openclaw_sanitised.json").read_text(encoding="utf-8")
    )
    agent_ids = {agent["id"] for agent in data["agents"]["list"]}
    assert "harvest-impl-a" in agent_ids
    assert "screen-val-a" in agent_ids
    assert "infra-impl-a" in agent_ids
    assert "infra-val-b" in agent_ids
    for agent_id in agent_ids:
        if agent_id == "pm":
            continue
        assert not contains_provider_token(agent_id)


def test_policy_check_passes_for_active_files() -> None:
    assert policy_violations() == []
