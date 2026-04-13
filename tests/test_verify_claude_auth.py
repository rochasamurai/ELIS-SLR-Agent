from __future__ import annotations

import json
import subprocess

from scripts import verify_claude_auth


def _write_credentials_file(tmp_path, monkeypatch, payload=None):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("CLAUDE_CREDENTIALS_JSON", '{"present": true}')
    creds_dir = tmp_path / ".claude"
    creds_dir.mkdir()
    creds_path = creds_dir / ".credentials.json"
    data = payload if payload is not None else {"claudeAiOauth": {"accessToken": "x"}}
    creds_path.write_text(json.dumps(data), encoding="utf-8")
    return creds_path


def test_fails_when_credentials_env_missing(monkeypatch, capsys):
    monkeypatch.delenv("CLAUDE_CREDENTIALS_JSON", raising=False)

    assert verify_claude_auth.main() == 1
    captured = capsys.readouterr()
    assert "CLAUDE_CREDENTIALS_JSON is not set" in captured.err


def test_fails_when_credentials_file_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("CLAUDE_CREDENTIALS_JSON", '{"present": true}')

    assert verify_claude_auth.main() == 1
    captured = capsys.readouterr()
    assert "credentials file not found" in captured.err


def test_fails_when_credentials_file_lacks_oauth_key(tmp_path, monkeypatch, capsys):
    _write_credentials_file(tmp_path, monkeypatch, payload={"unexpected": True})

    assert verify_claude_auth.main() == 1
    captured = capsys.readouterr()
    assert "missing 'claudeAiOauth' key" in captured.err


def test_fails_when_claude_missing(tmp_path, monkeypatch, capsys):
    _write_credentials_file(tmp_path, monkeypatch)
    monkeypatch.setattr(verify_claude_auth.shutil, "which", lambda _cmd: None)

    assert verify_claude_auth.main() == 1
    captured = capsys.readouterr()
    assert "'claude' CLI not found on PATH." in captured.err


def test_fails_when_claude_version_command_fails(tmp_path, monkeypatch, capsys):
    _write_credentials_file(tmp_path, monkeypatch)
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


def test_passes_without_leaking_credentials_json(tmp_path, monkeypatch, capsys):
    credentials_json = '{"accessToken":"sk-ant-st-secret-value"}'
    _write_credentials_file(tmp_path, monkeypatch)
    monkeypatch.setenv("CLAUDE_CREDENTIALS_JSON", credentials_json)
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
    assert credentials_json not in combined
