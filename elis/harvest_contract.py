"""Harvest workflow contract helpers for PE-SLR-01."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

CANONICAL_HARVEST_WORKFLOW = ".github/workflows/elis-agent-search.yml"
WORKFLOW_HARVEST_SOURCES = ("crossref", "openalex", "scopus")


@dataclass(frozen=True)
class HarvestWorkflowContract:
    """Stable path contract for workflow-governed harvest runs."""

    review_id: str
    root: Path = Path("artifacts/harvest")

    def bundle_root(self) -> Path:
        return self.root / self.review_id

    def raw_dir(self) -> Path:
        return self.bundle_root() / "raw"

    def canonical_dir(self) -> Path:
        return self.bundle_root() / "canonical"

    def evidence_dir(self) -> Path:
        return self.bundle_root() / "evidence"

    def raw_output(self, source: str) -> Path:
        return self.raw_dir() / f"{source}.json"

    def raw_manifest(self, source: str) -> Path:
        return self.raw_dir() / f"{source}_manifest.json"

    def canonical_output(self) -> Path:
        return self.canonical_dir() / "ELIS_Appendix_A_Search_rows.json"

    def canonical_manifest(self) -> Path:
        return self.canonical_dir() / "ELIS_Appendix_A_Search_rows_manifest.json"

    def merge_report(self) -> Path:
        return self.canonical_dir() / "merge_report.json"

    def evidence_json(self) -> Path:
        return self.evidence_dir() / "harvest_evidence.json"

    def audit_log(self) -> Path:
        return self.evidence_dir() / "harvest_audit_log.jsonl"

    def published_appendix_a(self) -> Path:
        return Path("json_jsonl/ELIS_Appendix_A_Search_rows.json")

    def published_appendix_a_manifest(self) -> Path:
        return Path("json_jsonl/ELIS_Appendix_A_Search_rows_manifest.json")


def build_harvest_evidence(
    *,
    review_id: str,
    search_config: str,
    tier: str,
    sources: Iterable[str],
    contract: HarvestWorkflowContract,
) -> dict[str, object]:
    """Build the representative harvest evidence payload."""

    source_entries = []
    for source in sources:
        source_entries.append(
            {
                "source": source,
                "output_path": str(contract.raw_output(source)),
                "manifest_path": str(contract.raw_manifest(source)),
            }
        )

    return {
        "schema_version": "1.0",
        "review_id": review_id,
        "workflow_path": CANONICAL_HARVEST_WORKFLOW,
        "search_config": search_config,
        "tier": tier,
        "sources": source_entries,
        "canonical_output_path": str(contract.canonical_output()),
        "canonical_manifest_path": str(contract.canonical_manifest()),
        "merge_report_path": str(contract.merge_report()),
    }


def write_harvest_evidence(
    *,
    review_id: str,
    search_config: str,
    tier: str,
    sources: Iterable[str],
    contract: HarvestWorkflowContract,
) -> Path:
    """Write the representative harvest evidence payload to disk."""

    payload = build_harvest_evidence(
        review_id=review_id,
        search_config=search_config,
        tier=tier,
        sources=sources,
        contract=contract,
    )
    target = contract.evidence_json()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return target
