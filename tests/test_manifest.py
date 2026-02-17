"""Tests for PE1a manifest utility and schemas."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from elis.manifest import write_manifest


def _sample_manifest() -> dict[str, object]:
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
        "tool_versions": {"python": "3.11.9", "requests": "2.31.0"},
    }


def _sample_validation_report() -> dict[str, object]:
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


def test_write_manifest_writes_json_and_returns_path(tmp_path) -> None:
    manifest_path = tmp_path / "runs" / "sample" / "run.manifest.json"
    manifest = _sample_manifest()
    written_path = write_manifest(manifest, manifest_path)

    assert written_path == manifest_path
    assert written_path.exists()
    assert json.loads(written_path.read_text(encoding="utf-8")) == manifest


def test_write_manifest_uses_sorted_keys_for_deterministic_output(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    write_manifest({"b": 2, "a": 1}, manifest_path)

    text = manifest_path.read_text(encoding="utf-8")
    assert text.startswith('{\n  "a": 1,\n  "b": 2\n}\n')


def test_run_manifest_schema_accepts_valid_manifest() -> None:
    schema = json.loads(
        Path("schemas/run_manifest.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=_sample_manifest(), schema=schema)


def test_run_manifest_schema_rejects_invalid_stage() -> None:
    schema = json.loads(
        Path("schemas/run_manifest.schema.json").read_text(encoding="utf-8")
    )
    manifest = _sample_manifest()
    manifest["stage"] = "invalid_stage"

    try:
        jsonschema.validate(instance=manifest, schema=schema)
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError("Expected ValidationError for invalid stage.")


def test_validation_report_schema_accepts_valid_report() -> None:
    schema = json.loads(
        Path("schemas/validation_report.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=_sample_validation_report(), schema=schema)


# ---------------------------------------------------------------------------
# Adversarial schema-rejection tests (Validator-added for PE1b)
# ---------------------------------------------------------------------------


def _schema() -> dict:
    return json.loads(
        Path("schemas/run_manifest.schema.json").read_text(encoding="utf-8")
    )


def test_schema_rejects_missing_required_field() -> None:
    """Manifest without 'record_count' must fail schema validation."""
    manifest = _sample_manifest()
    del manifest["record_count"]
    try:
        jsonschema.validate(instance=manifest, schema=_schema())
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError("Expected ValidationError for missing record_count.")


def test_schema_rejects_negative_record_count() -> None:
    """record_count must be >= 0; negative values must be rejected."""
    manifest = _sample_manifest()
    manifest["record_count"] = -1
    try:
        jsonschema.validate(instance=manifest, schema=_schema())
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError("Expected ValidationError for negative record_count.")


def test_schema_rejects_invalid_config_hash_format() -> None:
    """config_hash must match pattern ^sha256:.+; other prefixes must be rejected."""
    manifest = _sample_manifest()
    manifest["config_hash"] = "md5:badhash"
    try:
        jsonschema.validate(instance=manifest, schema=_schema())
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError("Expected ValidationError for non-sha256 config_hash.")


def test_schema_rejects_additional_properties() -> None:
    """additionalProperties: false — unknown fields must be rejected."""
    manifest = _sample_manifest()
    manifest["unexpected_field"] = "oops"
    try:
        jsonschema.validate(instance=manifest, schema=_schema())
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError(
            "Expected ValidationError for unexpected additional property."
        )


def test_schema_rejects_short_commit_sha() -> None:
    """commit_sha must have minLength 7; a 6-char value must be rejected."""
    manifest = _sample_manifest()
    manifest["commit_sha"] = "abc123"  # only 6 chars
    try:
        jsonschema.validate(instance=manifest, schema=_schema())
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError(
            "Expected ValidationError for commit_sha shorter than 7 chars."
        )


def test_manifest_path_for_output_stem_pattern(tmp_path: Path) -> None:
    """manifest_path_for_output returns <stem>_manifest.json next to the output."""
    from elis.manifest import manifest_path_for_output

    result = manifest_path_for_output(tmp_path / "appendix_b.json")
    assert result == tmp_path / "appendix_b_manifest.json"


def test_manifest_path_for_output_no_extension(tmp_path: Path) -> None:
    """Output path with no extension → <name>_manifest.json."""
    from elis.manifest import manifest_path_for_output

    result = manifest_path_for_output(tmp_path / "report")
    assert result == tmp_path / "report_manifest.json"
