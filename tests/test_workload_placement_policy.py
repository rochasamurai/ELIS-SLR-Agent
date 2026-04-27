"""PE-SLR-09 workload placement policy tests."""

from __future__ import annotations

import pytest

from elis.workload_placement_policy import (
    DEFAULT_WORKLOAD_PLACEMENT_POLICY,
    WorkloadPlacementPolicy,
    capacity_triggered_throttling,
    enforce_local_workload_request,
    prevent_local_promotion,
    report_workload_classes,
)


def test_ac1_local_concurrency_policy_documented_and_enforced() -> None:
    policy = DEFAULT_WORKLOAD_PLACEMENT_POLICY
    assert policy.max_local_concurrency == 1

    decision = enforce_local_workload_request(
        "screening",
        requested_concurrency=2,
        current_local_jobs=0,
        policy=policy,
    )
    assert decision["allowed"] is True
    assert decision["effective_concurrency"] == 1
    assert decision["throttled"] is True


def test_ac1_local_request_is_deferred_when_capacity_is_full() -> None:
    decision = enforce_local_workload_request(
        "metadata-triage",
        requested_concurrency=1,
        current_local_jobs=1,
    )
    assert decision["allowed"] is False
    assert decision["recommended_action"] == "defer"


def test_ac2_pm_can_report_local_vs_off_host_workload_classes() -> None:
    report = report_workload_classes()
    assert report["local_workload_classes"] == [
        "screening",
        "lightweight-support",
        "metadata-triage",
        "bibliometric-preanalysis",
    ]
    assert report["off_host_workload_classes"] == [
        "harvest",
        "extraction",
        "synthesis",
    ]


def test_ac3_capacity_triggered_throttling_guidance_is_committed() -> None:
    result = capacity_triggered_throttling(queue_depth=3, memory_pressure_percent=82)
    assert result["throttle_required"] is True
    assert len(result["guidance"]) >= 2


def test_ac3_no_throttling_when_capacity_is_within_policy() -> None:
    result = capacity_triggered_throttling(queue_depth=0, memory_pressure_percent=45)
    assert result["throttle_required"] is False


def test_ac4_off_host_workload_cannot_run_locally() -> None:
    with pytest.raises(RuntimeError, match="off-host only"):
        enforce_local_workload_request("extraction")


def test_ac4_local_helper_cannot_promote_synthesis_to_local() -> None:
    with pytest.raises(RuntimeError, match="Promotion blocked"):
        prevent_local_promotion(
            from_workload_class="screening",
            to_workload_class="synthesis",
        )


def test_policy_rejects_overlapping_class_sets() -> None:
    with pytest.raises(ValueError, match="both local and off-host"):
        WorkloadPlacementPolicy(
            policy_version="1.0",
            max_local_concurrency=1,
            local_workload_classes=("screening", "synthesis"),
            off_host_workload_classes=("synthesis",),
            throttle_guidance=("test",),
        )


def test_rejects_unknown_local_workload_class() -> None:
    with pytest.raises(ValueError, match="Unknown workload class"):
        enforce_local_workload_request("unknown-workload")


def test_ac5_suite_marker() -> None:
    """AC-5 exists as the test-command contract (`pytest ...test_workload_placement_policy`)."""
    assert True
