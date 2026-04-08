"""PE-AUTO-07 PM Arbiter — arbitration engine for blocked PEs."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class TriggerType(str, Enum):
    FAIL_ROUND_3 = "fail_round_3"
    SCOPE_DISPUTE = "scope_dispute"
    TECHNICAL_BLOCKER = "technical_blocker"
    TIMEOUT = "timeout"


class ArbDecision(str, Enum):
    SIDE_IMPLEMENTER = "SIDE_IMPLEMENTER"
    SIDE_VALIDATOR = "SIDE_VALIDATOR"
    SPLIT_PE = "SPLIT_PE"
    ESCALATE_PO = "ESCALATE_PO"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ArbContext:
    trigger_type: TriggerType
    fail_round: int
    pe_id: str
    review_content: str
    handoff_content: str
    scope_diff: str
    arbiter_iteration: int


@dataclass(frozen=True)
class ArbResult:
    decision: ArbDecision
    justification: str
    pr_comment_body: str
    lessons_entry: str
    ll_id: str


# ---------------------------------------------------------------------------
# Decision logic
# ---------------------------------------------------------------------------


def _scope_within_handoff(scope_diff: str, handoff_content: str) -> bool:
    """Return True if every file in scope_diff is declared in HANDOFF Files Changed."""
    diff_files = set()
    for line in scope_diff.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            diff_files.add(parts[-1].strip())

    # Extract declared files from HANDOFF "Files Changed" section.
    declared: set[str] = set()
    in_section = False
    for line in handoff_content.splitlines():
        if line.strip() == "## Files Changed":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            stripped = line.strip()
            # Lines like: `M  scripts/foo.py` or `A  scripts/bar.py`
            if stripped and stripped[0] in {"A", "M", "D", "R"}:
                parts = stripped.split()
                if len(parts) >= 2:
                    declared.add(parts[-1].strip())
            # Also match bare filenames inside fenced code blocks
            elif stripped and not stripped.startswith("```"):
                m = re.match(r"^[AMD]\s+(.+)$", stripped)
                if m:
                    declared.add(m.group(1).strip())

    if not diff_files:
        return True
    return diff_files.issubset(declared)


def decide(context: ArbContext) -> tuple[ArbDecision, str]:
    """Return (decision, justification) from the arbitration context."""

    # Hard escalation: too many arbiter iterations.
    if context.arbiter_iteration > 3:
        return (
            ArbDecision.ESCALATE_PO,
            f">3 arbitration iterations on PE {context.pe_id}. "
            "Beyond arbitration capacity; requires PO decision.",
        )

    if context.trigger_type == TriggerType.TECHNICAL_BLOCKER:
        return (
            ArbDecision.ESCALATE_PO,
            f"Technical blocker with `pm-escalation` flag on PE {context.pe_id}. "
            "Architectural or credential decision required from PO.",
        )

    if context.trigger_type == TriggerType.TIMEOUT:
        return (
            ArbDecision.ESCALATE_PO,
            f"Timeout: PE {context.pe_id} has been blocked for >24h without resolution "
            "(runner inactive for >4h). AC-5 threshold exceeded — PO must investigate.",
        )

    if context.trigger_type == TriggerType.SCOPE_DISPUTE:
        review_lower = context.review_content.lower()
        dispute_claimed = (
            "out-of-scope" in review_lower or "out of scope" in review_lower
        )
        if dispute_claimed and _scope_within_handoff(
            context.scope_diff, context.handoff_content
        ):
            return (
                ArbDecision.SIDE_IMPLEMENTER,
                f"Scope dispute on PE {context.pe_id}: diff is within declared HANDOFF scope. "
                "Validator assessment was over-scoped; PM sides with Implementer.",
            )
        return (
            ArbDecision.SIDE_VALIDATOR,
            f"Scope dispute on PE {context.pe_id}: Implementer changes extend beyond "
            "declared HANDOFF scope, or scope-dispute claim is unsubstantiated.",
        )

    # Default path: FAIL_ROUND_3 → side with Validator (Implementer must fix).
    return (
        ArbDecision.SIDE_VALIDATOR,
        f"Fail round {context.fail_round} on PE {context.pe_id}: Implementer must address "
        "Validator blocking findings. Review REVIEW file and fix all FAIL items.",
    )


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

_DECISION_LABEL: dict[ArbDecision, str] = {
    ArbDecision.SIDE_IMPLEMENTER: "SIDE_IMPLEMENTER — PM sides with Implementer",
    ArbDecision.SIDE_VALIDATOR: "SIDE_VALIDATOR — PM sides with Validator",
    ArbDecision.SPLIT_PE: "SPLIT_PE — Legitimate conflict; new PE will be created",
    ArbDecision.ESCALATE_PO: "ESCALATE_PO — Requires human PO decision",
}

_DECISION_INSTRUCTION: dict[ArbDecision, str] = {
    ArbDecision.SIDE_IMPLEMENTER: (
        "Validator: accept the Implementer's scope as declared in HANDOFF.md. "
        "Re-issue PASS verdict without the out-of-scope objection."
    ),
    ArbDecision.SIDE_VALIDATOR: (
        "Implementer: fix all blocking findings in the REVIEW file. "
        "Deliver an updated Status Packet. Do not address non-blocking findings."
    ),
    ArbDecision.SPLIT_PE: (
        "PM will create an additional PE in the plan to cover the disputed scope. "
        "Implementer: revert disputed changes and deliver HANDOFF for the original scope."
    ),
    ArbDecision.ESCALATE_PO: (
        "Human PO intervention required. "
        "PM Agent will notify the PO on Discord with a structured summary."
    ),
}


def format_pr_comment(
    context: ArbContext, decision: ArbDecision, justification: str
) -> str:
    lines = [
        "## PM Arbitration",
        "",
        f"**PE:** {context.pe_id}  ",
        f"**Trigger:** `{context.trigger_type.value}`  ",
        f"**Decision:** `{decision.value}`  ",
        "",
        f"**{_DECISION_LABEL[decision]}**",
        "",
        "### Justification",
        "",
        justification,
        "",
        "### Required action",
        "",
        _DECISION_INSTRUCTION[decision],
        "",
        "_PM Agent — automated arbitration_",
    ]
    return "\n".join(lines)


def _next_ll_id(lessons_content: str) -> str:
    matches = re.findall(r"^## LL-(\d+)", lessons_content, re.MULTILINE)
    number = max((int(m) for m in matches), default=0) + 1
    return f"LL-{number:02d}"


def format_lessons_entry(
    ll_id: str,
    context: ArbContext,
    decision: ArbDecision,
    justification: str,
    date: str,
) -> str:
    lines = [
        f"## {ll_id} — PM Arbitration: {context.trigger_type.value} on {context.pe_id}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| PE | {context.pe_id} |",
        f"| Trigger | {context.trigger_type.value} |",
        f"| Fail round | {context.fail_round} |",
        f"| Decision | {decision.value} |",
        f"| Date | {date} |",
        "",
        f"**Context:** {justification}",
        "",
        f"**Required action:** {_DECISION_INSTRUCTION[decision]}",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def append_lessons_learned(path: Path, entry: str) -> None:
    """Append *entry* to the LESSONS_LEARNED.md file at *path*."""
    current = path.read_text(encoding="utf-8")
    # Ensure file ends with a newline before appending.
    if not current.endswith("\n"):
        current += "\n"
    path.write_text(current + "\n" + entry, encoding="utf-8")


# ---------------------------------------------------------------------------
# Context loading
# ---------------------------------------------------------------------------


def load_context(
    *,
    trigger_type: TriggerType,
    fail_round: int,
    pe_id: str,
    review_file: str | None,
    handoff_file: str | None,
    scope_diff: str | None,
    arbiter_iteration: int,
) -> ArbContext:
    review_content = ""
    if review_file:
        p = Path(review_file)
        if p.exists():
            review_content = p.read_text(encoding="utf-8")

    handoff_content = ""
    if handoff_file:
        p = Path(handoff_file)
        if p.exists():
            handoff_content = p.read_text(encoding="utf-8")

    return ArbContext(
        trigger_type=trigger_type,
        fail_round=fail_round,
        pe_id=pe_id,
        review_content=review_content,
        handoff_content=handoff_content,
        scope_diff=scope_diff or "",
        arbiter_iteration=arbiter_iteration,
    )


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def _write_outputs(outputs: dict[str, str]) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT", "").strip()
    if github_output:
        with Path(github_output).open("a", encoding="utf-8") as handle:
            for key, value in outputs.items():
                handle.write(f"{key}={value}\n")
        return
    output_path = Path.cwd() / ".arbiter-outputs"
    output_path.write_text(
        "\n".join(f"{key}={value}" for key, value in outputs.items()) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="PM Arbiter — resolve PE escalations.")
    parser.add_argument(
        "--trigger",
        required=True,
        choices=[t.value for t in TriggerType],
        help="Trigger type for this arbitration.",
    )
    parser.add_argument(
        "--fail-round",
        type=int,
        default=0,
        help="Current fail round number (0 if not a fail trigger).",
    )
    parser.add_argument(
        "--pe-id",
        default="",
        help="Active PE identifier (e.g. PE-AUTO-07).",
    )
    parser.add_argument(
        "--review-file",
        default=None,
        help="Path to the Validator REVIEW_PE<N>.md file.",
    )
    parser.add_argument(
        "--handoff-file",
        default="HANDOFF.md",
        help="Path to HANDOFF.md (default: HANDOFF.md).",
    )
    parser.add_argument(
        "--scope-diff",
        default=None,
        help="git diff --name-status output (reads stdin if not supplied).",
    )
    parser.add_argument(
        "--arbiter-iteration",
        type=int,
        default=1,
        help="How many times the arbiter has run on this PE (default: 1).",
    )
    parser.add_argument(
        "--lessons-file",
        default="LESSONS_LEARNED.md",
        help="Path to LESSONS_LEARNED.md (default: LESSONS_LEARNED.md).",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Append entry to LESSONS_LEARNED.md in place.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the result as JSON.",
    )
    args = parser.parse_args()

    scope_diff = args.scope_diff
    if scope_diff is None and not sys.stdin.isatty():
        scope_diff = sys.stdin.read()

    context = load_context(
        trigger_type=TriggerType(args.trigger),
        fail_round=args.fail_round,
        pe_id=args.pe_id,
        review_file=args.review_file,
        handoff_file=args.handoff_file,
        scope_diff=scope_diff,
        arbiter_iteration=args.arbiter_iteration,
    )

    decision, justification = decide(context)

    lessons_path = Path(args.lessons_file)
    lessons_content = (
        lessons_path.read_text(encoding="utf-8") if lessons_path.exists() else ""
    )
    ll_id = _next_ll_id(lessons_content)
    today = dt.date.today().isoformat()

    pr_comment = format_pr_comment(context, decision, justification)
    lessons_entry = format_lessons_entry(ll_id, context, decision, justification, today)

    if args.write and lessons_path.exists():
        append_lessons_learned(lessons_path, lessons_entry)

    outputs = {
        "decision": decision.value,
        "justification": justification,
        "ll_id": ll_id,
        "pr_comment": pr_comment.replace("\n", "%0A"),
    }
    _write_outputs(outputs)

    if args.json:
        print(
            json.dumps(
                {
                    "decision": decision.value,
                    "justification": justification,
                    "ll_id": ll_id,
                    "pr_comment": pr_comment,
                    "lessons_entry": lessons_entry,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(f"{decision.value}: {justification}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
