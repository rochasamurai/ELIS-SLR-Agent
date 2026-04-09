from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.plan_loader import (
    LoaderError,
    _engine,
    _make_branch_name,
    generate_current_pe,
    validate,
    validate_alternation,
    validate_dag,
    validate_first_pe_ready,
    validate_schema,
)

# ---------------------------------------------------------------------------
# Minimal valid plan fixtures
# ---------------------------------------------------------------------------

VALID_PLAN = {
    "release": "Test Release",
    "base_branch": "main",
    "pes": [
        {
            "id": "PE-TEST-01",
            "domain": "infra",
            "depends_on": [],
            "implementer": "infra-impl-codex",
            "validator": "infra-val-claude",
            "acceptance_criteria": ["AC-1: does something"],
        },
        {
            "id": "PE-TEST-02",
            "domain": "infra",
            "depends_on": ["PE-TEST-01"],
            "implementer": "infra-impl-claude",
            "validator": "infra-val-codex",
            "acceptance_criteria": ["AC-1: does something else"],
        },
    ],
}


def _plan(**overrides) -> dict:
    import copy

    p = copy.deepcopy(VALID_PLAN)
    p.update(overrides)
    return p


# ---------------------------------------------------------------------------
# validate_schema — AC-1
# ---------------------------------------------------------------------------


def test_valid_plan_passes_schema() -> None:
    validate_schema(VALID_PLAN)  # must not raise


def test_schema_missing_release_raises() -> None:
    with pytest.raises(LoaderError, match="missing required field 'release'"):
        validate_schema({**VALID_PLAN, "release": None} | {"release": None})


def test_schema_missing_top_level_field() -> None:
    bad = {k: v for k, v in VALID_PLAN.items() if k != "base_branch"}
    with pytest.raises(LoaderError, match="base_branch"):
        validate_schema(bad)


def test_schema_empty_pes_raises() -> None:
    with pytest.raises(LoaderError, match="at least one PE"):
        validate_schema({**VALID_PLAN, "pes": []})


def test_schema_pe_missing_required_field() -> None:
    bad_pe = {
        k: v for k, v in VALID_PLAN["pes"][0].items() if k != "acceptance_criteria"
    }
    with pytest.raises(LoaderError, match="acceptance_criteria"):
        validate_schema({**VALID_PLAN, "pes": [bad_pe]})


def test_schema_pe_empty_acceptance_criteria() -> None:
    bad_pe = {**VALID_PLAN["pes"][0], "acceptance_criteria": []}
    with pytest.raises(LoaderError, match="must not be empty"):
        validate_schema({**VALID_PLAN, "pes": [bad_pe]})


def test_schema_pe_empty_string_in_ac() -> None:
    bad_pe = {**VALID_PLAN["pes"][0], "acceptance_criteria": [""]}
    with pytest.raises(LoaderError, match="criterion must not be empty"):
        validate_schema({**VALID_PLAN, "pes": [bad_pe]})


def test_schema_pe_wrong_type_for_depends_on() -> None:
    bad_pe = {**VALID_PLAN["pes"][0], "depends_on": "PE-TEST-00"}
    with pytest.raises(LoaderError, match="expected array"):
        validate_schema({**VALID_PLAN, "pes": [bad_pe]})


# ---------------------------------------------------------------------------
# validate_dag — AC-2
# ---------------------------------------------------------------------------


def test_dag_valid_plan_returns_topo_order() -> None:
    order = validate_dag(VALID_PLAN["pes"])
    assert order.index("PE-TEST-01") < order.index("PE-TEST-02")


def test_dag_direct_cycle_raises() -> None:
    cyclic_pes = [
        {
            "id": "PE-CYC-01",
            "domain": "infra",
            "depends_on": ["PE-CYC-02"],
            "implementer": "infra-impl-codex",
            "validator": "infra-val-claude",
            "acceptance_criteria": ["AC-1"],
        },
        {
            "id": "PE-CYC-02",
            "domain": "infra",
            "depends_on": ["PE-CYC-01"],
            "implementer": "infra-impl-claude",
            "validator": "infra-val-codex",
            "acceptance_criteria": ["AC-1"],
        },
    ]
    with pytest.raises(LoaderError, match="cycle"):
        validate_dag(cyclic_pes)


def test_dag_three_node_cycle_raises() -> None:
    pes = [
        {
            "id": f"PE-C-0{i}",
            "domain": "infra",
            "depends_on": [f"PE-C-0{(i % 3) + 1}"],
            "implementer": "infra-impl-codex",
            "validator": "infra-val-claude",
            "acceptance_criteria": ["AC-1"],
        }
        for i in range(1, 4)
    ]
    with pytest.raises(LoaderError, match="cycle"):
        validate_dag(pes)


def test_dag_external_dependency_not_treated_as_cycle() -> None:
    pes = [
        {
            "id": "PE-EXT-01",
            "domain": "infra",
            "depends_on": ["PE-EXTERNAL-99"],  # not in this plan
            "implementer": "infra-impl-codex",
            "validator": "infra-val-claude",
            "acceptance_criteria": ["AC-1"],
        }
    ]
    order = validate_dag(pes)
    assert order == ["PE-EXT-01"]


