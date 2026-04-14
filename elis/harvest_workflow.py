"""Harvest workflow reliability helpers for PE-SLR-02.

Provides:
  - HarvestRetryPolicy   — retry configuration (AC-3)
  - HarvestAuditEntry    — structured audit log entry (AC-1)
  - HarvestStepError     — operator-visible failure diagnostic (AC-2)
  - run_with_retry()     — execute a callable with retry semantics (AC-2, AC-3)
  - write_audit_log()    — persist audit entries for replay (AC-1)
  - package_harvest_output() — deterministic, review-scoped output manifest (AC-4)
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, TypeVar

from elis.harvest_contract import HarvestWorkflowContract

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ---------------------------------------------------------------------------
# AC-3 — Retry policy
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HarvestRetryPolicy:
    """Retry policy for harvest operations.

    Attributes:
        max_attempts: Total number of attempts (first try included).
        backoff_seconds: Wait between retries in seconds.
    """

    max_attempts: int = 3
    backoff_seconds: float = 2.0


# ---------------------------------------------------------------------------
# AC-1 — Audit log entry
# ---------------------------------------------------------------------------


@dataclass
class HarvestAuditEntry:
    """Structured audit log entry for a single harvest step.

    One entry is appended for each attempt.  ``status`` is one of:
    ``"success"``, ``"retry"``, or ``"failure"``.
    """

    timestamp: str
    review_id: str
    source: str
    step: str
    status: str
    attempt: int
    detail: str = ""
    error: str = ""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# AC-2 — Failure diagnostics
# ---------------------------------------------------------------------------


class HarvestStepError(Exception):
    """Raised when a harvest step exhausts all retry attempts.

    The string representation is the :meth:`diagnostic` message, which is
    suitable for operator-visible output (logs, Discord alerts, CI step
    summaries).
    """

    def __init__(
        self,
        *,
        review_id: str,
        source: str,
        step: str,
        attempts: int,
        cause: BaseException | None,
    ) -> None:
        self.review_id = review_id
        self.source = source
        self.step = step
        self.attempts = attempts
        self.cause = cause
        super().__init__(self.diagnostic())

    def diagnostic(self) -> str:
        """Return an operator-visible diagnostic string."""
        return (
            f"[HARVEST FAILURE] review={self.review_id!r} "
            f"source={self.source!r} step={self.step!r} "
            f"attempts={self.attempts} cause={self.cause!r}"
        )


# ---------------------------------------------------------------------------
# AC-2 + AC-3 — run_with_retry
# ---------------------------------------------------------------------------


def run_with_retry(
    fn: Callable[[], T],
    *,
    policy: HarvestRetryPolicy,
    review_id: str,
    source: str,
    step: str,
    audit_entries: list[HarvestAuditEntry],
    _sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Execute *fn* with retry semantics defined by *policy*.

    On each failed attempt a ``"retry"`` audit entry is appended and a
    warning is logged.  On the final failure a ``"failure"`` entry is
    appended and :exc:`HarvestStepError` is raised with an operator-visible
    diagnostic.

    Args:
        fn: Zero-argument callable to execute.
        policy: Retry configuration.
        review_id: Harvest review identifier (for audit and error context).
        source: Data source name (e.g. ``"crossref"``).
        step: Logical step label (e.g. ``"fetch"`` or ``"write"``).
        audit_entries: Mutable list to which entries are appended.
        _sleep: Injected sleep callable (override in tests to avoid delays).

    Returns:
        The return value of *fn* on success.

    Raises:
        HarvestStepError: When all attempts fail.
    """
    last_exc: BaseException | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            result = fn()
            audit_entries.append(
                HarvestAuditEntry(
                    timestamp=_utc_now(),
                    review_id=review_id,
                    source=source,
                    step=step,
                    status="success",
                    attempt=attempt,
                )
            )
            return result
        except Exception as exc:
            last_exc = exc
            is_final = attempt >= policy.max_attempts
            status = "failure" if is_final else "retry"
            audit_entries.append(
                HarvestAuditEntry(
                    timestamp=_utc_now(),
                    review_id=review_id,
                    source=source,
                    step=step,
                    status=status,
                    attempt=attempt,
                    error=str(exc),
                )
            )
            if is_final:
                break
            logger.warning(
                "Harvest step %r for source %r failed (attempt %d/%d): %s"
                " — retrying in %.1fs",
                step,
                source,
                attempt,
                policy.max_attempts,
                exc,
                policy.backoff_seconds,
            )
            _sleep(policy.backoff_seconds)

    raise HarvestStepError(
        review_id=review_id,
        source=source,
        step=step,
        attempts=policy.max_attempts,
        cause=last_exc,
    )


# ---------------------------------------------------------------------------
# AC-1 — write_audit_log
# ---------------------------------------------------------------------------


def write_audit_log(
    entries: list[HarvestAuditEntry],
    contract: HarvestWorkflowContract,
) -> Path:
    """Persist *entries* as a JSONL audit log in the evidence directory.

    Each line is a JSON object with stable, sorted keys, suitable for audit
    replay.  The file is written atomically (write-then-rename not needed at
    this scale; the contract directory is PE-owned).

    Returns:
        Path to the written audit log file.
    """
    target = contract.audit_log()
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(asdict(entry), sort_keys=True) for entry in entries]
    target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# AC-4 — package_harvest_output
# ---------------------------------------------------------------------------


def package_harvest_output(
    *,
    sources: list[str],
    contract: HarvestWorkflowContract,
) -> dict[str, object]:
    """Build a deterministic, review-specific output manifest.

    The manifest is reproducible: the source list is sorted and all path
    values are derived from the stable :class:`HarvestWorkflowContract`
    path methods.  Calling this function twice with the same inputs produces
    identical output.

    Args:
        sources: List of source names included in the run.
        contract: Path contract for the current review.

    Returns:
        Dict suitable for JSON serialisation as the package manifest.
    """
    sorted_sources = sorted(sources)
    return {
        "review_id": contract.review_id,
        "bundle_root": str(contract.bundle_root()),
        "sources": sorted_sources,
        "outputs": {
            source: {
                "manifest": str(contract.raw_manifest(source)),
                "raw": str(contract.raw_output(source)),
            }
            for source in sorted_sources
        },
        "canonical_manifest": str(contract.canonical_manifest()),
        "canonical_output": str(contract.canonical_output()),
        "audit_log": str(contract.audit_log()),
        "evidence": str(contract.evidence_json()),
        "merge_report": str(contract.merge_report()),
    }
