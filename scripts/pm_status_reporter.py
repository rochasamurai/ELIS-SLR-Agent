#!/usr/bin/env python
"""PE-OC-08 PM Agent — PO status reporting and immediate escalation handler.

Responds to PO "status" queries and "escalate PE-X" directives.

Usage:
    python scripts/pm_status_reporter.py --command status
    python scripts/pm_status_reporter.py --command escalate --pe-id PE-OC-08
    python scripts/pm_status_reporter.py --command status --registry CURRENT_PE.md
"""

from __future__ import annotations

import argparse
import datetime
import os
import pathlib
import re
import shutil
import sys

from elis.agent_id import engine_from_agent_id

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
_DEFAULT_LESSONS = pathlib.Path("LESSONS_LEARNED.md")


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
# Agent ID → display name
# ---------------------------------------------------------------------------

_ENGINE_MAP = {
    "codex": "CODEX",
    "claude": "Claude Code",
}


def _engine_display(agent_id: str) -> str:
    """Convert internal agent ID to PO-facing engine name.

    Examples:
        prog-impl-codex  → CODEX
        infra-val-claude → Claude Code
    """
    try:
        return _ENGINE_MAP[engine_from_agent_id(agent_id)]
    except (KeyError, ValueError):
        return agent_id


def _role_display(agent_id: str) -> str:
    """Return 'Implementer' or 'Validator' from agent ID."""
    lower = agent_id.lower()
    if "impl" in lower:
        return "Implementer"
    if "val" in lower:
        return "Validator"
    return "Agent"


# ---------------------------------------------------------------------------
# Status formatting (AGENTS.md §4.1)
# ---------------------------------------------------------------------------

_WEEK_DAYS = 7


def _merged_this_week(rows: list[dict[str, str]], now: datetime.date) -> int:
    week_start = now - datetime.timedelta(days=_WEEK_DAYS)
    count = 0
    for row in rows:
        if row.get("status", "").lower() != "merged":
            continue
        try:
            updated = datetime.date.fromisoformat(row.get("last-updated", ""))
        except ValueError:
            continue
        if updated >= week_start:
            count += 1
    return count


def _intervention_pe_ids(lessons_content: str) -> set[str]:
    pe_ids: set[str] = set()
    for block in re.split(r"(?=^## LL-\d+\b)", lessons_content, flags=re.MULTILINE):
        if "PM Arbitration" not in block and "ESCALATE_PO" not in block:
            continue
        pe_ids.update(re.findall(r"\bPE-[A-Z]+-[0-9]+\b", block))
    return pe_ids


def autonomy_rate_summary(
    rows: list[dict[str, str]],
    lessons_content: str,
) -> str:
    merged_ids = {
        row["pe-id"]
        for row in rows
        if row.get("status", "").lower() == "merged" and row.get("pe-id")
    }
    if not merged_ids:
        return "Autonomy rate: 0/0 PEs merged without escalation (0%)"

    intervention_ids = _intervention_pe_ids(lessons_content) & merged_ids
    autonomous = len(merged_ids) - len(intervention_ids)
    rate = round((autonomous / len(merged_ids)) * 100)
    return (
        f"Autonomy rate: {autonomous}/{len(merged_ids)} PEs merged without "
        f"escalation ({rate}%)"
    )


def auth_status_summary(
    env: dict[str, str] | None = None,
    *,
    which=shutil.which,
) -> str:
    if env is None:
        env = os.environ

    codex_ok = bool(env.get("OPENAI_API_KEY")) and which("codex") is not None
    claude_ok = bool(env.get("CLAUDE_SETUP_TOKEN")) and which("claude") is not None

    codex_text = "codex OK" if codex_ok else "codex unavailable"
    claude_text = "claude OK" if claude_ok else "claude unavailable"
    return f"Auth status: {codex_text} · {claude_text}"


def format_status_response(
    rows: list[dict[str, str]],
    now: datetime.date,
    *,
    lessons_content: str = "",
    auth_summary: str | None = None,
) -> str:
    """Format Active PE Registry for PO consumption (AGENTS.md §4.1).

    When more than one domain is present, active PEs are grouped under labelled
    ``### <domain> domain`` sections.  Single-domain registries retain the
    existing flat-list format.
    """
    active = [r for r in rows if r.get("status", "").lower() in ACTIVE_STATUSES]
    merged_week = _merged_this_week(rows, now)

    lines = [f"Active PEs — {now.isoformat()} UTC:", ""]
    if not active:
        lines.append("(no active PEs)")
    else:
        # Preserve insertion order while deduplicating domains.
        domains = list(dict.fromkeys(r.get("domain", "") for r in active))
        multi_domain = len(domains) > 1

        for domain in domains:
            if multi_domain:
                lines.append(f"### {domain} domain")
            for row in active:
                if row.get("domain", "") != domain:
                    continue
                pe_id = row.get("pe-id", "UNKNOWN")
                status = row.get("status", "")
                impl_id = row.get("implementer-agentid", "")
                updated = row.get("last-updated", "")
                engine = _engine_display(impl_id)
                lines.append(
                    f"{pe_id} | {domain} | {status}"
                    f" | Implementer: {engine} | last updated {updated}"
                )
            if multi_domain:
                lines.append("")

    lines.append("")
    lines.append(f"{len(active)} PEs active. {merged_week} merged this week.")
    lines.append(autonomy_rate_summary(rows, lessons_content))
    lines.append(auth_summary or auth_status_summary())
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Immediate escalation (AGENTS.md §4.2 + §5 — "escalate PE-X" directive)
# ---------------------------------------------------------------------------

