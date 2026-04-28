"""Tests for PE-AUTO-11 Parallel Track Scheduler.

Covers:
  AC-1  check_parallel_eligibility returns ELIGIBLE for valid independent pairs
  AC-2  check_parallel_eligibility returns INELIGIBLE for mutually dependent pairs
  AC-3  Sequencer performs dual dispatch when DAG has >=2 ready + eligible PEs
  AC-4  check_current_pe.py validates Track A + Track B structure
  AC-5  When Track A closes, Track B remains active as sole PE
  AC-6  Runtime/config sources still encode the documented parallel-track rules
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from scripts.check_parallel_eligibility import check_eligibility
from scripts.pe_sequencer import (
    PlanPE,
    advance_current_pe,
)

# ---------------------------------------------------------------------------
# Shared plan fixtures
# ---------------------------------------------------------------------------

#   PE-P-00  (codex impl) — root PE, already merged
#   PE-P-01  (codex impl) — parallel-ineligible with PE-P-02 (same engine)
#   PE-P-02  (claude impl) — parallel-eligible with PE-P-03
#   PE-P-03  (codex impl) — parallel-eligible with PE-P-02
#   PE-P-04  (codex impl) — depends on PE-P-03 (blocks until PE-P-03 merged)
#   PE-P-05  (claude impl) — depends on PE-P-03 (eligible with PE-P-04, but PE-P-04 also codex)

PLAN_PARALLEL = """\
### PE-P-00 · Root PE

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | — |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

---

### PE-P-01 · Alpha PE (codex — same engine as PE-P-00 successor)

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | — |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

---

### PE-P-02 · Beta PE (claude — eligible parallel with PE-P-01 not applicable; standalone)

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | — |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

---

### PE-P-03 · Gamma PE (depends on PE-P-01)

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-P-01 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

---

### PE-P-04 · Delta PE (depends on PE-P-01)

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-P-01 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

---

### PE-P-05 · Epsilon PE (depends on PE-P-03)

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-P-03, PE-P-04 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |
"""

# Simpler plan: two independent PEs ready simultaneously, eligible for parallel dispatch
PLAN_DUAL = """\
### PE-D-00 · Prerequisite

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | — |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

---

### PE-D-01 · Track A candidate (codex)

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | — |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

---

### PE-D-02 · Track B candidate (claude)

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | — |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

---

