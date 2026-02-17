"""Tests for elis CLI entrypoint."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import jsonschema

from elis import cli


def _assert_run_manifest(path: Path) -> None:
    schema = json.loads(
        Path("schemas/run_manifest.schema.json").read_text(encoding="utf-8")
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=payload, schema=schema)


def test_validate_without_paths_calls_legacy_main() -> None:
    """Wrapper mode should delegate to scripts.validate_json.main."""
    with (
        patch("scripts.validate_json.main") as legacy_main,
        patch("elis.cli.emit_run_manifest"),
    ):
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


def test_harvest_emits_manifest(tmp_path: Path) -> None:
    """harvest should emit a run manifest sidecar."""
    out = tmp_path / "harvest.json"

    class _Cfg:
        queries = [{"q": "x"}]
        max_results = 5
        output_path = str(out)
        config_mode = "test"

    class _Adapter:
        display_name = "OpenAlex"

        def harvest(self, *_args, **_kwargs):
            yield {"title": "T", "source": "openalex", "openalex_id": "W1", "doi": None}

    with (
        patch("elis.sources.config.load_harvest_config", return_value=_Cfg()),
        patch("elis.sources.get_adapter", return_value=_Adapter),
    ):
        code = cli.main(["harvest", "openalex"])

    assert code == 0
    _assert_run_manifest(tmp_path / "harvest_manifest.json")


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


def test_merge_reads_inputs_from_manifest(tmp_path: Path) -> None:
    """--from-manifest should supply merge inputs when --inputs is omitted."""
    manifest = tmp_path / "run_manifest.json"
    in_a = tmp_path / "a.json"
    in_a.write_text("[]", encoding="utf-8")
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "r1",
                "stage": "harvest",
                "source": "openalex",
                "commit_sha": "abc1234",
                "config_hash": "sha256:abc",
                "started_at": "2026-02-17T00:00:00Z",
                "finished_at": "2026-02-17T00:00:01Z",
                "record_count": 1,
                "input_paths": [str(in_a)],
                "output_path": str(in_a),
                "tool_versions": {"python": "3.11.0"},
            }
        ),
        encoding="utf-8",
    )

    with patch("elis.pipeline.merge.run_merge") as run_merge:
        code = cli.main(
            [
                "merge",
                "--from-manifest",
                str(manifest),
                "--output",
                str(tmp_path / "out.json"),
                "--report",
                str(tmp_path / "report.json"),
            ]
        )

    assert code == 0
    run_merge.assert_called_once()
    args = run_merge.call_args[0]
    assert args[0] == [str(in_a)]


def test_merge_inputs_override_from_manifest(tmp_path: Path) -> None:
    """When both are provided, --inputs must override --from-manifest."""
    in_direct = tmp_path / "direct.json"
    in_direct.write_text("[]", encoding="utf-8")
    in_manifest = tmp_path / "manifest_input.json"
    in_manifest.write_text("[]", encoding="utf-8")
    manifest = tmp_path / "run_manifest.json"
    manifest.write_text(
        json.dumps({"input_paths": [str(in_manifest)]}),
        encoding="utf-8",
    )

    with patch("elis.pipeline.merge.run_merge") as run_merge:
        code = cli.main(
            [
                "merge",
                "--inputs",
                str(in_direct),
                "--from-manifest",
                str(manifest),
                "--output",
                str(tmp_path / "out.json"),
                "--report",
                str(tmp_path / "report.json"),
            ]
        )
    assert code == 0
    run_merge.assert_called_once()
    assert run_merge.call_args[0][0] == [str(in_direct)]


def test_merge_emits_manifest(tmp_path: Path) -> None:
    """merge should emit a run manifest sidecar."""
    input_path = tmp_path / "input.json"
    input_path.write_text("[]", encoding="utf-8")
    output_path = tmp_path / "out.json"
    report_path = tmp_path / "report.json"

    def _fake_run_merge(inputs: list[str], output: str, report: str) -> None:
        Path(output).write_text('[{"_meta": true}]', encoding="utf-8")
        Path(report).write_text("{}", encoding="utf-8")

    with patch("elis.pipeline.merge.run_merge", side_effect=_fake_run_merge):
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
    _assert_run_manifest(tmp_path / "out_manifest.json")


def test_dedup_emits_manifest(tmp_path: Path) -> None:
    """dedup should emit a run manifest sidecar."""
    in_path = tmp_path / "in.json"
    in_path.write_text("[]", encoding="utf-8")
    out_path = tmp_path / "dedup.json"
    report_path = tmp_path / "dedup_report.json"

    def _fake_run_dedup(*_args, **_kwargs) -> None:
        out_path.write_text('[{"_meta": true}]', encoding="utf-8")
        report_path.write_text("{}", encoding="utf-8")

    with patch("elis.pipeline.dedup.run_dedup", side_effect=_fake_run_dedup):
        code = cli.main(
            [
                "dedup",
                "--input",
                str(in_path),
                "--output",
                str(out_path),
                "--report",
                str(report_path),
            ]
        )
    assert code == 0
    _assert_run_manifest(tmp_path / "dedup_manifest.json")


def test_screen_emits_manifest(tmp_path: Path) -> None:
    """screen should emit a run manifest sidecar."""
    in_path = tmp_path / "appendix_a.json"
    out_path = tmp_path / "appendix_b.json"
    in_path.write_text(
        json.dumps(
            [
                {
                    "_meta": True,
                    "global": {"year_from": 2000, "year_to": 2026, "languages": ["en"]},
                    "run_inputs": {},
                },
                {"source": "crossref", "title": "T", "year": 2020, "query_topic": "t1"},
            ]
        ),
        encoding="utf-8",
    )

    code = cli.main(["screen", "--input", str(in_path), "--output", str(out_path)])
    assert code == 0
    _assert_run_manifest(tmp_path / "appendix_b_manifest.json")


def test_validate_explicit_emits_manifest(tmp_path: Path) -> None:
    """validate <schema> <json> should emit companion manifest."""
    data_path = tmp_path / "rows.json"
    schema_path = tmp_path / "schema.json"
    data_path.write_text(json.dumps([{"id": "r1"}]), encoding="utf-8")
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
    _assert_run_manifest(tmp_path / "rows_manifest.json")


# ---------------------------------------------------------------------------
# Adversarial tests — PE1b (Validator-added)
# ---------------------------------------------------------------------------


def test_merge_no_inputs_no_from_manifest_raises() -> None:
    """merge with neither --inputs nor --from-manifest must exit with an error."""
    try:
        cli.main(
            [
                "merge",
                "--output",
                "out.json",
                "--report",
                "report.json",
            ]
        )
    except SystemExit:
        pass  # expected
    else:
        raise AssertionError(
            "Expected SystemExit when neither --inputs nor --from-manifest given."
        )


def test_merge_from_manifest_fallback_to_output_path(tmp_path: Path) -> None:
    """empty input_paths in manifest → fallback to manifest's output_path."""
    fallback_file = tmp_path / "fallback.json"
    fallback_file.write_text("[]", encoding="utf-8")
    manifest = tmp_path / "run_manifest.json"
    manifest.write_text(
        json.dumps({"input_paths": [], "output_path": str(fallback_file)}),
        encoding="utf-8",
    )

    with patch("elis.pipeline.merge.run_merge") as run_merge:
        code = cli.main(
            [
                "merge",
                "--from-manifest",
                str(manifest),
                "--output",
                str(tmp_path / "out.json"),
                "--report",
                str(tmp_path / "report.json"),
            ]
        )
    assert code == 0
    assert run_merge.call_args[0][0] == [str(fallback_file)]


