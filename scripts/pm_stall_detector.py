#!/usr/bin/env python
"""PE-OC-08 PM Agent — stall and iteration-threshold detection.

Cron-triggered script that scans the Active PE Registry for:
  - PEs stuck in the same status for > 48 hours (stall)
  - PEs with validator iteration count > 2 (iteration breach)

Emits escalation messages to stdout (one per finding) when thresholds are exceeded.

Usage:
    python scripts/pm_stall_detector.py
    python scripts/pm_stall_detector.py --registry CURRENT_PE.md --threshold-hours 48
    python scripts/pm_stall_detector.py --output escalations.json
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import sys

# ---------------------------------------------------------------------------
# Registry parsing (verbatim from scripts/pm_assign_pe.py)
# ---------------------------------------------------------------------------

VALID_STATUSES = {
    "planning",
    "implementing",
    "gate-1-pending",
    "validating",
    "gate-2-pending",
    "merged",
    "blocked",
}

ACTIVE_STATUSES = VALID_STATUSES - {"merged"}

_DEFAULT_REGISTRY = pathlib.Path("CURRENT_PE.md")
_DEFAULT_THRESHOLD_HOURS = 48
_DEFAULT_ITERATION_THRESHOLD = 2


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


# ---------------------------------------------------------------------------
# Stall detection
# ---------------------------------------------------------------------------


def _age_hours(last_updated: str, now: datetime.datetime) -> float | None:
    """Return age in hours from last-updated date string, or None if unparseable."""
    try:
        updated_date = datetime.date.fromisoformat(last_updated.strip())
    except ValueError:
        return None
    updated_dt = datetime.datetime(
        updated_date.year,
        updated_date.month,
        updated_date.day,
        tzinfo=datetime.timezone.utc,
    )
    return (now - updated_dt).total_seconds() / 3600


def detect_stalls(
    rows: list[dict[str, str]],
    now: datetime.datetime,
    threshold_hours: int = _DEFAULT_THRESHOLD_HOURS,
) -> list[dict[str, str]]:
    """Return active PE rows stalled beyond threshold_hours."""
    stalled: list[dict[str, str]] = []
    for row in rows:
        status = row.get("status", "").lower()
        if status not in ACTIVE_STATUSES:
            continue
        last_updated = row.get("last-updated", "")
        age = _age_hours(last_updated, now)
        if age is not None and age > threshold_hours:
            stalled.append(row)
    return stalled


# ---------------------------------------------------------------------------
# Iteration (validator round) counting
# ---------------------------------------------------------------------------

_ROUND_HISTORY_PATTERN = re.compile(r"^\s*\|\s*r\d+\s*\|", re.IGNORECASE)


def _review_file_path(pe_id: str, repo_root: pathlib.Path) -> pathlib.Path | None:
    """Locate the REVIEW file for a given PE-ID."""
    normalized = pe_id.upper().replace("-", "_")
    candidate = repo_root / f"REVIEW_{normalized}.md"
    if candidate.exists():
        return candidate
    return None


def count_validator_iterations(pe_id: str, repo_root: pathlib.Path) -> int:
    """Count completed validator rounds from the REVIEW file Round History table."""
    review_path = _review_file_path(pe_id, repo_root)
    if review_path is None:
        return 0
    content = review_path.read_text(encoding="utf-8")
    return sum(1 for line in content.splitlines() if _ROUND_HISTORY_PATTERN.match(line))


def detect_iteration_breaches(
    rows: list[dict[str, str]],
    repo_root: pathlib.Path,
    threshold: int = _DEFAULT_ITERATION_THRESHOLD,
) -> list[tuple[dict[str, str], int]]:
    """Return (row, iteration_count) pairs where count > threshold."""
    breaches: list[tuple[dict[str, str], int]] = []
    for row in rows:
        if row.get("status", "").lower() not in ACTIVE_STATUSES:
            continue
        pe_id = row.get("pe-id", "")
        if not pe_id:
            continue
        count = count_validator_iterations(pe_id, repo_root)
        if count > threshold:
            breaches.append((row, count))
    return breaches


# ---------------------------------------------------------------------------
# Escalation message builder (AGENTS.md §4.2)
# ---------------------------------------------------------------------------

_STALL_OPTIONS: list[tuple[str, str]] = [
    ("Unblock manually", "PM or PO takes direct action to resolve the blocker"),
    (
        "Reassign to other engine",
        "swap Implementer — adds one iteration but fresh eyes",
    ),
    ("Defer PE", "move PE to blocked status and reprioritize queue"),
]

_ITERATION_OPTIONS: list[tuple[str, str]] = [
    (
        "Scope-reduce the PE",
        "split off contested scope into a follow-up PE — fastest unblock",
    ),
    (
        "Escalate to PO for scope ruling",
        "PO decides contested scope — authoritative but slower",
    ),
    (
        "Reassign Validator",
        "bring in fresh perspective — resets iteration count but costs a round",
    ),
]


def build_escalation_message(
    pe_id: str,
    blocker: str,
    status: str,
    iteration_count: int,
    options: list[tuple[str, str]],
    recommendation: str,
) -> str:
    """Format escalation per AGENTS.md §4.2."""
    option_lines = "\n".join(
        f"{chr(65 + i)}. {opt} — {trade_off}"
        for i, (opt, trade_off) in enumerate(options)
    )
    return (
        f"\U0001f534 Escalation — {pe_id}\n\n"
        f"Blocker: {blocker}\n"
        f"Current status: {status}\n"
        f"Iteration count: {iteration_count}\n\n"
        f"Options:\n{option_lines}\n\n"
        f"PM recommendation: {recommendation}"
    )


def build_stall_escalation(row: dict[str, str], age_hours: float) -> str:
    pe_id = row.get("pe-id", "UNKNOWN")
    status = row.get("status", "unknown")
    return build_escalation_message(
        pe_id=pe_id,
        blocker=f"PE has been in '{status}' for {age_hours:.0f} hours (threshold: 48 h)",
        status=status,
        iteration_count=0,
        options=_STALL_OPTIONS,
        recommendation="A — unblock manually for fastest resolution",
    )


def build_iteration_escalation(row: dict[str, str], count: int) -> str:
    pe_id = row.get("pe-id", "UNKNOWN")
    status = row.get("status", "unknown")
    return build_escalation_message(
        pe_id=pe_id,
        blocker=f"Validator iteration count ({count}) exceeds threshold (2)",
        status=status,
        iteration_count=count,
        options=_ITERATION_OPTIONS,
        recommendation="A — scope-reduce to unblock fastest without losing work",
    )


# ---------------------------------------------------------------------------
# Main detection sweep
# ---------------------------------------------------------------------------


def run_detection(
    registry_path: pathlib.Path,
    repo_root: pathlib.Path,
    threshold_hours: int = _DEFAULT_THRESHOLD_HOURS,
    iteration_threshold: int = _DEFAULT_ITERATION_THRESHOLD,
    now: datetime.datetime | None = None,
) -> list[str]:
    """Return list of escalation message strings (empty if no issues found)."""
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)

    content = registry_path.read_text(encoding="utf-8")
    _, rows = parse_active_registry(content)
    if rows is None:
        raise ValueError(f"Could not parse Active PE Registry from {registry_path}")

    messages: list[str] = []

    for row in detect_stalls(rows, now, threshold_hours):
        last_updated = row.get("last-updated", "")
        age = _age_hours(last_updated, now)
        messages.append(build_stall_escalation(row, age or threshold_hours + 1))

    for row, count in detect_iteration_breaches(rows, repo_root, iteration_threshold):
        messages.append(build_iteration_escalation(row, count))

    return messages


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="PM Agent stall and iteration-threshold detector"
    )
    parser.add_argument(
        "--registry",
        default=str(_DEFAULT_REGISTRY),
        help="Path to CURRENT_PE.md (default: CURRENT_PE.md)",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repo root for locating REVIEW files (default: .)",
    )
    parser.add_argument(
        "--threshold-hours",
        type=int,
        default=_DEFAULT_THRESHOLD_HOURS,
        help="Stall threshold in hours (default: 48)",
    )
    parser.add_argument(
        "--iteration-threshold",
        type=int,
        default=_DEFAULT_ITERATION_THRESHOLD,
        help="Max validator iterations before escalation (default: 2)",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON output file path (list of escalation strings)",
    )
    args = parser.parse_args()

    try:
        messages = run_detection(
            registry_path=pathlib.Path(args.registry),
            repo_root=pathlib.Path(args.repo_root),
            threshold_hours=args.threshold_hours,
            iteration_threshold=args.iteration_threshold,
        )
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    for msg in messages:
        print(msg)
        print()

    if args.output:
        pathlib.Path(args.output).write_text(
            json.dumps(messages, indent=2) + "\n", encoding="utf-8"
        )

    if not messages:
        print("No stalls or iteration breaches detected.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
