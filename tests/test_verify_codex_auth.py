from __future__ import annotations

import json
import subprocess

from scripts import verify_codex_auth


def _prepare_oauth_auth_file(tmp_path, monkeypatch, payload=None, *, legacy=False):
    monkeypatch.setenv("HOME", str(tmp_path))
    auth_dir = tmp_path / ".config" / "openai" if legacy else tmp_path / ".codex"
    auth_dir.mkdir(parents=True)
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
    combined = capsys.readouterr().out
    assert "RESULT: Invalid authentication" in combined
    assert "OAuth credential file not found." in combined
    assert (
        "NEXT STEP: Run `codex` interactively on elis-server to refresh OAuth, or set OPENAI_API_KEY as the fallback."
        in combined
    )


def test_valid_oauth_authentication(tmp_path, monkeypatch, capsys):
    _prepare_oauth_auth_file(tmp_path, monkeypatch)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    _patch_codex_cli(monkeypatch)

    assert verify_codex_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid OAuth authentication" in combined
    assert "auth_mode: chatgpt" in combined
    assert "refresh_token present: yes" in combined


def test_valid_oauth_authentication_from_legacy_path(tmp_path, monkeypatch, capsys):
    _prepare_oauth_auth_file(tmp_path, monkeypatch, legacy=True)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(verify_codex_auth.shutil, "which", lambda _cmd: None)

    assert verify_codex_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid OAuth authentication" in combined
    assert ".config/openai/auth.json" in combined


def test_valid_api_key_fallback_when_oauth_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-key")
    monkeypatch.setattr(verify_codex_auth.shutil, "which", lambda _cmd: None)

    assert verify_codex_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid API Key authentication" in combined
    assert "WARN: OAuth credential file not found" in combined
    assert "WARN: Falling back to OPENAI_API_KEY." in combined
    assert "OPENAI_API_KEY env present" in combined


def test_valid_api_key_fallback_when_auth_file_has_no_oauth_markers(
    tmp_path, monkeypatch, capsys
):
    _prepare_oauth_auth_file(tmp_path, monkeypatch, payload={"auth_mode": "api_key"})
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-key")
    monkeypatch.setattr(verify_codex_auth.shutil, "which", lambda _cmd: None)

    assert verify_codex_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid API Key authentication" in combined
    assert "OAuth markers are absent" in combined
    assert (
        "WARN: Falling back to OPENAI_API_KEY because OAuth could not be verified."
        in combined
    )


def test_invalid_when_auth_file_has_no_oauth_markers_and_no_fallback(
    tmp_path, monkeypatch, capsys
):
    _prepare_oauth_auth_file(tmp_path, monkeypatch, payload={"auth_mode": "api_key"})
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(verify_codex_auth.shutil, "which", lambda _cmd: None)

    assert verify_codex_auth.main([]) == 1
    combined = capsys.readouterr().out
    assert "RESULT: Invalid authentication" in combined
    assert "OAuth markers are absent" in combined


def test_invalid_when_cli_version_command_fails(tmp_path, monkeypatch, capsys):
    _prepare_oauth_auth_file(tmp_path, monkeypatch)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    _patch_codex_cli(monkeypatch, returncode=1, stdout="", stderr="boom")

    assert verify_codex_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid OAuth authentication" in combined
    assert "WARN: local CLI --version exited 1" in combined


def test_passes_without_leaking_api_key(tmp_path, monkeypatch, capsys):
    api_key = "sk-openai-secret-value"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", api_key)
    monkeypatch.setattr(verify_codex_auth.shutil, "which", lambda _cmd: None)

    assert verify_codex_auth.main([]) == 0
    combined = capsys.readouterr().out
    assert "RESULT: Valid API Key authentication" in combined
    assert "length=" in combined
    assert api_key not in combined
