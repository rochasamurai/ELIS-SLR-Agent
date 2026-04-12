"""Run GitHub CLI commands under an explicit ELIS bot identity.

PE-AUTO-12 introduces this helper for `elis-server` and other host-side
runtime paths where ambient `gh` authentication may otherwise fall back to the
repository owner's account.

Usage examples:
    python scripts/gh_bot.py codex --check-only
    python scripts/gh_bot.py claude -- pr review 123 --approve --body "PASS"
    python scripts/gh_bot.py pm -- pr comment 123 --body "Gate-1 posted."

Security rule §13:
- token values are read from environment variables only
- token values are never printed
- the helper verifies the bot login before executing the requested `gh` command
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BotIdentity:
    bot: str
    env_var: str
    expected_login: str
    config_dir_name: str


_BOTS: dict[str, BotIdentity] = {
    "codex": BotIdentity(
        bot="codex",
        env_var="CODEX_BOT_TOKEN",
        expected_login="elis-codex-bot",
        config_dir_name="codex",
    ),
    "claude": BotIdentity(
        bot="claude",
        env_var="CLAUDE_BOT_TOKEN",
        expected_login="elis-claude-bot",
        config_dir_name="claude",
    ),
    "pm": BotIdentity(
        bot="pm",
        env_var="PM_BOT_TOKEN",
        expected_login="elis-pm-bot",
        config_dir_name="pm",
    ),
}


def _config_dir(identity: BotIdentity) -> Path:
    return Path.home() / ".config" / "elis-gh" / identity.config_dir_name


def _gh_env(identity: BotIdentity) -> dict[str, str]:
    token = os.environ.get(identity.env_var, "")
    if not token:
        raise RuntimeError(
            f"{identity.env_var} is not set. Export it in the current shell or "
            "source it from secure host storage before running gh_bot.py."
        )

    config_dir = _config_dir(identity)
    config_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["GH_TOKEN"] = token
    env["GH_CONFIG_DIR"] = str(config_dir)
    return env


def _run_gh(
    gh_args: list[str],
    *,
    env: dict[str, str],
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *gh_args],
        capture_output=capture_output,
        text=True,
        check=False,
        env=env,
        timeout=60,
    )


def verify_identity(identity: BotIdentity) -> str:
    env = _gh_env(identity)
    result = _run_gh(["api", "/user", "--jq", ".login"], env=env)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "gh api /user failed."
        raise RuntimeError(
            f"{identity.env_var} could not authenticate via gh — {stderr}"
        )

    login = result.stdout.strip()
    if login != identity.expected_login:
        raise RuntimeError(
            f"{identity.env_var} authenticated as '{login}', expected "
            f"'{identity.expected_login}'."
        )

    return login


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run GitHub CLI commands under an explicit ELIS bot identity."
    )
    parser.add_argument("bot", choices=sorted(_BOTS))
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Verify the selected bot login and exit without running a gh command.",
    )
    args, gh_args = parser.parse_known_args(argv[1:])
    args.gh_args = gh_args
    return args


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    args = parse_args(argv)
    identity = _BOTS[args.bot]

    try:
        login = verify_identity(identity)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        f"OK: {identity.env_var} authenticated via gh as {login} "
        f"(GH_CONFIG_DIR={_config_dir(identity)})"
    )

    if args.check_only:
        print("gh bot verification PASS")
        return 0

    gh_args = list(args.gh_args)
    if gh_args and gh_args[0] == "--":
        gh_args = gh_args[1:]
    if not gh_args:
        print(
            "FAIL: no gh command provided. Example: "
            "python scripts/gh_bot.py claude -- pr review 123 --approve",
            file=sys.stderr,
        )
        return 1

    env = _gh_env(identity)
    result = _run_gh(gh_args, env=env, capture_output=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
