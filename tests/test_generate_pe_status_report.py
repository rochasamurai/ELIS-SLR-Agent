from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from scripts.generate_pe_status_report import (
    build_dashboard,
    main,
    parse_active_registry,
    parse_plan_markdown,
    parse_release_context,
)

_CURRENT_PE = """\
# Current PE Assignment

## Release context

| Field | Value |
|---|---|
| Release | ELIS 2-Agent Automation Plan |
| Base branch | main |
| Plan file | ELIS_2Agent_Automation_Plan_v2_0.md |
| Plan location | repo root |

## Current PE

| Field | Value |
|---|---|
| PE | PE-AUTO-10 |
| Branch | feature/pe-auto-10-observability-dashboard |

## Active PE Registry

| PE-ID | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |
|---|---|---|---|---|---|---|
| PE-AUTO-09 | infra | infra-impl-claude | infra-val-codex | feature/pe-auto-09-plan-loader-new-plan-ingestion | merged | 2026-04-10 |
| PE-AUTO-10 | infra | infra-impl-codex | infra-val-claude | feature/pe-auto-10-observability-dashboard | implementing | 2026-04-10 |
"""

_PLAN = """\
### PE-AUTO-09 · Plan Loader — New Plan Ingestion

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-06, PE-AUTO-08 |

### PE-AUTO-10 · Observability Dashboard

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-09 |

### PE-AUTO-11 · Parallel Track Scheduler

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-06, PE-AUTO-09 |
"""

_LESSONS = """\
## LL-20 — Arbitration

## PM Arbitration

PE-AUTO-09 required escalation.
"""

_REVIEW = """\
## Round 1 — 2026-04-10

### Verdict

PASS
"""


def test_parse_release_context() -> None:
    context = parse_release_context(_CURRENT_PE)
    assert context["release"] == "ELIS 2-Agent Automation Plan"
    assert context["plan_file"] == "ELIS_2Agent_Automation_Plan_v2_0.md"


def test_parse_plan_markdown_extracts_pe_sections() -> None:
    plan_pes = parse_plan_markdown(_PLAN)
    assert [pe.pe_id for pe in plan_pes] == ["PE-AUTO-09", "PE-AUTO-10", "PE-AUTO-11"]
    assert plan_pes[2].depends_on == ["PE-AUTO-06", "PE-AUTO-09"]


def test_build_dashboard_includes_merged_active_and_planned_rows(
    tmp_path: Path,
) -> None:
    rows = parse_active_registry(_CURRENT_PE)
    plan_pes = parse_plan_markdown(_PLAN)
    (tmp_path / "REVIEW_PE_AUTO_09.md").write_text(_REVIEW, encoding="utf-8")

    report = build_dashboard(
        release_name="ELIS 2-Agent Automation Plan",
        plan_pes=plan_pes,
        registry_rows=rows,
        lessons_content=_LESSONS,
        repo_root=tmp_path,
        auth_summary="Auth status: codex OK · claude OK",
    )

    assert "PE Series: ELIS 2-Agent Automation Plan" in report
    assert re.search(r"PE-AUTO-09\s+merged", report)
    assert "PASS (round 1" in report
    assert re.search(r"PE-AUTO-10\s+active", report)
    assert "implementing · CODEX" in report
    assert re.search(r"PE-AUTO-11\s+planned", report)
    assert "waiting on PE-AUTO-06" in report
    assert "Autonomy rate:" in report
    assert "Auth status: codex OK · claude OK" in report


def test_main_outputs_json_report(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path
    (repo / "CURRENT_PE.md").write_text(_CURRENT_PE, encoding="utf-8")
    (repo / "ELIS_2Agent_Automation_Plan_v2_0.md").write_text(_PLAN, encoding="utf-8")
    (repo / "LESSONS_LEARNED.md").write_text(_LESSONS, encoding="utf-8")
    (repo / "REVIEW_PE_AUTO_09.md").write_text(_REVIEW, encoding="utf-8")
    monkeypatch.setattr(
        "scripts.generate_pe_status_report.auth_status_summary",
        lambda: "Auth status: codex OK · claude OK",
    )

    old_argv = sys.argv
    sys.argv = [
        "generate_pe_status_report.py",
        "--current-pe",
        str(repo / "CURRENT_PE.md"),
        "--lessons",
        str(repo / "LESSONS_LEARNED.md"),
        "--json",
    ]
    try:
        rc = main()
    finally:
        sys.argv = old_argv

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert "report" in payload
    assert "PE-AUTO-10" in payload["report"]


def test_build_dashboard_uses_latest_verdict_from_multi_round_review(
    tmp_path: Path,
) -> None:
    rows = parse_active_registry(_CURRENT_PE)
    plan_pes = parse_plan_markdown(_PLAN)
    (tmp_path / "REVIEW_PE_AUTO_09.md").write_text(
        """## Round 1

### Verdict
FAIL

## Round 2

### Verdict
PASS
""",
        encoding="utf-8",
    )

    report = build_dashboard(
        release_name="ELIS 2-Agent Automation Plan",
        plan_pes=plan_pes,
        registry_rows=rows,
        lessons_content="",
        repo_root=tmp_path,
        auth_summary="Auth status: codex OK · claude OK",
    )

    assert "PE-AUTO-09  merged    2026-04-10  PASS (round 2)" in report


def test_build_dashboard_uses_explicit_round_number_from_revalidation_heading(
    tmp_path: Path,
) -> None:
    rows = parse_active_registry(_CURRENT_PE)
    plan_pes = parse_plan_markdown(_PLAN)
    (tmp_path / "REVIEW_PE_AUTO_09.md").write_text(
        """### Verdict
FAIL

## Re-validation — 2026-04-10 (Round 5)

### Verdict
PASS
""",
        encoding="utf-8",
    )

    report = build_dashboard(
        release_name="ELIS 2-Agent Automation Plan",
        plan_pes=plan_pes,
        registry_rows=rows,
        lessons_content="",
        repo_root=tmp_path,
        auth_summary="Auth status: codex OK · claude OK",
    )

    assert "PE-AUTO-09  merged    2026-04-10  PASS (round 5)" in report
