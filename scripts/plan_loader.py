"""PE-AUTO-09 Plan Loader — validate and ingest a JSON PE execution plan.

Usage:
    python scripts/plan_loader.py plan.json
    python scripts/plan_loader.py plan.json --write-current-pe
    python scripts/plan_loader.py plan.json --already-merged PE-AUTO-01,PE-AUTO-02
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Schema path
# ---------------------------------------------------------------------------

_SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "plan_schema.json"

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


class LoaderError(ValueError):
    """Raised when plan validation fails."""


# ---------------------------------------------------------------------------
# JSON Schema validation (lightweight — no external dependency)
# ---------------------------------------------------------------------------


def _check_type(value: Any, expected: str, path: str) -> None:
    type_map: dict[str, type | tuple[type, ...]] = {
        "string": str,
        "array": list,
        "object": dict,
        "boolean": bool,
        "integer": int,
        "number": (int, float),
    }
    if expected not in type_map:
        return
    if not isinstance(value, type_map[expected]):
        raise LoaderError(f"{path}: expected {expected}, got {type(value).__name__}")


def _validate_pe(pe: Any, idx: int) -> None:
    path = f"pes[{idx}]"
    _check_type(pe, "object", path)
    required = [
        "id",
        "domain",
        "depends_on",
        "implementer",
        "validator",
        "acceptance_criteria",
    ]
    for field in required:
        if field not in pe:
            raise LoaderError(f"{path}: missing required field '{field}'")
    _check_type(pe["id"], "string", f"{path}.id")
    _check_type(pe["domain"], "string", f"{path}.domain")
    _check_type(pe["implementer"], "string", f"{path}.implementer")
    _check_type(pe["validator"], "string", f"{path}.validator")
    _check_type(pe["depends_on"], "array", f"{path}.depends_on")
    _check_type(pe["acceptance_criteria"], "array", f"{path}.acceptance_criteria")
    if not pe["id"]:
        raise LoaderError(f"{path}.id: must not be empty")
    if not pe["domain"]:
        raise LoaderError(f"{path}.domain: must not be empty")
    if not pe["implementer"]:
        raise LoaderError(f"{path}.implementer: must not be empty")
    if not pe["validator"]:
        raise LoaderError(f"{path}.validator: must not be empty")
    if not pe["acceptance_criteria"]:
        raise LoaderError(f"{path}.acceptance_criteria: must not be empty")
    for i, ac in enumerate(pe["acceptance_criteria"]):
        _check_type(ac, "string", f"{path}.acceptance_criteria[{i}]")
        if not ac:
            raise LoaderError(
                f"{path}.acceptance_criteria[{i}]: criterion must not be empty"
            )
    for i, dep in enumerate(pe["depends_on"]):
        _check_type(dep, "string", f"{path}.depends_on[{i}]")


def validate_schema(plan: Any) -> None:
    """Validate plan object against the required structure (AC-1)."""
    _check_type(plan, "object", "plan")
    for field in ("release", "base_branch", "pes"):
        if field not in plan or plan[field] is None:
            raise LoaderError(f"plan: missing required field '{field}'")
    _check_type(plan["release"], "string", "plan.release")
    _check_type(plan["base_branch"], "string", "plan.base_branch")
    _check_type(plan["pes"], "array", "plan.pes")
    if not plan["pes"]:
        raise LoaderError("plan.pes: must contain at least one PE")
    for idx, pe in enumerate(plan["pes"]):
        _validate_pe(pe, idx)


# ---------------------------------------------------------------------------
# DAG cycle detection (AC-2)
# ---------------------------------------------------------------------------


def _topological_sort(pe_ids: list[str], deps: dict[str, list[str]]) -> list[str]:
    """Kahn's algorithm; raises LoaderError with cycle diagram on cycle."""
    in_degree: dict[str, int] = {pe_id: 0 for pe_id in pe_ids}
    graph: dict[str, list[str]] = {pe_id: [] for pe_id in pe_ids}

    for pe_id in pe_ids:
        for dep in deps.get(pe_id, []):
            if dep not in graph:
                # External (already-merged) dependency — skip for cycle purposes.
                continue
            graph[dep].append(pe_id)
            in_degree[pe_id] += 1

    queue = [pe_id for pe_id in pe_ids if in_degree[pe_id] == 0]
    order: list[str] = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for neighbour in graph[node]:
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                queue.append(neighbour)

    if len(order) != len(pe_ids):
        # Identify nodes still in a cycle.
        cyclic = [pe_id for pe_id in pe_ids if pe_id not in order]
        diagram = " → ".join(cyclic) + " → (cycle)"
        raise LoaderError(
            f"Dependency DAG contains a cycle: {diagram}\n"
            f"Cyclic PEs: {', '.join(cyclic)}"
        )
    return order


