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
