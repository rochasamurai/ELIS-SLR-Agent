"""PE-SLR-03 local screening contract tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from elis.screening_local_contract import (
    ScreeningWorkspaceContract,
    assert_non_runtime_storage,
    detect_asreview_installation,
    run_bounded_screening_pilot,
)


def _write_appendix_a(path: Path, n: int) -> None:
    rows = [
        {"_meta": True, "protocol_version": "ELIS 2025 (MVP)"},
    ]
    for idx in range(n):
        rows.append(
            {
                "id": f"rec-{idx}",
                "source_id": f"src-{idx}",
                "title": f"Candidate {idx}",
                "year": 2024,
                "language": "en",
            }
        )
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def test_contract_paths_are_review_scoped(tmp_path: Path) -> None:
    contract = ScreeningWorkspaceContract(review_id="review-123", root=tmp_path)

    assert contract.appendix_a_input() == tmp_path / "review-123" / "input" / (
        "ELIS_Appendix_A_Search_rows.json"
    )
    assert contract.appendix_b_output() == tmp_path / "review-123" / "output" / (
        "ELIS_Appendix_B_Screening_rows.json"
    )
    assert contract.pilot_report() == tmp_path / "review-123" / "audit" / (
        "screening_pilot_report.json"
    )
    assert contract.pilot_manifest() == tmp_path / "review-123" / "audit" / (
        "screening_pilot_manifest.json"
    )


def test_runtime_state_storage_is_rejected() -> None:
    bad = Path(".openclaw") / "agents" / "pm" / "screening.json"
    try:
        assert_non_runtime_storage(bad)
    except ValueError as exc:
        assert "outside runtime state directories" in str(exc)
    else:
        raise AssertionError("Runtime-state path must be rejected")


def test_asreview_detection_accepts_python_module_without_cli() -> None:
    with (
        patch("subprocess.run", side_effect=FileNotFoundError),
        patch("importlib.import_module") as mocked_import,
    ):
        mocked_import.return_value = type("Dummy", (), {"__version__": "0.0"})()
        result = detect_asreview_installation()
    assert result["installed"] is True
    assert result["python_module_available"] is True


def test_asreview_detection_reports_missing() -> None:
    with (
        patch("subprocess.run", side_effect=FileNotFoundError),
        patch("importlib.import_module", side_effect=ModuleNotFoundError),
    ):
        result = detect_asreview_installation()
    assert result["installed"] is False
    assert result["python_module_available"] is False


def test_bounded_pilot_writes_schema_bound_auditable_outputs(tmp_path: Path) -> None:
    contract = ScreeningWorkspaceContract(review_id="review-xyz", root=tmp_path)
    appendix_a = tmp_path / "appendix_a_input.json"
    _write_appendix_a(appendix_a, n=8)

    report = run_bounded_screening_pilot(
        contract=contract,
        appendix_a_path=appendix_a,
        record_cap=3,
    )

    output_payload = json.loads(
        contract.appendix_b_output().read_text(encoding="utf-8")
    )
    assert len(output_payload) == 3
    assert all(
        "decision" in row and row["decision"] == "included" for row in output_payload
    )

    report_payload = json.loads(contract.pilot_report().read_text(encoding="utf-8"))
    assert report_payload["records_seen"] == 8
    assert report_payload["records_processed"] == 3
    assert report_payload["appendix_b_schema_path"] == "schemas/appendix_b.schema.json"

    manifest_payload = json.loads(
        contract.pilot_manifest().read_text(encoding="utf-8")
    )
    assert manifest_payload["stage"] == "screening"
    assert manifest_payload["pilot_mode"] == "bounded"
    assert manifest_payload["record_cap"] == 3

    assert report["stored_outside_runtime_state"] is True
