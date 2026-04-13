"""PE-SLR-01 harvest workflow contract tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import jsonschema
import yaml

from elis import cli
from elis.harvest_contract import (
    CANONICAL_HARVEST_WORKFLOW,
    HarvestWorkflowContract,
    WORKFLOW_HARVEST_SOURCES,
    write_harvest_evidence,
)


def _load_workflow(path: str) -> dict[str, object]:
    return yaml.load(Path(path).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_contract_paths_are_review_scoped() -> None:
    contract = HarvestWorkflowContract(review_id="review-001")

    assert contract.raw_output("crossref") == Path(
        "artifacts/harvest/review-001/raw/crossref.json"
    )
    assert contract.raw_manifest("openalex") == Path(
        "artifacts/harvest/review-001/raw/openalex_manifest.json"
    )
    assert contract.canonical_output() == Path(
        "artifacts/harvest/review-001/canonical/ELIS_Appendix_A_Search_rows.json"
    )
    assert contract.evidence_json() == Path(
        "artifacts/harvest/review-001/evidence/harvest_evidence.json"
    )


def test_canonical_workflow_dispatch_contract_is_present() -> None:
    workflow = _load_workflow(CANONICAL_HARVEST_WORKFLOW)
    dispatch_inputs = workflow["on"]["workflow_dispatch"]["inputs"]

    assert "review_id" in dispatch_inputs
    assert "search_config" in dispatch_inputs
    assert "cap_per_source" in dispatch_inputs
    assert "job_result_cap" in dispatch_inputs


def test_canonical_workflow_uploads_review_scoped_harvest_bundle() -> None:
    workflow_text = Path(CANONICAL_HARVEST_WORKFLOW).read_text(encoding="utf-8")

    assert "artifacts/harvest/${{ steps.knobs.outputs.review_id }}" in workflow_text
    assert "write_harvest_evidence" in workflow_text
    assert "PUBLISHED_APPENDIX_A_MANIFEST" in workflow_text
    assert "actions/upload-artifact@v4" in workflow_text
    assert "SEARCH_CONFIG:  ${{ steps.knobs.outputs.search_config }}" in workflow_text
    assert 'src = pathlib.Path(os.environ["SEARCH_CONFIG"])' in workflow_text
    assert "PATCHED_SEARCH_CONFIG={out}" in workflow_text
    assert '--search-config "$PATCHED_SEARCH_CONFIG"' in workflow_text


def test_harvest_contract_documentation_states_off_host_boundary() -> None:
    text = Path("docs/slr/HARVEST_WORKFLOW_CONTRACT.md").read_text(encoding="utf-8")

    assert ".github/workflows/elis-agent-search.yml" in text
    assert "off `elis-server`" in text
    assert "workflow-only" in text
    assert "schemas/harvest_evidence.schema.json" in text


def test_representative_run_writes_manifest_and_evidence(tmp_path: Path) -> None:
    contract = HarvestWorkflowContract(review_id="review-xyz", root=tmp_path)
    raw_output = contract.raw_output("openalex")
    evidence_schema = json.loads(
        Path("schemas/harvest_evidence.schema.json").read_text(encoding="utf-8")
    )
    manifest_schema = json.loads(
        Path("schemas/run_manifest.schema.json").read_text(encoding="utf-8")
    )

    class _Cfg:
        queries = [{"q": "x"}]
        max_results = 5
        output_path = str(raw_output)
        config_mode = "TEST"

    class _Adapter:
        display_name = "OpenAlex"

        def harvest(self, *_args, **_kwargs):
            yield {"title": "T", "source": "openalex", "openalex_id": "W1", "doi": None}

    with (
        patch("elis.sources.config.load_harvest_config", return_value=_Cfg()),
        patch("elis.sources.get_adapter", return_value=_Adapter),
    ):
        assert cli.main(["harvest", "openalex"]) == 0

    manifest_payload = json.loads(
        contract.raw_manifest("openalex").read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=manifest_payload, schema=manifest_schema)

    evidence_path = write_harvest_evidence(
        review_id="review-xyz",
        search_config="config/searches/electoral_integrity_search.yml",
        tier="testing",
        sources=["openalex"],
        contract=contract,
    )
    evidence_payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=evidence_payload, schema=evidence_schema)
    assert evidence_payload["canonical_manifest_path"].endswith(
        "ELIS_Appendix_A_Search_rows_manifest.json"
    )


def test_supported_sources_match_contract_doc() -> None:
    text = Path("docs/slr/HARVEST_WORKFLOW_CONTRACT.md").read_text(encoding="utf-8")

    for source in WORKFLOW_HARVEST_SOURCES:
        assert source.capitalize() in text or source == "openalex"
