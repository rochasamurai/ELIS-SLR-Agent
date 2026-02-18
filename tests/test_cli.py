"""Tests for elis.cli — top-level CLI dispatcher (v2.0 contract)."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from elis.cli import main


class TestCLIDispatch:
    """Basic command dispatch contract for the v2.0 CLI."""

    def test_no_args_raises_system_exit(self):
        """Subcommand is required; no args must exit."""
        with pytest.raises(SystemExit):
            main([])

    def test_help_exits_zero(self):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    def test_unknown_command_exits_nonzero(self):
        with pytest.raises(SystemExit) as exc:
            main(["unknown-cmd"])
        assert exc.value.code != 0

    def test_harvest_help(self):
        with pytest.raises(SystemExit) as exc:
            main(["harvest", "--help"])
        assert exc.value.code == 0

    def test_screen_help(self):
        with pytest.raises(SystemExit) as exc:
            main(["screen", "--help"])
        assert exc.value.code == 0

    def test_validate_help(self):
        with pytest.raises(SystemExit) as exc:
            main(["validate", "--help"])
        assert exc.value.code == 0

    def test_merge_help(self):
        with pytest.raises(SystemExit) as exc:
            main(["merge", "--help"])
        assert exc.value.code == 0

    def test_dedup_help(self):
        with pytest.raises(SystemExit) as exc:
            main(["dedup", "--help"])
        assert exc.value.code == 0

    def test_search_subcommand_removed(self):
        """search subcommand was removed in v2.0; must exit non-zero."""
        with pytest.raises(SystemExit) as exc:
            main(["search"])
        assert exc.value.code != 0


class TestModuleEntrypoint:
    """Verify ``python -m elis`` works (entrypoint contract)."""

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
    """Tests for validate subcommand contract (v2.0 positional args)."""

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

    def test_validate_one_positional_raises(self, tmp_path):
        """Single positional arg → SystemExit (must provide both schema and data)."""
        df = tmp_path / "data.json"
        df.write_text(json.dumps([{"id": "1"}]), encoding="utf-8")
        with pytest.raises(SystemExit):
            main(["validate", str(df)])

    def test_validate_explicit_two_positionals(self, tmp_path):
        """<schema_path> <json_path> positionals run single-file validation."""
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

        rc = main(["validate", str(sf), str(df)])
        assert rc == 0

    def test_validate_old_flags_removed(self, tmp_path):
        """--data/--schema flags from the old CLI no longer exist; argparse exits."""
        df = tmp_path / "data.json"
        df.write_text(json.dumps([{"id": "1"}]), encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            main(["validate", "--data", str(df)])
        assert exc.value.code != 0
