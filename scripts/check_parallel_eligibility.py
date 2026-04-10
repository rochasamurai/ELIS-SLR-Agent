"""PE-AUTO-11 — Check whether two PEs are eligible for parallel dispatch.

Usage:
    python -m scripts.check_parallel_eligibility PE-X PE-Y plan.md
    python scripts/check_parallel_eligibility.py PE-X PE-Y plan.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.pe_sequencer import PlanPE, SequencerError, parse_plan


def _engine(agent_id: str) -> str:
    lowered = agent_id.lower()
    if "codex" in lowered:
        return "codex"
    if "claude" in lowered:
        return "claude"
    raise SequencerError(
        f"Cannot infer engine from agent id '{agent_id}'. "
        "Expected 'codex' or 'claude' in the agent ID."
    )


def _has_transitive_dependency(
    source: str,
    target: str,
    pe_map: dict[str, PlanPE],
) -> bool:
    """Return True if *source* has a transitive dependency on *target*."""
    visited: set[str] = set()
    stack = list(pe_map[source].depends_on) if source in pe_map else []
    while stack:
        dep = stack.pop()
        if dep == target:
            return True
        if dep in visited:
            continue
        visited.add(dep)
        if dep in pe_map:
            stack.extend(pe_map[dep].depends_on)
    return False


def check_eligibility(
    pe_a_id: str,
    pe_b_id: str,
    plan_pes: list[PlanPE],
) -> tuple[bool, list[str]]:
    """Return (eligible, failures).

    *failures* is an empty list when *eligible* is True.

    Eligibility criteria:
      1. Both PE IDs must exist in *plan_pes*.
      2. No direct dependency between them (in either direction).
      3. No transitive dependency between them (in either direction).
      4. Different implementer engines (parallel tracks must use opposite engines).
    """
    pe_map = {pe.pe_id: pe for pe in plan_pes}
    failures: list[str] = []

    if pe_a_id not in pe_map:
        failures.append(f"PE {pe_a_id} not found in plan.")
    if pe_b_id not in pe_map:
        failures.append(f"PE {pe_b_id} not found in plan.")
    if failures:
        return False, failures

    pe_a = pe_map[pe_a_id]
    pe_b = pe_map[pe_b_id]

    # Direct dependency
    if pe_b_id in pe_a.depends_on:
        failures.append(f"{pe_a_id} directly depends on {pe_b_id}.")
    if pe_a_id in pe_b.depends_on:
        failures.append(f"{pe_b_id} directly depends on {pe_a_id}.")

    # Transitive dependency (only when not already flagged as direct)
    if pe_b_id not in pe_a.depends_on and _has_transitive_dependency(
        pe_a_id, pe_b_id, pe_map
    ):
        failures.append(f"{pe_a_id} transitively depends on {pe_b_id}.")
    if pe_a_id not in pe_b.depends_on and _has_transitive_dependency(
        pe_b_id, pe_a_id, pe_map
    ):
        failures.append(f"{pe_b_id} transitively depends on {pe_a_id}.")

    # Engine check
    try:
        engine_a = _engine(pe_a.implementer_agent)
        engine_b = _engine(pe_b.implementer_agent)
        if engine_a == engine_b:
            failures.append(
                f"{pe_a_id} and {pe_b_id} use the same implementer engine "
                f"('{engine_a}'). Parallel tracks must use opposite engines."
            )
    except SequencerError as exc:
        failures.append(str(exc))

    if failures:
        return False, failures
    return True, []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether two PEs are eligible for parallel dispatch."
    )
    parser.add_argument("pe_a", help="First PE ID (e.g. PE-AUTO-11)")
    parser.add_argument("pe_b", help="Second PE ID (e.g. PE-AUTO-12)")
    parser.add_argument("plan_file", help="Path to the plan markdown file.")
    args = parser.parse_args()

    try:
        plan_pes = parse_plan(Path(args.plan_file))
    except (SequencerError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    eligible, failures = check_eligibility(args.pe_a, args.pe_b, plan_pes)
    if eligible:
        print(f"ELIGIBLE: {args.pe_a} and {args.pe_b} may run in parallel.")
        return 0

    print(f"INELIGIBLE: {args.pe_a} and {args.pe_b} cannot run in parallel.")
    for reason in failures:
        print(f"  - {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
