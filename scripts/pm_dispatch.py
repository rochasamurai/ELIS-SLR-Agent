#!/usr/bin/env python3
"""pm_dispatch.py — deterministic PM dispatch opening-packet wrapper.

Phase 1 only:
- dry-run / check / generate
- no live dispatch APIs
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

APPROVED_FILE_SCOPE: tuple[str, ...] = (
    "CURRENT_PE.md",
    ".elis/pe/PE-OPS-PM-DISPATCH-01/PE_TASK.md",
    ".elis/pe/PE-OPS-PM-DISPATCH-01/HANDOFF.md",
    "docs/governance/ELIS_PM_Dispatch_Wrapper.md",
    "scripts/pm_dispatch.py",
    "tests/test_pm_dispatch.py",
    "tests/test_pm_dispatch_contract.py",
)
PHASE_1_GATES: tuple[str, ...] = ("dry-run", "check", "generate")
HARD_STOPS: tuple[str, ...] = (
    "do not touch openclaw.json",
    "do not change auth/secret state",
    "do not restart services",
    "do not call live dispatch APIs",
    "do not replace live dispatch behaviour",
    "do not push/open PR/merge",
    "do not alter files outside approved scope",
)
LIVE_DISPATCH_STATEMENT = (
    "Phase 1 only generates and checks dispatch contracts and does not call live dispatch APIs."
)


@dataclass(frozen=True)
class DispatchPacket:
    pe_id: str
    objective: str
    branch: str
    baseline: str
    lane: str
    implementer: str
    validator: str
    phase: str = "Phase 1"
    mode: str = "dry-run"
    file_scope: tuple[str, ...] = APPROVED_FILE_SCOPE
    phase_1_gates: tuple[str, ...] = PHASE_1_GATES
    tests: tuple[str, ...] = ("tests/test_pm_dispatch.py", "tests/test_pm_dispatch_contract.py")
    rollback: str = (
        "Revert only the approved scoped files to the accepted origin/main baseline."
    )
    hard_stops: tuple[str, ...] = HARD_STOPS
    live_dispatch_statement: str = LIVE_DISPATCH_STATEMENT


def build_packet(
    *,
    pe_id: str,
    branch: str,
    baseline: str,
    lane: str,
    implementer: str,
    validator: str,
    mode: str = "dry-run",
) -> DispatchPacket:
    """Build the immutable Phase 1 opening packet."""

    return DispatchPacket(
        pe_id=pe_id,
        objective="Deterministic PM dispatch wrapper for PE-OPS-PM-DISPATCH-01.",
        branch=branch,
        baseline=baseline,
        lane=lane,
        implementer=implementer,
        validator=validator,
        mode=mode,
    )


def _packet_payload(packet: DispatchPacket) -> dict[str, object]:
    payload = asdict(packet)
    payload["file_scope"] = list(packet.file_scope)
    payload["phase_1_gates"] = list(packet.phase_1_gates)
    payload["tests"] = list(packet.tests)
    payload["hard_stops"] = list(packet.hard_stops)
    return payload


def render_summary(packet: DispatchPacket) -> str:
    """Render a concise human-readable packet summary."""

    lines = [
        "PM DISPATCH OPENING PACKET",
        f"PE: {packet.pe_id}",
        f"Mode: {packet.mode}",
        f"Objective: {packet.objective}",
        f"Branch: {packet.branch}",
        f"Baseline: {packet.baseline}",
        f"Lane: {packet.lane}",
        f"Implementer: {packet.implementer}",
        f"Validator: {packet.validator}",
        "File scope:",
    ]
    lines.extend(f"- {item}" for item in packet.file_scope)
    lines.extend(
        [
            "Phase 1 gates:",
            *[f"- {gate}" for gate in packet.phase_1_gates],
            "Tests:",
            *[f"- {test}" for test in packet.tests],
            f"Rollback: {packet.rollback}",
            "Hard stops:",
            *[f"- {stop}" for stop in packet.hard_stops],
            f"Statement: {packet.live_dispatch_statement}",
        ]
    )
    return "\n".join(lines)


def render_contract_json(packet: DispatchPacket) -> str:
    """Render the opening packet as formatted JSON."""

    return json.dumps(_packet_payload(packet), indent=2, sort_keys=True)


def validate_packet(packet: DispatchPacket) -> list[str]:
    """Validate the deterministic Phase 1 packet shape."""

    failures: list[str] = []
    if packet.phase != "Phase 1":
        failures.append(f"Phase must be 'Phase 1', got {packet.phase!r}")
    if packet.mode not in PHASE_1_GATES:
        failures.append(f"Unsupported mode {packet.mode!r}")
    if packet.lane != "Strict":
        failures.append(f"Lane must be 'Strict', got {packet.lane!r}")
    if not packet.pe_id:
        failures.append("PE ID is required")
    if not packet.branch:
        failures.append("Branch is required")
    if not packet.baseline:
        failures.append("Baseline is required")
    if not packet.implementer:
        failures.append("Implementer is required")
    if not packet.validator:
        failures.append("Validator is required")
    if packet.file_scope != APPROVED_FILE_SCOPE:
        failures.append("Approved file scope does not match the controlled PE opening packet")
    if packet.phase_1_gates != PHASE_1_GATES:
        failures.append("Phase 1 gates do not match the controlled wrapper contract")
    if packet.live_dispatch_statement != LIVE_DISPATCH_STATEMENT:
        failures.append("Live dispatch statement is missing or altered")
    return failures


def validate_scoped_files(repo_root: Path) -> list[str]:
    """Confirm the approved PE artefacts exist in the clean PE worktree."""

    missing = [path for path in APPROVED_FILE_SCOPE if not (repo_root / path).exists()]
    return missing


def _read_current_pe(repo_root: Path) -> str:
    current_pe = repo_root / "CURRENT_PE.md"
    return current_pe.read_text(encoding="utf-8") if current_pe.exists() else ""


def _check_current_pe_metadata(repo_root: Path, packet: DispatchPacket) -> list[str]:
    content = _read_current_pe(repo_root)
    failures: list[str] = []
    if packet.pe_id not in content:
        failures.append("CURRENT_PE.md does not reference the approved PE ID")
    if packet.branch not in content:
        failures.append("CURRENT_PE.md does not reference the approved branch")
    if "infra-impl-b" not in content or "infra-val-a" not in content:
        failures.append("CURRENT_PE.md does not assign the approved implementer/validator roles")
    return failures


def _emit_summary(packet: DispatchPacket) -> None:
    print(render_summary(packet))
    print()
    print(packet.live_dispatch_statement)


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic PM dispatch wrapper.")
    parser.add_argument("--pe-id", required=True, help="Approved PE identifier.")
    parser.add_argument("--branch", required=True, help="Approved feature branch.")
    parser.add_argument("--baseline", required=True, help="Approved baseline ref and commit.")
    parser.add_argument("--lane", required=True, choices=["Strict"], help="Approved execution lane.")
    parser.add_argument("--implementer", required=True, help="Approved implementer agent ID.")
    parser.add_argument("--validator", required=True, help="Approved validator agent ID.")
    parser.add_argument(
        "--mode",
        choices=PHASE_1_GATES,
        default="dry-run",
        help="Phase 1 mode: dry-run, check, or generate.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used for check mode (defaults to current directory).",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON file path for generate mode; if omitted, JSON is printed to stdout.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
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
    if args.mode == "check":
        failures.extend(_check_current_pe_metadata(repo_root, packet))
        missing = validate_scoped_files(repo_root)
        if missing:
            failures.append(
                "Missing approved PE artefacts: " + ", ".join(missing)
            )

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

    print("PASS: Phase 1 packet is well-formed and does not call live dispatch APIs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
