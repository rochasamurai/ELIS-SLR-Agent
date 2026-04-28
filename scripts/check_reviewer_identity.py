#!/usr/bin/env python3
"""
Verify that the reviewer who submitted an approval review is the mapped bot
identity for the current PE's validator role.

Reads CURRENT_PE.md to determine the active validator's agent ID and resolves
the expected reviewer by canonical slot first (a/b/c). This avoids ambiguous
engine-only matching when multiple validator-capable entries share an engine.

For backwards compatibility, if a canonical slot key is missing from the config,
it falls back to engine-based lookup only when it is unambiguous.

Environment variables
---------------------
REVIEWER_LOGIN        GitHub login of the review submitter (required)
CURRENT_PE_PATH       Path to CURRENT_PE.md (default: CURRENT_PE.md)
OPENCLAW_CONFIG_PATH  Path to openclaw/openclaw.json
                      (default: openclaw/openclaw.json)

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
OPENCLAW_CONFIG_PATH = os.environ.get(
    "OPENCLAW_CONFIG_PATH", "openclaw/openclaw.json"
)

# Canonical slot-to-engine mapping (AGENTS.md §14.2)
_SLOT_TO_ENGINE: dict[str, str] = {"a": "codex", "b": "claude", "c": "gemini"}
_SLOT_TO_AGENT_KEY: dict[str, str] = {
    "a": "CODEX",
    "b": "Claude Code",
    "c": "Gemini CLI",
}


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_reviewer_identities(path: str) -> dict:
    data = _load_json(path)
    agents = data.get("agents")
    if not isinstance(agents, dict):
        raise KeyError("agents")
    identities = agents.get("reviewerIdentities")
    if not isinstance(identities, dict):
        raise KeyError("agents.reviewerIdentities")
    return {"agents": identities}


def _get_validator_agent_id(current_pe_path: str) -> str | None:
    """Return the validator agentId from the note line in CURRENT_PE.md.

    Matches lines of the form:
        `infra-val-a` (CODEX @ `elis-server`) as Validator.
    """
    with open(current_pe_path, encoding="utf-8") as fh:
        content = fh.read()
    m = re.search(r"`([\w-]+)`\s*([^)]+)\s+as Validator", content)
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


def _slot_from_agent_id(agent_id: str) -> str | None:
    parts = agent_id.split("-")
    if not parts:
        return None
    return parts[-1]


def _expected_review_login_for_slot(reviewer_map: dict, slot: str) -> str | None:
    """Resolve expected review login by canonical slot mapping."""
    agent_key = _SLOT_TO_AGENT_KEY.get(slot)
    if not agent_key:
        return None
    agent_data = reviewer_map.get("agents", {}).get(agent_key)
    if not agent_data:
        return None
    if not agent_data.get("validator_capable_on_protected_branches", False):
        return None
    return agent_data.get("review_login")


def _expected_review_login_by_engine_unambiguous(
    reviewer_map: dict, engine: str
) -> str | None:
    """Fallback engine lookup allowed only when exactly one candidate exists."""
    candidates = []
    for agent_data in reviewer_map.get("agents", {}).values():
        if agent_data.get("engine") == engine and agent_data.get(
            "validator_capable_on_protected_branches", False
        ):
            login = agent_data.get("review_login")
            if login:
                candidates.append(login)
    if not candidates:
        return None
    unique = sorted(set(candidates))
    if len(unique) == 1:
        return unique[0]
    return None


def main() -> int:
    reviewer_login = os.environ.get("REVIEWER_LOGIN", "").strip()
    if not reviewer_login:
        print("ERROR: REVIEWER_LOGIN is not set.", file=sys.stderr)
        return 1

    try:
        reviewer_map = _load_reviewer_identities(OPENCLAW_CONFIG_PATH)
    except FileNotFoundError:
        print(
            f"ERROR: openclaw config not found at '{OPENCLAW_CONFIG_PATH}'.",
            file=sys.stderr,
        )
        return 1
    except KeyError as exc:
        print(
            f"ERROR: openclaw config missing reviewer identities ({exc}).",
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

    slot = _slot_from_agent_id(validator_id)
    expected_login = None
    if slot:
        expected_login = _expected_review_login_for_slot(reviewer_map, slot)
    if not expected_login:
        expected_login = _expected_review_login_by_engine_unambiguous(
            reviewer_map, engine
        )
    if not expected_login:
        print(
            "ERROR: Could not resolve a unique validator mapped bot login.\n"
            f"  validator_id={validator_id} slot={slot or '?'} engine={engine}\n"
            "  Expected canonical slot key mapping first (CODEX/Claude Code/Gemini CLI),\n"
            "  else an unambiguous single validator-capable engine match in\n"
            f"  '{OPENCLAW_CONFIG_PATH}'.",
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
