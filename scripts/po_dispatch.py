#!/usr/bin/env python3
"""po_dispatch.py — dry-run helper for the safe PO→PM PE start sequence.

Phase 1 only:
- dry-run / check / generate
- no Discord API calls
- no live message sending
- no OpenClaw calls
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

PE_ID = "PE-OPS-DISPATCH-WRAPPER-HARDENING-01"
OBJECTIVE = (
    "Provide a dry-run helper that verifies the PO→PM start sequence for safe new PE/task flows."
)
APPROVED_BRANCH = "feature/pe-ops-dispatch-wrapper-hardening-01"
APPROVED_BASELINE_PATTERN = re.compile(r"^origin/main @ [0-9a-f]{40}$")
APPROVED_IMPLEMENTER = "infra-impl-b"
APPROVED_VALIDATOR = "infra-val-a"
PHASE_1_GATES: tuple[str, ...] = ("dry-run", "check", "generate")
HARD_STOPS: tuple[str, ...] = (
    "do not call Discord APIs",
    "do not send live messages",
    "do not create threads",
    "do not call OpenClaw",
    "do not mutate repo state",
    "do not alter CURRENT_PE.md",
    "do not dispatch PM or agents",
    "do not replace live dispatch behaviour",
)
PM_RESET_BINDING_ACK_FORMAT = "RESET_BINDING_ACK_FORMAT"
SEQUENCE_STEPS: tuple[tuple[str, str, str, str], ...] = (
    (
        "1",
        "PO",
        "Ask PM to create a dedicated PE thread",
        "The PE must start in its own thread; do not reuse an existing thread.",
    ),
    (
        "2",
        "PM",
        "Send /reset in that PE thread",
        "Reset must happen before any PE instruction is opened.",
    ),
    (
        "3",
        "PM",
        f"Require complete {PM_RESET_BINDING_ACK_FORMAT}",
        "Generic reset acknowledgement is insufficient.",
    ),
    (
        "4",
        "PM",
        "Only after a valid acknowledgement, send/open the PE instruction",
        "The opening instruction follows the valid reset binding acknowledgement only.",
    ),
    (
        "5",
        "PM",
        "Block if PM gives a generic reset acknowledgement only",
        "No generic ack means no dispatch.",
    ),
    (
        "6",
        "PM",
        "Remind that opening starts from current origin/main and CURRENT_PE.md must be plan-complete unless explicitly resuming a PE",
        "Use the live origin/main baseline and the plan-complete / explicit-resume rule.",
    ),
)
REQUEST_TEMPLATE_PATTERNS = {
    "dedicated_thread": "Please create a dedicated PE thread for {pe_id} before any further instructions.",
    "reset": "Send /reset in that PE thread before opening the PE instruction.",
    "ack_required": "Require the full {ack_format}; a generic reset acknowledgement is insufficient.",
    "open_instruction": "Only after a valid {ack_format} do you send/open the PE instruction.",
    "baseline_reminder": "Opening must begin from current origin/main ({baseline}) and CURRENT_PE.md must be plan-complete unless this is an explicit PE resumption.",
}
PHASE_1_ONLY_STATEMENT = (
    "Phase 1 only generates and checks the PO→PM sequence and acknowledgement structure; it does not call live automation."
)
EXPECTED_SEQUENCE = tuple(step[2] for step in SEQUENCE_STEPS)
EXPECTED_ACTORS = tuple(step[1] for step in SEQUENCE_STEPS)
EXPECTED_ORDERS = tuple(step[0] for step in SEQUENCE_STEPS)


def _expected_request_templates(pe_id: str, baseline: str) -> dict[str, str]:
    return {
        "dedicated_thread": REQUEST_TEMPLATE_PATTERNS["dedicated_thread"].format(pe_id=pe_id),
        "reset": REQUEST_TEMPLATE_PATTERNS["reset"],
        "ack_required": (
            f"Require the full {PM_RESET_BINDING_ACK_FORMAT}; a generic reset acknowledgement is insufficient."
        ),
        "open_instruction": (
            f"Only after a valid {PM_RESET_BINDING_ACK_FORMAT} do you send/open the PE instruction."
        ),
        "baseline_reminder": (
            f"Opening must begin from current origin/main ({baseline}) and CURRENT_PE.md must be plan-complete unless this is an explicit PE resumption."
        ),
    }


@dataclass(frozen=True)
class SequenceStep:
    order: str
    actor: str
    action: str
    guardrail: str


@dataclass(frozen=True)
class POStartPacket:
    pe_id: str
    objective: str
    branch: str
    baseline: str
    lane: str
    implementer: str
    validator: str
    phase: str = "Phase 1"
    mode: str = "dry-run"
    sequence_steps: tuple[SequenceStep, ...] = tuple(
        SequenceStep(*step) for step in SEQUENCE_STEPS
    )
    hard_stops: tuple[str, ...] = HARD_STOPS
    phase_1_gates: tuple[str, ...] = PHASE_1_GATES
    request_templates: dict[str, str] = None  # type: ignore[assignment]
    live_dispatch_statement: str = PHASE_1_ONLY_STATEMENT

    def __post_init__(self):
        if self.request_templates is None:
            object.__setattr__(
                self,
                "request_templates",
                _expected_request_templates(self.pe_id, self.baseline),
            )


def build_packet(
    *,
    pe_id: str,
    branch: str,
    baseline: str,
    lane: str,
    implementer: str,
    validator: str,
    mode: str = "dry-run",
) -> POStartPacket:
    return POStartPacket(
        pe_id=pe_id,
        objective=OBJECTIVE,
        branch=branch,
        baseline=baseline,
        lane=lane,
        implementer=implementer,
        validator=validator,
        mode=mode,
    )


def validate_packet(packet: POStartPacket) -> list[str]:
    failures: list[str] = []
    if packet.pe_id != PE_ID:
        failures.append(f"PE ID must be {PE_ID!r}, got {packet.pe_id!r}")
    if packet.objective != OBJECTIVE:
        failures.append("Objective text is missing or altered")
    if packet.branch != APPROVED_BRANCH:
        failures.append(f"Branch must be {APPROVED_BRANCH!r}, got {packet.branch!r}")
    if not APPROVED_BASELINE_PATTERN.fullmatch(packet.baseline):
        failures.append(
            "Baseline must be expressed as 'origin/main @ <full-commit-sha>'"
        )
    if packet.lane != "Strict":
        failures.append(f"Lane must be 'Strict', got {packet.lane!r}")
    if packet.implementer != APPROVED_IMPLEMENTER:
        failures.append(
            f"Implementer must be {APPROVED_IMPLEMENTER!r}, got {packet.implementer!r}"
        )
    if packet.validator != APPROVED_VALIDATOR:
        failures.append(
            f"Validator must be {APPROVED_VALIDATOR!r}, got {packet.validator!r}"
        )
    if packet.phase != "Phase 1":
        failures.append(f"Phase must be 'Phase 1', got {packet.phase!r}")
    if packet.mode not in PHASE_1_GATES:
        failures.append(f"Unsupported mode {packet.mode!r}")
    if tuple(step.order for step in packet.sequence_steps) != EXPECTED_ORDERS:
        failures.append("Sequence order is not the approved safe PO→PM sequence")
    if tuple(step.actor for step in packet.sequence_steps) != EXPECTED_ACTORS:
        failures.append("Sequence actors are not the approved safe PO→PM sequence")
    if tuple(step.action for step in packet.sequence_steps) != EXPECTED_SEQUENCE:
        failures.append("Sequence actions are not the approved safe PO→PM sequence")
    if packet.hard_stops != HARD_STOPS:
        failures.append("Hard stops do not match the approved Phase 1 boundary")
    if packet.phase_1_gates != PHASE_1_GATES:
        failures.append("Phase 1 gates do not match the approved helper contract")
    if packet.live_dispatch_statement != PHASE_1_ONLY_STATEMENT:
        failures.append("Live dispatch statement is missing or altered")
    if packet.request_templates != _expected_request_templates(packet.pe_id, packet.baseline):
        failures.append("Request templates do not match the approved helper contract")
    return failures


def _packet_payload(packet: POStartPacket) -> dict[str, object]:
    payload = asdict(packet)
    payload["sequence_steps"] = [asdict(step) for step in packet.sequence_steps]
    payload["hard_stops"] = list(packet.hard_stops)
    payload["phase_1_gates"] = list(packet.phase_1_gates)
    payload["request_templates"] = dict(packet.request_templates)
    return payload


def render_summary(packet: POStartPacket) -> str:
    lines = [
        "PO DISPATCH HELPER",
        f"PE: {packet.pe_id}",
        f"Mode: {packet.mode}",
        f"Objective: {packet.objective}",
        f"Branch: {packet.branch}",
        f"Baseline: {packet.baseline}",
        f"Lane: {packet.lane}",
        f"Implementer: {packet.implementer}",
        f"Validator: {packet.validator}",
        "Approved sequence:",
    ]
    for step in packet.sequence_steps:
        lines.extend(
            [
                f"- {step.order}. {step.actor}: {step.action}",
                f"  Guardrail: {step.guardrail}",
            ]
        )
    lines.extend(
        [
            "Request templates:",
            *[f"- {key}: {value}" for key, value in packet.request_templates.items()],
            f"Phase 1 statement: {packet.live_dispatch_statement}",
            "Hard stops:",
            *[f"- {stop}" for stop in packet.hard_stops],
        ]
    )
    return "\n".join(lines)


def render_contract_json(packet: POStartPacket) -> str:
    return json.dumps(_packet_payload(packet), indent=2, sort_keys=True)


def _emit_summary(packet: POStartPacket) -> None:
    print(render_summary(packet))
    print()
    print(packet.live_dispatch_statement)


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dry-run PO→PM safe start-sequence helper.")
    parser.add_argument("--pe-id", required=True, help="Approved PE identifier.")
    parser.add_argument("--branch", required=True, help="Approved feature branch.")
    parser.add_argument(
        "--baseline", required=True, help="Approved baseline ref and commit."
    )
    parser.add_argument(
        "--lane", required=True, choices=["Strict"], help="Approved execution lane."
    )
    parser.add_argument(
        "--implementer", required=True, help="Approved implementer agent ID."
    )
    parser.add_argument(
        "--validator", required=True, help="Approved validator agent ID."
    )
    parser.add_argument(
        "--mode",
        choices=PHASE_1_GATES,
        default="dry-run",
        help="Phase 1 mode: dry-run, check, or generate.",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON file path for generate mode; if omitted, JSON is printed to stdout.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    packet = build_packet(
        pe_id=args.pe_id,
        branch=args.branch,
        baseline=args.baseline,
        lane=args.lane,
        implementer=args.implementer,
        validator=args.validator,
        mode=args.mode,
    )

    failures = validate_packet(packet)
    if args.mode == "generate":
        json_text = render_contract_json(packet)
        if args.output:
            Path(args.output).write_text(json_text + "\n", encoding="utf-8")
        print(json_text)
        return 0 if not failures else 1

    _emit_summary(packet)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: Phase 1 helper is well-formed and contains no live automation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
