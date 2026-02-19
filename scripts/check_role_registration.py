import os
import re


def fail(message: str) -> int:
    print(message)
    return 1


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def detect_role(content: str, agent: str) -> str | None:
    pattern = re.compile(
        rf"^\|\s*{re.escape(agent)}\s*\|\s*([^|]+?)\s*\|\s*$", re.MULTILINE
    )
    match = pattern.search(content)
    if not match:
        return None
    role = match.group(1).strip()
    if role not in {"Implementer", "Validator"}:
        return None
    return role


def main() -> int:
    path = os.environ.get("CURRENT_PE_PATH", "CURRENT_PE.md")

    if not os.path.exists(path):
        return fail("ERROR: CURRENT_PE.md not found.")

    content = read_text(path)

    if not re.search(r"^PE:\s*.+$", content, re.MULTILINE):
        return fail("ERROR: PE field missing.")

    if not re.search(r"^Branch:\s*.+$", content, re.MULTILINE):
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

    print("CURRENT_PE.md OK — role registration valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
