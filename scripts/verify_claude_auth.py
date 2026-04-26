"""
verify_claude_auth.py — PE-AUTH-02

Verifies whether the Claude Code CLI is authenticated in the current environment.
Primary mechanism: OAuth-backed CLAUDE_CREDENTIALS_JSON.
Fallback mechanism: ANTHROPIC_API_KEY.

Exit codes:
    0 — valid OAuth or API key authentication
    1 — invalid or missing authentication / CLI prerequisites

Usage:
    python scripts/verify_claude_auth.py [--json]

Security rule §13: never prints credential values.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict


@dataclass
class VerificationResult:
    auth_mode: str
    valid: bool
    source: str
    details: list[str]
    next_step: str | None = None


def _credentials_file() -> pathlib.Path:
    return pathlib.Path.home() / ".claude" / ".credentials.json"


def classify_auth() -> VerificationResult:
    credentials_json = os.environ.get("CLAUDE_CREDENTIALS_JSON", "")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    creds_path = _credentials_file()

    details: list[str] = []

    # Primary path: OAuth-backed credentials file injected from the secret.
    if credentials_json:
        details.append(
            f"CLAUDE_CREDENTIALS_JSON env present (length={len(credentials_json)})"
        )
        if creds_path.exists():
            try:
                data = json.loads(creds_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                if api_key:
                    return VerificationResult(
                        auth_mode="api_key",
                        valid=True,
                        source="env:ANTHROPIC_API_KEY",
                        details=[
                            f"primary OAuth file unreadable: {exc}",
                            f"ANTHROPIC_API_KEY env present (length={len(api_key)})",
                        ],
                    )
                return VerificationResult(
                    auth_mode="invalid",
                    valid=False,
                    source=str(creds_path),
                    details=[f"credentials file unreadable: {exc}"],
                    next_step=(
                        "Ask PO to run 'claude setup-token' on a machine with browser access "
                        "(or otherwise refresh Claude Code credentials) and then update "
                        "CLAUDE_CREDENTIALS_JSON from the secret source; or set "
                        "ANTHROPIC_API_KEY as the fallback."
                    ),
                )

            if "claudeAiOauth" in data:
                if api_key:
                    details.append("ANTHROPIC_API_KEY fallback present: yes")
                details.append(f"credentials file: {creds_path}")
                details.append("claudeAiOauth entry present: yes")
                return VerificationResult(
                    auth_mode="oauth",
                    valid=True,
                    source=str(creds_path),
                    details=details,
                )

            if api_key:
                return VerificationResult(
                    auth_mode="api_key",
                    valid=True,
                    source="env:ANTHROPIC_API_KEY",
                    details=[
                        f"credentials file missing claudeAiOauth: {creds_path}",
                        f"ANTHROPIC_API_KEY env present (length={len(api_key)})",
                    ],
                )

            return VerificationResult(
                auth_mode="invalid",
                valid=False,
                source=str(creds_path),
                details=["credentials file missing 'claudeAiOauth' key."],
                next_step=(
                    "Ask PO to run 'claude setup-token' on a machine with browser access "
                    "(or otherwise refresh Claude Code credentials) and then update "
                    "CLAUDE_CREDENTIALS_JSON from the secret source; or set "
                    "ANTHROPIC_API_KEY as the fallback."
                ),
            )

        if api_key:
            return VerificationResult(
                auth_mode="api_key",
                valid=True,
                source="env:ANTHROPIC_API_KEY",
                details=[
                    "OAuth credentials file not found, but fallback API key is present.",
                    f"ANTHROPIC_API_KEY env present (length={len(api_key)})",
                ],
            )

        return VerificationResult(
            auth_mode="invalid",
            valid=False,
            source=str(creds_path),
            details=[
                "CLAUDE_CREDENTIALS_JSON is set but ~/.claude/.credentials.json is missing.",
            ],
            next_step=(
                "Ask PO to refresh CLAUDE_CREDENTIALS_JSON from the secret source "
                "or set ANTHROPIC_API_KEY as the fallback."
            ),
        )

    # Fallback path: API key authentication.
    if api_key:
        return VerificationResult(
            auth_mode="api_key",
            valid=True,
            source="env:ANTHROPIC_API_KEY",
            details=[f"ANTHROPIC_API_KEY env present (length={len(api_key)})"],
        )

    return VerificationResult(
        auth_mode="invalid",
        valid=False,
        source="missing",
        details=["CLAUDE_CREDENTIALS_JSON is not set in environment."],
        next_step=(
            "Ask PO to run 'claude setup-token' on a machine with browser access "
            "(or otherwise refresh Claude Code credentials) and then update "
            "CLAUDE_CREDENTIALS_JSON from the secret source; or set "
            "ANTHROPIC_API_KEY as the fallback."
        ),
    )


def verify_claude_cli(details: list[str]) -> tuple[bool, str | None]:
    claude_path = shutil.which("claude")
    if claude_path is None:
        details.append("FAIL: 'claude' CLI not found on PATH.")
        details.append(
            "Install Claude Code with the official Anthropic installer before retrying."
        )
        return False, None

    details.append(f"claude CLI: {claude_path}")
    result = subprocess.run(
        ["claude", "--version"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    if result.returncode != 0:
        details.append(f"FAIL: 'claude --version' exited {result.returncode}")
        stderr = result.stderr.strip()
        if stderr:
            details.append(stderr)
        return False, None

    version = result.stdout.strip() or result.stderr.strip() or "<unknown>"
    details.append(f"claude --version: {version}")
    return True, version


def render_text(
    result: VerificationResult, cli_ok: bool, cli_version: str | None
) -> str:
    lines: list[str] = []
    if result.valid and cli_ok:
        lines.append(
            "RESULT: Valid OAuth authentication"
            if result.auth_mode == "oauth"
            else "RESULT: Valid API Key authentication"
        )
    else:
        lines.append("RESULT: Invalid authentication")

    lines.append(f"AUTH MODE: {result.auth_mode}")
    lines.append(f"SOURCE: {result.source}")
    if cli_version is not None:
        lines.append(f"CLI VERSION: {cli_version}")
    for detail in result.details:
        lines.append(detail)
    if result.valid and cli_ok:
        lines.append("NEXT STEP: none")
    elif result.next_step:
        lines.append(f"NEXT STEP: {result.next_step}")
    return "\n".join(lines) + "\n"


def render_json(
    result: VerificationResult, cli_ok: bool, cli_version: str | None
) -> str:
    payload = asdict(result)
    payload["cli_ok"] = cli_ok
    payload["cli_version"] = cli_version
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Claude authentication state.")
    parser.add_argument(
        "--json", action="store_true", help="Print JSON instead of text output."
    )
    args = parser.parse_args(argv)

    result = classify_auth()
    cli_details: list[str] = []
    cli_ok, cli_version = verify_claude_cli(cli_details)
    result.details = cli_details + result.details

    output = (
        render_json(result, cli_ok, cli_version)
        if args.json
        else render_text(result, cli_ok, cli_version)
    )
    sys.stdout.write(output)

    if result.valid and cli_ok:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
