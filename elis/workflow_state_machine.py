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

IMPLEMENTER_DISPATCH_STATE = "implementing"
IMPLEMENTER_COMPLETION_TARGET_STATE = "gate-1-pending"
VALIDATOR_DISPATCH_SOURCE_STATE = "gate-1-pending"
VALIDATOR_DISPATCH_TARGET_STATE = "validating"
LOCAL_AGENT_EXECUTION_SURFACE = "elis-server"

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


def ensure_canonical_state(state: str) -> str:
    """Return *state* if it is canonical; raise ValueError otherwise."""

    if not is_canonical_state(state):
        raise ValueError(f"Unknown PE workflow state: {state!r}.")
    return state


def can_transition(source: str, target: str) -> bool:
    """Return whether the state machine permits a source -> target move."""

    return (source, target) in ALLOWED_TRANSITIONS


def implementer_dispatch_allowed(state: str) -> bool:
    """Return whether the control plane may dispatch an implementer session."""

    return ensure_canonical_state(state) == IMPLEMENTER_DISPATCH_STATE


def implementer_completion_observable(state: str) -> bool:
    """Return whether guard evidence may move implementation to Gate 1."""

    ensure_canonical_state(state)
    return can_transition(state, IMPLEMENTER_COMPLETION_TARGET_STATE)


def validator_dispatch_allowed(state: str) -> bool:
    """Return whether the control plane may dispatch a validator session."""

    ensure_canonical_state(state)
    return can_transition(state, VALIDATOR_DISPATCH_TARGET_STATE)


def validator_dispatch_allowed_after_evidence(state: str) -> bool:
    """Return whether validator dispatch may proceed after evidence checks pass.

    In live automation, ``CURRENT_PE.md`` can still record ``implementing`` while
    the PR branch already contains complete handoff evidence. In that case the
    control plane observes ``implementing -> gate-1-pending`` and then dispatches
    through ``gate-1-pending -> validating``.
    """

    return validator_dispatch_allowed(state) or (
        implementer_completion_observable(state)
        and validator_dispatch_allowed(IMPLEMENTER_COMPLETION_TARGET_STATE)
    )


def guards_for(source: str, target: str) -> tuple[str, ...]:
    """Return the guard evidence required for a source -> target move."""

    return TRANSITION_GUARDS.get((source, target), ())


def undocumented_states(states: Iterable[str]) -> tuple[str, ...]:
    """Return canonical states missing from a discovered state collection."""

    discovered = set(states)
    return tuple(state for state in CANONICAL_STATES if state not in discovered)
