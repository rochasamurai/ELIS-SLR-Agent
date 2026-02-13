"""Tests for elis.cli — top-level CLI dispatcher."""

from __future__ import annotations

from elis.cli import main


class TestCLIDispatch:
    def test_no_args_returns_zero(self):
        assert main([]) == 0

    def test_help_returns_zero(self):
        assert main(["--help"]) == 0

    def test_unknown_command_returns_two(self):
        assert main(["unknown-cmd"]) == 2

    def test_search_help(self, capsys):
        """search --help should trigger argparse SystemExit(0)."""
        import pytest

        with pytest.raises(SystemExit) as exc:
            main(["search", "--help"])
        assert exc.value.code == 0

    def test_screen_help(self, capsys):
        import pytest

        with pytest.raises(SystemExit) as exc:
            main(["screen", "--help"])
        assert exc.value.code == 0

    def test_search_missing_config(self, tmp_path):
        rc = main(["search", "--config", str(tmp_path / "nope.yml")])
        assert rc == 2
