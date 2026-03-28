"""Validate CURRENT_PE.md for PE-AUTO-02."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


VALID_ACTIVE_STATUSES = {"planning", "implementing"}
VALID_REGISTRY_STATUSES = {
    "planning",
    "implementing",
    "gate-1-pending",
    "validating",
    "gate-2-pending",
    "merged",
    "blocked",
}
PE_ID_RE = re.compile(r"^PE-[A-Z]+-[0-9]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BRANCH_RE = re.compile(r"^(feature/pe-[a-z0-9-]+|chore/[a-z0-9-]+)$")


def fail(message: str) -> int:
    print(f"ERROR: {message}")
    return 1


def _table_value(lines: list[str], field: str) -> str | None:
    for line in lines:
        parts = [part.strip() for part in line.split("|")]
        if len(parts) >= 4 and parts[1] == field:
            return parts[2]
    return None


def _table_block(lines: list[str], heading: str) -> list[str]:
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == heading.lower():
            start = idx + 1
            break
    if start is None:
        return []

    block: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            if block:
                break
            continue
        if stripped.startswith("|"):
            block.append(stripped)
            continue
        if block:
            break
    return block


def _parse_roles(content: str) -> dict[str, str]:
    roles: dict[str, str] = {}
    for agent in ("CODEX", "Claude Code"):
        match = re.search(
            rf"^\|\s*{re.escape(agent)}\s*\|\s*([^|]+?)\s*\|$",
            content,
            re.MULTILINE,
        )
        if not match:
            raise ValueError(f"Agent role row missing for {agent}.")
        role = match.group(1).strip()
        if role not in {"Implementer", "Validator"}:
            raise ValueError(f"Agent {agent} has invalid role '{role}'.")
        roles[agent] = role
    return roles


def _parse_registry(content: str) -> tuple[list[str], list[dict[str, str]]]:
    block = _table_block(content.splitlines(), "## Active PE Registry")
    if len(block) < 3:
        raise ValueError("Active PE Registry table missing or malformed.")

    header = [
        part.strip().lower() for part in block[0].strip("|").split("|")
    ]
    rows: list[dict[str, str]] = []
    for raw in block[2:]:
        values = [part.strip() for part in raw.strip("|").split("|")]
        if len(values) != len(header):
            raise ValueError("Active PE Registry row has wrong column count.")
        rows.append(dict(zip(header, values)))
    return header, rows


def _engine(agent_id: str) -> str | None:
    lowered = agent_id.lower()
    if "codex" in lowered:
        return "codex"
    if "claude" in lowered:
        return "claude"
    return None


def _validate_release_context(lines: list[str]) -> None:
    for field in ("Release", "Base branch", "Plan file", "Plan location"):
        value = _table_value(lines, field)
        if not value:
            raise ValueError(f"Release context field '{field}' has no value.")


def _validate_current_pe(lines: list[str]) -> tuple[str, str]:
    pe = _table_value(lines, "PE")
    if not pe:
        raise ValueError("PE field missing or blank.")
    if not PE_ID_RE.fullmatch(pe):
        raise ValueError(f"PE field has invalid format: '{pe}'.")

    branch = _table_value(lines, "Branch")
    if not branch:
        raise ValueError("Branch field missing or blank.")
    if not BRANCH_RE.fullmatch(branch):
        raise ValueError(f"Branch has invalid format: '{branch}'.")
    return pe, branch


def _validate_registry(pe: str, branch: str, rows: list[dict[str, str]]) -> None:
    current = next((row for row in rows if row["pe-id"] == pe), None)
    if current is None:
        raise ValueError(f"Current PE '{pe}' not found in Active PE Registry.")

    if current["branch"] != branch:
        raise ValueError(
            "Current PE branch mismatch: "
            f"table has '{current['branch']}', expected '{branch}'."
        )

    status = current["status"].lower()
    if status not in VALID_REGISTRY_STATUSES:
        raise ValueError(f"Invalid registry status '{current['status']}'.")
    if status not in VALID_ACTIVE_STATUSES:
        raise ValueError(
            "Active PE status must be planning or implementing, "
            f"found '{current['status']}'."
        )
    if not DATE_RE.fullmatch(current["last-updated"]):
        raise ValueError(
            "Registry last-updated must be YYYY-MM-DD, "
            f"found '{current['last-updated']}'."
        )

    impl_engine = _engine(current["implementer-agentid"])
    val_engine = _engine(current["validator-agentid"])
    if impl_engine is None:
        raise ValueError(
            "Implementer agent id has no valid engine: "
            f"'{current['implementer-agentid']}'."
        )
    if val_engine is None:
        raise ValueError(
            "Validator agent id has no valid engine: "
            f"'{current['validator-agentid']}'."
        )
    if impl_engine == val_engine:
        raise ValueError("Implementer and validator must use opposite engines.")

    domain = current["domain"].strip().lower()
    merged_same_domain = [
        row
        for row in rows
        if row["domain"].strip().lower() == domain
        and row["status"].strip().lower() == "merged"
    ]
    if not merged_same_domain:
        return

    previous_engine = _engine(merged_same_domain[-1]["implementer-agentid"])
    if previous_engine is None:
        raise ValueError(
            "Previous merged implementer has no valid engine: "
            f"'{merged_same_domain[-1]['implementer-agentid']}'."
        )
    if previous_engine == impl_engine:
        raise ValueError(
            "Alternation rule violated: current implementer engine matches "
            "the last merged PE in the same domain."
        )


def main() -> int:
    path = Path(os.environ.get("CURRENT_PE_PATH", "CURRENT_PE.md"))
    if not path.exists():
        return fail("CURRENT_PE.md not found.")

    content = path.read_text(encoding="utf-8")
    if not content.strip():
        return fail("CURRENT_PE.md is empty.")

    lines = content.splitlines()
    try:
        _validate_release_context(lines)
        pe, branch = _validate_current_pe(lines)
        roles = _parse_roles(content)
        if roles["CODEX"] == roles["Claude Code"]:
            raise ValueError("Agent roles must differ.")

        header, rows = _parse_registry(content)
        required_columns = {
            "pe-id",
            "domain",
            "implementer-agentid",
            "validator-agentid",
            "branch",
            "status",
            "last-updated",
        }
        missing = sorted(required_columns.difference(header))
        if missing:
            raise ValueError(
                f"Active PE Registry columns missing: {', '.join(missing)}."
            )
        _validate_registry(pe, branch, rows)
        current = next(row for row in rows if row["pe-id"] == pe)
        impl_engine = _engine(current["implementer-agentid"])
        val_engine = _engine(current["validator-agentid"])
        expected_codex_role = "Implementer" if impl_engine == "codex" else "Validator"
        expected_claude_role = "Implementer" if impl_engine == "claude" else "Validator"
        if (
            roles["CODEX"] != expected_codex_role
            or roles["Claude Code"] != expected_claude_role
        ):
            raise ValueError(
                "Agent roles table does not match the active PE registry "
                "engines."
            )
        if val_engine != ("claude" if impl_engine == "codex" else "codex"):
            raise ValueError("Active PE registry engines are not opposite.")
    except ValueError as exc:
        return fail(str(exc))

    print(
        "CURRENT_PE.md OK — release context, roles, registry, and "
        "alternation valid."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