### PE-D-03 · Final (depends on both)

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-D-01, PE-D-02 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |
"""


def _plan_pes_parallel() -> list[PlanPE]:
    from scripts.pe_sequencer import parse_plan
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(PLAN_PARALLEL)
        name = f.name
    try:
        return parse_plan(Path(name))
    finally:
        os.unlink(name)


def _plan_pes_dual() -> list[PlanPE]:
    from scripts.pe_sequencer import parse_plan
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(PLAN_DUAL)
        name = f.name
    try:
        return parse_plan(Path(name))
    finally:
        os.unlink(name)


# ---------------------------------------------------------------------------
# AC-1 — ELIGIBLE cases
# ---------------------------------------------------------------------------


def test_eligible_independent_different_engines() -> None:
    """PE-P-01 and PE-P-02 have no mutual dependency and different engines."""
    plan_pes = _plan_pes_parallel()
    eligible, failures = check_eligibility("PE-P-01", "PE-P-02", plan_pes)
    assert eligible, f"Expected ELIGIBLE but got: {failures}"
    assert failures == []


def test_eligible_auth_01_and_auth_02_analogue() -> None:
    """PE-D-01 (codex) and PE-D-02 (claude) — both depend on nothing, opposite engines."""
    plan_pes = _plan_pes_dual()
    eligible, failures = check_eligibility("PE-D-01", "PE-D-02", plan_pes)
    assert eligible, f"Expected ELIGIBLE but got: {failures}"


def test_eligible_symmetric() -> None:
    """Eligibility is symmetric: (A, B) == (B, A)."""
    plan_pes = _plan_pes_parallel()
    e1, _ = check_eligibility("PE-P-01", "PE-P-02", plan_pes)
    e2, _ = check_eligibility("PE-P-02", "PE-P-01", plan_pes)
    assert e1 == e2


# ---------------------------------------------------------------------------
# AC-2 — INELIGIBLE cases
# ---------------------------------------------------------------------------


def test_ineligible_direct_dependency_a_depends_on_b() -> None:
    plan_pes = _plan_pes_parallel()
    eligible, failures = check_eligibility("PE-P-03", "PE-P-01", plan_pes)
    assert not eligible
    assert any("PE-P-03" in f and "PE-P-01" in f for f in failures)


def test_ineligible_direct_dependency_b_depends_on_a() -> None:
    plan_pes = _plan_pes_parallel()
    eligible, failures = check_eligibility("PE-P-01", "PE-P-03", plan_pes)
    assert not eligible
    assert any("PE-P-03" in f and "PE-P-01" in f for f in failures)


def test_ineligible_transitive_dependency() -> None:
    """PE-P-05 depends transitively on PE-P-01 (via PE-P-03)."""
    plan_pes = _plan_pes_parallel()
    eligible, failures = check_eligibility("PE-P-01", "PE-P-05", plan_pes)
    assert not eligible
    assert any("transitively" in f for f in failures)


def test_ineligible_same_engine() -> None:
    """PE-P-01 (codex) and PE-P-00 (codex) — same implementer engine."""
    plan_pes = _plan_pes_parallel()
    eligible, failures = check_eligibility("PE-P-00", "PE-P-01", plan_pes)
    assert not eligible
    assert any("same implementer engine" in f for f in failures)


def test_ineligible_pe_not_in_plan() -> None:
    plan_pes = _plan_pes_parallel()
    eligible, failures = check_eligibility("PE-GHOST-99", "PE-P-01", plan_pes)
    assert not eligible
    assert any("not found" in f for f in failures)


def test_ineligible_both_same_engine_different_from_dependency() -> None:
    """PE-P-03 and PE-P-04 both depend on PE-P-01; PE-P-03=codex, PE-P-04=claude — ELIGIBLE."""
    plan_pes = _plan_pes_parallel()
    eligible, failures = check_eligibility("PE-P-03", "PE-P-04", plan_pes)
    assert eligible, f"Expected ELIGIBLE but got: {failures}"


# ---------------------------------------------------------------------------
# AC-3 — Sequencer dual dispatch
# ---------------------------------------------------------------------------

CURRENT_PE_DUAL_READY = """\
# Current PE Assignment

## Release context

| Field          | Value |
|----------------|-------|
| Release        | Test Release |
| Base branch    | main |
| Plan file      | plan.md |
| Plan location  | repo root |

## Current PE

| Field   | Value |
|---------|-------|
| PE      | PE-D-00 |
| Branch  | feature/pe-d-00-prerequisite |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Validator   |
| Claude Code | Implementer |

## Active PE Registry

| PE-ID  | Domain | Implementer-agentId  | Validator-agentId | Branch                    | Status        | Last-updated |
|--------|--------|----------------------|-------------------|---------------------------|---------------|--------------|
| PE-D-00 | infra | infra-impl-claude    | infra-val-codex   | feature/pe-d-00-prerequisite | implementing | 2026-04-10  |

| Chore ID    | Description                  | Date       |
|-------------|------------------------------|------------|
| PM-CHORE-01 | Opened PE-D-00.              | 2026-04-10 |
"""


def test_sequencer_dual_dispatch_when_two_ready(tmp_path: Path) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    plan_file = tmp_path / "plan.md"
    current_pe.write_text(CURRENT_PE_DUAL_READY, encoding="utf-8")
    plan_file.write_text(PLAN_DUAL, encoding="utf-8")

    decision = advance_current_pe(current_pe)

    assert decision.action == "dual_advance"
    assert decision.next_pe == "PE-D-01"
    assert decision.track_b_pe == "PE-D-02"
    assert decision.track_b_branch is not None
    assert "pe-d-02" in decision.track_b_branch
    assert decision.implementer_engine == "codex"
    assert decision.track_b_implementer_engine == "claude"
    assert decision.updated_content is not None
    assert "Track A PE" in decision.updated_content
    assert "Track B PE" in decision.updated_content
    assert "PE-D-01" in decision.updated_content
    assert "PE-D-02" in decision.updated_content


def test_sequencer_single_dispatch_when_only_one_ready(tmp_path: Path) -> None:
    """When PE-P-00 merges, only PE-P-01 and PE-P-02 are ready; PE-P-01(codex) + PE-P-02(claude)
    are both ready and eligible — so dual dispatch is expected. Verify single dispatch when
    we use a plan where only one PE is ready."""
    plan_single_ready = """\
