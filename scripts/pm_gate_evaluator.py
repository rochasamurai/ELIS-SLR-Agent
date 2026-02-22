#!/usr/bin/env python
"""PE-OC-07 gate automation decision engine.

This script evaluates Gate 1 and Gate 2 conditions and returns a normalized
decision payload for PM Agent automation.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

GATE_1 = "gate-1"
GATE_2 = "gate-2"
PM_REVIEW_REQUIRED = "pm-review-required"


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return False


def _normalize_verdict(verdict: Any) -> str:
    if verdict is None:
        return ""
    return str(verdict).strip().upper()


def _normalize_labels(labels: Any) -> list[str]:
    if not isinstance(labels, list):
        return []
    return [str(x).strip().lower() for x in labels]


def build_validator_assignment_comment(validator_handle: str) -> str:
    return (
        "## Gate 1 — automated by PM Agent\n\n"
        "All Gate 1 conditions are satisfied:\n"
        "- CI pipeline is green\n"
        "- `HANDOFF.md` is present\n"
        "- Status Packet is complete\n\n"
        f"{validator_handle} — assigned as Validator. Begin review."
    )


def build_po_message(
    pe_id: str,
    gate: str,
    decision: str,
    status: str,
    details: list[str] | None = None,
) -> str:
    detail_text = ""
    if details:
        detail_text = f"\nDetails: {', '.join(details)}"
    return (
        f"PE {pe_id}: {gate} {decision.upper()}.\n"
        f"Registry status: {status}.{detail_text}"
    )


def evaluate_gate_1(payload: dict[str, Any], validator_handle: str) -> dict[str, Any]:
    ci_green = _as_bool(payload.get("ci_green"))
    handoff_present = _as_bool(payload.get("handoff_present"))
    status_packet_complete = _as_bool(payload.get("status_packet_complete"))
    pe_id = str(payload.get("pe_id", "UNKNOWN"))
    missing: list[str] = []

    if not ci_green:
        missing.append("ci_green")
    if not handoff_present:
        missing.append("handoff_present")
    if not status_packet_complete:
        missing.append("status_packet_complete")

    if missing:
        status = "gate-1-pending"
        return {
            "gate": GATE_1,
            "decision": "fail",
            "ready": False,
            "registry_status": status,
            "missing_conditions": missing,
            "actions": {
                "assign_validator": False,
                "post_comment": (
                    "## Gate 1 — blocked\n\nMissing: " + ", ".join(missing)
                ),
                "notify_po": build_po_message(pe_id, GATE_1, "fail", status, missing),
            },
        }

    status = "validating"
    return {
        "gate": GATE_1,
        "decision": "pass",
        "ready": True,
        "registry_status": status,
        "missing_conditions": [],
        "actions": {
            "assign_validator": True,
            "post_comment": build_validator_assignment_comment(validator_handle),
            "notify_po": build_po_message(pe_id, GATE_1, "pass", status),
        },
    }


def evaluate_gate_2(payload: dict[str, Any]) -> dict[str, Any]:
    verdict = _normalize_verdict(payload.get("review_verdict"))
    ci_green = _as_bool(payload.get("ci_green"))
    labels = _normalize_labels(payload.get("labels"))
    pe_id = str(payload.get("pe_id", "UNKNOWN"))

    if PM_REVIEW_REQUIRED in labels:
        status = "gate-2-pending"
        return {
            "gate": GATE_2,
            "decision": "escalate",
            "ready": False,
            "registry_status": status,
            "actions": {
                "merge_pr": False,
                "escalate_to_po": True,
                "reason": "pm-review-required label present",
                "notify_po": build_po_message(
                    pe_id, GATE_2, "escalate", status, [PM_REVIEW_REQUIRED]
                ),
            },
        }

    if verdict != "PASS":
        status = "implementing" if verdict == "FAIL" else "gate-2-pending"
        return {
            "gate": GATE_2,
            "decision": "fail",
            "ready": False,
            "registry_status": status,
            "actions": {
                "merge_pr": False,
                "escalate_to_po": verdict == "FAIL",
                "reason": f"review verdict is {verdict or 'IN_PROGRESS'}",
                "notify_po": build_po_message(
                    pe_id, GATE_2, "fail", status, [verdict or "IN_PROGRESS"]
                ),
            },
        }

    if not ci_green:
        status = "gate-2-pending"
        return {
            "gate": GATE_2,
            "decision": "wait",
            "ready": False,
            "registry_status": status,
            "actions": {
                "merge_pr": False,
                "escalate_to_po": False,
                "reason": "ci not green",
                "notify_po": build_po_message(pe_id, GATE_2, "wait", status),
            },
        }

    status = "merged"
    return {
        "gate": GATE_2,
        "decision": "pass",
        "ready": True,
        "registry_status": status,
        "actions": {
            "merge_pr": True,
            "escalate_to_po": False,
            "reason": "pass verdict and green ci",
            "notify_po": build_po_message(pe_id, GATE_2, "pass", status),
        },
    }


def evaluate_gate(
    gate: str, payload: dict[str, Any], validator_handle: str = "@claude-code"
) -> dict[str, Any]:
    if gate == GATE_1:
        return evaluate_gate_1(payload, validator_handle)
    if gate == GATE_2:
        return evaluate_gate_2(payload)
    raise ValueError(f"Unsupported gate: {gate}")


def _read_payload(event_file: str | None) -> dict[str, Any]:
    if not event_file:
        return {}
    data = json.loads(pathlib.Path(event_file).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Event payload must be a JSON object.")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate PM Agent gate decisions")
    parser.add_argument(
        "--gate", required=True, choices=[GATE_1, GATE_2], help="Gate to evaluate"
    )
    parser.add_argument("--event-file", help="Path to JSON payload file")
    parser.add_argument(
        "--validator-handle",
        default="@claude-code",
        help="Validator handle for Gate 1 assignment comment",
    )
    parser.add_argument("--output", help="Optional output JSON file path")
    args = parser.parse_args()

    try:
        payload = _read_payload(args.event_file)
        result = evaluate_gate(args.gate, payload, args.validator_handle)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    output = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        pathlib.Path(args.output).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
