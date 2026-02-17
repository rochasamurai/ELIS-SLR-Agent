"""Adversarial tests for PE1a manifest schemas and writer utility.

Validator tests covering: schema rejection of invalid data, edge cases,
empty inputs, determinism, and boundary conditions.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from elis.manifest import write_manifest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_schema(name: str) -> dict:
    path = Path(f"schemas/{name}")
    if not path.exists():
        pytest.skip(f"Schema {name} not found")
    return json.loads(path.read_text(encoding="utf-8"))


def _valid_manifest() -> dict:
    return {
        "schema_version": "1.0",
        "run_id": "20260217_120000_scopus",
        "stage": "harvest",
        "source": "scopus",
        "commit_sha": "c81328e",
        "config_hash": "sha256:abc123",
        "started_at": "2026-02-17T12:00:00Z",
        "finished_at": "2026-02-17T12:01:00Z",
        "record_count": 10,
        "input_paths": ["config/elis_search_queries.yml"],
        "output_path": "runs/20260217_120000_scopus/harvest/scopus.json",
        "tool_versions": {"python": "3.11.9"},
    }


def _valid_report() -> dict:
    return {
        "schema_version": "1.0",
        "run_id": "20260217_120000_scopus",
        "stage": "validate",
        "checked_at": "2026-02-17T12:02:00Z",
        "target_path": "runs/20260217_120000_scopus/merge/appendix_a.json",
        "schema_path": "schemas/appendix_a.schema.json",
        "is_valid": True,
        "record_count": 10,
        "error_count": 0,
        "errors": [],
    }


# ---------------------------------------------------------------------------
# run_manifest.schema.json — rejection tests
# ---------------------------------------------------------------------------


class TestRunManifestSchemaRejections:
    """Schema must reject invalid manifests."""

    @pytest.fixture()
    def schema(self) -> dict:
        return _load_schema("run_manifest.schema.json")

    @pytest.mark.parametrize(
        "field",
        [
            "schema_version",
            "run_id",
            "stage",
            "source",
            "commit_sha",
            "config_hash",
            "started_at",
            "finished_at",
            "record_count",
            "input_paths",
            "output_path",
            "tool_versions",
        ],
    )
    def test_missing_required_field_rejected(self, schema, field) -> None:
        manifest = _valid_manifest()
        del manifest[field]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_additional_property_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["extra_field"] = "should_fail"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_wrong_schema_version_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["schema_version"] = "2.0"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    @pytest.mark.parametrize(
        "bad_stage",
        [
            "invalid",
            "HARVEST",
            "Merge",
            "",
            "search",
        ],
    )
    def test_invalid_stage_rejected(self, schema, bad_stage) -> None:
        manifest = _valid_manifest()
        manifest["stage"] = bad_stage
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_empty_run_id_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["run_id"] = ""
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_empty_source_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["source"] = ""
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_short_commit_sha_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["commit_sha"] = "abc"  # less than 7 chars
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_config_hash_missing_prefix_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["config_hash"] = "abc123"  # missing sha256: prefix
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_negative_record_count_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["record_count"] = -1
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_string_record_count_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["record_count"] = "10"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_empty_tool_versions_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["tool_versions"] = {}
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_non_string_tool_version_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["tool_versions"] = {"python": 311}
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_empty_output_path_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["output_path"] = ""
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)

    def test_input_paths_empty_string_item_rejected(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["input_paths"] = [""]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=manifest, schema=schema)


class TestRunManifestSchemaAcceptance:
    """Schema must accept valid edge-case manifests."""

    @pytest.fixture()
    def schema(self) -> dict:
        return _load_schema("run_manifest.schema.json")

    @pytest.mark.parametrize(
        "stage",
        [
            "harvest",
            "merge",
            "dedup",
            "screen",
            "validate",
        ],
    )
    def test_all_valid_stages_accepted(self, schema, stage) -> None:
        manifest = _valid_manifest()
        manifest["stage"] = stage
        jsonschema.validate(instance=manifest, schema=schema)

    def test_zero_record_count_accepted(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["record_count"] = 0
        jsonschema.validate(instance=manifest, schema=schema)

    def test_empty_input_paths_accepted(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["input_paths"] = []
        jsonschema.validate(instance=manifest, schema=schema)

    def test_full_commit_sha_accepted(self, schema) -> None:
        manifest = _valid_manifest()
        manifest["commit_sha"] = "c81328e4f5a9b2d3e6f7a8b9c0d1e2f3a4b5c6d7"
        jsonschema.validate(instance=manifest, schema=schema)


# ---------------------------------------------------------------------------
# validation_report.schema.json — rejection tests
# ---------------------------------------------------------------------------


class TestValidationReportSchemaRejections:
    @pytest.fixture()
    def schema(self) -> dict:
        return _load_schema("validation_report.schema.json")

    @pytest.mark.parametrize(
        "field",
        [
            "schema_version",
            "run_id",
            "stage",
            "checked_at",
            "target_path",
            "schema_path",
            "is_valid",
            "record_count",
            "error_count",
            "errors",
        ],
    )
    def test_missing_required_field_rejected(self, schema, field) -> None:
        report = _valid_report()
        del report[field]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)

    def test_additional_property_rejected(self, schema) -> None:
        report = _valid_report()
        report["extra"] = "nope"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)

    def test_is_valid_string_rejected(self, schema) -> None:
        report = _valid_report()
        report["is_valid"] = "true"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)

    def test_negative_error_count_rejected(self, schema) -> None:
        report = _valid_report()
        report["error_count"] = -1
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)

    def test_errors_non_string_item_rejected(self, schema) -> None:
        report = _valid_report()
        report["errors"] = [123]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)


# ---------------------------------------------------------------------------
# write_manifest — adversarial
# ---------------------------------------------------------------------------


class TestWriteManifestAdversarial:
    def test_empty_mapping_writes_empty_object(self, tmp_path) -> None:
        path = tmp_path / "empty.json"
        write_manifest({}, path)
        assert json.loads(path.read_text(encoding="utf-8")) == {}

    def test_unicode_values_preserved(self, tmp_path) -> None:
        path = tmp_path / "unicode.json"
        data = {"title": "Intégrité électorale", "source": "日本語"}
        write_manifest(data, path)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["title"] == "Intégrité électorale"
        assert loaded["source"] == "日本語"

    def test_deeply_nested_parent_dirs_created(self, tmp_path) -> None:
        path = tmp_path / "a" / "b" / "c" / "d" / "manifest.json"
        write_manifest({"ok": True}, path)
        assert path.exists()

    def test_overwrite_existing_file(self, tmp_path) -> None:
        path = tmp_path / "manifest.json"
        write_manifest({"version": 1}, path)
        write_manifest({"version": 2}, path)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["version"] == 2

    def test_output_ends_with_newline(self, tmp_path) -> None:
        path = tmp_path / "manifest.json"
        write_manifest({"a": 1}, path)
        text = path.read_text(encoding="utf-8")
        assert text.endswith("\n")

    def test_deterministic_key_order(self, tmp_path) -> None:
        """Keys must be sorted regardless of insertion order."""
        path1 = tmp_path / "m1.json"
        path2 = tmp_path / "m2.json"
        write_manifest({"z": 1, "a": 2, "m": 3}, path1)
        write_manifest({"m": 3, "z": 1, "a": 2}, path2)
        assert path1.read_text(encoding="utf-8") == path2.read_text(encoding="utf-8")

    def test_returns_path_object(self, tmp_path) -> None:
        path = tmp_path / "out.json"
        result = write_manifest({}, path)
        assert isinstance(result, Path)
        assert result == path

    def test_accepts_string_path(self, tmp_path) -> None:
        path_str = str(tmp_path / "str_path.json")
        result = write_manifest({"key": "val"}, path_str)
        assert result == Path(path_str)
        assert result.exists()
