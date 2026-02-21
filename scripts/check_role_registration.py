import os
import re

VALID_STATUSES = {
    "planning",
    "implementing",
    "gate-1-pending",
    "validating",
    "gate-2-pending",
    "merged",
    "blocked",
}


def fail(message: str) -> int:
    print(message)
    return 1


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def has_non_empty_table_value(lines: list[str], field: str) -> bool:
    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4 and parts[1] == field:
            return bool(parts[2])
    return False


def detect_role(content: str, agent: str) -> str | None:
    pattern = re.compile(
        rf"^\|\s*{re.escape(agent)}\s*\|\s*([^|]+?)\s*\|\s*$", re.MULTILINE
    )
    matches = pattern.findall(content)
    if len(matches) != 1:
        return None
    role = matches[0].strip()
    if role not in {"Implementer", "Validator"}:
        return None
    return role


def parse_active_registry(
    content: str,
) -> tuple[list[str], list[dict[str, str]]] | tuple[None, None]:
    lines = content.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == "## active pe registry":
            start = idx + 1
            break
    if start is None:
        return None, None

    table_lines: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            if table_lines:
                break
            continue
        if stripped.startswith("|"):
            table_lines.append(stripped)
            continue
        if table_lines:
            break

    if len(table_lines) < 3:
        return None, None

    header = [part.strip().lower() for part in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for row_line in table_lines[2:]:
        parts = [part.strip() for part in row_line.strip("|").split("|")]
        if len(parts) != len(header):
            return None, None
        rows.append(dict(zip(header, parts)))
    return header, rows


def extract_engine(agent_id: str) -> str | None:
    text = agent_id.strip().lower()
    if "codex" in text:
        return "codex"
    if "claude" in text:
        return "claude"
    return None


def main() -> int:
    path = os.environ.get("CURRENT_PE_PATH", "CURRENT_PE.md")

    if not os.path.exists(path):
        return fail("ERROR: CURRENT_PE.md not found.")

    content = read_text(path)
    lines = content.splitlines()

    has_pe = bool(
        re.search(r"^PE:\s*.+$", content, re.MULTILINE)
    ) or has_non_empty_table_value(lines, "PE")
    if not has_pe:
        return fail("ERROR: PE field missing.")

    has_branch = bool(
        re.search(r"^Branch:\s*.+$", content, re.MULTILINE)
    ) or has_non_empty_table_value(lines, "Branch")
    if not has_branch:
        return fail("ERROR: Branch field missing.")

    agents = ["CODEX", "Claude Code"]
    roles = {}

    for agent in agents:
        if agent not in content:
            return fail(f"ERROR: Agent {agent} not listed in CURRENT_PE.md.")
        role = detect_role(content, agent)
        if role is None:
            return fail(f"ERROR: Agent {agent} has no valid role.")
        roles[agent] = role

    if roles["CODEX"] == roles["Claude Code"]:
        return fail("ERROR: Both agents have the same role. Roles must differ.")

    required_release_fields = ["Release", "Base branch", "Plan file", "Plan location"]
    for field in required_release_fields:
        if not any(line.strip().startswith(f"| {field}") for line in lines):
            return fail(f"ERROR: Release context field missing: '{field}'")
        if not has_non_empty_table_value(lines, field):
            return fail(f"ERROR: Release context field '{field}' has no value.")

    header, rows = parse_active_registry(content)
    if header is None or rows is None:
        return fail("ERROR: Active PE Registry table missing or malformed.")
    required_columns = [
        "pe-id",
        "domain",
        "implementer-agentid",
        "validator-agentid",
        "branch",
        "status",
        "last-updated",
    ]
    for column in required_columns:
        if column not in header:
            return fail(f"ERROR: Active PE Registry column missing: '{column}'")

    if not rows:
        return fail("ERROR: Active PE Registry has no rows.")

    active_rows: list[dict[str, str]] = []
    for row in rows:
        pe_id = row["pe-id"]
        domain = row["domain"]
        implementer = row["implementer-agentid"]
        validator = row["validator-agentid"]
        branch = row["branch"]
        status = row["status"].lower()
        updated = row["last-updated"]

        if not all([pe_id, domain, implementer, validator, branch, status, updated]):
            return fail("ERROR: Active PE Registry contains empty required fields.")
        if status not in VALID_STATUSES:
            return fail(
                f"ERROR: Invalid status value '{row['status']}' in Active PE Registry."
            )

        impl_engine = extract_engine(implementer)
        val_engine = extract_engine(validator)
        if impl_engine is None:
            return fail(
                f"ERROR: Implementer agent id has no valid engine: '{implementer}'"
            )
        if val_engine is None:
            return fail(f"ERROR: Validator agent id has no valid engine: '{validator}'")
        if impl_engine == val_engine:
            return fail(
                "ERROR: Active PE Registry row has same engine for implementer and validator."
            )

        if status not in {"merged", "blocked"}:
            active_rows.append(row)

    previous_by_domain: dict[str, str] = {}
    for row in active_rows:
        domain = row["domain"].strip().lower()
        implementer_engine = extract_engine(row["implementer-agentid"])
        if implementer_engine is None:
            return fail(
                f"ERROR: Implementer agent id has no valid engine: '{row['implementer-agentid']}'"
            )
        previous_engine = previous_by_domain.get(domain)
        if previous_engine == implementer_engine:
            return fail(
                "ERROR: Consecutive same-domain PEs use the same implementer engine."
            )
        previous_by_domain[domain] = implementer_engine

    print("CURRENT_PE.md OK — role registration valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
