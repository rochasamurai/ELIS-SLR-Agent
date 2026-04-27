from __future__ import annotations

import json
import subprocess

from scripts import verify_claude_auth


def _prepare_oauth_credentials(tmp_path, monkeypatch, payload=None):
    monkeypatch.setenv("HOME", str(tmp_path))
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


def test_invalid_when_no_credentials(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(verify_claude_auth.shutil, "which", lambda _cmd: None)

    assert verify_claude_auth.main([]) == 1
    combined = capsys.readouterr().out
    assert "RESULT: Invalid authentication" in combined
    assert "OAuth credential file not found at ~/.claude/.credentials.json." in combined
    assert (
        "NEXT STEP: Run `claude` interactively on elis-server to refresh OAuth, or set ANTHROPIC_API_KEY as the fallback."
        in combined
    )


def test_valid_oauth_authentication(tmp_path, monkeypatch, capsys):
    _prepare_oauth_credentials(tmp_path, monkeypatch)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    _patch_claude_cli(monkeypatch)

    assert verify_claude_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid OAuth authentication" in combined
    assert "claudeAiOauth entry present: yes" in combined
    assert "ANTHROPIC_API_KEY fallback present: no" in combined


def test_valid_api_key_fallback_when_oauth_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-test-key")
    monkeypatch.setattr(verify_claude_auth.shutil, "which", lambda _cmd: None)

    assert verify_claude_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid API Key authentication" in combined
    assert "WARN: OAuth credential file not found" in combined
    assert "WARN: Falling back to ANTHROPIC_API_KEY." in combined
    assert "ANTHROPIC_API_KEY env present" in combined


def test_valid_api_key_fallback_when_oauth_key_missing(tmp_path, monkeypatch, capsys):
    _prepare_oauth_credentials(tmp_path, monkeypatch, payload={"other": True})
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-test-key")
    monkeypatch.setattr(verify_claude_auth.shutil, "which", lambda _cmd: None)

    assert verify_claude_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid API Key authentication" in combined
    assert "does not contain claudeAiOauth" in combined
    assert (
        "WARN: Falling back to ANTHROPIC_API_KEY because OAuth could not be verified."
        in combined
    )


def test_invalid_when_oauth_key_missing_and_no_fallback(tmp_path, monkeypatch, capsys):
    _prepare_oauth_credentials(tmp_path, monkeypatch, payload={"other": True})
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(verify_claude_auth.shutil, "which", lambda _cmd: None)

    assert verify_claude_auth.main([]) == 1
    combined = capsys.readouterr().out
    assert "RESULT: Invalid authentication" in combined
    assert "credentials file missing 'claudeAiOauth' key." in combined


def test_fails_when_claude_version_command_fails(tmp_path, monkeypatch, capsys):
    _prepare_oauth_credentials(tmp_path, monkeypatch)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    _patch_claude_cli(monkeypatch, returncode=1, stdout="", stderr="boom")

    assert verify_claude_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid OAuth authentication" in combined
    assert "WARN: local CLI --version exited 1" in combined


def test_passes_without_leaking_api_key(tmp_path, monkeypatch, capsys):
    api_key = "anthropic-secret-value"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("ANTHROPIC_API_KEY", api_key)
    monkeypatch.setattr(verify_claude_auth.shutil, "which", lambda _cmd: None)

    assert verify_claude_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid API Key authentication" in combined
    assert "length=" in combined
    assert api_key not in combined
