"""Adversarial / edge-case tests for the elis CLI (PE0a validator)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from elis import cli


# ---------------------------------------------------------------------------
# Parser-level tests (argparse rejection)
# ---------------------------------------------------------------------------


class TestParserRejection:
    """Argparse should reject invalid invocations before any handler runs."""

    def test_no_subcommand(self) -> None:
        """Running 'elis' with no subcommand must exit with code 2."""
        with pytest.raises(SystemExit) as exc_info:
            cli.main([])
        assert exc_info.value.code == 2

    def test_unknown_subcommand(self) -> None:
        """An unrecognised subcommand must be rejected."""
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["foobar"])
        assert exc_info.value.code == 2

    def test_validate_extra_positional_args(self) -> None:
        """More than two positional args to 'validate' must be rejected."""
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["validate", "a", "b", "c"])
        assert exc_info.value.code == 2

    def test_validate_unknown_flag(self) -> None:
        """Unknown flags must be rejected."""
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["validate", "--nonexistent-flag"])
        assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# validate subcommand — file-level edge cases
# ---------------------------------------------------------------------------


class TestValidateFilePaths:
    """Test validate behaviour with missing / malformed files."""

    def test_nonexistent_schema_and_data(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Both paths missing should produce [ERR] and mention 'not found'."""
        cli.main(["validate", "no_such_schema.json", "no_such_data.json"])
        out = capsys.readouterr().out
        assert "[ERR]" in out
        assert "not found" in out.lower() or "No such file" in out

    def test_nonexistent_data_only(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valid schema but missing data file should produce [ERR]."""
        schema = tmp_path / "s.json"
        schema.write_text(json.dumps({"type": "object"}), encoding="utf-8")
        cli.main(["validate", str(schema), "missing_data.json"])
        out = capsys.readouterr().out
        assert "[ERR]" in out

    def test_nonexistent_schema_only(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Valid data but missing schema should produce [ERR]."""
        data = tmp_path / "d.json"
        data.write_text(json.dumps([{"id": "r1"}]), encoding="utf-8")
        cli.main(["validate", "missing_schema.json", str(data)])
        out = capsys.readouterr().out
        assert "[ERR]" in out


# ---------------------------------------------------------------------------
# validate subcommand — malformed inputs
# ---------------------------------------------------------------------------


class TestValidateMalformedInput:
    """Feed corrupt / unexpected data and verify graceful handling."""

    def test_invalid_json_data(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Non-JSON data file should produce [ERR] with 'Invalid JSON'."""
        schema = tmp_path / "s.json"
        schema.write_text(json.dumps({"type": "object"}), encoding="utf-8")
        bad = tmp_path / "bad.json"
        bad.write_text("THIS IS NOT JSON", encoding="utf-8")

        cli.main(["validate", str(schema), str(bad)])
        out = capsys.readouterr().out
        assert "[ERR]" in out
        assert "Invalid JSON" in out

    def test_invalid_json_schema(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Non-JSON schema file should produce [ERR]."""
        data = tmp_path / "d.json"
        data.write_text(json.dumps([{"id": "1"}]), encoding="utf-8")
        bad_schema = tmp_path / "bad_schema.json"
        bad_schema.write_text("{{{NOT VALID", encoding="utf-8")

        cli.main(["validate", str(bad_schema), str(data)])
        out = capsys.readouterr().out
        assert "[ERR]" in out

    def test_empty_json_array(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Empty array should be valid (0 records, no errors)."""
        schema = tmp_path / "s.json"
        schema.write_text(
            json.dumps({"type": "object", "properties": {"id": {"type": "string"}}}),
            encoding="utf-8",
        )
        data = tmp_path / "empty.json"
        data.write_text(json.dumps([]), encoding="utf-8")

        cli.main(["validate", str(schema), str(data)])
        out = capsys.readouterr().out
        assert "[OK]" in out
        assert "rows=0" in out

    def test_data_not_array(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Object root should validate when schema root is object."""
        schema = tmp_path / "s.json"
        schema.write_text(json.dumps({"type": "object"}), encoding="utf-8")
        data = tmp_path / "obj.json"
        data.write_text(json.dumps({"id": "single"}), encoding="utf-8")

        cli.main(["validate", str(schema), str(data)])
        out = capsys.readouterr().out
        assert "[OK]" in out

    def test_object_data_fails_when_schema_requires_array(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Object root should fail when schema explicitly requires an array root."""
        schema = tmp_path / "s.json"
        schema.write_text(
            json.dumps({"type": "array", "items": {"type": "object"}}), encoding="utf-8"
        )
        data = tmp_path / "obj.json"
        data.write_text(json.dumps({"id": "single"}), encoding="utf-8")

        cli.main(["validate", str(schema), str(data)])
        out = capsys.readouterr().out
        assert "[ERR]" in out


# ---------------------------------------------------------------------------
# validate subcommand — schema-violation paths
# ---------------------------------------------------------------------------


class TestValidateSchemaViolation:
    """Verify that validation errors are reported when data breaks the schema."""

    def test_missing_required_field(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Record missing a required field should trigger [ERR]."""
        schema = tmp_path / "s.json"
        schema.write_text(
            json.dumps(
                {
                    "type": "object",
                    "required": ["name"],
                    "properties": {"name": {"type": "string"}},
                }
            ),
            encoding="utf-8",
        )
        data = tmp_path / "d.json"
        data.write_text(json.dumps([{"id": "no-name"}]), encoding="utf-8")

        cli.main(["validate", str(schema), str(data)])
        out = capsys.readouterr().out
        assert "[ERR]" in out
        assert "'name' is a required property" in out

    def test_wrong_field_type(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Field with wrong type should trigger [ERR]."""
        schema = tmp_path / "s.json"
        schema.write_text(
            json.dumps(
                {
                    "type": "object",
                    "properties": {"count": {"type": "integer"}},
                }
            ),
            encoding="utf-8",
        )
        data = tmp_path / "d.json"
        data.write_text(json.dumps([{"count": "not-an-integer"}]), encoding="utf-8")

        cli.main(["validate", str(schema), str(data)])
        out = capsys.readouterr().out
        assert "[ERR]" in out

    def test_many_errors_truncated(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """When more than 10 errors, output should indicate truncation."""
        schema = tmp_path / "s.json"
        schema.write_text(
            json.dumps(
                {
                    "type": "object",
                    "required": ["x"],
                    "properties": {"x": {"type": "string"}},
                }
            ),
            encoding="utf-8",
        )
        # 15 records all missing required 'x'
        data = tmp_path / "d.json"
        data.write_text(json.dumps([{"id": i} for i in range(15)]), encoding="utf-8")

        cli.main(["validate", str(schema), str(data)])
        out = capsys.readouterr().out
        assert "[ERR]" in out
        assert "more errors" in out


# ---------------------------------------------------------------------------
# Partial argument rejection (schema_path without json_path)
# ---------------------------------------------------------------------------


class TestPartialArgs:
    """Only one of (schema_path, json_path) must be rejected."""

    def test_only_schema_path(self) -> None:
        with pytest.raises(SystemExit, match="Provide both"):
            cli.main(["validate", "some_schema.json"])

    def test_build_parser_returns_parser(self) -> None:
        """build_parser() should return an ArgumentParser."""
        import argparse

        parser = cli.build_parser()
        assert isinstance(parser, argparse.ArgumentParser)


# ---------------------------------------------------------------------------
# __main__ entrypoint
# ---------------------------------------------------------------------------


class TestMainEntrypoint:
    """Ensure 'python -m elis' works correctly."""

    def test_python_m_elis_help(self) -> None:
        """'python -m elis --help' must exit 0 and print usage."""
        result = subprocess.run(
            [sys.executable, "-m", "elis", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "ELIS SLR Agent CLI" in result.stdout

    def test_python_m_elis_no_args(self) -> None:
        """'python -m elis' with no args must exit non-zero."""
        result = subprocess.run(
            [sys.executable, "-m", "elis"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode != 0

    def test_python_m_elis_validate_help(self) -> None:
        """'python -m elis validate --help' must exit 0 with usage."""
        result = subprocess.run(
            [sys.executable, "-m", "elis", "validate", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "schema_path" in result.stdout


# ---------------------------------------------------------------------------
# Determinism: no timestamps in outputs
# ---------------------------------------------------------------------------


class TestDeterminism:
    """Outputs from validate (single-file mode) must not contain timestamps."""

    def test_output_has_no_timestamp(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Single-file validate output should be timestamp-free."""
        import re

        schema = tmp_path / "s.json"
        schema.write_text(
            json.dumps({"type": "object", "properties": {"id": {"type": "string"}}}),
            encoding="utf-8",
        )
        data = tmp_path / "d.json"
        data.write_text(json.dumps([{"id": "1"}]), encoding="utf-8")

        cli.main(["validate", str(schema), str(data)])
        out = capsys.readouterr().out
        # ISO-style timestamps
        assert not re.search(
            r"\d{4}-\d{2}-\d{2}", out
        ), f"Output contains date-like pattern: {out!r}"


# ---------------------------------------------------------------------------
# Legacy delegation (no-args validate)
# ---------------------------------------------------------------------------


class TestLegacyDelegation:
    """When validate is called with no paths, it must delegate to legacy main."""

    def test_legacy_main_system_exit_zero(self) -> None:
        """Legacy main raising SystemExit(0) → return 0."""
        with patch("scripts._archive.validate_json.main", side_effect=SystemExit(0)):
            code = cli.main(["validate"])
        assert code == 0

    def test_legacy_main_system_exit_nonzero(self) -> None:
        """Legacy main raising SystemExit(1) → return 1."""
        with patch("scripts._archive.validate_json.main", side_effect=SystemExit(1)):
            code = cli.main(["validate"])
        assert code == 1

    def test_legacy_main_system_exit_none(self) -> None:
        """Legacy main raising SystemExit(None) → return 0."""
        with patch("scripts._archive.validate_json.main", side_effect=SystemExit(None)):
            code = cli.main(["validate"])
        assert code == 0

    def test_legacy_main_normal_return(self) -> None:
        """Legacy main returning normally → return 0."""
        with patch("scripts._archive.validate_json.main"):
            code = cli.main(["validate"])
        assert code == 0
