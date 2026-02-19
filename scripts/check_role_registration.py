import os
import re


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

    print("CURRENT_PE.md OK — role registration valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