### PE-S-00 · Only PE

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | — |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

---

### PE-S-01 · Blocked PE

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-S-00 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |
"""
    current_pe_body = """\
# Current PE Assignment

## Release context

| Field          | Value |
|----------------|-------|
| Release        | Test |
| Base branch    | main |
| Plan file      | plan.md |
| Plan location  | repo root |

## Current PE

| Field   | Value |
|---------|-------|
| PE      | PE-S-00 |
| Branch  | feature/pe-s-00-only-pe |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |

## Active PE Registry

| PE-ID   | Domain | Implementer-agentId | Validator-agentId | Branch                | Status       | Last-updated |
|---------|--------|---------------------|-------------------|-----------------------|--------------|--------------|
| PE-S-00 | infra  | infra-impl-codex    | infra-val-claude  | feature/pe-s-00-only-pe | implementing | 2026-04-10  |

| Chore ID    | Description      | Date       |
|-------------|------------------|------------|
| PM-CHORE-01 | Opened PE-S-00.  | 2026-04-10 |
"""
    current_pe = tmp_path / "CURRENT_PE.md"
    plan_file = tmp_path / "plan.md"
    current_pe.write_text(current_pe_body, encoding="utf-8")
    plan_file.write_text(plan_single_ready, encoding="utf-8")

    decision = advance_current_pe(current_pe)

    assert decision.action == "advance"
    assert decision.next_pe == "PE-S-01"
    assert decision.track_b_pe is None


# ---------------------------------------------------------------------------
# AC-4 — check_current_pe dual-track validation
# ---------------------------------------------------------------------------

CHECK_CURRENT_PE_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "check_current_pe.py"
)


def _load_check_current_pe():
    spec = importlib.util.spec_from_file_location(
        "check_current_pe", CHECK_CURRENT_PE_SCRIPT
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CCP = _load_check_current_pe()

VALID_DUAL_TRACK_CURRENT_PE = """\
# Current PE Assignment

## Release context

| Field          | Value                               |
|----------------|-------------------------------------|
| Release        | Test Release                        |
| Base branch    | main                                |
| Plan file      | plan.md                             |
| Plan location  | repo root                           |

## Current PE

| Field          | Value                                              |
|----------------|----------------------------------------------------|
| Track A PE     | PE-D-01                                            |
| Track A Branch | feature/pe-d-01-track-a-candidate                  |
| Track B PE     | PE-D-02                                            |
| Track B Branch | feature/pe-d-02-track-b-candidate                  |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |

## Active PE Registry

