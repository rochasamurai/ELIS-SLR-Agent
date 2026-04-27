"""Workload placement policy for PE-SLR-09.

This module enforces host-capacity safeguards so local SLR execution remains
bounded on ``elis-server`` and Extraction/Synthesis cannot be promoted to local
execution surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkloadPlacementPolicy:
    """Policy declaring local-safe and off-host-only workload classes."""

    policy_version: str
    max_local_concurrency: int
    local_workload_classes: tuple[str, ...]
    off_host_workload_classes: tuple[str, ...]
    throttle_guidance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.policy_version.strip():
            raise ValueError("policy_version must not be blank")
        if self.max_local_concurrency < 1:
            raise ValueError("max_local_concurrency must be at least 1")
        if not self.local_workload_classes:
            raise ValueError("local_workload_classes must not be empty")
        if not self.off_host_workload_classes:
            raise ValueError("off_host_workload_classes must not be empty")
        overlap = set(self.local_workload_classes) & set(self.off_host_workload_classes)
        if overlap:
            raise ValueError(
                "Workload classes cannot be both local and off-host: "
                + ", ".join(sorted(overlap))
            )


DEFAULT_WORKLOAD_PLACEMENT_POLICY = WorkloadPlacementPolicy(
    policy_version="1.0",
    max_local_concurrency=1,
    local_workload_classes=(
        "screening",
        "lightweight-support",
        "metadata-triage",
        "bibliometric-preanalysis",
    ),
    off_host_workload_classes=(
        "harvest",
        "extraction",
        "synthesis",
    ),
    throttle_guidance=(
        "If local queue depth exceeds max_local_concurrency, defer new local runs.",
        "If memory pressure reaches 80% or more, pause non-essential local helper runs.",
        "Keep Extraction and Synthesis pinned to off-host workflow surfaces.",
    ),
)


def report_workload_classes(
    policy: WorkloadPlacementPolicy = DEFAULT_WORKLOAD_PLACEMENT_POLICY,
) -> dict[str, object]:
    """Return PM-facing workload class report (local vs off-host)."""
    return {
        "policy_version": policy.policy_version,
        "max_local_concurrency": policy.max_local_concurrency,
        "local_workload_classes": list(policy.local_workload_classes),
        "off_host_workload_classes": list(policy.off_host_workload_classes),
        "throttle_guidance": list(policy.throttle_guidance),
    }


def enforce_local_workload_request(
    workload_class: str,
    *,
    requested_concurrency: int = 1,
    current_local_jobs: int = 0,
    policy: WorkloadPlacementPolicy = DEFAULT_WORKLOAD_PLACEMENT_POLICY,
) -> dict[str, object]:
    """Enforce local placement constraints and return scheduling decision."""
    if requested_concurrency < 1:
        raise ValueError("requested_concurrency must be at least 1")
    if current_local_jobs < 0:
        raise ValueError("current_local_jobs must not be negative")

    candidate = workload_class.strip().lower()
    if candidate in policy.off_host_workload_classes:
        raise RuntimeError(
            f"'{candidate}' is off-host only and cannot run locally on elis-server."
        )
    if candidate not in policy.local_workload_classes:
        raise ValueError(
            f"Unknown workload class '{candidate}'. Must be declared in policy."
        )

    available_slots = max(policy.max_local_concurrency - current_local_jobs, 0)
    if available_slots == 0:
        return {
            "allowed": False,
            "workload_class": candidate,
            "effective_concurrency": 0,
            "throttled": True,
            "reason": "local capacity reached",
            "recommended_action": "defer",
        }

    effective_concurrency = min(requested_concurrency, available_slots)
    return {
        "allowed": True,
        "workload_class": candidate,
        "effective_concurrency": effective_concurrency,
        "throttled": effective_concurrency < requested_concurrency,
        "reason": "within local capacity",
        "recommended_action": "run-now",
    }


def capacity_triggered_throttling(
    *,
    queue_depth: int,
    memory_pressure_percent: int,
    policy: WorkloadPlacementPolicy = DEFAULT_WORKLOAD_PLACEMENT_POLICY,
) -> dict[str, object]:
    """Return deterministic throttling guidance for operators."""
    if queue_depth < 0:
        raise ValueError("queue_depth must not be negative")
    if memory_pressure_percent < 0 or memory_pressure_percent > 100:
        raise ValueError("memory_pressure_percent must be in range 0..100")

    queue_overloaded = queue_depth > policy.max_local_concurrency
    memory_overloaded = memory_pressure_percent >= 80

    if queue_overloaded or memory_overloaded:
        return {
            "throttle_required": True,
            "queue_depth": queue_depth,
            "memory_pressure_percent": memory_pressure_percent,
            "guidance": list(policy.throttle_guidance),
        }

    return {
        "throttle_required": False,
        "queue_depth": queue_depth,
        "memory_pressure_percent": memory_pressure_percent,
        "guidance": [
            "Capacity within policy. Continue bounded local support workloads only."
        ],
    }


def prevent_local_promotion(
    *,
    from_workload_class: str,
    to_workload_class: str,
    policy: WorkloadPlacementPolicy = DEFAULT_WORKLOAD_PLACEMENT_POLICY,
) -> None:
    """Block promotion from local helper/screening classes to off-host classes."""
    source = from_workload_class.strip().lower()
    target = to_workload_class.strip().lower()

    if source not in policy.local_workload_classes:
        raise ValueError(
            "from_workload_class must be a declared local workload class "
            f"(got '{source}')"
        )
    if target in policy.off_host_workload_classes:
        raise RuntimeError(
            f"Promotion blocked: local '{source}' cannot promote '{target}' "
            "to local execution."
        )
