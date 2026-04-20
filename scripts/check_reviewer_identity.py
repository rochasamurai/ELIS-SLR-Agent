#!/usr/bin/env python3
"""
Verify that the reviewer who submitted an approval review is the mapped bot
identity for the current PE's validator role.

Reads CURRENT_PE.md to determine the active validator's agent ID, resolves its
engine from the slot suffix (a → codex, b → claude, c → gemini), then looks up
the expected review_login in config/reviewer_identity_map.json.

Environment variables
---------------------
REVIEWER_LOGIN    GitHub login of the review submitter (required)
CURRENT_PE_PATH   Path to CURRENT_PE.md (default: CURRENT_PE.md)
REVIEWER_MAP_PATH Path to config/reviewer_identity_map.json
                  (default: config/reviewer_identity_map.json)

Exit codes
----------
0  Reviewer is the mapped bot for this PE's validator role.
1  Reviewer is NOT the expected bot, or a configuration error occurred.
"""

import json
import os
import re
import sys

CURRENT_PE_PATH = os.environ.get("CURRENT_PE_PATH", "CURRENT_PE.md")
REVIEWER_MAP_PATH = os.environ.get(
    "REVIEWER_MAP_PATH", "config/reviewer_identity_map.json"
)

# Canonical slot-to-engine mapping (AGENTS.md §14.2)
_SLOT_TO_ENGINE: dict[str, str] = {"a": "codex", "b": "claude", "c": "gemini"}


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _get_validator_agent_id(current_pe_path: str) -> str | None:
    """Return the validator agentId from the note line in CURRENT_PE.md.

    Matches lines of the form:
        `infra-val-a` (CODEX @ `elis-server`) as Validator.
    """
    with open(current_pe_path, encoding="utf-8") as fh:
        content = fh.read()
    m = re.search(r"`([\w-]+)`\s*\([^)]+\)\s+as Validator", content)
    if m:
        return m.group(1)
    return None


def _engine_from_agent_id(agent_id: str) -> str | None:
    """Derive engine name from the slot suffix of a canonical agent ID.

    Examples:
        infra-val-a → codex
        infra-impl-b → claude
    """
    parts = agent_id.split("-")
    if not parts:
        return None
    slot = parts[-1]
    return _SLOT_TO_ENGINE.get(slot)


def _expected_review_login(reviewer_map: dict, engine: str) -> str | None:
    """Return the review_login for an engine, only if validator-capable."""
    for agent_data in reviewer_map.get("agents", {}).values():
        if agent_data.get("engine") == engine and agent_data.get(
            "validator_capable_on_protected_branches", False
        ):
            return agent_data.get("review_login")
    return None


def main() -> int:
    reviewer_login = os.environ.get("REVIEWER_LOGIN", "").strip()
    if not reviewer_login:
        print("ERROR: REVIEWER_LOGIN is not set.", file=sys.stderr)
        return 1

    try:
        reviewer_map = _load_json(REVIEWER_MAP_PATH)
    except FileNotFoundError:
        print(
            f"ERROR: reviewer_identity_map not found at '{REVIEWER_MAP_PATH}'.",
            file=sys.stderr,
        )
        return 1

    validator_id = _get_validator_agent_id(CURRENT_PE_PATH)
    if not validator_id:
        print(
            "ERROR: Could not determine validator agentId from CURRENT_PE.md.\n"
            "  Expected a line: `<agentId>` (...) as Validator",
            file=sys.stderr,
        )
        return 1

    engine = _engine_from_agent_id(validator_id)
    if not engine:
        print(
            f"ERROR: Cannot derive engine from agentId '{validator_id}'."
            f" Slot suffix must be one of: {list(_SLOT_TO_ENGINE)}",
            file=sys.stderr,
        )
        return 1

    expected_login = _expected_review_login(reviewer_map, engine)
    if not expected_login:
        print(
            f"ERROR: No validator-capable mapped bot for engine '{engine}'"
            f" in '{REVIEWER_MAP_PATH}'.",
            file=sys.stderr,
        )
        return 1

    if reviewer_login == expected_login:
        print(
            f"OK: reviewer '{reviewer_login}' matches mapped bot"
            f" for engine '{engine}' (validator: {validator_id})."
        )
        return 0

    print(
        f"FAIL: reviewer '{reviewer_login}' does not match expected"
        f" '{expected_login}' for engine '{engine}'"
        f" (validator: {validator_id}).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