def validate_dag(pes: list[dict[str, Any]]) -> list[str]:
    """Return topological order; raise LoaderError if a cycle exists (AC-2)."""
    pe_ids = [pe["id"] for pe in pes]
    deps = {pe["id"]: pe["depends_on"] for pe in pes}
    return _topological_sort(pe_ids, deps)


# ---------------------------------------------------------------------------
# Alternation rule (AC-3)
# ---------------------------------------------------------------------------


def _engine(agent_id: str) -> str:
    lower = agent_id.lower()
    if "codex" in lower:
        return "codex"
    if "claude" in lower:
        return "claude"
    raise LoaderError(
        f"Cannot infer engine from agent id '{agent_id}'. "
        "Expected 'codex' or 'claude' in the agent ID."
    )


def validate_alternation(pes: list[dict[str, Any]], topo_order: list[str]) -> None:
    """Verify the implementer engine alternates in topological order (AC-3).

    Only checks consecutive PEs in the same domain.
    """
    pe_by_id = {pe["id"]: pe for pe in pes}
    domain_last_engine: dict[str, str] = {}

    for pe_id in topo_order:
        pe = pe_by_id[pe_id]
        domain = pe["domain"]
        engine = _engine(pe["implementer"])
        validator_engine = _engine(pe["validator"])

        if validator_engine == engine:
            raise LoaderError(
                f"PE {pe_id}: implementer and validator use the same engine "
                f"('{engine}'). They must alternate."
            )

        last = domain_last_engine.get(domain)
        if last is not None and last == engine:
            raise LoaderError(
                f"PE {pe_id} (domain '{domain}'): implementer engine '{engine}' "
                f"does not alternate — previous PE in this domain also used '{engine}'."
            )
        domain_last_engine[domain] = engine


# ---------------------------------------------------------------------------
# First PE readiness (AC-4 precondition)
# ---------------------------------------------------------------------------


def validate_first_pe_ready(
    pes: list[dict[str, Any]],
    topo_order: list[str],
    already_merged: set[str],
) -> str:
    """Return the first-ready PE id; raise LoaderError if no PE is ready to start."""
    pe_by_id = {pe["id"]: pe for pe in pes}
    for pe_id in topo_order:
        if pe_id in already_merged:
            continue
        pe = pe_by_id[pe_id]
        # A dependency is satisfied only if it appears in already_merged.
        # This applies equally to internal and external dependencies.
        unsatisfied = [dep for dep in pe["depends_on"] if dep not in already_merged]
        if not unsatisfied:
            return pe_id
    raise LoaderError(
        "No PE is ready to start: all PEs have unsatisfied dependencies. "
        f"Already merged: {sorted(already_merged) or '(none)'}. "
        "Ensure at least one PE has depends_on: [] or all its dependencies are merged."
    )


# ---------------------------------------------------------------------------
# CURRENT_PE.md generation (AC-4)
# ---------------------------------------------------------------------------

_CURRENT_PE_TEMPLATE = """\
# Current PE Assignment

> Maintained by PM. Update ALL fields at the start of every new PE or release.
> Both agents read this file as Step 0. It is the only file that needs editing
> when switching release lines.

---

## Release context

| Field          | Value                                                          |
|----------------|----------------------------------------------------------------|
| Release        | {release}                                                      |
| Base branch    | {base_branch}                                                  |
| Plan file      | {plan_file}                                                    |
| Plan location  | repo root                                                      |

---

## Current PE

| Field   | Value                                              |
|---------|----------------------------------------------------|
| PE      | {pe_id}                                            |
| Branch  | {branch}                                           |

---

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | {codex_role:<11} |
| Claude Code | {claude_role:<11} |

---

## Active PE Registry

| PE-ID       | Domain          | Implementer-agentId  | Validator-agentId  | Branch                                            | Status          | Last-updated |
|-------------|-----------------|----------------------|--------------------|---------------------------------------------------|-----------------|--------------|
| {pe_id:<11} | {domain:<15} | {implementer:<20} | {validator:<18} | {branch:<49} | implementing    | {today}   |

PM housekeeping entries (prefix `PM-CHORE-XX`):
- Direct commits to main by PM, no PE workflow required.

| Chore ID     | Description                                                                 | Date       |
|--------------|-----------------------------------------------------------------------------|------------|
| PM-CHORE-01  | Plan loaded via plan_loader.py — opened {pe_id}.                            | {today} |
"""


