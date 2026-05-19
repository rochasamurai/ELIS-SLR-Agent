#!/usr/bin/env python3
"""pm_dispatch.py — deterministic PM dispatch opening-packet wrapper.

Phase 1 only:
- dry-run / check / generate
- no live dispatch APIs
- no Discord API automation
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

PE_ID = "PE-OPS-DISPATCH-WRAPPER-HARDENING-01"
OBJECTIVE = (
    "Harden the deterministic PM dispatch wrapper so approved OpenClaw runtime/bootstrap "
    "artefacts in fixed agent workspaces do not trigger false dispatch blocks, and add a "
    "PO-side helper to verify the safe PM start sequence for new PE/task flows."
)
APPROVED_BRANCH = "feature/pe-ops-dispatch-wrapper-hardening-01"
APPROVED_BASELINE_PATTERN = re.compile(r"^origin/main @ [0-9a-f]{40}$")
APPROVED_IMPLEMENTER = "infra-impl-b"
APPROVED_VALIDATOR = "infra-val-a"
APPROVED_FILE_SCOPE: tuple[str, ...] = (
    "CURRENT_PE.md",
    ".elis/pe/PE-OPS-DISPATCH-WRAPPER-HARDENING-01/PE_TASK.md",
    ".elis/pe/PE-OPS-DISPATCH-WRAPPER-HARDENING-01/HANDOFF.md",
    "docs/governance/ELIS_Dispatch_Wrapper_Hardening.md",
    "scripts/pm_dispatch.py",
    "scripts/po_dispatch.py",
    "tests/test_pm_dispatch.py",
    "tests/test_pm_dispatch_contract.py",
    "tests/test_po_dispatch.py",
)
RUNTIME_BOOTSTRAP_ALLOWLIST_NAMES: tuple[str, ...] = (
    "AGENTS.md",
    "TOOLS.md",
    "USER.md",
    "HEARTBEAT.md",
    "SOUL.md",
    "IDENTITY.md",
)
RUNTIME_BOOTSTRAP_ALLOWLIST_PREFIXES: tuple[str, ...] = (
    ".openclaw/",
    "memory/",
    "skills/",
    "canvas/",
)
RUNTIME_BOOTSTRAP_ALLOWLIST: tuple[str, ...] = (
    *RUNTIME_BOOTSTRAP_ALLOWLIST_NAMES,
    *RUNTIME_BOOTSTRAP_ALLOWLIST_PREFIXES,
)
SECRET_BEARING_HINTS: tuple[str, ...] = (
    ".env",
    "auth.json",
    "credentials.json",
    "secret",
    "secrets",
    "token",
    "tokens",
    "password",
    "private_key",
)
REQUIRED_RULES: tuple[str, ...] = (
    "PRESERVED_RUNTIME_BOOTSTRAP_FILES_ARE_NOT_DISPATCH_BLOCKERS_RULE",
    "NEW_PE_REQUIRES_FRESH_THREAD_AND_RESET_ACK_RULE",
    "DISPATCH_CONTRACT_MUST_USE_TARGET_AGENT_WORKSPACE_RULE",
    "FRESH_VALIDATOR_SUBAGENT_DISPATCH_RULE",
    "VALIDATOR_MUST_NOT_USE_PM_WORKTREE_RULE",
    "VALIDATION_PASS_REQUIRES_PRIOR_RESET_ACK_RULE",
    "TARGET_REF_AVAILABLE_BEFORE_AGENT_BINDING_RULE",
    "FIXED_AGENT_WORKTREE_READINESS_BEFORE_DISPATCH_RULE",
    "ROLE_CORRECT_GIT_AUTHOR_IDENTITY_RULE",
    "COMPLETE_BRANCH_FILE_SCOPE_EVIDENCE_RULE",
)
PHASE_1_GATES: tuple[str, ...] = ("dry-run", "check", "generate")
HARD_STOPS: tuple[str, ...] = (
    "do not create the branch here",
    "do not call Discord APIs",
    "do not send live messages",
    "do not call OpenClaw live dispatch actions",
    "do not mutate repo state outside approved scope",
    "do not alter CURRENT_PE.md outside approved scope",
    "do not change OpenClaw/Hermes config",
    "do not change auth or secret state",
    "do not restart services",
    "do not replace live dispatch behaviour",
    "do not push, open PRs, or merge without PO approval",
)
PHASE_1_ONLY_STATEMENT = (
    "Phase 1 only generates and checks dispatch contracts; it does not call live dispatch APIs "
    "or Discord APIs."
)
RUNTIME_BOOTSTRAP_POLICY = (
    "Approved OpenClaw runtime/bootstrap files are non-blocking only when they are untracked or "
    "workspace-local, not staged, not part of the PE-approved file scope, not secret-bearing, "
    "not modified tracked repository files, not being committed, and not masking unsafe PE residue."
)
EXPECTED_TESTS: tuple[str, ...] = (
    "tests/test_pm_dispatch.py",
    "tests/test_pm_dispatch_contract.py",
    "tests/test_po_dispatch.py",
)
ROLLBACK_PLAN = (
    "Revert only the approved scoped files to the accepted origin/main baseline and keep "
    "OpenClaw/Hermes configuration unchanged."
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
    runtime_bootstrap_allowlist: tuple[str, ...] = RUNTIME_BOOTSTRAP_ALLOWLIST
    required_rules: tuple[str, ...] = REQUIRED_RULES
    phase_1_gates: tuple[str, ...] = PHASE_1_GATES
    tests: tuple[str, ...] = EXPECTED_TESTS
    rollback: str = ROLLBACK_PLAN
    hard_stops: tuple[str, ...] = HARD_STOPS
    live_dispatch_statement: str = PHASE_1_ONLY_STATEMENT
    runtime_bootstrap_policy: str = RUNTIME_BOOTSTRAP_POLICY


@dataclass(frozen=True)
class WorkspaceFinding:
    status: str
    path: str
    category: str
    reason: str


@dataclass(frozen=True)
class WorkspaceAssessment:
    findings: tuple[WorkspaceFinding, ...]
    approved_scope_changes: tuple[WorkspaceFinding, ...]
    preserved_runtime_bootstrap: tuple[WorkspaceFinding, ...]
    blockers: tuple[WorkspaceFinding, ...]


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
        objective=OBJECTIVE,
        branch=branch,
        baseline=baseline,
        lane=lane,
        implementer=implementer,
        validator=validator,
        mode=mode,
    )


def _normalise_path(raw_path: str) -> str:
    return PurePosixPath(raw_path.strip()).as_posix()


def _parse_porcelain_line(line: str) -> tuple[str, str]:
    code = line[:2]
    path = line[3:] if len(line) > 3 else ""
    if " -> " in path:
        path = path.rsplit(" -> ", 1)[-1]
    return code, _normalise_path(path)


def _looks_secret_bearing(path: str) -> bool:
    lower = path.lower()
    basename = PurePosixPath(lower).name
    return any(hint in lower or hint in basename for hint in SECRET_BEARING_HINTS)


def is_preserved_runtime_bootstrap_path(path: str) -> bool:
    normalised = _normalise_path(path)
    if normalised in APPROVED_FILE_SCOPE:
        return False
    if _looks_secret_bearing(normalised):
        return False
    if normalised in RUNTIME_BOOTSTRAP_ALLOWLIST_NAMES:
        return True
    return any(
        normalised == prefix.rstrip("/") or normalised.startswith(prefix)
        for prefix in RUNTIME_BOOTSTRAP_ALLOWLIST_PREFIXES
    )


def classify_workspace_line(line: str) -> WorkspaceFinding:
    code, path = _parse_porcelain_line(line)
    if not code.strip():
        return WorkspaceFinding(code, path, "clean", "No change")

    if path in APPROVED_FILE_SCOPE:
        return WorkspaceFinding(
            code, path, "approved-scope", "Change is inside the approved PE scope"
        )

    if code == "??" and is_preserved_runtime_bootstrap_path(path):
        return WorkspaceFinding(
            code,
            path,
            "preserved-runtime-bootstrap",
            "Untracked runtime/bootstrap residue is allowed in fixed workspaces",
        )

    if _looks_secret_bearing(path):
        return WorkspaceFinding(
            code,
            path,
            "blocker",
            "Secret-bearing artefact must block dispatch",
        )

    if code == "??":
        return WorkspaceFinding(
            code,
            path,
            "blocker",
            "Untracked file outside approved scope",
        )

    if code[0] != " ":
        return WorkspaceFinding(
            code,
            path,
            "blocker",
            "Staged change outside approved scope",
        )

    if code[1] != " ":
        return WorkspaceFinding(
            code,
            path,
            "blocker",
            "Modified tracked file outside approved scope",
        )

    return WorkspaceFinding(code, path, "clean", "No change")


def assess_workspace_state(repo_root: Path) -> WorkspaceAssessment:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return WorkspaceAssessment((), (), (), ())

    findings = tuple(
        classify_workspace_line(line)
        for line in result.stdout.splitlines()
        if line.strip()
    )
    approved_scope_changes = tuple(
        finding for finding in findings if finding.category == "approved-scope"
    )
    preserved_runtime_bootstrap = tuple(
        finding
        for finding in findings
        if finding.category == "preserved-runtime-bootstrap"
    )
    blockers = tuple(finding for finding in findings if finding.category == "blocker")
    return WorkspaceAssessment(
        findings=findings,
        approved_scope_changes=approved_scope_changes,
        preserved_runtime_bootstrap=preserved_runtime_bootstrap,
        blockers=blockers,
    )


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
    if packet.implementer not in content or packet.validator not in content:
        failures.append(
            "CURRENT_PE.md does not assign the approved implementer/validator roles"
        )
    if (
        "Phase 1 dry-run/check/generate only" not in content
        and "dry-run / check / generate only" not in content
    ):
        failures.append(
            "CURRENT_PE.md does not state the Phase 1 dry-run/check/generate constraint"
        )
    return failures


def validate_packet(packet: DispatchPacket) -> list[str]:
    """Validate the deterministic Phase 1 packet shape."""

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
    if packet.file_scope != APPROVED_FILE_SCOPE:
        failures.append(
            "Approved file scope does not match the controlled PE opening packet"
        )
    if packet.runtime_bootstrap_allowlist != RUNTIME_BOOTSTRAP_ALLOWLIST:
        failures.append(
            "Runtime/bootstrap allow-list does not match the approved safety policy"
        )
    if packet.required_rules != REQUIRED_RULES:
        failures.append("Required governance rules do not match the approved packet")
    if packet.phase_1_gates != PHASE_1_GATES:
        failures.append("Phase 1 gates do not match the controlled wrapper contract")
    if packet.tests != EXPECTED_TESTS:
        failures.append("Test plan does not match the approved Phase 1 scope")
    if packet.live_dispatch_statement != PHASE_1_ONLY_STATEMENT:
        failures.append("Live dispatch statement is missing or altered")
    if packet.runtime_bootstrap_policy != RUNTIME_BOOTSTRAP_POLICY:
        failures.append("Runtime/bootstrap policy text is missing or altered")
    if packet.hard_stops != HARD_STOPS:
        failures.append("Hard stops do not match the approved Phase 1 boundary")
    if packet.rollback != ROLLBACK_PLAN:
        failures.append("Rollback plan does not match the approved scope")
    return failures


def _packet_payload(packet: DispatchPacket) -> dict[str, object]:
    payload = asdict(packet)
    payload["file_scope"] = list(packet.file_scope)
    payload["runtime_bootstrap_allowlist"] = list(packet.runtime_bootstrap_allowlist)
    payload["required_rules"] = list(packet.required_rules)
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
        "Approved file scope:",
    ]
    lines.extend(f"- {item}" for item in packet.file_scope)
    lines.extend(
        [
            "Runtime/bootstrap allow-list:",
            *[f"- {item}" for item in packet.runtime_bootstrap_allowlist],
            "Required rules:",
            *[f"- {item}" for item in packet.required_rules],
            "Phase 1 gates:",
            *[f"- {gate}" for gate in packet.phase_1_gates],
            "Tests:",
            *[f"- {test}" for test in packet.tests],
            f"Runtime/bootstrap policy: {packet.runtime_bootstrap_policy}",
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


def validate_scoped_files(repo_root: Path) -> list[str]:
    """Confirm the approved PE artefacts exist in the PE worktree."""

    missing = [path for path in APPROVED_FILE_SCOPE if not (repo_root / path).exists()]
    return missing


def _emit_summary(packet: DispatchPacket) -> None:
    print(render_summary(packet))
    print()
    print(packet.live_dispatch_statement)


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic PM dispatch wrapper.")
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
            failures.append("Missing approved PE artefacts: " + ", ".join(missing))
        assessment = assess_workspace_state(repo_root)
        if assessment.blockers:
            failures.append(
                "Dispatch blockers detected: "
                + "; ".join(
                    f"{finding.status} {finding.path} ({finding.reason})"
                    for finding in assessment.blockers
                )
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
