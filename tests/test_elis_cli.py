"""Tests for elis CLI entrypoint."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from elis import cli


def test_validate_without_paths_calls_legacy_main() -> None:
    """Wrapper mode should delegate to scripts.validate_json.main."""
    with patch("scripts.validate_json.main") as legacy_main:
        code = cli.main(["validate"])
    assert code == 0
    legacy_main.assert_called_once()


def test_validate_with_explicit_paths_runs_single_validation(tmp_path: Path) -> None:
    """Single-file validate mode should accept schema and data paths."""
    data_path = tmp_path / "rows.json"
    schema_path = tmp_path / "schema.json"

    data_path.write_text(
        json.dumps([{"id": "r1", "source": "test", "retrieved_at": "x"}]),
        encoding="utf-8",
    )
    schema_path.write_text(
        json.dumps(
            {
                "type": "object",
                "required": ["id"],
                "properties": {"id": {"type": "string"}},
            }
        ),
        encoding="utf-8",
    )

    code = cli.main(["validate", str(schema_path), str(data_path)])
    assert code == 0


def test_validate_rejects_partial_paths() -> None:
    """Partial custom target args should fail fast."""
    try:
        cli.main(["validate", "schemas/appendix_a.schema.json"])
    except SystemExit as exc:
        assert str(exc) == "Provide both <schema_path> and <json_path>, or neither."
    else:
        raise AssertionError("Expected SystemExit for partial validate args.")


def test_merge_calls_pipeline_merge(tmp_path: Path) -> None:
    """merge subcommand should delegate to pipeline merge runner."""
    input_path = tmp_path / "input.json"
    input_path.write_text("[]", encoding="utf-8")
    output_path = tmp_path / "out.json"
    report_path = tmp_path / "report.json"

    with patch("elis.pipeline.merge.run_merge") as run_merge:
        code = cli.main(
            [
                "merge",
                "--inputs",
                str(input_path),
                "--output",
                str(output_path),
                "--report",
                str(report_path),
            ]
        )

    assert code == 0
    run_merge.assert_called_once_with(
        [str(input_path)],
        str(output_path),
        str(report_path),
    )
