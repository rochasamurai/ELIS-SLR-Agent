"""Synthesis off-host contract helpers for PE-SLR-08.

Synthesis remains workflow-governed and off-host. Cross-study reasoning must
preserve evidence traceability, high-impact outputs must include explicit human
review checkpoints, and local migration criteria remain documented but inactive.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_utc_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class SynthesisWorkflowEnvelope:
    """Execution envelope proving synthesis remains workflow-governed off-host."""

    review_id: str
    run_id: str
    trigger_source: str
    execution_surface: str = "off-host-workflow"
    local_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if self.execution_surface != "off-host-workflow":
            raise ValueError(
                "Synthesis must run on off-host workflow surfaces only "
                "(execution_surface='off-host-workflow')."
            )
        if self.local_execution_allowed:
            raise ValueError(
                "Local synthesis execution is unsupported for current host."
            )
        if not self.review_id.strip():
            raise ValueError("review_id must not be blank")
        if not self.run_id.strip():
            raise ValueError("run_id must not be blank")
        if not self.trigger_source.strip():
            raise ValueError("trigger_source must not be blank")


@dataclass(frozen=True)
class SynthesisReasoningTrace:
    """Traceability record linking synthesis claims to source evidence."""

    claim_id: str
    supporting_record_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    reasoning_summary: str

    def __post_init__(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("claim_id must not be blank")
        if not self.supporting_record_ids:
            raise ValueError("supporting_record_ids must not be empty")
        if not self.evidence_refs:
            raise ValueError("evidence_refs must not be empty")
        if not self.reasoning_summary.strip():
            raise ValueError("reasoning_summary must not be blank")


@dataclass(frozen=True)
class HumanReviewCheckpoint:
    """Mandatory review checkpoint for high-impact synthesis outputs."""

    checkpoint_id: str
    claim_id: str
    impact_level: str
    reviewer_required: bool = True
    status: str = "pending"

    def __post_init__(self) -> None:
        if self.impact_level not in {"high", "critical"}:
            raise ValueError("impact_level must be 'high' or 'critical'")
        if not self.reviewer_required:
            raise ValueError("High-impact checkpoints must require human review")
        if self.status not in {"pending", "approved", "rejected"}:
            raise ValueError("status must be pending/approved/rejected")


@dataclass(frozen=True)
class LocalMigrationCriteria:
    """Documented future criteria for local migration, not currently activated."""

    criteria_version: str
    prerequisites: tuple[str, ...]
    activation_requested: bool = False

    def __post_init__(self) -> None:
        if not self.criteria_version.strip():
            raise ValueError("criteria_version must not be blank")
        if not self.prerequisites:
            raise ValueError("prerequisites must not be empty")


def assert_local_migration_not_activated(criteria: LocalMigrationCriteria) -> None:
    """Enforce AC-4: migration criteria are documented but not active."""
    if criteria.activation_requested:
        raise RuntimeError(
            "Local synthesis migration criteria cannot be activated in PE-SLR-08."
        )


@dataclass(frozen=True)
class SynthesisOffHostContract:
    """Path contract for synthesis off-host audit artefacts."""

    review_id: str
    root: Path = Path("artifacts/synthesis_offhost")

    def review_root(self) -> Path:
        return self.root / self.review_id

    def audit_dir(self) -> Path:
        return self.review_root() / "audit"

    def envelope_path(self) -> Path:
        return self.audit_dir() / "synthesis_workflow_envelope.json"

    def trace_bundle_path(self) -> Path:
        return self.audit_dir() / "synthesis_trace_bundle.json"

    def checkpoints_path(self) -> Path:
        return self.audit_dir() / "synthesis_human_review_checkpoints.json"

    def extraction_input_schema_path(self) -> Path:
        return Path("schemas/appendix_c.schema.json")

    def ensure_dirs(self) -> None:
        self.audit_dir().mkdir(parents=True, exist_ok=True)


def build_synthesis_trace_bundle(
    *,
    envelope: SynthesisWorkflowEnvelope,
    contract: SynthesisOffHostContract,
    traces: list[SynthesisReasoningTrace],
    commit_sha: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build auditable bundle preserving claim-to-evidence traceability."""
    claim_ids = sorted(trace.claim_id for trace in traces)
    trace_payload = [
        {
            "claim_id": trace.claim_id,
            "supporting_record_ids": list(trace.supporting_record_ids),
            "evidence_refs": list(trace.evidence_refs),
            "reasoning_summary": trace.reasoning_summary,
        }
        for trace in traces
    ]
    digest = hashlib.sha256(_canonical_json(trace_payload).encode("utf-8")).hexdigest()
    return {
        "schema_version": "1.0",
        "review_id": envelope.review_id,
        "run_id": envelope.run_id,
        "trigger_source": envelope.trigger_source,
        "execution_surface": envelope.execution_surface,
        "local_execution_allowed": envelope.local_execution_allowed,
        "extraction_input_schema_path": contract.extraction_input_schema_path().as_posix(),
        "claim_count": len(traces),
        "claim_ids": claim_ids,
        "trace_sha256": digest,
        "commit_sha": commit_sha,
        "generated_at": generated_at or now_utc_iso(),
        "traces": trace_payload,
    }


def build_high_impact_checkpoints(
    findings: list[dict[str, Any]],
) -> list[HumanReviewCheckpoint]:
    """Create explicit human-review checkpoints for high-impact findings."""
    checkpoints: list[HumanReviewCheckpoint] = []
    for finding in findings:
        impact_level = str(finding.get("impact_level", "")).strip().lower()
        if impact_level in {"high", "critical"}:
            claim_id = str(finding.get("claim_id", "")).strip()
            checkpoints.append(
                HumanReviewCheckpoint(
                    checkpoint_id=f"chk-{claim_id or len(checkpoints)}",
                    claim_id=claim_id or "unknown-claim",
                    impact_level=impact_level,
                )
            )
    return checkpoints


def persist_synthesis_contract_artefacts(
    *,
    envelope: SynthesisWorkflowEnvelope,
    contract: SynthesisOffHostContract,
    traces: list[SynthesisReasoningTrace],
    findings: list[dict[str, Any]],
    commit_sha: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Persist envelope, trace bundle, and high-impact review checkpoints."""
    contract.ensure_dirs()
    bundle = build_synthesis_trace_bundle(
        envelope=envelope,
        contract=contract,
        traces=traces,
        commit_sha=commit_sha,
        generated_at=generated_at,
    )
    checkpoints = build_high_impact_checkpoints(findings)

    contract.envelope_path().write_text(
        json.dumps(
            {
                "review_id": envelope.review_id,
                "run_id": envelope.run_id,
                "trigger_source": envelope.trigger_source,
                "execution_surface": envelope.execution_surface,
                "local_execution_allowed": envelope.local_execution_allowed,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    contract.trace_bundle_path().write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    contract.checkpoints_path().write_text(
        json.dumps(
            [
                {
                    "checkpoint_id": c.checkpoint_id,
                    "claim_id": c.claim_id,
                    "impact_level": c.impact_level,
                    "reviewer_required": c.reviewer_required,
                    "status": c.status,
                }
                for c in checkpoints
            ],
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return bundle
