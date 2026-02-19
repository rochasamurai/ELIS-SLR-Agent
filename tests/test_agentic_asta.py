"""Tests for PE5 ASTA sidecar integration wrappers."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from elis.agentic import asta


def test_run_discover_writes_under_runs_sidecar_default(tmp_path: Path) -> None:
    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.search_candidates.return_value = [{"title": "Candidate A"}]

        with patch("elis.agentic.asta._run_dir", return_value=tmp_path / "runsidecar"):
            out = asta.run_discover(
                query="electoral integrity",
                run_id="r100",
                output=None,
                config_path="DOES_NOT_EXIST.yml",
                limit=3,
            )

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["mode"] == "discover"
    assert payload["run_id"] == "r100"
    assert payload["candidate_count"] == 1
    assert out.parent == tmp_path / "runsidecar"


def test_run_enrich_outputs_jsonl_with_validated_spans(tmp_path: Path) -> None:
    input_path = tmp_path / "input.json"
    input_path.write_text(
        json.dumps(
            [
                {
                    "_meta": True,
                    "protocol_version": "x",
                },
                {
                    "id": "r1",
                    "title": "Secure e-voting systems",
                    "abstract": "Includes auditability evidence.",
                    "asta_id": "paper-1",
                },
            ]
        ),
        encoding="utf-8",
    )

    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.find_snippets.return_value = [
            {"snippet_text": "Secure e-voting systems"},
            {"snippet_text": "not present"},
        ]

        out = asta.run_enrich(
            input_path=str(input_path),
            run_id="r200",
            output=str(tmp_path / "asta_outputs.jsonl"),
            config_path="DOES_NOT_EXIST.yml",
            limit=5,
        )

    lines = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 1
    row = lines[0]
    assert row["record_id"] == "r1"
    assert row["run_id"] == "r200"
    assert row["suggestion"] == "review"
    assert row["evidence_spans"][0]["valid"] is True
    assert row["evidence_spans"][1]["valid"] is False


def test_run_enrich_default_output_path_uses_runs_sidecar(tmp_path: Path) -> None:
    input_path = tmp_path / "input.jsonl"
    input_path.write_text(
        json.dumps({"id": "x", "title": "T", "abstract": ""}) + "\n",
        encoding="utf-8",
    )

    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.find_snippets.return_value = []

        with patch("elis.agentic.asta._run_dir", return_value=tmp_path / "runsidecar"):
            out = asta.run_enrich(
                input_path=str(input_path),
                run_id="r300",
                output=None,
                config_path="DOES_NOT_EXIST.yml",
                limit=1,
            )

    assert out == (tmp_path / "runsidecar" / "asta_outputs.jsonl")
    assert out.exists()


# ---------------------------------------------------------------------------
# Adversarial tests (Validator-added)
# ---------------------------------------------------------------------------


def test_run_discover_empty_candidates_still_writes_report(tmp_path: Path) -> None:
    """Empty candidate list: file still written with candidate_count == 0."""
    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.search_candidates.return_value = []

        out = asta.run_discover(
            query="no results query",
            run_id="r400",
            output=str(tmp_path / "report.json"),
            config_path="DOES_NOT_EXIST.yml",
            limit=10,
        )

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["candidate_count"] == 0
    assert payload["candidates"] == []
    assert out.exists()


def test_run_discover_report_has_required_keys(tmp_path: Path) -> None:
    """Discovery report must include all required schema keys."""
    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.search_candidates.return_value = [{"title": "X"}]

        out = asta.run_discover(
            query="q",
            run_id="r401",
            output=str(tmp_path / "report.json"),
            config_path="DOES_NOT_EXIST.yml",
            limit=1,
        )

    payload = json.loads(out.read_text(encoding="utf-8"))
    for key in (
        "mode",
        "policy",
        "run_id",
        "query",
        "limit",
        "candidate_count",
        "timestamp",
        "outputs_path",
        "candidates",
    ):
        assert key in payload, f"Missing required key: {key!r}"


def test_run_discover_policy_field_value(tmp_path: Path) -> None:
    """Policy field must state the ASTA advisory-only principle."""
    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.search_candidates.return_value = []

        out = asta.run_discover(
            query="q",
            run_id="r402",
            output=str(tmp_path / "report.json"),
            config_path="DOES_NOT_EXIST.yml",
            limit=1,
        )

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "ASTA proposes" in payload["policy"]


def test_run_enrich_empty_input_produces_empty_output(tmp_path: Path) -> None:
    """No records after _meta stripping → output file is empty."""
    input_path = tmp_path / "input.json"
    input_path.write_text(
        json.dumps([{"_meta": True, "protocol_version": "x"}]),
        encoding="utf-8",
    )

    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.find_snippets.return_value = []

        out = asta.run_enrich(
            input_path=str(input_path),
            run_id="r500",
            output=str(tmp_path / "out.jsonl"),
            config_path="DOES_NOT_EXIST.yml",
            limit=1,
        )

    assert out.read_text(encoding="utf-8") == ""


def test_run_enrich_record_without_id_uses_tmp_prefix(tmp_path: Path) -> None:
    """Records with no id or _stable_id get a tmp: prefixed record_id."""
    input_path = tmp_path / "input.jsonl"
    input_path.write_text(
        json.dumps({"title": "Some Paper", "abstract": "Abstract."}) + "\n",
        encoding="utf-8",
    )

    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.find_snippets.return_value = []

        out = asta.run_enrich(
            input_path=str(input_path),
            run_id="r501",
            output=str(tmp_path / "out.jsonl"),
            config_path="DOES_NOT_EXIST.yml",
            limit=1,
        )

    row = json.loads(out.read_text(encoding="utf-8").strip())
    assert row["record_id"].startswith("tmp:")


def test_run_enrich_required_sidecar_fields(tmp_path: Path) -> None:
    """Every JSONL row must have all required sidecar schema fields."""
    input_path = tmp_path / "input.jsonl"
    input_path.write_text(
        json.dumps({"id": "r1", "title": "T", "abstract": "A"}) + "\n",
        encoding="utf-8",
    )

    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.find_snippets.return_value = []

        out = asta.run_enrich(
            input_path=str(input_path),
            run_id="r502",
            output=str(tmp_path / "out.jsonl"),
            config_path="DOES_NOT_EXIST.yml",
            limit=1,
        )

    row = json.loads(out.read_text(encoding="utf-8").strip())
    for field in (
        "record_id",
        "suggestion",
        "confidence",
        "evidence_spans",
        "model_id",
        "prompt_hash",
        "run_id",
        "timestamp",
    ):
        assert field in row, f"Missing required sidecar field: {field!r}"


def test_run_enrich_confidence_with_one_valid_span(tmp_path: Path) -> None:
    """One valid span → confidence = 0.5 + 0.1 = 0.6."""
    input_path = tmp_path / "input.jsonl"
    input_path.write_text(
        json.dumps({"id": "r1", "title": "Secure voting", "abstract": ""}) + "\n",
        encoding="utf-8",
    )

    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.find_snippets.return_value = [{"snippet_text": "Secure voting"}]

        out = asta.run_enrich(
            input_path=str(input_path),
            run_id="r503",
            output=str(tmp_path / "out.jsonl"),
            config_path="DOES_NOT_EXIST.yml",
            limit=1,
        )

    row = json.loads(out.read_text(encoding="utf-8").strip())
    assert row["confidence"] == 0.6


def test_run_enrich_no_canonical_paths_written(tmp_path: Path) -> None:
    """PE5 must NOT write to json_jsonl/ or any canonical pipeline path."""
    input_path = tmp_path / "input.jsonl"
    input_path.write_text(
        json.dumps({"id": "r1", "title": "T", "abstract": ""}) + "\n",
        encoding="utf-8",
    )
    canonical = tmp_path / "json_jsonl"
    canonical.mkdir()

    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.find_snippets.return_value = []

        asta.run_enrich(
            input_path=str(input_path),
            run_id="r504",
            output=str(tmp_path / "sidecar.jsonl"),
            config_path="DOES_NOT_EXIST.yml",
            limit=1,
        )

    assert list(canonical.iterdir()) == [], "No files must be written to canonical path"


def test_run_enrich_invalid_spans_preserved_in_output(tmp_path: Path) -> None:
    """Both valid and invalid spans appear in evidence_spans — none are silently dropped."""
    input_path = tmp_path / "input.jsonl"
    input_path.write_text(
        json.dumps({"id": "r1", "title": "Auditability study", "abstract": ""}) + "\n",
        encoding="utf-8",
    )

    with patch("elis.agentic.asta.AstaMCPAdapter") as adapter_cls:
        adapter = adapter_cls.return_value
        adapter.find_snippets.return_value = [
            {"snippet_text": "auditability study"},  # valid
            {"snippet_text": "hallucinated phrase"},  # invalid
        ]

        out = asta.run_enrich(
            input_path=str(input_path),
            run_id="r505",
            output=str(tmp_path / "out.jsonl"),
            config_path="DOES_NOT_EXIST.yml",
            limit=2,
        )

    row = json.loads(out.read_text(encoding="utf-8").strip())
    spans = row["evidence_spans"]
    assert len(spans) == 2
    valid_flags = {s["text"]: s["valid"] for s in spans}
    assert valid_flags["auditability study"] is True
    assert valid_flags["hallucinated phrase"] is False


def test_asta_missing_adapter_raises_controlled_error(tmp_path: Path) -> None:
    """If adapter module is unavailable, command should fail with controlled message."""
    input_path = tmp_path / "input.jsonl"
    input_path.write_text(
        json.dumps({"id": "r1", "title": "T", "abstract": ""}) + "\n",
        encoding="utf-8",
    )

    with (
        patch("elis.agentic.asta.AstaMCPAdapter", None),
        patch(
            "elis.agentic.asta.importlib.import_module", side_effect=ModuleNotFoundError
        ),
    ):
        try:
            asta.run_enrich(
                input_path=str(input_path),
                run_id="r506",
                output=str(tmp_path / "out.jsonl"),
                config_path="DOES_NOT_EXIST.yml",
                limit=1,
            )
        except SystemExit as exc:
            assert "ASTA adapter unavailable" in str(exc)
        else:
            raise AssertionError(
                "Expected SystemExit when ASTA adapter is unavailable."
            )
