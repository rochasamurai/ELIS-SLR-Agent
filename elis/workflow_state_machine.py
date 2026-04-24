"""Canonical PE workflow state machine contract.

This module keeps the state labels and guarded transitions discoverable by
scripts, tests, and documentation checks. Human-facing governance remains in
AGENTS.md and the architecture docs; this module is the machine-readable mirror.
"""

from __future__ import annotations

from collections.abc import Iterable

CANONICAL_STATES: tuple[str, ...] = (
    "planning",
    "implementing",
    "gate-1-pending",
    "validating",
    "gate-2-pending",
    "merged",
    "blocked",
    "superseded",
)

ACTIVE_STATES: tuple[str, ...] = (
    "planning",
    "implementing",
    "gate-1-pending",
    "validating",
    "gate-2-pending",
    "blocked",
)

TERMINAL_STATES: tuple[str, ...] = ("merged", "superseded")

_DIRECT_TRANSITIONS: tuple[tuple[str, str], ...] = (
    ("planning", "implementing"),
    ("implementing", "gate-1-pending"),
    ("gate-1-pending", "validating"),
    ("gate-1-pending", "blocked"),
    ("validating", "gate-2-pending"),
    ("gate-2-pending", "merged"),
    ("gate-2-pending", "blocked"),
)

ALLOWED_TRANSITIONS: tuple[tuple[str, str], ...] = (
    *_DIRECT_TRANSITIONS,
    *tuple((state, "superseded") for state in ACTIVE_STATES),
)

IMPLEMENTER_COMPLETION_GUARDS: tuple[str, ...] = (
    "HANDOFF.md is present and complete",
    "Status Packet sections are complete",
    "Handoff artefacts are committed on the PE branch",
    "The runner observes a matching PE and branch pair",
)

VALIDATOR_AUTHORISATION_GUARDS: tuple[str, ...] = (
    "Explicit PM authorisation is recorded",
    "Validator assignment evidence is present",
    "The PE remains active in CURRENT_PE.md",
)

REVIEW_COMPLETION_GUARDS: tuple[str, ...] = (
    "REVIEW evidence is present",
    "A formal verdict is recorded in the REVIEW file",
    "CI gates are not broken by validator artefacts",
)

MERGE_APPROVAL_GUARDS: tuple[str, ...] = (
    "CI is green",
    "Required review approval is satisfied",
    "No pm-review-required veto label is present",
)

TRANSITION_GUARDS: dict[tuple[str, str], tuple[str, ...]] = {
    ("implementing", "gate-1-pending"): IMPLEMENTER_COMPLETION_GUARDS,
    ("gate-1-pending", "validating"): VALIDATOR_AUTHORISATION_GUARDS,
    ("validating", "gate-2-pending"): REVIEW_COMPLETION_GUARDS,
    ("gate-2-pending", "merged"): MERGE_APPROVAL_GUARDS,
}


def is_canonical_state(state: str) -> bool:
    """Return whether *state* is one of the governed PE state labels."""

    return state in CANONICAL_STATES


def can_transition(source: str, target: str) -> bool:
    """Return whether the state machine permits a source -> target move."""

    return (source, target) in ALLOWED_TRANSITIONS


def guards_for(source: str, target: str) -> tuple[str, ...]:
    """Return the guard evidence required for a source -> target move."""

    return TRANSITION_GUARDS.get((source, target), ())


def undocumented_states(states: Iterable[str]) -> tuple[str, ...]:
    """Return canonical states missing from a discovered state collection."""

    discovered = set(states)
    return tuple(state for state in CANONICAL_STATES if state not in discovered)