# ---------------------------------------------------------------------------
# validate_alternation — AC-3
# ---------------------------------------------------------------------------


def test_alternation_valid_plan_passes() -> None:
    topo = validate_dag(VALID_PLAN["pes"])
    validate_alternation(VALID_PLAN["pes"], topo)  # must not raise


def test_alternation_same_engine_consecutive_raises() -> None:
    bad_pes = [
        {
            "id": "PE-ALT-01",
            "domain": "infra",
            "depends_on": [],
            "implementer": "infra-impl-codex",
            "validator": "infra-val-claude",
            "acceptance_criteria": ["AC-1"],
        },
        {
            "id": "PE-ALT-02",
            "domain": "infra",
            "depends_on": ["PE-ALT-01"],
            "implementer": "infra-impl-codex",  # same as PE-ALT-01
            "validator": "infra-val-claude",
            "acceptance_criteria": ["AC-1"],
        },
    ]
    topo = validate_dag(bad_pes)
    with pytest.raises(LoaderError, match="does not alternate"):
        validate_alternation(bad_pes, topo)


def test_alternation_same_engine_for_impl_and_val_raises() -> None:
    bad_pes = [
        {
            "id": "PE-SAME-01",
            "domain": "infra",
            "depends_on": [],
            "implementer": "infra-impl-codex",
            "validator": "infra-val-codex",  # same engine as implementer
            "acceptance_criteria": ["AC-1"],
        }
    ]
    topo = validate_dag(bad_pes)
    with pytest.raises(LoaderError, match="same engine"):
        validate_alternation(bad_pes, topo)


def test_alternation_different_domains_independent() -> None:
    # codex → codex is fine when they are in different domains.
    pes = [
        {
            "id": "PE-DOM-01",
            "domain": "infra",
            "depends_on": [],
            "implementer": "infra-impl-codex",
            "validator": "infra-val-claude",
            "acceptance_criteria": ["AC-1"],
        },
        {
            "id": "PE-DOM-02",
            "domain": "slr",  # different domain
            "depends_on": [],
            "implementer": "slr-impl-codex",
            "validator": "slr-val-claude",
            "acceptance_criteria": ["AC-1"],
        },
    ]
    topo = validate_dag(pes)
    validate_alternation(pes, topo)  # must not raise


# ---------------------------------------------------------------------------
# validate_first_pe_ready — AC-4 precondition
# ---------------------------------------------------------------------------


def test_first_pe_ready_no_deps() -> None:
    topo = validate_dag(VALID_PLAN["pes"])
    first = validate_first_pe_ready(VALID_PLAN["pes"], topo, set())
    assert first == "PE-TEST-01"


def test_first_pe_ready_with_already_merged() -> None:
    first = validate_first_pe_ready(
        VALID_PLAN["pes"],
        ["PE-TEST-01", "PE-TEST-02"],
        {"PE-TEST-01"},
    )
    assert first == "PE-TEST-02"


def test_first_pe_ready_all_blocked_raises() -> None:
    pes = [
        {
            "id": "PE-BLK-01",
            "domain": "infra",
            "depends_on": ["PE-MISSING-99"],
            "implementer": "infra-impl-codex",
            "validator": "infra-val-claude",
            "acceptance_criteria": ["AC-1"],
        }
    ]
    with pytest.raises(LoaderError, match="No PE is ready"):
        validate_first_pe_ready(pes, ["PE-BLK-01"], set())


# ---------------------------------------------------------------------------
# validate() — integration
# ---------------------------------------------------------------------------


def test_validate_returns_topo_and_first_pe() -> None:
    topo, first = validate(VALID_PLAN)
    assert first == "PE-TEST-01"
    assert topo[0] == "PE-TEST-01"


def test_validate_exits_1_on_cycle(capsys) -> None:
    """Full validate() raises LoaderError for cyclic plan."""
    cyclic = {
        **VALID_PLAN,
        "pes": [
            {
                "id": "PE-CYC-01",
                "domain": "infra",
                "depends_on": ["PE-CYC-02"],
                "implementer": "infra-impl-codex",
                "validator": "infra-val-claude",
                "acceptance_criteria": ["AC-1"],
            },
            {
                "id": "PE-CYC-02",
                "domain": "infra",
                "depends_on": ["PE-CYC-01"],
                "implementer": "infra-impl-claude",
                "validator": "infra-val-codex",
                "acceptance_criteria": ["AC-1"],
            },
        ],
    }
    with pytest.raises(LoaderError, match="cycle"):
        validate(cyclic)


# ---------------------------------------------------------------------------
# generate_current_pe — AC-4
# ---------------------------------------------------------------------------


