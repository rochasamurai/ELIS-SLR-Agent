from __future__ import annotations

from pathlib import Path

from scripts.check_implementer_runner_local_first import (
    validate_implementer_runner_local_first,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

CURRENT_PE_BODY = """\
## Release context

| Field          | Value                       |
|----------------|-----------------------------|
| Release        | ELIS SLR Agent              |
| Base branch    | main                        |
| Plan file      | ELIS_MultiAgent_Implementation_Plan_v1_9.md |
| Plan location  | repo root                   |

## Current PE

| Field   | Value |
|---------|-------|
| PE      | PE-SLR-11 |
| Branch  | feature/pe-slr-11-implementer-runner-local-first-confirmation |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |

## Active PE Registry

| PE-ID     | Domain | Implementer-agentId | Validator-agentId | Branch | Status | Last-updated |
|-----------|--------|---------------------|-------------------|--------|--------|--------------|
| PE-SLR-11 | slr    | infra-impl-codex    | infra-val-claude  | feature/pe-slr-11-implementer-runner-local-first-confirmation | implementing | 2026-04-25 |
"""

PLAN_BODY = """\
### PE-SLR-11 · Implementer Runner Local-First Confirmation

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Implementer runner launches from the governed workflow and starts a local session on `elis-server`. |
| AC-2 | The implementer session reads `CURRENT_PE.md` and the active plan before changing files. |
| AC-3 | `HANDOFF.md` is committed before the PR is opened. |
| AC-4 | The feature branch stays scope-safe and contains only PE-intended changes. |
| AC-5 | Local verification proves the runner invocation path is stable. |

---
"""


def test_implementer_runner_local_first_check_passes_with_active_context(tmp_path):
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text(PLAN_BODY, encoding="utf-8")

    assert (
        validate_implementer_runner_local_first(
            repo_root=REPO_ROOT,
            current_pe_path=current_pe,
            plan_path=plan,
        )
        == []
    )


def test_implementer_runner_check_reports_missing_plan_section(tmp_path):
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(CURRENT_PE_BODY, encoding="utf-8")
    plan.write_text("# Wrong plan\n", encoding="utf-8")

    errors = validate_implementer_runner_local_first(
        repo_root=REPO_ROOT,
        current_pe_path=current_pe,
        plan_path=plan,
    )

    assert any("Could not find plan section for PE-SLR-11" in error for error in errors)


def test_implementer_runner_check_requires_implementing_state(tmp_path):
    current_pe = tmp_path / "CURRENT_PE.md"
    plan = tmp_path / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
    current_pe.write_text(
        CURRENT_PE_BODY.replace("implementing", "gate-1-pending"),
        encoding="utf-8",
    )
    plan.write_text(PLAN_BODY, encoding="utf-8")

    errors = validate_implementer_runner_local_first(
        repo_root=REPO_ROOT,
        current_pe_path=current_pe,
        plan_path=plan,
    )

    assert any(
        "implementer dispatch requires an implementing PE" in error for error in errors
    )
