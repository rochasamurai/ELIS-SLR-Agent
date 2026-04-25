from __future__ import annotations

from pathlib import Path

from elis.workflow_state_machine import (
    ACTIVE_STATES,
    ALLOWED_TRANSITIONS,
    CANONICAL_STATES,
    MERGE_APPROVAL_GUARDS,
    REVIEW_COMPLETION_GUARDS,
    TRANSITION_GUARDS,
    VALIDATOR_AUTHORISATION_GUARDS,
    VALIDATOR_DISPATCH_SOURCE_STATE,
    VALIDATOR_DISPATCH_TARGET_STATE,
    can_transition,
    guards_for,
    implementer_dispatch_allowed,
    validator_dispatch_allowed,
)
from scripts import check_current_pe, check_role_registration


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_canonical_states_are_complete_and_ordered() -> None:
    assert CANONICAL_STATES == (
        "planning",
        "implementing",
        "gate-1-pending",
        "validating",
        "gate-2-pending",
        "merged",
        "blocked",
        "superseded",
    )
    assert ACTIVE_STATES == (
        "planning",
        "implementing",
        "gate-1-pending",
        "validating",
        "gate-2-pending",
        "blocked",
    )


def test_allowed_transitions_and_guard_lookup_are_discoverable() -> None:
    expected = {
        ("planning", "implementing"),
        ("implementing", "gate-1-pending"),
        ("gate-1-pending", "validating"),
        ("gate-1-pending", "blocked"),
        ("validating", "gate-2-pending"),
        ("gate-2-pending", "merged"),
        ("gate-2-pending", "blocked"),
    }
    assert expected.issubset(set(ALLOWED_TRANSITIONS))
    assert all(can_transition(state, "superseded") for state in ACTIVE_STATES)
    assert not can_transition("planning", "merged")
    assert guards_for("gate-1-pending", "validating") == (
        "Explicit PM authorisation is recorded",
        "Validator assignment evidence is present",
        "The PE remains active in CURRENT_PE.md",
    )


def test_dispatch_helpers_follow_state_machine_transitions() -> None:
    assert implementer_dispatch_allowed("implementing") is True
    assert implementer_dispatch_allowed("planning") is False
    assert validator_dispatch_allowed(VALIDATOR_DISPATCH_SOURCE_STATE) is True
    assert validator_dispatch_allowed("implementing") is False
    assert can_transition(
        VALIDATOR_DISPATCH_SOURCE_STATE,
        VALIDATOR_DISPATCH_TARGET_STATE,
    )


def test_existing_status_validators_reuse_the_state_machine_contract() -> None:
    assert check_current_pe.VALID_REGISTRY_STATUSES == set(CANONICAL_STATES)
    assert check_current_pe.VALID_ACTIVE_STATUSES == set(ACTIVE_STATES)
    assert check_role_registration.VALID_STATUSES == set(CANONICAL_STATES)


def test_governing_docs_expose_states_and_guard_language() -> None:
    docs = {
        "architecture": _read("ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_9.md"),
        "agents": _read("AGENTS.md"),
        "state_machine": _read("docs/workflow/PE_STATE_MACHINE.md"),
        "plan": _read("ELIS_MultiAgent_Implementation_Plan_v1_9.md"),
    }

    for state in CANONICAL_STATES:
        for name, text in docs.items():
            assert f"`{state}`" in text, f"{state} missing from {name}"

    guard_text = "\n".join(
        item for guards in TRANSITION_GUARDS.values() for item in guards
    )
    for phrase in (
        "HANDOFF.md is present and complete",
        VALIDATOR_AUTHORISATION_GUARDS[0],
        REVIEW_COMPLETION_GUARDS[1],
        MERGE_APPROVAL_GUARDS[1],
    ):
        assert phrase in guard_text
        assert phrase in docs["state_machine"]

    for phrase in (
        "Implementer completion",
        "Validator authorisation",
        "Review completion",
        "Merge approval",
        "GitHub Actions is the control plane, not the development-agent coding substrate",
        "GitHub Actions may observe state, validate guards, post audit evidence",
    ):
        assert phrase in docs["agents"]
        assert phrase in docs["state_machine"]