def test_merge_from_manifest_no_usable_paths_raises(tmp_path: Path) -> None:
    """Manifest with no input_paths and no output_path must raise ValueError."""
    manifest = tmp_path / "bad_manifest.json"
    manifest.write_text(
        json.dumps({"input_paths": [], "output_path": "  "}), encoding="utf-8"
    )

    try:
        cli.main(
            [
                "merge",
                "--from-manifest",
                str(manifest),
                "--output",
                str(tmp_path / "out.json"),
                "--report",
                str(tmp_path / "report.json"),
            ]
        )
    except (ValueError, SystemExit):
        pass
    else:
        raise AssertionError(
            "Expected ValueError or SystemExit for unusable manifest paths."
        )


def test_screen_dry_run_does_not_emit_manifest(tmp_path: Path) -> None:
    """screen --dry-run must not write a manifest sidecar."""
    in_path = tmp_path / "appendix_a.json"
    out_path = tmp_path / "appendix_b.json"
    in_path.write_text(
        json.dumps(
            [
                {
                    "_meta": True,
                    "global": {"year_from": 2000, "year_to": 2026, "languages": ["en"]},
                    "run_inputs": {},
                },
                {"source": "crossref", "title": "T", "year": 2020, "query_topic": "t1"},
            ]
        ),
        encoding="utf-8",
    )

    code = cli.main(
        ["screen", "--input", str(in_path), "--output", str(out_path), "--dry-run"]
    )
    assert code == 0
    manifest = tmp_path / "appendix_b_manifest.json"
    assert not manifest.exists(), "dry-run must not emit a manifest sidecar"


