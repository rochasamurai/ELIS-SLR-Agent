from __future__ import annotations

from pathlib import Path

from scripts import pe_sequencer


PLAN_BODY = """\
### PE-AUTO-06 · PE Sequencer — Automatic Advance Between PEs

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-02, PE-AUTO-05 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

---

### PE-AUTO-07 · PM Agent Arbitration Protocol

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-04, PE-AUTO-05 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

---

### PE-AUTO-08 · PM Agent Discord Loop

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-06, PE-AUTO-07 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |
"""


CURRENT_PE_BODY = """\
# Current PE Assignment

## Release context

| Field          | Value |
|----------------|-------|
| Release        | ELIS 2-Agent Automation Plan |
| Base branch    | main |
| Plan file      | ELIS_2Agent_Automation_Plan_v2_0.md |
| Plan location  | repo root |

## Current PE

| Field   | Value |
|---------|-------|
| PE      | PE-AUTO-06 |
| Branch  | feature/pe-auto-06-pe-sequencer |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |

## Active PE Registry

| PE-ID       | Domain          | Implementer-agentId | Validator-agentId | Branch                                            | Status          | Last-updated |
|-------------|-----------------|---------------------|-------------------|---------------------------------------------------|-----------------|--------------|
| PE-AUTO-04  | infra           | infra-impl-codex    | infra-val-claude  | feature/pe-auto-04-impl-runner                    | merged          | 2026-04-03   |
| PE-AUTO-05  | infra           | infra-impl-claude   | infra-val-codex   | feature/pe-auto-05-validator-runner               | merged          | 2026-04-07   |
| PE-AUTO-06  | infra           | infra-impl-codex    | infra-val-claude  | feature/pe-auto-06-pe-sequencer                   | implementing    | 2026-04-07   |

| Chore ID     | Description                                                                 | Date       |
|--------------|-----------------------------------------------------------------------------|------------|
| PM-CHORE-24  | Closed PE-AUTO-05 as merged and opened PE-AUTO-06.                         | 2026-04-07 |
"""


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_advance_current_pe_updates_registry_and_tables(tmp_path: Path) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_2Agent_Automation_Plan_v2_0.md"
    _write(current_pe, CURRENT_PE_BODY)
    _write(plan, PLAN_BODY)

    decision = pe_sequencer.advance_current_pe(current_pe)

    assert decision.action == "advance"
    assert decision.next_pe == "PE-AUTO-07"
    assert decision.next_branch == "feature/pe-auto-07-pm-agent-arbitration-protocol"
    assert decision.implementer_engine == "claude"
    assert decision.validator_engine == "codex"
    assert decision.pm_chore_id == "PM-CHORE-25"
    assert decision.updated_content is not None
    assert "| PE      | PE-AUTO-07 " in decision.updated_content
    assert (
        "| Branch  | feature/pe-auto-07-pm-agent-arbitration-protocol "
        in decision.updated_content
    )
    assert "infra-impl-claude" in decision.updated_content
    assert "infra-val-codex" in decision.updated_content
    assert "PM-CHORE-25" in decision.updated_content


def test_halts_when_next_dependency_is_unsatisfied(tmp_path: Path) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_2Agent_Automation_Plan_v2_0.md"
    _write(
        current_pe,
        CURRENT_PE_BODY.replace(
            "merged          | 2026-04-03", "implementing    | 2026-04-03", 1
        ),
    )
    _write(plan, PLAN_BODY)

    decision = pe_sequencer.advance_current_pe(current_pe)

    assert decision.action == "halt_blocked"
    assert decision.next_pe == "PE-AUTO-07"
    assert "unsatisfied dependency" in decision.reason
    assert decision.updated_content is None


def test_halts_when_series_is_complete(tmp_path: Path) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_2Agent_Automation_Plan_v2_0.md"
    _write(
        current_pe,
        CURRENT_PE_BODY.replace("PE-AUTO-06", "PE-AUTO-08", 1)
        .replace(
            "feature/pe-auto-06-pe-sequencer",
            "feature/pe-auto-08-pm-agent-discord-loop",
            1,
        )
        .replace(
            "| PE-AUTO-06  | infra           | infra-impl-codex    | infra-val-claude  | feature/pe-auto-06-pe-sequencer                   | implementing    | 2026-04-07   |",
            "| PE-AUTO-06  | infra           | infra-impl-codex    | infra-val-claude  | feature/pe-auto-06-pe-sequencer                   | merged          | 2026-04-07   |\n| PE-AUTO-07  | infra           | infra-impl-claude   | infra-val-codex   | feature/pe-auto-07-pm-agent-arbitration-protocol  | merged          | 2026-04-08   |\n| PE-AUTO-08  | infra           | infra-impl-codex    | infra-val-claude  | feature/pe-auto-08-pm-agent-discord-loop          | implementing    | 2026-04-09   |",
        ),
    )
    _write(
        plan,
        PLAN_BODY.replace(
            "| Depends On | PE-AUTO-06, PE-AUTO-07 |",
            "| Depends On | PE-AUTO-06, PE-AUTO-07 |",
        ),
    )

    decision = pe_sequencer.advance_current_pe(current_pe)

    assert decision.action == "halt_complete"
    assert decision.next_pe is None
    assert "No further PEs remain" in decision.reason


def test_skips_when_merged_branch_does_not_match_active_branch(tmp_path: Path) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_2Agent_Automation_Plan_v2_0.md"
    _write(current_pe, CURRENT_PE_BODY)
    _write(plan, PLAN_BODY)

    decision = pe_sequencer.advance_current_pe(
        current_pe,
        merged_branch="feature/not-the-active-pe",
    )

    assert decision.action == "skip"
    assert "skipping sequencer advance" in decision.reason


def test_halts_when_loop_control_is_paused(tmp_path: Path) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_2Agent_Automation_Plan_v2_0.md"
    control = tmp_path / "pm_loop_control.json"
    _write(current_pe, CURRENT_PE_BODY)
    _write(plan, PLAN_BODY)
    control.write_text(
        '{"paused": true, "reason": "PO pause requested"}\n',
        encoding="utf-8",
    )

    decision = pe_sequencer.advance_current_pe(current_pe, control_file=control)

    assert decision.action == "halt_paused"
    assert "PO pause requested" in decision.reason
