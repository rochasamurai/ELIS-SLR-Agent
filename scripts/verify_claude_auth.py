"""
verify_claude_auth.py — PE-AGT-00

Verifies whether Claude Code authentication is available on elis-server.
Primary mechanism: OAuth-backed ~/.claude/.credentials.json containing
`claudeAiOauth`.
Fallback mechanism: ANTHROPIC_API_KEY.

Exit codes:
    0 — valid OAuth or API key authentication
    1 — missing or invalid authentication

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
from dataclasses import asdict, dataclass


@dataclass
class VerificationResult:
    auth_mode: str
    valid: bool
    source: str
    details: list[str]
    next_step: str | None = None


def credentials_file() -> pathlib.Path:
    return pathlib.Path.home() / ".claude" / ".credentials.json"


def classify_auth() -> VerificationResult:
    creds_path = credentials_file()
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

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
                        f"WARN: OAuth credential file unreadable: {exc}",
                        (
                            "WARN: Falling back to ANTHROPIC_API_KEY because "
                            "OAuth could not be verified."
                        ),
                        f"ANTHROPIC_API_KEY env present (length={len(api_key)})",
                    ],
                )
            return VerificationResult(
                auth_mode="invalid",
                valid=False,
                source=str(creds_path),
                details=[f"credentials file unreadable: {exc}"],
                next_step=(
                    "Run `claude` interactively on elis-server to refresh OAuth, "
                    "or set ANTHROPIC_API_KEY as the fallback."
                ),
            )

        if isinstance(data, dict) and "claudeAiOauth" in data:
            return VerificationResult(
                auth_mode="oauth",
                valid=True,
                source=str(creds_path),
                details=[
                    f"credentials file: {creds_path}",
                    "claudeAiOauth entry present: yes",
                    "OAuth is the primary authentication path.",
                    (
                        "ANTHROPIC_API_KEY fallback present: yes"
                        if api_key
                        else "ANTHROPIC_API_KEY fallback present: no"
                    ),
                ],
            )

        if api_key:
            return VerificationResult(
                auth_mode="api_key",
                valid=True,
                source="env:ANTHROPIC_API_KEY",
                details=[
                    (
                        "WARN: ~/.claude/.credentials.json is present but does not "
                        "contain claudeAiOauth."
                    ),
                    (
                        "WARN: Falling back to ANTHROPIC_API_KEY because "
                        "OAuth could not be verified."
                    ),
                    f"ANTHROPIC_API_KEY env present (length={len(api_key)})",
                ],
            )

        return VerificationResult(
            auth_mode="invalid",
            valid=False,
            source=str(creds_path),
            details=["credentials file missing 'claudeAiOauth' key."],
            next_step=(
                "Run `claude` interactively on elis-server to refresh OAuth, "
                "or set ANTHROPIC_API_KEY as the fallback."
            ),
        )

    if api_key:
        return VerificationResult(
            auth_mode="api_key",
            valid=True,
            source="env:ANTHROPIC_API_KEY",
            details=[
                "WARN: OAuth credential file not found at ~/.claude/.credentials.json.",
                "WARN: Falling back to ANTHROPIC_API_KEY.",
                f"ANTHROPIC_API_KEY env present (length={len(api_key)})",
            ],
        )

    return VerificationResult(
        auth_mode="invalid",
        valid=False,
        source=str(creds_path),
        details=["OAuth credential file not found at ~/.claude/.credentials.json."],
        next_step=(
            "Run `claude` interactively on elis-server to refresh OAuth, or set "
            "ANTHROPIC_API_KEY as the fallback."
        ),
    )


def verify_claude_cli(details: list[str]) -> tuple[bool, str | None]:
    claude_path = shutil.which("claude")
    if claude_path is None:
        details.append("INFO: local CLI not found on PATH (expected on elis-server).")
        return False, None

    details.append(f"local CLI: {claude_path}")
    result = subprocess.run(
        ["claude", "--version"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    if result.returncode != 0:
        details.append(f"WARN: local CLI --version exited {result.returncode}")
        stderr = result.stderr.strip()
        if stderr:
            details.append(stderr)
        return False, None

    version = result.stdout.strip() or result.stderr.strip() or "<unknown>"
    details.append(f"CLI version: {version}")
    return True, version


def render_text(
    result: VerificationResult, cli_ok: bool, cli_version: str | None
) -> str:
    lines: list[str] = []
    if result.valid:
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
        lines.append(f"RUNTIME VERSION: {cli_version}")
    for detail in result.details:
        lines.append(detail)
    if result.valid:
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

    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
