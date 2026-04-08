from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts.pm_discord_command import (
    handle_command,
    load_loop_control,
    main,
    write_loop_control,
)


def test_veto_command_requires_label_and_pause() -> None:
    control = load_loop_control(Path("missing.json"))
    result = handle_command(
        command="veto",
        control=control,
        actor="PO",
        pr_number=314,
    )
    assert result.label_to_apply == "pm-review-required"
    assert result.pause_loop is True
    assert result.control.paused is True
    assert "PR #314" in result.message


def test_resume_command_clears_pause() -> None:
    control = load_loop_control(Path("missing.json"))
    result = handle_command(
        command="resume",
        control=control,
        actor="PO",
    )
    assert result.pause_loop is False
    assert result.control.paused is False


def test_write_and_reload_control_file(tmp_path: Path) -> None:
    path = tmp_path / "pm_loop_control.json"
    control = load_loop_control(path)
    result = handle_command(
        command="pause",
        control=control,
        actor="PO",
        reason="Manual pause for review",
    )
    write_loop_control(path, result.control)
    reloaded = load_loop_control(path)
    assert reloaded.paused is True
    assert reloaded.reason == "Manual pause for review"


def test_main_writes_json_for_pause(tmp_path: Path, capsys) -> None:
    control_path = tmp_path / "pm_loop_control.json"
    old_argv = sys.argv
    sys.argv = [
        "pm_discord_command.py",
        "--command",
        "pause",
        "--actor",
        "PO",
        "--control-file",
        str(control_path),
        "--write",
        "--json",
    ]
    try:
        rc = main()
    finally:
        sys.argv = old_argv
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["command"] == "pause"
    assert payload["control"]["paused"] is True
    assert json.loads(control_path.read_text(encoding="utf-8"))["paused"] is True
