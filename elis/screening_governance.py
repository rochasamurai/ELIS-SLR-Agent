"""Screening governance helpers for PE-SLR-04.

Adds provenance/rationale field enforcement, borderline-case detection,
reproducible audit bundles, and capacity/throttling policy for local screening.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Timestamp helper
# ---------------------------------------------------------------------------


def _now_utc_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


# ---------------------------------------------------------------------------
# AC-1: Screening decision with provenance and rationale fields
# ---------------------------------------------------------------------------

VALID_DECISIONS = frozenset({"included", "excluded", "borderline"})


@dataclass(frozen=True)
class ScreeningDecision:
    """A single screening decision with full provenance and rationale.

    All fields are required so no provenance or rationale is silently dropped.
    """

    record_id: str
    source_id: str
    title: str
    decision: str
    rationale: str
    decided_at: str
    reviewer: str = "automated"

    def __post_init__(self) -> None:
        if not self.record_id:
            raise ValueError("record_id must not be empty")
        if not self.source_id:
            raise ValueError("source_id must not be empty")
        if self.decision not in VALID_DECISIONS:
            raise ValueError(
                f"decision must be one of {sorted(VALID_DECISIONS)}, got {self.decision!r}"
            )
        if not self.rationale:
            raise ValueError("rationale must not be empty")
        if not self.decided_at:
            raise ValueError("decided_at must not be empty")


# ---------------------------------------------------------------------------
# AC-2: Borderline / discrepant case detection and surfacing
# ---------------------------------------------------------------------------

_BORDERLINE_MARKERS: frozenset[str] = frozenset(
    {
        "uncertain",
        "borderline",
        "ambiguous",
        "unclear",
        "inconclusive",
        "marginal",
        "review required",
        "needs review",
    }
)


def is_borderline(decision: ScreeningDecision) -> bool:
    """Return True when a decision requires explicit human review."""
    if decision.decision == "borderline":
        return True
    rationale_lower = decision.rationale.lower()
    return any(marker in rationale_lower for marker in _BORDERLINE_MARKERS)


def surface_borderline_cases(
    decisions: list[ScreeningDecision],
) -> list[ScreeningDecision]:
    """Return all decisions that require explicit human review."""
    return [d for d in decisions if is_borderline(d)]


# ---------------------------------------------------------------------------
# AC-3: Reproducible audit bundle
# ---------------------------------------------------------------------------


def generate_audit_bundle(
    review_id: str,
    decisions: list[ScreeningDecision],
    policy: "CapacityPolicy | None" = None,
) -> dict[str, Any]:
    """Return a reproducible, schema-stable audit bundle for a screening run.

    The bundle is deterministic given the same inputs: counts are computed
    from the decisions list, borderline IDs are sorted, and timestamps are
    the only time-varying field.
    """
    if policy is None:
        policy = DEFAULT_CAPACITY_POLICY

    counts: dict[str, int] = dict(Counter(d.decision for d in decisions))
    borderline = surface_borderline_cases(decisions)

    return {
        "schema_version": "1.0",
        "review_id": review_id,
        "stage": "screening-governance",
        "record_total": len(decisions),
        "decision_counts": counts,
        "borderline_count": len(borderline),
        "borderline_ids": sorted(d.record_id for d in borderline),
        "capacity_policy": {
            "max_records_per_run": policy.max_records_per_run,
            "max_records_per_batch": policy.max_records_per_batch,
            "max_concurrent_runs": policy.max_concurrent_runs,
            "min_seconds_between_runs": policy.min_seconds_between_runs,
        },
        "generated_at": _now_utc_iso(),
    }


# ---------------------------------------------------------------------------
# AC-4: Capacity / throttling policy
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CapacityPolicy:
    """Capacity and throttling rules for local screening runs.

    Attributes:
        max_records_per_run:      Hard cap on records processed in a single
                                  bounded pilot invocation.
        max_records_per_batch:    Soft cap for batch operations (e.g. bulk
                                  import from Appendix A).
        max_concurrent_runs:      Maximum parallel screening processes on
                                  elis-server (1 = serialised).
        min_seconds_between_runs: Minimum wall-clock gap between consecutive
                                  screening runs to avoid I/O contention.
    """

    max_records_per_run: int = 100
    max_records_per_batch: int = 500
    max_concurrent_runs: int = 1
    min_seconds_between_runs: int = 0

    def __post_init__(self) -> None:
        if self.max_records_per_run <= 0:
            raise ValueError("max_records_per_run must be positive")
        if self.max_records_per_batch <= 0:
            raise ValueError("max_records_per_batch must be positive")
        if self.max_concurrent_runs <= 0:
            raise ValueError("max_concurrent_runs must be positive")
        if self.min_seconds_between_runs < 0:
            raise ValueError("min_seconds_between_runs must be non-negative")


DEFAULT_CAPACITY_POLICY = CapacityPolicy()


def enforce_capacity(
    records: list[Any],
    policy: CapacityPolicy = DEFAULT_CAPACITY_POLICY,
) -> list[Any]:
    """Return records truncated to policy.max_records_per_run."""
    return records[: policy.max_records_per_run]
