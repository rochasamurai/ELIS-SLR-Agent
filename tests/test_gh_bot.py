from __future__ import annotations

from pathlib import Path

from scripts import gh_bot


class _Result:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _fake_home() -> Path:
    return Path.cwd() / "tests" / "outputs" / "gh_bot_home"


def test_check_only_passes_with_expected_login(monkeypatch, capsys) -> None:
    fake_home = _fake_home()
    monkeypatch.setattr(gh_bot.Path, "home", lambda: fake_home)
    monkeypatch.setenv("CODEX_BOT_TOKEN", "tok-codex")

    calls: list[tuple[list[str], str, str]] = []

    def fake_run_gh(
        gh_args: list[str], *, env: dict[str, str], capture_output: bool = True
    ) -> _Result:
        calls.append((gh_args, env["GH_TOKEN"], env["GH_CONFIG_DIR"]))
        return _Result(0, stdout="elis-codex-bot\n")

    monkeypatch.setattr(gh_bot, "_run_gh", fake_run_gh)

    rc = gh_bot.main(["gh_bot.py", "codex", "--check-only"])

    assert rc == 0
    out = capsys.readouterr().out
    assert "authenticated via gh as elis-codex-bot" in out
    assert "gh bot verification PASS" in out
    assert calls == [
        (
            ["api", "/user", "--jq", ".login"],
            "tok-codex",
            str(fake_home / ".config" / "elis-gh" / "codex"),
        )
    ]


def test_check_only_fails_when_login_is_wrong(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gh_bot.Path, "home", lambda: _fake_home())
    monkeypatch.setenv("CLAUDE_BOT_TOKEN", "tok-claude")

    def fake_run_gh(
        gh_args: list[str], *, env: dict[str, str], capture_output: bool = True
    ) -> _Result:
        return _Result(0, stdout="rochasamurai\n")

    monkeypatch.setattr(gh_bot, "_run_gh", fake_run_gh)

    rc = gh_bot.main(["gh_bot.py", "claude", "--check-only"])

    assert rc == 1
    err = capsys.readouterr().err
    assert "authenticated as 'rochasamurai'" in err
    assert "expected 'elis-claude-bot'" in err


def test_run_command_executes_requested_gh_args(monkeypatch) -> None:
    monkeypatch.setattr(gh_bot.Path, "home", lambda: _fake_home())
    monkeypatch.setenv("PM_BOT_TOKEN", "tok-pm")

    calls: list[tuple[list[str], bool, str]] = []

    def fake_run_gh(
        gh_args: list[str], *, env: dict[str, str], capture_output: bool = True
    ) -> _Result:
        calls.append((gh_args, capture_output, env["GH_TOKEN"]))
        if gh_args[:3] == ["api", "/user", "--jq"]:
            return _Result(0, stdout="elis-pm-bot\n")
        return _Result(0)

    monkeypatch.setattr(gh_bot, "_run_gh", fake_run_gh)

    rc = gh_bot.main(
        [
            "gh_bot.py",
            "pm",
            "--",
            "pr",
            "comment",
            "320",
            "--body",
            "Gate-1 posted.",
        ]
    )

    assert rc == 0
    assert calls == [
        (["api", "/user", "--jq", ".login"], True, "tok-pm"),
        (["pr", "comment", "320", "--body", "Gate-1 posted."], False, "tok-pm"),
    ]


def test_missing_token_fails_without_leaking_secret(capsys, monkeypatch) -> None:
    monkeypatch.delenv("CODEX_BOT_TOKEN", raising=False)

    rc = gh_bot.main(["gh_bot.py", "codex", "--check-only"])

    assert rc == 1
    err = capsys.readouterr().err
    assert "CODEX_BOT_TOKEN is not set" in err
