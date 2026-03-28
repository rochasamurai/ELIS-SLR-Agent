from __future__ import annotations

import json
from unittest.mock import patch, MagicMock
from urllib import error as url_error

from scripts import verify_bot_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(payload: dict, status: int = 200):
    """Return a mock context-manager response that yields JSON bytes."""
    raw = json.dumps(payload).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw
    mock_resp.status = status
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def _urlopen_login(login: str):
    """Return a urlopen side-effect that always yields the given login."""

    def _side_effect(req, timeout=10):
        return _make_response({"login": login})

    return _side_effect


# ---------------------------------------------------------------------------
# Failure: missing tokens
# ---------------------------------------------------------------------------


def test_fails_when_all_tokens_missing(monkeypatch, capsys):
    for var in ("CODEX_BOT_TOKEN", "CLAUDE_BOT_TOKEN", "PM_BOT_TOKEN"):
        monkeypatch.delenv(var, raising=False)

    rc = verify_bot_config.main()

    assert rc == 1
    err = capsys.readouterr().err
    assert "CODEX_BOT_TOKEN is not set" in err
    assert "CLAUDE_BOT_TOKEN is not set" in err
    assert "PM_BOT_TOKEN is not set" in err


def test_fails_when_one_token_missing(monkeypatch, capsys):
    monkeypatch.setenv("CODEX_BOT_TOKEN", "tok-codex")
    monkeypatch.setenv("CLAUDE_BOT_TOKEN", "tok-claude")
    monkeypatch.delenv("PM_BOT_TOKEN", raising=False)

    with patch(
        "scripts.verify_bot_config.request.urlopen",
        side_effect=[
            _make_response({"login": "elis-codex-bot"}),
            _make_response({"login": "elis-claude-bot"}),
        ],
    ):
        rc = verify_bot_config.main()

    assert rc == 1
    assert "PM_BOT_TOKEN is not set" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Failure: wrong login
# ---------------------------------------------------------------------------


def test_fails_when_wrong_login(monkeypatch, capsys):
    monkeypatch.setenv("CODEX_BOT_TOKEN", "tok-codex")
    monkeypatch.setenv("CLAUDE_BOT_TOKEN", "tok-claude")
    monkeypatch.setenv("PM_BOT_TOKEN", "tok-pm")

    with patch(
        "scripts.verify_bot_config.request.urlopen",
        side_effect=[
            _make_response({"login": "wrong-user"}),  # codex wrong
            _make_response({"login": "elis-claude-bot"}),
            _make_response({"login": "elis-pm-bot"}),
            _make_response({"role_name": "admin"}),  # pm permission check
        ],
    ):
        rc = verify_bot_config.main()

    assert rc == 1
    err = capsys.readouterr().err
    assert "authenticated as 'wrong-user'" in err
    assert "expected 'elis-codex-bot'" in err


# ---------------------------------------------------------------------------
# Failure: HTTP error from GitHub API
# ---------------------------------------------------------------------------


def test_fails_on_api_http_error(monkeypatch, capsys):
    monkeypatch.setenv("CODEX_BOT_TOKEN", "bad-token")
    monkeypatch.setenv("CLAUDE_BOT_TOKEN", "tok-claude")
    monkeypatch.setenv("PM_BOT_TOKEN", "tok-pm")

    http_err = url_error.HTTPError(
        url="https://api.github.com/user",
        code=401,
        msg="Unauthorized",
        hdrs=None,  # type: ignore[arg-type]
        fp=MagicMock(read=lambda: b'{"message":"Bad credentials"}'),
    )

    with patch(
        "scripts.verify_bot_config.request.urlopen",
        side_effect=[
            http_err,
            _make_response({"login": "elis-claude-bot"}),
            _make_response({"login": "elis-pm-bot"}),
            _make_response({"role_name": "admin"}),
        ],
    ):
        rc = verify_bot_config.main()

    assert rc == 1
    assert "could not authenticate" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Failure: pm-bot missing workflows permission
# ---------------------------------------------------------------------------


def test_fails_when_pm_bot_lacks_admin_role(monkeypatch, capsys):
    monkeypatch.setenv("CODEX_BOT_TOKEN", "tok-codex")
    monkeypatch.setenv("CLAUDE_BOT_TOKEN", "tok-claude")
    monkeypatch.setenv("PM_BOT_TOKEN", "tok-pm")

    with patch(
        "scripts.verify_bot_config.request.urlopen",
        side_effect=[
            _make_response({"login": "elis-codex-bot"}),
            _make_response({"login": "elis-claude-bot"}),
            _make_response({"login": "elis-pm-bot"}),
            _make_response({"role_name": "write"}),  # not admin/maintain
        ],
    ):
        rc = verify_bot_config.main()

    assert rc == 1
    assert "does not have admin/maintain repository role" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Success: all tokens set, correct logins, pm-bot has permission
# ---------------------------------------------------------------------------


def test_passes_all_bots_configured(monkeypatch, capsys):
    monkeypatch.setenv("CODEX_BOT_TOKEN", "tok-codex-secret")
    monkeypatch.setenv("CLAUDE_BOT_TOKEN", "tok-claude-secret")
    monkeypatch.setenv("PM_BOT_TOKEN", "tok-pm-secret")

    with patch(
        "scripts.verify_bot_config.request.urlopen",
        side_effect=[
            _make_response({"login": "elis-codex-bot"}),
            _make_response({"login": "elis-claude-bot"}),
            _make_response({"login": "elis-pm-bot"}),
            _make_response({"role_name": "admin"}),
        ],
    ):
        rc = verify_bot_config.main()

    assert rc == 0
    out = capsys.readouterr().out
    assert "bot config verification PASS" in out


def test_passes_does_not_leak_token_values(monkeypatch, capsys):
    secret_codex = "tok-codex-DO-NOT-PRINT"
    secret_claude = "tok-claude-DO-NOT-PRINT"
    secret_pm = "tok-pm-DO-NOT-PRINT"

    monkeypatch.setenv("CODEX_BOT_TOKEN", secret_codex)
    monkeypatch.setenv("CLAUDE_BOT_TOKEN", secret_claude)
    monkeypatch.setenv("PM_BOT_TOKEN", secret_pm)

    with patch(
        "scripts.verify_bot_config.request.urlopen",
        side_effect=[
            _make_response({"login": "elis-codex-bot"}),
            _make_response({"login": "elis-claude-bot"}),
            _make_response({"login": "elis-pm-bot"}),
            _make_response({"role_name": "admin"}),
        ],
    ):
        rc = verify_bot_config.main()

    assert rc == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    for secret in (secret_codex, secret_claude, secret_pm):
        assert secret not in combined, f"Token value leaked into output: {secret}"
    assert "length=" in combined
    assert "admin repository role" in combined
