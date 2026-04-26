from __future__ import annotations

import json
import subprocess

from scripts import verify_claude_auth


def _prepare_oauth_credentials(tmp_path, monkeypatch, payload=None):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("CLAUDE_CREDENTIALS_JSON", '{"present": true}')
    creds_dir = tmp_path / ".claude"
    creds_dir.mkdir()
    creds_path = creds_dir / ".credentials.json"
    data = payload if payload is not None else {"claudeAiOauth": {"accessToken": "x"}}
    creds_path.write_text(json.dumps(data), encoding="utf-8")
    return creds_path


def _patch_claude_cli(monkeypatch, returncode=0, stdout="1.2.3", stderr=""):
    monkeypatch.setattr(
        verify_claude_auth.shutil,
        "which",
        lambda _cmd: "/usr/local/bin/claude",
    )
    monkeypatch.setattr(
        verify_claude_auth.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            args=["claude", "--version"],
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        ),
    )


def test_invalid_when_credentials_env_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("CLAUDE_CREDENTIALS_JSON", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(verify_claude_auth.shutil, "which", lambda _cmd: None)

    assert verify_claude_auth.main([]) == 1
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Invalid authentication" in combined
    assert "INFO: 'claude' CLI not found on PATH (expected on elis-server)." in combined


def test_valid_oauth_authentication(tmp_path, monkeypatch, capsys):
    _prepare_oauth_credentials(tmp_path, monkeypatch)
    _patch_claude_cli(monkeypatch)

    assert verify_claude_auth.main([]) == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Valid OAuth authentication" in combined
    assert "claudeAiOauth entry present: yes" in combined


def test_valid_api_key_fallback_when_oauth_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-test-key")
    monkeypatch.delenv("CLAUDE_CREDENTIALS_JSON", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(verify_claude_auth.shutil, "which", lambda _cmd: None)

    assert verify_claude_auth.main([]) == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Valid API Key authentication" in combined
    assert "ANTHROPIC_API_KEY env present" in combined
    assert "INFO: 'claude' CLI not found on PATH (expected on elis-server)." in combined


def test_invalid_when_credentials_file_missing_and_no_fallback(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("CLAUDE_CREDENTIALS_JSON", '{"present": true}')
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

    assert verify_claude_auth.main([]) == 1
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Invalid authentication" in combined
    assert (
        "CLAUDE_CREDENTIALS_JSON is set but ~/.claude/.credentials.json is missing."
        in combined
    )


def test_fails_when_claude_version_command_fails(tmp_path, monkeypatch, capsys):
    _prepare_oauth_credentials(tmp_path, monkeypatch)
    _patch_claude_cli(monkeypatch, returncode=1, stdout="", stderr="boom")

    assert verify_claude_auth.main([]) == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Valid OAuth authentication" in combined
    assert "WARN: 'claude --version' exited 1" in combined


def test_passes_without_leaking_credentials_json(tmp_path, monkeypatch, capsys):
    credentials_json = '{"accessToken":"sk-ant...alue"}'
    _prepare_oauth_credentials(tmp_path, monkeypatch)
    monkeypatch.setenv("CLAUDE_CREDENTIALS_JSON", credentials_json)
    _patch_claude_cli(monkeypatch)

    assert verify_claude_auth.main([]) == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Valid OAuth authentication" in combined
    assert "length=" in combined
    assert credentials_json not in combined
