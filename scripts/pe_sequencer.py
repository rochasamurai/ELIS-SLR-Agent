"""PE-AUTO-06 sequencer for automatic PE advance after merge."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from scripts.pm_assign_pe import make_branch_name


CURRENT_PE_HEADING = "## Current PE"
RELEASE_HEADING = "## Release context"
ROLES_HEADING = "## Agent roles"
REGISTRY_HEADING = "## Active PE Registry"
SECTION_BREAK_RE = re.compile(r"^---\s*$", re.MULTILINE)
PE_SECTION_RE = re.compile(r"^###\s+(PE-[A-Z]+-[0-9]+)\s+·\s+(.+?)\s*$", re.MULTILINE)
TABLE_FIELD_RE = re.compile(r"^\|\s*(?P<field>[^|]+?)\s*\|\s*(?P<value>[^|]+?)\s*\|$")


@dataclass(frozen=True)
class PlanPE:
    pe_id: str
    title: str
    domain: str
    depends_on: tuple[str, ...]
    implementer_agent: str
    validator_agent: str


@dataclass(frozen=True)
class SequencerDecision:
    action: str
    merged_pe: str
    next_pe: str | None
    next_branch: str | None
    reason: str
    updated_content: str | None
    implementer_engine: str | None
    validator_engine: str | None
    pm_chore_id: str | None

    def as_outputs(self) -> dict[str, str]:
        return {
            "action": self.action,
            "merged_pe": self.merged_pe,
            "next_pe": self.next_pe or "",
            "next_branch": self.next_branch or "",
            "reason": self.reason,
            "implementer_engine": self.implementer_engine or "",
            "validator_engine": self.validator_engine or "",
            "pm_chore_id": self.pm_chore_id or "",
        }


class SequencerError(RuntimeError):
    """Raised when the sequencer cannot update CURRENT_PE.md safely."""


def _extract_table_value(content: str, heading: str, field: str) -> str:
    lines = content.splitlines()
    in_heading = False
    for line in lines:
        if line.strip() == heading:
            in_heading = True
            continue
        if in_heading and line.startswith("## ") and line.strip() != heading:
            break
        match = TABLE_FIELD_RE.match(line.strip())
        if match and match.group("field").strip() == field:
            return match.group("value").strip()
    raise SequencerError(f"Missing '{field}' in section '{heading}'.")


def _engine(agent_id: str) -> str:
    lowered = agent_id.lower()
    if "codex" in lowered:
        return "codex"
    if "claude" in lowered:
        return "claude"
    raise SequencerError(f"Cannot infer engine from agent id '{agent_id}'.")


def _current_pe_id(content: str) -> str:
    return _extract_table_value(content, CURRENT_PE_HEADING, "PE")


def _current_branch(content: str) -> str:
    return _extract_table_value(content, CURRENT_PE_HEADING, "Branch")


def _parse_registry_rows(content: str) -> tuple[list[str], list[list[str]]]:
    lines = content.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == REGISTRY_HEADING:
            start = idx + 1
            break
    if start is None:
        raise SequencerError("Active PE Registry table not found.")

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
        raise SequencerError("Active PE Registry table is malformed.")

    header = [part.strip() for part in table_lines[0].strip("|").split("|")]
    rows = []
    for row_line in table_lines[2:]:
        values = [part.strip() for part in row_line.strip("|").split("|")]
        if len(values) != len(header):
            raise SequencerError("Active PE Registry row has wrong column count.")
        rows.append(values)
    return header, rows


def _find_registry_row(rows: list[list[str]], pe_id: str) -> list[str]:
    for row in rows:
        if row[0] == pe_id:
            return row
    raise SequencerError(f"Registry row not found for {pe_id}.")


def _format_registry_row(row: list[str]) -> str:
    return (
        f"| {row[0]:<11} | {row[1]:<15} | {row[2]:<20} | {row[3]:<18} | "
        f"{row[4]:<49} | {row[5]:<15} | {row[6]:<12} |"
    )


def _replace_table_value(content: str, heading: str, field: str, value: str) -> str:
    lines = content.splitlines()
    in_heading = False
    for idx, line in enumerate(lines):
        if line.strip() == heading:
            in_heading = True
            continue
        if in_heading and line.startswith("## ") and line.strip() != heading:
            break
        match = TABLE_FIELD_RE.match(line.strip())
        if match and match.group("field").strip() == field:
            lines[idx] = re.sub(
                r"(\|\s*" + re.escape(field) + r"\s*\|\s*)([^|]+)(\|\s*)$",
                rf"\1{value} \3",
                line,
            )
            return "\n".join(lines) + "\n"
    raise SequencerError(f"Could not replace '{field}' in section '{heading}'.")


def _replace_roles_table(content: str, implementer_engine: str) -> str:
    roles = {
        "CODEX": "Implementer" if implementer_engine == "codex" else "Validator",
        "Claude Code": "Validator" if implementer_engine == "codex" else "Implementer",
    }
    lines = content.splitlines()
    in_roles = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == ROLES_HEADING:
            in_roles = True
            continue
        if in_roles and stripped.startswith("## ") and stripped != ROLES_HEADING:
            break
        for agent, role in roles.items():
            if re.match(rf"^\|\s*{re.escape(agent)}\s*\|", stripped):
                lines[idx] = f"| {agent:<11} | {role:<11} |"
    return "\n".join(lines) + "\n"


def _replace_registry_table(
    content: str, header: list[str], rows: list[list[str]]
) -> str:
    formatted = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join("-" * (len(column) + 2) for column in header) + "|",
        *[_format_registry_row(row) for row in rows],
    ]
    lines = content.splitlines()
    start = None
    end = None
    seen_registry_rows = False
    for idx, line in enumerate(lines):
        if line.strip() == REGISTRY_HEADING:
            start = idx + 1
            continue
        if start is not None and idx >= start:
            stripped = line.strip()
            if stripped.startswith("|"):
                seen_registry_rows = True
                continue
            if seen_registry_rows and not stripped:
                end = idx
                break
            if stripped and not stripped.startswith("|"):
                end = idx
                break
    if start is None:
        raise SequencerError("Active PE Registry table not found.")
    if end is None:
        end = len(lines)
    new_lines = lines[:start]
    new_lines.extend(["", *formatted, ""])
    new_lines.extend(lines[end:])
    return "\n".join(new_lines).rstrip() + "\n"


def _next_pm_chore_id(content: str) -> str:
    matches = re.findall(r"\|\s*PM-CHORE-(\d+)\s*\|", content)
    number = max((int(match) for match in matches), default=0) + 1
    return f"PM-CHORE-{number:02d}"


def _append_pm_chore(content: str, chore_id: str, description: str, date: str) -> str:
    lines = content.splitlines()
    insert_at = None
    for idx, line in enumerate(lines):
        if line.startswith("| PM-CHORE-"):
            insert_at = idx + 1
    if insert_at is None:
        for idx, line in enumerate(lines):
            if line.strip().startswith("| Chore ID"):
                insert_at = idx + 2
                break
    if insert_at is None:
        raise SequencerError("PM housekeeping table not found.")
    lines.insert(insert_at, f"| {chore_id:<12} | {description} | {date} |")
    return "\n".join(lines).rstrip() + "\n"


def parse_plan(plan_path: Path) -> list[PlanPE]:
    content = plan_path.read_text(encoding="utf-8")
    matches = list(PE_SECTION_RE.finditer(content))
    pes: list[PlanPE] = []
    for idx, match in enumerate(matches):
        section_start = match.end()
        next_start = (
            matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        )
        section = content[section_start:next_start]
        stop = SECTION_BREAK_RE.search(section)
        if stop is not None:
            section = section[: stop.start()]
        fields = {
            field: value
            for field, value in re.findall(
                r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$", section, re.MULTILINE
            )
        }
        if "Domain" not in fields:
            continue
        depends_raw = fields.get("Depends On", "—").strip()
        depends_on = tuple(
            part.strip()
            for part in depends_raw.split(",")
            if part.strip() and part.strip() not in {"—", "-"}
        )
        pes.append(
            PlanPE(
                pe_id=match.group(1).strip(),
                title=match.group(2).strip(),
                domain=fields["Domain"].strip(),
                depends_on=depends_on,
                implementer_agent=fields["Implementer"].strip().strip("`"),
                validator_agent=fields["Validator"].strip().strip("`"),
            )
        )
    if not pes:
        raise SequencerError(f"No PE sections found in {plan_path}.")
    return pes


def _find_next_ready_pe(
    plan_pes: list[PlanPE],
    merged_pe: str,
    registry_rows: list[list[str]],
) -> PlanPE | None:
    merged = {row[0] for row in registry_rows if row[5].lower() == "merged"}
    merged.add(merged_pe)
    seen_merged = False
    for pe in plan_pes:
        if pe.pe_id == merged_pe:
            seen_merged = True
            continue
        if not seen_merged:
            continue
        if pe.pe_id in merged:
            continue
        if all(dep in merged for dep in pe.depends_on):
            return pe
        return None
    return None


def _next_unready_pe(
    plan_pes: list[PlanPE],
    merged_pe: str,
    registry_rows: list[list[str]],
) -> PlanPE | None:
    merged = {row[0] for row in registry_rows if row[5].lower() == "merged"}
    merged.add(merged_pe)
    seen_merged = False
    for pe in plan_pes:
        if pe.pe_id == merged_pe:
            seen_merged = True
            continue
        if not seen_merged:
            continue
        if pe.pe_id in merged:
            continue
        if not all(dep in merged for dep in pe.depends_on):
            return pe
    return None


def _ensure_registry_row(
    rows: list[list[str]], pe: PlanPE, branch: str, date: str
) -> list[list[str]]:
    for row in rows:
        if row[0] == pe.pe_id:
            row[1] = pe.domain
            row[2] = pe.implementer_agent
            row[3] = pe.validator_agent
            row[4] = branch
            row[5] = "implementing"
            row[6] = date
            return rows
    rows.append(
        [
            pe.pe_id,
            pe.domain,
            pe.implementer_agent,
            pe.validator_agent,
            branch,
            "implementing",
            date,
        ]
    )
    return rows


def advance_current_pe(
    current_pe_path: Path,
    merged_pe: str | None = None,
    merged_branch: str | None = None,
) -> SequencerDecision:
    content = current_pe_path.read_text(encoding="utf-8")
    active_pe = _current_pe_id(content)
    active_branch = _current_branch(content)
    if merged_pe is None:
        merged_pe = active_pe
    if merged_pe != active_pe:
        raise SequencerError(
            f"CURRENT_PE.md says active PE is {active_pe}, not {merged_pe}."
        )
    if merged_branch is not None and merged_branch != active_branch:
        return SequencerDecision(
            action="skip",
            merged_pe=merged_pe,
            next_pe=None,
            next_branch=None,
            reason=(
                f"Merged branch {merged_branch} does not match active branch "
                f"{active_branch}; skipping sequencer advance."
            ),
            updated_content=None,
            implementer_engine=None,
            validator_engine=None,
            pm_chore_id=None,
        )

    plan_file = _extract_table_value(content, RELEASE_HEADING, "Plan file")
    plan_location = _extract_table_value(content, RELEASE_HEADING, "Plan location")
    plan_path = (
        current_pe_path.parent / plan_file
        if plan_location == "repo root"
        else current_pe_path.parent / plan_location / plan_file
    )
    plan_pes = parse_plan(plan_path)

    today = dt.date.today().isoformat()
    header, rows = _parse_registry_rows(content)
    merged_row = _find_registry_row(rows, merged_pe)
    merged_row[5] = "merged"
    merged_row[6] = today

    next_pe = _find_next_ready_pe(plan_pes, merged_pe, rows)
    if next_pe is None:
        blocked = _next_unready_pe(plan_pes, merged_pe, rows)
        if blocked is not None:
            return SequencerDecision(
                action="halt_blocked",
                merged_pe=merged_pe,
                next_pe=blocked.pe_id,
                next_branch=None,
                reason=(
                    f"Next PE {blocked.pe_id} has unsatisfied dependency: "
                    + ", ".join(blocked.depends_on)
                ),
                updated_content=None,
                implementer_engine=None,
                validator_engine=None,
                pm_chore_id=None,
            )
        return SequencerDecision(
            action="halt_complete",
            merged_pe=merged_pe,
            next_pe=None,
            next_branch=None,
            reason="No further PEs remain in the plan sequence.",
            updated_content=None,
            implementer_engine=None,
            validator_engine=None,
            pm_chore_id=None,
        )

    branch = make_branch_name(next_pe.pe_id, next_pe.title)
    rows = _ensure_registry_row(rows, next_pe, branch, today)
    content = _replace_registry_table(content, header, rows)
    content = _replace_table_value(content, CURRENT_PE_HEADING, "PE", next_pe.pe_id)
    content = _replace_table_value(content, CURRENT_PE_HEADING, "Branch", branch)
    content = _replace_roles_table(content, _engine(next_pe.implementer_agent))
    chore_id = _next_pm_chore_id(content)
    description = (
        f"Auto-advanced from {merged_pe} to {next_pe.pe_id} after merge. "
        f"Opened {branch} with `{next_pe.implementer_agent}` as Implementer and "
        f"`{next_pe.validator_agent}` as Validator per plan sequence."
    )
    content = _append_pm_chore(content, chore_id, description, today)
    return SequencerDecision(
        action="advance",
        merged_pe=merged_pe,
        next_pe=next_pe.pe_id,
        next_branch=branch,
        reason=f"Advanced to {next_pe.pe_id}.",
        updated_content=content,
        implementer_engine=_engine(next_pe.implementer_agent),
        validator_engine=_engine(next_pe.validator_agent),
        pm_chore_id=chore_id,
    )


def _write_outputs(outputs: dict[str, str]) -> None:
    output_path = Path.cwd() / ".sequencer-outputs"
    github_output = os.environ.get("GITHUB_OUTPUT", "").strip()
    if github_output:
        with Path(github_output).open("a", encoding="utf-8") as handle:
            for key, value in outputs.items():
                handle.write(f"{key}={value}\n")
        return
    output_path.write_text(
        "\n".join(f"{key}={value}" for key, value in outputs.items()) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Advance CURRENT_PE.md after a merge.")
    parser.add_argument(
        "--current-pe",
        default="CURRENT_PE.md",
        help="Path to CURRENT_PE.md (default: CURRENT_PE.md)",
    )
    parser.add_argument(
        "--merged-pe",
        help="Merged PE id. Defaults to the active PE in CURRENT_PE.md.",
    )
    parser.add_argument(
        "--merged-branch",
        help="Merged branch name. Must match the active branch in CURRENT_PE.md.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the updated CURRENT_PE.md in place when an advance is available.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the decision as JSON.",
    )
    args = parser.parse_args()

    try:
        current_pe_path = Path(args.current_pe)
        decision = advance_current_pe(
            current_pe_path,
            args.merged_pe,
            args.merged_branch,
        )
        if args.write and decision.updated_content is not None:
            current_pe_path.write_text(decision.updated_content, encoding="utf-8")
        _write_outputs(decision.as_outputs())
        if args.json:
            print(json.dumps(decision.as_outputs(), indent=2, sort_keys=True))
        else:
            print(decision.reason)
        return 0
    except SequencerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
