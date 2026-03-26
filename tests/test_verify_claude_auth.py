from __future__ import annotations

import subprocess

from scripts import verify_claude_auth


def test_fails_when_setup_token_missing(monkeypatch, capsys):
    monkeypatch.delenv("CLAUDE_SETUP_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    assert verify_claude_auth.main() == 1
    captured = capsys.readouterr()
    assert "CLAUDE_SETUP_TOKEN is not set" in captured.err


def test_fails_when_anthropic_api_key_present(monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_SETUP_TOKEN", "token-123")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api")

    assert verify_claude_auth.main() == 1
    captured = capsys.readouterr()
    assert "ANTHROPIC_API_KEY is set" in captured.err


def test_fails_when_claude_missing(monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_SETUP_TOKEN", "token-123")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(verify_claude_auth.shutil, "which", lambda _cmd: None)

    assert verify_claude_auth.main() == 1
    captured = capsys.readouterr()
    assert "'claude' CLI not found on PATH." in captured.err


def test_fails_when_claude_version_command_fails(monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_SETUP_TOKEN", "token-123")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(
        verify_claude_auth.shutil, "which", lambda _cmd: "/usr/local/bin/claude"
    )
    monkeypatch.setattr(
        verify_claude_auth.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            args=["claude", "--version"],
            returncode=1,
            stdout="",
            stderr="boom",
        ),
    )

    assert verify_claude_auth.main() == 1
    captured = capsys.readouterr()
    assert "'claude --version' exited 1" in captured.err


def test_passes_without_leaking_token(monkeypatch, capsys):
    token = "sk-ant-st-secret-value"
    monkeypatch.setenv("CLAUDE_SETUP_TOKEN", token)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(
        verify_claude_auth.shutil, "which", lambda _cmd: "/usr/local/bin/claude"
    )
    monkeypatch.setattr(
        verify_claude_auth.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            args=["claude", "--version"],
            returncode=0,
            stdout="1.2.3",
            stderr="",
        ),
    )

    assert verify_claude_auth.main() == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "claude auth verification PASS" in combined
    assert "length=" in combined
    assert token not in combined