def test_generate_current_pe_contains_first_pe() -> None:
    _, first = validate(VALID_PLAN)
    content = generate_current_pe(VALID_PLAN, first, "2026-04-09")
    assert "PE-TEST-01" in content
    assert "Test Release" in content
    assert "main" in content
    assert "2026-04-09" in content


def test_generate_current_pe_roles_codex_implementer() -> None:
    _, first = validate(VALID_PLAN)
    content = generate_current_pe(VALID_PLAN, first, "2026-04-09")
    assert "CODEX       | Implementer" in content
    assert "Claude Code | Validator" in content


def test_generate_current_pe_roles_claude_implementer() -> None:
    plan = {
        **VALID_PLAN,
        "pes": [
            {
                "id": "PE-CL-01",
                "domain": "infra",
                "depends_on": [],
                "implementer": "infra-impl-claude",
                "validator": "infra-val-codex",
                "acceptance_criteria": ["AC-1"],
            }
        ],
    }
    _, first = validate(plan)
    content = generate_current_pe(plan, first, "2026-04-09")
    assert "CODEX       | Validator" in content
    assert "Claude Code | Implementer" in content


def test_generate_current_pe_written_to_file(tmp_path: Path) -> None:
    import subprocess
    import sys

    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(VALID_PLAN), encoding="utf-8")
    output = tmp_path / "CURRENT_PE.md"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.plan_loader",
            str(plan_file),
            "--write-current-pe",
            str(output),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    content = output.read_text(encoding="utf-8")
    assert "PE-TEST-01" in content


# ---------------------------------------------------------------------------
# CLI — exit codes
# ---------------------------------------------------------------------------


def test_cli_valid_plan_exits_0(tmp_path: Path) -> None:
    import subprocess
    import sys

    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(VALID_PLAN), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.plan_loader", str(plan_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "VALID" in result.stdout


def test_cli_invalid_plan_exits_1(tmp_path: Path) -> None:
    import subprocess
    import sys

    bad_plan = {"release": "Test", "base_branch": "main", "pes": []}
    plan_file = tmp_path / "bad.json"
    plan_file.write_text(json.dumps(bad_plan), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.plan_loader", str(plan_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "INVALID" in result.stderr


def test_cli_cycle_exits_1_with_diagram(tmp_path: Path) -> None:
    import subprocess
    import sys

    cyclic = {
        **VALID_PLAN,
        "pes": [
            {
                "id": "PE-CYC-01",
                "domain": "infra",
                "depends_on": ["PE-CYC-02"],
                "implementer": "infra-impl-codex",
                "validator": "infra-val-claude",
                "acceptance_criteria": ["AC-1"],
            },
            {
                "id": "PE-CYC-02",
                "domain": "infra",
                "depends_on": ["PE-CYC-01"],
                "implementer": "infra-impl-claude",
                "validator": "infra-val-codex",
                "acceptance_criteria": ["AC-1"],
            },
        ],
    }
    plan_file = tmp_path / "cyclic.json"
    plan_file.write_text(json.dumps(cyclic), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.plan_loader", str(plan_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "cycle" in result.stderr.lower()


def test_cli_alternation_violation_exits_1(tmp_path: Path) -> None:
    import subprocess
    import sys

    bad = {
        **VALID_PLAN,
        "pes": [
            {
                "id": "PE-ALT-01",
                "domain": "infra",
                "depends_on": [],
                "implementer": "infra-impl-codex",
                "validator": "infra-val-claude",
                "acceptance_criteria": ["AC-1"],
            },
            {
                "id": "PE-ALT-02",
                "domain": "infra",
                "depends_on": ["PE-ALT-01"],
                "implementer": "infra-impl-codex",
                "validator": "infra-val-claude",
                "acceptance_criteria": ["AC-1"],
            },
        ],
    }
    plan_file = tmp_path / "bad_alt.json"
    plan_file.write_text(json.dumps(bad), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.plan_loader", str(plan_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "alternate" in result.stderr.lower()


def test_cli_json_flag(tmp_path: Path) -> None:
    import subprocess
    import sys

    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(VALID_PLAN), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.plan_loader", str(plan_file), "--json"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["valid"] is True
    assert data["first_pe"] == "PE-TEST-01"
    assert data["pe_count"] == 2


# ---------------------------------------------------------------------------
# _engine helper
# ---------------------------------------------------------------------------


def test_engine_codex() -> None:
    assert _engine("infra-impl-codex") == "codex"


def test_engine_claude() -> None:
    assert _engine("infra-val-claude") == "claude"


def test_engine_unknown_raises() -> None:
    with pytest.raises(LoaderError, match="Cannot infer engine"):
        _engine("unknown-agent")


# ---------------------------------------------------------------------------
# _make_branch_name helper
# ---------------------------------------------------------------------------


def test_make_branch_name_no_title() -> None:
    assert _make_branch_name("PE-AUTO-09") == "feature/pe-auto-09"


def test_make_branch_name_with_title() -> None:
    name = _make_branch_name("PE-AUTO-09", "Plan Loader New Plan")
    assert name.startswith("feature/pe-auto-09-")
    assert "plan" in name
