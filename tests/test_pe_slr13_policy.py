"""PE-SLR-13 policy documentation checks.

These tests validate that the v1.9 implementation plan states the
local-first placement policy for screening and lightweight support on
elis-server, matching the active PE scope.
"""

from __future__ import annotations

from pathlib import Path


PLAN = (
    Path(__file__).resolve().parents[1] / "ELIS_MultiAgent_Implementation_Plan_v1_9.md"
)


def test_pe_slr13_policy_section_is_present() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert (
        "#### PE-SLR-13 · Screening and Lightweight Support Local-First Validation"
        in text
    )
    assert "| Domain | SLR |" in text
    assert "| Track | Placement policy |" in text
    assert "| Implementer | `slr-impl-a` |" in text
    assert "| Validator | `slr-val-b` |" in text
    assert "| Depends On | PE-SLR-12 |" in text
    assert "| Status | Planned |" in text


def test_pe_slr13_scope_and_acceptance_criteria_are_local_first() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert (
        "Validate that screening and lightweight support agents are local-first on `elis-server` "
        "and that placement follows workload shape and host capacity." in text
    )
    assert (
        "| AC-1 | Screening work is documented and validated as local-first on `elis-server`. |"
        in text
    )
    assert (
        "| AC-2 | Lightweight support agents are documented and validated as local-first on `elis-server`. |"
        in text
    )
    assert (
        "| AC-3 | The placement policy states that local execution is chosen for low-latency, "
        "persistent-context, or supervision-sensitive tasks. |" in text
    )
    assert (
        "| AC-4 | The placement policy states that off-host execution is acceptable when quality, "
        "boundedness, or scalability justify it. |" in text
    )
    assert "| AC-5 | The relevant policy checks or tests pass. |" in text
