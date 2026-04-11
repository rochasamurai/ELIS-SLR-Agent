#!/usr/bin/env python
"""Generate an observability dashboard for the active PE series."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass

if __package__ in {None, ""}:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from scripts.pm_status_reporter import auth_status_summary

_DEFAULT_CURRENT_PE = pathlib.Path("CURRENT_PE.md")
_DEFAULT_LESSONS = pathlib.Path("LESSONS_LEARNED.md")
_REVIEW_FILE_GLOB = "REVIEW_PE*.md"
_PE_ID_RE = re.compile(r"^PE-[A-Z]+-[0-9]+$")


@dataclass(frozen=True)
class PlanPE:
    pe_id: str
    title: str
    domain: str
    depends_on: list[str]


def _table_value(content: str, field: str) -> str | None:
    match = re.search(
        rf"^\|\s*{re.escape(field)}\s*\|\s*([^|]+?)\s*\|$",
        content,
        re.MULTILINE,
    )
    return match.group(1).strip() if match else None


def parse_release_context(content: str) -> dict[str, str]:
    release = _table_value(content, "Release")
    base_branch = _table_value(content, "Base branch")
    plan_file = _table_value(content, "Plan file")
    if not release or not base_branch or not plan_file:
        raise ValueError("CURRENT_PE.md release context is incomplete.")
    return {
        "release": release,
        "base_branch": base_branch,
        "plan_file": plan_file,
    }


def parse_active_registry(content: str) -> list[dict[str, str]]:
    lines = content.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == "## active pe registry":
            start = idx + 1
            break
    if start is None:
        raise ValueError("Active PE Registry section missing.")

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
        raise ValueError("Active PE Registry table missing or malformed.")

    header = [part.strip().lower() for part in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for row_line in table_lines[2:]:
        parts = [part.strip() for part in row_line.strip("|").split("|")]
        if len(parts) != len(header):
            raise ValueError("Active PE Registry row has wrong column count.")
        rows.append(dict(zip(header, parts)))
    return rows


def parse_plan_markdown(content: str) -> list[PlanPE]:
    matches = list(
        re.finditer(r"^### (PE-[A-Z]+-[0-9]+) · (.+)$", content, flags=re.MULTILINE)
    )
    plan_pes: list[PlanPE] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        block = content[start:end]
        domain = _table_value(block, "Domain") or ""
        depends_on_text = _table_value(block, "Depends On") or ""
        if not domain:
            continue
        depends_on = [
            dep.strip("` ")
            for dep in re.split(r"[;,]", depends_on_text)
            if dep.strip() and dep.strip() != "—"
        ]
        depends_on = [dep for dep in depends_on if _PE_ID_RE.fullmatch(dep)]
        plan_pes.append(
            PlanPE(
                pe_id=match.group(1),
                title=match.group(2).strip(),
                domain=domain,
                depends_on=depends_on,
            )
        )
    if not plan_pes:
        raise ValueError("No PE sections found in plan file.")
    return plan_pes


def _engine_display(agent_id: str) -> str:
    lowered = agent_id.lower()
    if "codex" in lowered:
        return "CODEX"
    if "claude" in lowered:
        return "Claude Code"
    return agent_id


def _review_file_for_pe(pe_id: str, repo_root: pathlib.Path) -> pathlib.Path | None:
    expected = repo_root / f"REVIEW_{pe_id.replace('-', '_')}.md"
    if expected.exists():
        return expected
    for path in sorted(repo_root.glob(_REVIEW_FILE_GLOB)):
        if pe_id.replace("-", "_") in path.stem:
            return path
    return None


def _latest_verdict(review_content: str) -> str | None:
    verdict: str | None = None
    for match in re.finditer(r"^### Verdict\s*$", review_content, flags=re.MULTILINE):
        tail = review_content[match.end() :]
        verdict_match = re.search(
            r"^\s*(PASS|FAIL|IN PROGRESS)\b",
            tail,
            flags=re.MULTILINE,
        )
        if verdict_match:
            verdict = verdict_match.group(1)
    return verdict


def _round_count(review_content: str) -> int:
    rounds = re.findall(r"^## Round\b", review_content, flags=re.MULTILINE)
    if rounds:
        return len(rounds)
    verdicts = re.findall(r"^### Verdict\b", review_content, flags=re.MULTILINE)
    return 1 if verdicts else 0


def _lessons_blocks(lessons_content: str) -> list[str]:
    return [
        block
        for block in re.split(r"(?=^## LL-\d+\b)", lessons_content, flags=re.MULTILINE)
        if block.strip()
    ]


def intervention_counts(
    lessons_content: str, pe_ids: set[str]
) -> tuple[dict[str, int], int]:
    per_pe = {pe_id: 0 for pe_id in pe_ids}
    po_count = 0
    for block in _lessons_blocks(lessons_content):
        mentioned = {pe_id for pe_id in pe_ids if pe_id in block}
        if not mentioned:
            continue
        if "PM Arbitration" in block or "ESCALATE_PO" in block:
            for pe_id in mentioned:
                per_pe[pe_id] += 1
        if "ESCALATE_PO" in block:
            po_count += 1
    return per_pe, po_count


def build_dashboard(
    release_name: str,
    plan_pes: list[PlanPE],
    registry_rows: list[dict[str, str]],
    lessons_content: str,
    repo_root: pathlib.Path,
    auth_summary: str,
) -> str:
    row_by_pe = {row["pe-id"]: row for row in registry_rows if row.get("pe-id")}
    merged_ids = {
        row["pe-id"]
        for row in registry_rows
        if row.get("status", "").lower() == "merged"
    }
    release_pe_ids = {pe.pe_id for pe in plan_pes}
    interventions_by_pe, po_count = intervention_counts(lessons_content, release_pe_ids)

    lines = [
        f"PE Series: {release_name}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for pe in plan_pes:
        row = row_by_pe.get(pe.pe_id)
        if row is None:
            unsatisfied = [dep for dep in pe.depends_on if dep not in merged_ids]
            if unsatisfied:
                status_text = f"waiting on {', '.join(unsatisfied)}"
            else:
                status_text = "ready to start"
            lines.append(f"{pe.pe_id:<11} planned   —           {status_text}")
            continue

        status = row.get("status", "").lower()
        updated = row.get("last-updated", "—")
        if status == "merged":
            review_file = _review_file_for_pe(pe.pe_id, repo_root)
            verdict_text = "merged"
            if review_file is not None:
                review_content = review_file.read_text(encoding="utf-8")
                verdict = _latest_verdict(review_content) or "PASS"
                rounds = _round_count(review_content)
                interventions = interventions_by_pe.get(pe.pe_id, 0)
                verdict_text = f"{verdict} (round {rounds})"
                if interventions:
                    noun = "intervention" if interventions == 1 else "interventions"
                    verdict_text = (
                        f"{verdict} (round {rounds} — {interventions} arbiter {noun})"
                    )
            lines.append(f"{pe.pe_id:<11} merged    {updated:<11} {verdict_text}")
            continue

        implementer = _engine_display(row.get("implementer-agentid", ""))
        lines.append(
            f"{pe.pe_id:<11} active    —           {status} · {implementer} · updated {updated}"
        )

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    autonomous_merged = sum(
        1
        for pe_id in merged_ids & release_pe_ids
        if interventions_by_pe.get(pe_id, 0) == 0
    )
    merged_count = len(merged_ids & release_pe_ids)
    autonomy_rate = (
        round((autonomous_merged / merged_count) * 100) if merged_count else 0
    )
    lines.append(
        f"Autonomy rate: {autonomous_merged}/{merged_count} PEs merged without escalation "
        f"({autonomy_rate}%)"
    )
    lines.append(
        f"Arbiter interventions: {sum(interventions_by_pe.values())} "
        f"({', '.join(pe_id for pe_id, count in interventions_by_pe.items() if count) or 'none'})"
    )
    lines.append(f"PO interventions: {po_count}")
    lines.append(auth_summary)
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Generate the PM observability dashboard for the active PE series."
    )
    parser.add_argument(
        "--current-pe",
        default=str(_DEFAULT_CURRENT_PE),
        help="Path to CURRENT_PE.md (default: CURRENT_PE.md)",
    )
    parser.add_argument(
        "--lessons",
        default=str(_DEFAULT_LESSONS),
        help="Path to LESSONS_LEARNED.md (default: LESSONS_LEARNED.md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON object with the dashboard text.",
    )
    args = parser.parse_args()

    current_pe_path = pathlib.Path(args.current_pe)
    repo_root = current_pe_path.resolve().parent
    try:
        current_content = current_pe_path.read_text(encoding="utf-8")
        release_context = parse_release_context(current_content)
        registry_rows = parse_active_registry(current_content)
        plan_path = repo_root / release_context["plan_file"]
        plan_content = plan_path.read_text(encoding="utf-8")
        plan_pes = parse_plan_markdown(plan_content)
        lessons_content = pathlib.Path(args.lessons).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    dashboard = build_dashboard(
        release_name=release_context["release"],
        plan_pes=plan_pes,
        registry_rows=registry_rows,
        lessons_content=lessons_content,
        repo_root=repo_root,
        auth_summary=auth_status_summary(),
    )

    if args.json:
        import json

        print(json.dumps({"report": dashboard}, indent=2))
    else:
        print(dashboard)
    return 0


if __name__ == "__main__":
    sys.exit(main())