def _make_branch_name(pe_id: str, title: str = "") -> str:
    """Generate a branch name from a PE id and optional title."""
    slug = pe_id.lower().replace("-", "-")
    if title:
        title_slug = title.lower()
        title_slug = "".join(c if c.isalnum() else "-" for c in title_slug)
        title_slug = "-".join(part for part in title_slug.split("-") if part)
        return f"feature/{slug}-{title_slug}"
    return f"feature/{slug}"


def generate_current_pe(
    plan: dict[str, Any],
    first_pe_id: str,
    today: str,
) -> str:
    """Generate the content of CURRENT_PE.md for the first PE (AC-4)."""
    pe_by_id = {pe["id"]: pe for pe in plan["pes"]}
    pe = pe_by_id[first_pe_id]
    title = pe.get("title", "")
    branch = _make_branch_name(first_pe_id, title)
    impl_engine = _engine(pe["implementer"])
    codex_role = "Implementer" if impl_engine == "codex" else "Validator"
    claude_role = "Implementer" if impl_engine == "claude" else "Validator"

    return _CURRENT_PE_TEMPLATE.format(
        release=plan["release"],
        base_branch=plan["base_branch"],
        plan_file=plan.get("plan_file", "plan.json"),
        pe_id=first_pe_id,
        branch=branch,
        codex_role=codex_role,
        claude_role=claude_role,
        domain=pe["domain"],
        implementer=pe["implementer"],
        validator=pe["validator"],
        today=today,
    )


# ---------------------------------------------------------------------------
# Top-level validate()
# ---------------------------------------------------------------------------


def validate(
    plan: Any,
    already_merged: set[str] | None = None,
) -> tuple[list[str], str]:
    """Validate *plan* fully; return (topo_order, first_ready_pe_id).

    Raises LoaderError with a descriptive message on any failure.
    """
    if already_merged is None:
        already_merged = set()
    validate_schema(plan)
    topo_order = validate_dag(plan["pes"])
    validate_alternation(plan["pes"], topo_order)
    first_pe_id = validate_first_pe_ready(plan["pes"], topo_order, already_merged)
    return topo_order, first_pe_id


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and ingest a JSON PE execution plan."
    )
    parser.add_argument("plan_file", help="Path to the JSON plan file.")
    parser.add_argument(
        "--already-merged",
        default="",
        help="Comma-separated PE IDs already merged (satisfies their dependencies).",
    )
    parser.add_argument(
        "--write-current-pe",
        metavar="OUTPUT",
        default=None,
        help="Write generated CURRENT_PE.md to OUTPUT path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print result summary as JSON.",
    )
    args = parser.parse_args()

    try:
        raw = Path(args.plan_file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read plan file: {exc}", file=sys.stderr)
        return 1

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 1

    already_merged: set[str] = set()
    if args.already_merged:
        already_merged = {
            s.strip() for s in args.already_merged.split(",") if s.strip()
        }

    try:
        topo_order, first_pe_id = validate(plan, already_merged)
    except LoaderError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    today = dt.date.today().isoformat()
    current_pe_content = generate_current_pe(plan, first_pe_id, today)

    if args.write_current_pe:
        Path(args.write_current_pe).write_text(current_pe_content, encoding="utf-8")

    result = {
        "valid": True,
        "topo_order": topo_order,
        "first_pe": first_pe_id,
        "pe_count": len(plan["pes"]),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"VALID: {len(plan['pes'])} PEs, first ready: {first_pe_id}")
        print(f"Topological order: {' -> '.join(topo_order)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
