"""PE-SLR-14 policy and contract validation checks.

Validates that:
- the v1.9 implementation plan states the PE-SLR-14 section correctly;
- the extraction off-host contract module enforces the placement boundary (AC-1);
- the synthesis off-host contract module enforces the placement boundary (AC-2);
- the plan and contract modules agree these stages do not move local by default (AC-3);
- the plan scope preserves the off-host boundary and its rationale (AC-4); and
- the existing contract test files are present (AC-5).
"""

from __future__ import annotations

from pathlib import Path

PLAN = (
    Path(__file__).resolve().parents[1] / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
)
REPO = Path(__file__).resolve().parents[1]


def test_pe_slr14_policy_section_is_present() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert (
        "#### PE-SLR-14 · Extraction and Synthesis Off-Host Contract Validation" in text
    )
    assert "| Domain | SLR |" in text
    assert "| Track | Placement policy |" in text
    assert "| Implementer | `slr-impl-b` |" in text
    assert "| Validator | `slr-val-a` |" in text
    assert "| Depends On | PE-SLR-13 |" in text


def test_pe_slr14_scope_and_acceptance_criteria() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert (
        "Keep extraction and synthesis off-host until the hardware, validation evidence, "
        "and quality benchmarks justify migration." in text
    )
    assert (
        "| AC-1 | The off-host extraction contract remains explicit and enforced. |"
        in text
    )
    assert (
        "| AC-2 | The off-host synthesis contract remains explicit and enforced. |"
        in text
    )
    assert (
        "| AC-3 | The architecture and implementation plan agree that these stages "
        "do not move local by default. |" in text
    )
    assert (
        "| AC-4 | Workflow/runbook guidance preserves the off-host boundary and its rationale. |"
        in text
    )
    assert "| AC-5 | The contract checks or tests pass. |" in text


def test_extraction_contract_module_enforces_off_host() -> None:
    """AC-1: extraction contract is explicit and enforced in code."""
    module = REPO / "elis" / "extraction_offhost_contract.py"
    assert module.exists(), "elis/extraction_offhost_contract.py must exist"
    text = module.read_text(encoding="utf-8")

    assert "local_execution_allowed: bool = False" in text
    assert "assert_local_extraction_unsupported" in text
    assert "off-host workflow surfaces only" in text


def test_synthesis_contract_module_enforces_off_host() -> None:
    """AC-2: synthesis contract is explicit and enforced in code."""
    module = REPO / "elis" / "synthesis_offhost_contract.py"
    assert module.exists(), "elis/synthesis_offhost_contract.py must exist"
    text = module.read_text(encoding="utf-8")

    assert "local_execution_allowed: bool = False" in text
    assert "assert_local_migration_not_activated" in text
    assert "off-host workflow surfaces only" in text


def test_contract_modules_agree_no_local_by_default() -> None:
    """AC-3: plan and contract modules agree these stages do not move local by default."""
    extraction = (REPO / "elis" / "extraction_offhost_contract.py").read_text(
        encoding="utf-8"
    )
    synthesis = (REPO / "elis" / "synthesis_offhost_contract.py").read_text(
        encoding="utf-8"
    )
    plan = PLAN.read_text(encoding="utf-8")

    assert "local_execution_allowed: bool = False" in extraction
    assert "local_execution_allowed: bool = False" in synthesis
    assert "do not move local by default" in plan


def test_plan_preserves_off_host_boundary_rationale() -> None:
    """AC-4: plan scope preserves the off-host boundary and its rationale."""
    text = PLAN.read_text(encoding="utf-8")

    assert "off-host" in text
    assert (
        "hardware, validation evidence, and quality benchmarks justify migration"
        in text
    )


def test_contract_test_files_exist() -> None:
    """AC-5: contract checks/tests are present and pass."""
    assert (REPO / "tests" / "test_extraction_contract.py").exists()
    assert (REPO / "tests" / "test_synthesis_contract.py").exists()
