from __future__ import annotations

import json
import subprocess

from scripts import verify_codex_auth


def _prepare_oauth_auth_file(tmp_path, monkeypatch, payload=None):
    monkeypatch.setenv("HOME", str(tmp_path))
    auth_dir = tmp_path / ".codex"
    auth_dir.mkdir()
    auth_path = auth_dir / "auth.json"
    data = (
        payload
        if payload is not None
        else {
            "auth_mode": "chatgpt",
            "tokens": {"refresh_token": "refresh-x", "access_token": "access-x"},
        }
    )
    auth_path.write_text(json.dumps(data), encoding="utf-8")
    return auth_path


def _patch_codex_cli(monkeypatch, returncode=0, stdout="0.0.0", stderr=""):
    monkeypatch.setattr(
        verify_codex_auth.shutil,
        "which",
        lambda _cmd: "/usr/local/bin/codex",
    )
    monkeypatch.setattr(
        verify_codex_auth.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            args=["codex", "--version"],
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        ),
    )


def test_invalid_when_no_credentials(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(verify_codex_auth.shutil, "which", lambda _cmd: None)

    assert verify_codex_auth.main([]) == 1
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Invalid authentication" in combined
    assert "INFO: 'codex' CLI not found on PATH (expected on elis-server)." in combined


def test_valid_oauth_authentication(tmp_path, monkeypatch, capsys):
    _prepare_oauth_auth_file(tmp_path, monkeypatch)
    _patch_codex_cli(monkeypatch)

    assert verify_codex_auth.main([]) == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Valid OAuth authentication" in combined
    assert "auth_mode: chatgpt" in combined
    assert "refresh_token present: yes" in combined


def test_valid_api_key_fallback_when_oauth_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-key")
    monkeypatch.setattr(verify_codex_auth.shutil, "which", lambda _cmd: None)

    assert verify_codex_auth.main([]) == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Valid API Key authentication" in combined
    assert "OPENAI_API_KEY env present" in combined
    assert "INFO: 'codex' CLI not found on PATH (expected on elis-server)." in combined


def test_invalid_when_cli_version_command_fails(tmp_path, monkeypatch, capsys):
    _prepare_oauth_auth_file(tmp_path, monkeypatch)
    _patch_codex_cli(monkeypatch, returncode=1, stdout="", stderr="boom")

    assert verify_codex_auth.main([]) == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Valid OAuth authentication" in combined
    assert "WARN: 'codex --version' exited 1" in combined


def test_passes_without_leaking_api_key(tmp_path, monkeypatch, capsys):
    api_key = "sk-openai-secret-value"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", api_key)
    _patch_codex_cli(monkeypatch)

    assert verify_codex_auth.main([]) == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "RESULT: Valid API Key authentication" in combined
    assert "length=" in combined
    assert api_key not in combined
