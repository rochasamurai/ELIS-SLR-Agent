"""Local support analysis helpers for PE-SLR-06.

Bibliometric clustering and discrepancy pre-analysis for bounded local
SLR datasets on elis-server. All outputs are advisory-only and carry a
runtime safeguard that prevents them from being treated as final review
decisions.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from time import monotonic
from typing import Any

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

_ADVISORY_DISCLAIMER = (
    "This output is advisory only and must not be used as a final review decision."
)

DEFAULT_MAX_RECORDS = 500


def _now_utc_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


# ---------------------------------------------------------------------------
# AC-1: Bibliometric clustering on bounded local datasets
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BibliometricCluster:
    """A group of records sharing bibliometric similarity.

    advisory_only is always True — clusters are for exploration, not decisions.
    """

    cluster_id: str
    record_ids: tuple[str, ...]
    representative_title: str
    similarity_basis: str
    advisory_only: bool = True

    def __post_init__(self) -> None:
        if not self.advisory_only:
            raise ValueError(
                "advisory_only must be True — clusters are not final decisions"
            )
        if not self.record_ids:
            raise ValueError("record_ids must not be empty")


def _title_tokens(title: str) -> frozenset[str]:
    """Return lowercased non-trivial word tokens from a title."""
    stop = {"a", "an", "the", "of", "in", "on", "at", "to", "and", "or", "for"}
    return frozenset(w for w in title.lower().split() if w not in stop and len(w) > 2)


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def cluster_by_title_similarity(
    records: list[dict[str, Any]],
    threshold: float = 0.5,
    max_records: int = DEFAULT_MAX_RECORDS,
) -> list[BibliometricCluster]:
    """Cluster records by title word-overlap similarity (Jaccard index).

    Records must have 'record_id' and 'title' keys.
    Returns advisory-only clusters in deterministic order given stable input.
    Input is bounded to max_records before processing.
    """
    bounded = records[:max_records]
    if not bounded:
        return []

    n = len(bounded)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        parent[find(x)] = find(y)

    tokens = [_title_tokens(r.get("title", "")) for r in bounded]

    for i in range(n):
        for j in range(i + 1, n):
            if _jaccard(tokens[i], tokens[j]) >= threshold:
                union(i, j)

    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)

    clusters = []
    for cluster_idx, (_, indices) in enumerate(sorted(groups.items())):
        rep_title = bounded[indices[0]].get("title", "")
        clusters.append(
            BibliometricCluster(
                cluster_id=f"cluster-{cluster_idx:04d}",
                record_ids=tuple(sorted(bounded[i]["record_id"] for i in indices)),
                representative_title=rep_title,
                similarity_basis="jaccard-title-tokens",
            )
        )

    return clusters


# ---------------------------------------------------------------------------
# AC-2 + AC-3: Discrepancy pre-analysis — advisory artefacts only
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DiscrepancyReport:
    """Advisory pre-analysis of potential duplicate or conflicting records.

    This report must not be used to exclude records from screening without
    explicit human review. Calling as_final_decision() raises unconditionally
    (AC-3 runtime safeguard).
    """

    report_id: str
    potential_duplicates: tuple[tuple[str, str], ...]
    conflict_count: int
    generated_at: str
    advisory_only: bool = True
    disclaimer: str = _ADVISORY_DISCLAIMER

    def __post_init__(self) -> None:
        if not self.advisory_only:
            raise ValueError(
                "advisory_only must be True — discrepancy reports are not final decisions"
            )

    def as_final_decision(self) -> None:
        """Raises unconditionally — AC-3 runtime safeguard."""
        raise TypeError(
            "DiscrepancyReport cannot be used as a final review decision. "
            + _ADVISORY_DISCLAIMER
        )


def detect_discrepancies(
    records: list[dict[str, Any]],
    similarity_threshold: float = 0.8,
    max_records: int = DEFAULT_MAX_RECORDS,
) -> DiscrepancyReport:
    """Identify potential duplicate records by title similarity.

    Returns an advisory-only DiscrepancyReport. Input is bounded to
    max_records before processing.
    """
    bounded = records[:max_records]
    tokens = [_title_tokens(r.get("title", "")) for r in bounded]

    pairs: list[tuple[str, str]] = []
    for i in range(len(bounded)):
        for j in range(i + 1, len(bounded)):
            if _jaccard(tokens[i], tokens[j]) >= similarity_threshold:
                id_i = bounded[i]["record_id"]
                id_j = bounded[j]["record_id"]
                pairs.append((min(id_i, id_j), max(id_i, id_j)))

    pairs.sort()

    return DiscrepancyReport(
        report_id=f"discrepancy-{_now_utc_iso()}",
        potential_duplicates=tuple(pairs),
        conflict_count=len(pairs),
        generated_at=_now_utc_iso(),
    )


# ---------------------------------------------------------------------------
# AC-4: Capacity impact measurement and documentation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CapacityReport:
    """Measured capacity impact of a local support analysis run.

    Produced by measure_capacity_impact() to satisfy AC-4: capacity impact
    must be measurable and documentable for every run on elis-server.
    """

    operation: str
    record_count: int
    elapsed_seconds: float
    max_records_used: int
    notes: str = ""


def measure_capacity_impact(
    operation_fn: Any,
    records: list[Any],
    max_records: int = DEFAULT_MAX_RECORDS,
    **kwargs: Any,
) -> tuple[Any, CapacityReport]:
    """Run operation_fn(records[:max_records], **kwargs) and return its result
    alongside a CapacityReport documenting record count and elapsed time.
    """
    bounded = records[:max_records]
    start = monotonic()
    result = operation_fn(bounded, **kwargs)
    elapsed = monotonic() - start

    report = CapacityReport(
        operation=getattr(operation_fn, "__name__", str(operation_fn)),
        record_count=len(bounded),
        elapsed_seconds=round(elapsed, 6),
        max_records_used=max_records,
    )
    return result, report