def test_harvest_manifest_source_matches_adapter(tmp_path: Path) -> None:
    """Manifest source field must equal the harvested source name, not 'system'."""
    out = tmp_path / "harvest.json"

    class _Cfg:
        queries = [{"q": "x"}]
        max_results = 5
        output_path = str(out)
        config_mode = "test"

    class _Adapter:
        display_name = "CrossRef"

        def harvest(self, *_args, **_kwargs):
            yield {"title": "T", "source": "crossref", "crossref_id": "X1", "doi": None}

    with (
        patch("elis.sources.config.load_harvest_config", return_value=_Cfg()),
        patch("elis.sources.get_adapter", return_value=_Adapter),
    ):
        cli.main(["harvest", "crossref"])

    manifest_path = tmp_path / "harvest_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["source"] == "crossref"
    assert payload["stage"] == "harvest"


def test_merge_manifest_stage_field_is_merge(tmp_path: Path) -> None:
    """Emitted merge manifest must have stage == 'merge'."""
    input_path = tmp_path / "input.json"
    input_path.write_text("[]", encoding="utf-8")
    output_path = tmp_path / "out.json"
    report_path = tmp_path / "report.json"

    def _fake_run_merge(inputs, output, report):
        Path(output).write_text('[{"_meta": true}]', encoding="utf-8")
        Path(report).write_text("{}", encoding="utf-8")

    with patch("elis.pipeline.merge.run_merge", side_effect=_fake_run_merge):
        cli.main(
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

    manifest = json.loads((tmp_path / "out_manifest.json").read_text(encoding="utf-8"))
    assert manifest["stage"] == "merge"
    assert manifest["source"] == "system"


def test_dedup_manifest_stage_field_is_dedup(tmp_path: Path) -> None:
    """Emitted dedup manifest must have stage == 'dedup'."""
    in_path = tmp_path / "in.json"
    in_path.write_text("[]", encoding="utf-8")
    out_path = tmp_path / "dedup.json"
    report_path = tmp_path / "dedup_report.json"

    def _fake_run_dedup(*_args, **_kwargs):
        out_path.write_text('[{"_meta": true}]', encoding="utf-8")
        report_path.write_text("{}", encoding="utf-8")

    with patch("elis.pipeline.dedup.run_dedup", side_effect=_fake_run_dedup):
        cli.main(
            [
                "dedup",
                "--input",
                str(in_path),
                "--output",
                str(out_path),
                "--report",
                str(report_path),
            ]
        )

    manifest = json.loads(
        (tmp_path / "dedup_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["stage"] == "dedup"
    assert manifest["source"] == "system"


def test_agentic_asta_discover_calls_runner() -> None:
    with patch("elis.agentic.asta.run_discover") as run_discover:
        code = cli.main(
            [
                "agentic",
                "asta",
                "discover",
                "--query",
                "electoral integrity",
                "--run-id",
                "r001",
            ]
        )
    assert code == 0
    run_discover.assert_called_once()


def test_agentic_asta_enrich_calls_runner(tmp_path: Path) -> None:
    inp = tmp_path / "a.json"
    inp.write_text("[]", encoding="utf-8")
    with patch("elis.agentic.asta.run_enrich") as run_enrich:
        code = cli.main(
            [
                "agentic",
                "asta",
                "enrich",
                "--input",
                str(inp),
                "--run-id",
                "r002",
            ]
        )
    assert code == 0
    run_enrich.assert_called_once()
