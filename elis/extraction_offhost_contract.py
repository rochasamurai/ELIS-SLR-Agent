"""Extraction off-host contract helpers for PE-SLR-07.

This module formalises that Extraction remains workflow-governed and off-host.
Local execution is explicitly unsupported for the current hardware profile.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_utc_iso() -> str:
    """Return UTC timestamp in ISO format with `Z` suffix."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class ExtractionWorkflowEnvelope:
    """Execution envelope proving extraction remains off-host and workflow-governed."""

    review_id: str
    run_id: str
    trigger_source: str
    execution_surface: str = "off-host-workflow"
    local_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if self.execution_surface != "off-host-workflow":
            raise ValueError(
                "Extraction must run on off-host workflow surfaces only "
                "(execution_surface='off-host-workflow')."
            )
        if self.local_execution_allowed:
            raise ValueError(
                "Local extraction execution is unsupported for current host."
            )
        if not self.review_id.strip():
            raise ValueError("review_id must not be blank")
        if not self.run_id.strip():
            raise ValueError("run_id must not be blank")
        if not self.trigger_source.strip():
            raise ValueError("trigger_source must not be blank")


@dataclass(frozen=True)
class ExtractionOffHostContract:
    """Stable contract for extraction input/output schemas and audit artefacts."""

    review_id: str
    root: Path = Path("artifacts/extraction_offhost")

    def review_root(self) -> Path:
        return self.root / self.review_id

    def audit_dir(self) -> Path:
        return self.review_root() / "audit"

    def envelope_path(self) -> Path:
        return self.audit_dir() / "extraction_workflow_envelope.json"

    def evidence_bundle_path(self) -> Path:
        return self.audit_dir() / "extraction_evidence_bundle.json"

    def input_schema_path(self) -> Path:
        return Path("schemas/appendix_b.schema.json")

    def output_schema_path(self) -> Path:
        return Path("schemas/appendix_c.schema.json")

    def output_rows_path(self) -> Path:
        return Path("json_jsonl/ELIS_Appendix_C_DataExtraction_rows.json")

    def ensure_dirs(self) -> None:
        self.audit_dir().mkdir(parents=True, exist_ok=True)


def assert_local_extraction_unsupported() -> None:
    """Always fail for local extraction execution.

    PE-SLR-07 explicitly keeps Extraction off-host for current hardware.
    """
    raise RuntimeError(
        "Local extraction execution is unsupported on current hardware. "
        "Use off-host workflow execution only."
    )


def build_extraction_evidence_bundle(
    *,
    envelope: ExtractionWorkflowEnvelope,
    contract: ExtractionOffHostContract,
    output_rows: list[dict[str, Any]],
    commit_sha: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build an auditable and reproducible extraction evidence bundle."""
    output_record_ids = sorted(
        str(row.get("record_id", "")).strip()
        for row in output_rows
        if str(row.get("record_id", "")).strip()
    )
    output_digest = hashlib.sha256(
        _canonical_json(output_rows).encode("utf-8")
    ).hexdigest()

    bundle = {
        "schema_version": "1.0",
        "review_id": envelope.review_id,
        "run_id": envelope.run_id,
        "trigger_source": envelope.trigger_source,
        "execution_surface": envelope.execution_surface,
        "local_execution_allowed": envelope.local_execution_allowed,
        "input_schema_path": contract.input_schema_path().as_posix(),
        "output_schema_path": contract.output_schema_path().as_posix(),
        "output_rows_path": contract.output_rows_path().as_posix(),
        "output_record_count": len(output_rows),
        "output_record_ids": output_record_ids,
        "output_rows_sha256": output_digest,
        "commit_sha": commit_sha,
        "generated_at": generated_at or now_utc_iso(),
    }
    return bundle


def persist_extraction_contract_artefacts(
    *,
    envelope: ExtractionWorkflowEnvelope,
    contract: ExtractionOffHostContract,
    output_rows: list[dict[str, Any]],
    commit_sha: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Persist workflow envelope + evidence bundle JSON artefacts."""
    contract.ensure_dirs()
    bundle = build_extraction_evidence_bundle(
        envelope=envelope,
        contract=contract,
        output_rows=output_rows,
        commit_sha=commit_sha,
        generated_at=generated_at,
    )
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
    contract.evidence_bundle_path().write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return bundle
