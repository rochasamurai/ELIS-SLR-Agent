"""
verify_bot_config.py — PE-AUTO-01

Verifies that the three ELIS bot account PATs are configured and that each
token authenticates successfully against the GitHub API.

Exit codes:
    0 — all three tokens are set and each authenticates as the expected login
    1 — one or more tokens missing, unauthenticated, or wrong login

Usage:
    python scripts/verify_bot_config.py

Security rule §13: token values are never printed. Only token length,
login name, and boolean permission flags are reported.
"""

from __future__ import annotations

import os
import sys
from urllib import request, error as url_error
import json


_BOTS: list[tuple[str, str, bool]] = [
    # (env_var, expected_login, require_workflows_permission)
    ("CODEX_BOT_TOKEN", "elis-codex-bot", False),
    ("CLAUDE_BOT_TOKEN", "elis-claude-bot", False),
    ("PM_BOT_TOKEN", "elis-pm-bot", True),
]


def _github_get(path: str, token: str) -> dict:
    url = f"https://api.github.com{path}"
    req = request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except url_error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc


def _check_workflows_permission(token: str, login: str) -> bool:
    """Return True if the token has workflows permission on the repository."""
    try:
        data = _github_get(
            "/repos/rochasamurai/ELIS-SLR-Agent/collaborators/" f"{login}/permission",
            token,
        )
        role = data.get("role_name", "")
        # admin role has full access including workflows
        return role in ("admin", "maintain")
    except RuntimeError:
        return False


def main() -> int:
    all_ok = True

    for env_var, expected_login, need_workflows in _BOTS:
        token = os.environ.get(env_var, "")
        if not token:
            print(
                f"FAIL: {env_var} is not set in environment.",
                file=sys.stderr,
            )
            all_ok = False
            continue

        print(f"OK: {env_var} set (length={len(token)})")

        try:
            user_data = _github_get("/user", token)
        except RuntimeError as exc:
            print(
                f"FAIL: {env_var} could not authenticate — {exc}",
                file=sys.stderr,
            )
            all_ok = False
            continue

        actual_login = user_data.get("login", "")
        if actual_login != expected_login:
            print(
                f"FAIL: {env_var} authenticated as '{actual_login}', "
                f"expected '{expected_login}'.",
                file=sys.stderr,
            )
            all_ok = False
            continue

        print(f"OK: {expected_login} authenticated — login={actual_login}")

        if need_workflows:
            has_perm = _check_workflows_permission(token, expected_login)
            if not has_perm:
                print(
                    f"FAIL: {expected_login} does not have admin/maintain "
                    f"permission (required for workflows).",
                    file=sys.stderr,
                )
                all_ok = False
            else:
                print(f"OK: {expected_login} has workflows permission")

    if not all_ok:
        return 1

    print()
    print("bot config verification PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
