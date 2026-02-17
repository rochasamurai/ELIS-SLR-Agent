"""Tests for elis.cli — top-level CLI dispatcher."""

from __future__ import annotations

import subprocess
import sys

import pytest

from elis.cli import main


class TestCLIDispatch:
    def test_no_args_returns_zero(self):
        assert main([]) == 0

    def test_help_returns_zero(self):
        assert main(["--help"]) == 0

    def test_unknown_command_returns_two(self):
        assert main(["unknown-cmd"]) == 2

    def test_search_help(self):
        """search --help should trigger argparse SystemExit(0)."""
        with pytest.raises(SystemExit) as exc:
            main(["search", "--help"])
        assert exc.value.code == 0

    def test_screen_help(self):
        with pytest.raises(SystemExit) as exc:
            main(["screen", "--help"])
        assert exc.value.code == 0

    def test_validate_help(self):
        """validate --help must show help and exit 0 (no side effects)."""
        with pytest.raises(SystemExit) as exc:
            main(["validate", "--help"])
        assert exc.value.code == 0

    def test_search_missing_config(self, tmp_path):
        rc = main(["search", "--config", str(tmp_path / "nope.yml")])
        assert rc == 2


class TestModuleEntrypoint:
    """Verify ``python -m elis`` works (BLOCKER A)."""

    def test_python_m_elis_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "elis", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "usage:" in result.stderr.lower() or "usage:" in result.stdout.lower()


class TestValidateCLIContract:
    """Tests for BLOCKER B + C — validate subcommand contract."""

    def test_validate_help_no_side_effects(self, tmp_path, monkeypatch):
        """--help must NOT write any reports."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "validation_reports").mkdir()

        with pytest.raises(SystemExit) as exc:
            main(["validate", "--help"])
        assert exc.value.code == 0

        # No new files should appear.
        created = list((tmp_path / "validation_reports").iterdir())
        assert created == []

    def test_validate_missing_file_exits_nonzero(self, tmp_path):
        rc = main(["validate", str(tmp_path / "DOES_NOT_EXIST.json")])
        assert rc != 0

    def test_validate_explicit_schema_and_data(self, tmp_path):
        """Explicit --data + --schema should work."""
        import json

        data = [{"_meta": True}, {"id": "1", "name": "test"}]
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {"id": {"type": "string"}},
        }
        df = tmp_path / "data.json"
        sf = tmp_path / "schema.json"
        df.write_text(json.dumps(data), encoding="utf-8")
        sf.write_text(json.dumps(schema), encoding="utf-8")

        rc = main(["validate", "--data", str(df), "--schema", str(sf)])
        assert rc == 0

    def test_validate_positional_infers_schema(self, tmp_path, monkeypatch):
        """Positional data path with appendix_a in name should infer schema."""
        import json

        monkeypatch.chdir(tmp_path)

        # Create the schema at the expected relative path.
        (tmp_path / "schemas").mkdir()
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {"id": {"type": "string"}},
        }
        (tmp_path / "schemas" / "appendix_a.schema.json").write_text(
            json.dumps(schema), encoding="utf-8"
        )

        data = [{"_meta": True}, {"id": "1"}]
        df = tmp_path / "ELIS_Appendix_A_Search_rows.json"
        df.write_text(json.dumps(data), encoding="utf-8")

        rc = main(["validate", str(df)])
        assert rc == 0

    def test_validate_unknown_name_no_schema_exits(self, tmp_path):
        """Data file with unrecognised name and no --schema should fail."""
        import json

        df = tmp_path / "mystery.json"
        df.write_text(json.dumps([{"id": "1"}]), encoding="utf-8")
        rc = main(["validate", str(df)])
        assert rc == 2  # cannot infer schema