_IMMEDIATE_OPTIONS: list[tuple[str, str]] = [
    ("Unblock manually", "PM or PO takes direct action to resolve the blocker"),
    (
        "Reassign to other engine",
        "swap Implementer — adds one iteration but fresh eyes",
    ),
    ("Defer PE", "move PE to blocked status and reprioritize queue"),
]
_IMMEDIATE_RECOMMENDATION = "A — fastest path if blocker is well-understood"


def build_escalation_message(
    pe_id: str,
    blocker: str,
    status: str,
    iteration_count: int,
    options: list[tuple[str, str]] | None = None,
    recommendation: str | None = None,
) -> str:
    """Format escalation message per AGENTS.md §4.2."""
    if options is None:
        options = _IMMEDIATE_OPTIONS
    if recommendation is None:
        recommendation = _IMMEDIATE_RECOMMENDATION

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


def handle_escalate(pe_id: str, rows: list[dict[str, str]]) -> str:
    """Immediate escalation handler for PO `escalate PE-X` directive."""
    pe_id = pe_id.upper()
    row = next(
        (r for r in rows if r.get("pe-id", "").upper() == pe_id),
        None,
    )
    if row is None:
        return (
            f"\U0001f534 Escalation — {pe_id}\n\n"
            f"Blocker: PE not found in Active PE Registry.\n"
            f"Current status: unknown\n"
            f"Iteration count: 0\n\n"
            f"Options:\n"
            f"A. Verify PE-ID and re-submit — registry may not yet contain this PE\n"
            f"B. Check CURRENT_PE.md directly — may need manual inspection\n\n"
            f"PM recommendation: A — verify the PE-ID first"
        )
    status = row.get("status", "unknown")
    return build_escalation_message(
        pe_id=pe_id,
        blocker=f"PO-initiated escalation for {pe_id} (status: {status})",
        status=status,
        iteration_count=0,
        options=_IMMEDIATE_OPTIONS,
        recommendation=_IMMEDIATE_RECOMMENDATION,
    )


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------


def load_registry(registry_path: pathlib.Path) -> list[dict[str, str]]:
    content = registry_path.read_text(encoding="utf-8")
    _, rows = parse_active_registry(content)
    if rows is None:
        raise ValueError(f"Could not parse Active PE Registry from {registry_path}")
    return rows


def load_lessons(lessons_path: pathlib.Path) -> str:
    if not lessons_path.exists():
        return ""
    return lessons_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="PM Agent PO status reporter and escalation handler"
    )
    parser.add_argument(
        "--command",
        required=True,
        choices=["status", "escalate", "auth-check"],
        help="Command to execute",
    )
    parser.add_argument(
        "--pe-id",
        help="PE ID for escalate command (e.g. PE-OC-08)",
    )
    parser.add_argument(
        "--registry",
        default=str(_DEFAULT_REGISTRY),
        help="Path to CURRENT_PE.md (default: CURRENT_PE.md)",
    )
    parser.add_argument(
        "--lessons",
        default=str(_DEFAULT_LESSONS),
        help="Path to LESSONS_LEARNED.md (default: LESSONS_LEARNED.md)",
    )
    args = parser.parse_args()

    try:
        rows = load_registry(pathlib.Path(args.registry))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    lessons_content = load_lessons(pathlib.Path(args.lessons))

    if args.command == "status":
        now = datetime.date.today()
        print(
            format_status_response(
                rows,
                now,
                lessons_content=lessons_content,
                auth_summary=auth_status_summary(which=shutil.which),
            )
        )
        return 0

    if args.command == "auth-check":
        print(auth_status_summary(which=shutil.which))
        return 0

    if args.command == "escalate":
        if not args.pe_id:
            print("ERROR: --pe-id is required for escalate command")
            return 1
        print(handle_escalate(args.pe_id, rows))
        return 0

    print(f"ERROR: unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