| PE-ID   | Domain | Implementer-agentId  | Validator-agentId | Branch                               | Status       | Last-updated |
|---------|--------|----------------------|-------------------|--------------------------------------|--------------|--------------|
| PE-D-00 | infra  | infra-impl-claude    | infra-val-codex   | feature/pe-d-00-prerequisite         | merged       | 2026-04-10   |
| PE-D-01 | infra  | infra-impl-codex     | infra-val-claude  | feature/pe-d-01-track-a-candidate    | implementing | 2026-04-10   |
| PE-D-02 | infra  | infra-impl-claude    | infra-val-codex   | feature/pe-d-02-track-b-candidate    | implementing | 2026-04-10   |
"""


def test_check_current_pe_valid_dual_track(tmp_path, monkeypatch, capsys) -> None:
    path = tmp_path / "CURRENT_PE.md"
    path.write_text(VALID_DUAL_TRACK_CURRENT_PE, encoding="utf-8")
    # Write a minimal plan file so eligibility check can run
    plan = tmp_path / "plan.md"
    plan.write_text(PLAN_DUAL, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    rc = CCP.main()
    assert rc == 0
    out = capsys.readouterr().out
    assert "dual-track" in out.lower()


def test_check_current_pe_dual_track_honours_plan_location(
    tmp_path, monkeypatch, capsys
) -> None:
    docs_dir = tmp_path / "docs" / "plans"
    docs_dir.mkdir(parents=True)
    path = tmp_path / "CURRENT_PE.md"
    path.write_text(
        VALID_DUAL_TRACK_CURRENT_PE.replace(
            "| Plan location  | repo root                           |",
            "| Plan location  | docs/plans                          |",
        ),
        encoding="utf-8",
    )
    (docs_dir / "plan.md").write_text(PLAN_DUAL, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    rc = CCP.main()
    assert rc == 0
    out = capsys.readouterr().out
    assert "dual-track" in out.lower()


def test_check_current_pe_dual_track_missing_field(tmp_path, monkeypatch) -> None:
    content = VALID_DUAL_TRACK_CURRENT_PE.replace(
        "| Track B PE     | PE-D-02", "| Track B PE     |"
    )
    path = tmp_path / "CURRENT_PE.md"
    path.write_text(content, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert CCP.main() == 1


def test_check_current_pe_dual_track_same_pe(tmp_path, monkeypatch) -> None:
    content = VALID_DUAL_TRACK_CURRENT_PE.replace(
        "| Track B PE     | PE-D-02",
        "| Track B PE     | PE-D-01",
    ).replace(
        "| Track B Branch | feature/pe-d-02-track-b-candidate",
        "| Track B Branch | feature/pe-d-01-track-a-candidate",
    )
    path = tmp_path / "CURRENT_PE.md"
    path.write_text(content, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert CCP.main() == 1


def test_check_current_pe_dual_track_same_engine(tmp_path, monkeypatch) -> None:
    """Both tracks with codex implementer should fail."""
    content = VALID_DUAL_TRACK_CURRENT_PE.replace(
        "| PE-D-02 | infra  | infra-impl-claude    | infra-val-codex   |",
        "| PE-D-02 | infra  | infra-impl-codex     | infra-val-claude  |",
    )
    path = tmp_path / "CURRENT_PE.md"
    path.write_text(content, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert CCP.main() == 1


def test_check_current_pe_dual_track_registry_row_missing(
    tmp_path, monkeypatch
) -> None:
    content = VALID_DUAL_TRACK_CURRENT_PE.replace(
        "| PE-D-02 | infra  | infra-impl-claude    | infra-val-codex   | feature/pe-d-02-track-b-candidate    | implementing | 2026-04-10   |\n",
        "",
    )
    path = tmp_path / "CURRENT_PE.md"
    path.write_text(content, encoding="utf-8")
    monkeypatch.setenv("CURRENT_PE_PATH", str(path))
    assert CCP.main() == 1


# ---------------------------------------------------------------------------
# AC-5 — Track A closes, Track B remains active
# ---------------------------------------------------------------------------

DUAL_TRACK_CURRENT_PE_FOR_SEQUENCER = """\
# Current PE Assignment

## Release context

| Field          | Value |
|----------------|-------|
| Release        | Test Release |
| Base branch    | main |
| Plan file      | plan.md |
| Plan location  | repo root |

## Current PE

| Field          | Value                                              |
|----------------|----------------------------------------------------|
| Track A PE     | PE-D-01                                            |
| Track A Branch | feature/pe-d-01-track-a-candidate                  |
| Track B PE     | PE-D-02                                            |
| Track B Branch | feature/pe-d-02-track-b-candidate                  |

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |

## Active PE Registry

| PE-ID   | Domain | Implementer-agentId  | Validator-agentId | Branch                               | Status       | Last-updated |
|---------|--------|----------------------|-------------------|--------------------------------------|--------------|--------------|
| PE-D-00 | infra  | infra-impl-claude    | infra-val-codex   | feature/pe-d-00-prerequisite         | merged       | 2026-04-10   |
| PE-D-01 | infra  | infra-impl-codex     | infra-val-claude  | feature/pe-d-01-track-a-candidate    | implementing | 2026-04-10   |
| PE-D-02 | infra  | infra-impl-claude    | infra-val-codex   | feature/pe-d-02-track-b-candidate    | implementing | 2026-04-10   |

| Chore ID    | Description               | Date       |
|-------------|---------------------------|------------|
| PM-CHORE-01 | Dual dispatch: D-01, D-02 | 2026-04-10 |
"""


def test_track_a_close_leaves_track_b_active(tmp_path: Path) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    plan_file = tmp_path / "plan.md"
    current_pe.write_text(DUAL_TRACK_CURRENT_PE_FOR_SEQUENCER, encoding="utf-8")
    plan_file.write_text(PLAN_DUAL, encoding="utf-8")

    decision = advance_current_pe(current_pe, merged_pe="PE-D-01")

    assert decision.action == "track_a_closed"
    assert decision.merged_pe == "PE-D-01"
    assert decision.next_pe == "PE-D-02"
    assert decision.next_branch == "feature/pe-d-02-track-b-candidate"
    assert decision.updated_content is not None
    # Track B should be the single active PE — no dual-track fields in updated content
    assert "Track A PE" not in decision.updated_content
    assert "Track B PE" not in decision.updated_content
    assert "PE-D-02" in decision.updated_content
    # Track A should be marked merged in the registry
    assert "PE-D-01" in decision.updated_content
    assert "merged" in decision.updated_content


def test_track_a_close_updates_roles_for_track_b(tmp_path: Path) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    plan_file = tmp_path / "plan.md"
    current_pe.write_text(DUAL_TRACK_CURRENT_PE_FOR_SEQUENCER, encoding="utf-8")
    plan_file.write_text(PLAN_DUAL, encoding="utf-8")

    decision = advance_current_pe(current_pe, merged_pe="PE-D-01")

    # Track B implementer is claude → Claude Code should be Implementer
    assert decision.implementer_engine == "claude"
    assert "Claude Code | Implementer" in decision.updated_content


def test_track_a_close_skips_when_merged_branch_is_not_track_a(tmp_path: Path) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    plan_file = tmp_path / "plan.md"
    current_pe.write_text(DUAL_TRACK_CURRENT_PE_FOR_SEQUENCER, encoding="utf-8")
    plan_file.write_text(PLAN_DUAL, encoding="utf-8")

    decision = advance_current_pe(
        current_pe,
        merged_pe="PE-D-01",
        merged_branch="feature/pe-d-02-track-b-candidate",
    )

    assert decision.action == "skip"
    assert decision.updated_content is None
    assert "does not match Track A branch" in decision.reason


def test_track_a_close_wrong_pe_raises(tmp_path: Path) -> None:
    current_pe = tmp_path / "CURRENT_PE.md"
    plan_file = tmp_path / "plan.md"
    current_pe.write_text(DUAL_TRACK_CURRENT_PE_FOR_SEQUENCER, encoding="utf-8")
    plan_file.write_text(PLAN_DUAL, encoding="utf-8")

    from scripts.pe_sequencer import SequencerError

    try:
        advance_current_pe(current_pe, merged_pe="PE-D-99")
        assert False, "Expected SequencerError"
    except SequencerError as exc:
        assert "Track A" in str(exc)


def test_pe_sequencer_workflow_persists_dual_track_actions() -> None:
    workflow_text = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "pe-sequencer.yml"
    ).read_text(encoding="utf-8")
    assert "contains('advance,dual_advance,track_a_closed'" in workflow_text


# ---------------------------------------------------------------------------
# AC-6 — runtime/config sources cover the parallel-track eligibility rules
# ---------------------------------------------------------------------------

CHECK_ELIGIBILITY_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "check_parallel_eligibility.py"
)
AUTOMATION_PLAN_ARCHIVE = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "_archive"
    / "2026-04"
    / "ELIS_2Agent_Automation_Plan_v2_0.md"
)


def test_parallel_eligibility_script_covers_no_direct_dependency() -> None:
    text = CHECK_ELIGIBILITY_SCRIPT.read_text(encoding="utf-8")
    assert "# Direct dependency" in text
    assert "directly depends on" in text


def test_parallel_eligibility_script_covers_no_transitive_dependency() -> None:
    text = CHECK_ELIGIBILITY_SCRIPT.read_text(encoding="utf-8")
    assert "# Transitive dependency" in text
    assert "transitively depends on" in text


def test_parallel_eligibility_script_covers_opposite_engines() -> None:
    text = CHECK_ELIGIBILITY_SCRIPT.read_text(encoding="utf-8")
    assert "Different implementer engines" in text
    assert "opposite engines" in text


def test_parallel_track_rules_still_include_examples_eligible_and_ineligible() -> None:
    text = AUTOMATION_PLAN_ARCHIVE.read_text(encoding="utf-8")
    assert "ELIGIBLE" in text
    assert "INELIGIBLE" in text


def test_parallel_eligibility_script_covers_file_scope_overlap_criterion() -> None:
    plan_pes = _plan_pes_parallel()
    eligible, failures = check_eligibility("PE-P-03", "PE-P-04", plan_pes)
    assert eligible, f"Expected ELIGIBLE but got: {failures}"
    assert failures == []
