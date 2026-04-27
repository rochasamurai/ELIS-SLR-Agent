"""
verify_codex_auth.py — PE-AGT-00

Verifies whether Codex authentication is available on elis-server.
Primary mechanism: OAuth-backed auth.json.
Fallback mechanism: OPENAI_API_KEY.

Exit codes:
    0 — valid OAuth or API key authentication
    1 — missing or invalid authentication

Usage:
    python scripts/verify_codex_auth.py [--json]

Security rule §13: never prints token values.
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


def auth_file_candidates() -> list[pathlib.Path]:
    return [
        pathlib.Path.home() / ".codex" / "auth.json",
        pathlib.Path.home() / ".config" / "openai" / "auth.json",
    ]


def find_auth_file() -> pathlib.Path | None:
    for path in auth_file_candidates():
        if path.exists():
            return path
    return None


def has_oauth_tokens(data: object) -> bool:
    if not isinstance(data, dict):
        return False

    auth_mode = str(data.get("auth_mode", "")).strip().lower()
    if auth_mode in {"chatgpt", "oauth"}:
        return True

    tokens = data.get("tokens")
    if not isinstance(tokens, dict):
        return False

    return bool(tokens.get("refresh_token") or tokens.get("access_token"))


def classify_auth() -> VerificationResult:
    auth_file = find_auth_file()
    api_key = os.environ.get("OPENAI_API_KEY", "")

    if auth_file is not None:
        try:
            data = json.loads(auth_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            if api_key:
                return VerificationResult(
                    auth_mode="api_key",
                    valid=True,
                    source="env:OPENAI_API_KEY",
                    details=[
                        f"WARN: OAuth credential file unreadable: {exc}",
                        (
                            "WARN: Falling back to OPENAI_API_KEY because OAuth "
                            "could not be verified."
                        ),
                        f"OPENAI_API_KEY env present (length={len(api_key)})",
                    ],
                )
            return VerificationResult(
                auth_mode="invalid",
                valid=False,
                source=str(auth_file),
                details=[f"credentials file unreadable: {exc}"],
                next_step=(
                    "Run `codex` interactively on elis-server to refresh OAuth, "
                    "or set OPENAI_API_KEY as the fallback."
                ),
            )

        if has_oauth_tokens(data):
            auth_mode = str(data.get("auth_mode", "")).strip().lower()
            tokens = data.get("tokens") if isinstance(data, dict) else {}
            details = [
                f"auth.json location: {auth_file}",
                (
                    f"auth_mode: {auth_mode}"
                    if auth_mode
                    else "auth_mode: <not recorded>"
                ),
                (
                    "refresh_token present: yes"
                    if isinstance(tokens, dict) and bool(tokens.get("refresh_token"))
                    else "refresh_token present: no"
                ),
                (
                    "access_token present: yes"
                    if isinstance(tokens, dict) and bool(tokens.get("access_token"))
                    else "access_token present: no"
                ),
                (
                    "OPENAI_API_KEY fallback present: yes"
                    if api_key
                    else "OPENAI_API_KEY fallback present: no"
                ),
                "OAuth is the primary authentication path.",
            ]
            return VerificationResult(
                auth_mode="oauth",
                valid=True,
                source=str(auth_file),
                details=details,
            )

        if api_key:
            return VerificationResult(
                auth_mode="api_key",
                valid=True,
                source="env:OPENAI_API_KEY",
                details=[
                    f"WARN: auth.json found at {auth_file} but OAuth markers are absent.",
                    (
                        "WARN: Falling back to OPENAI_API_KEY because OAuth "
                        "could not be verified."
                    ),
                    f"OPENAI_API_KEY env present (length={len(api_key)})",
                ],
            )

        return VerificationResult(
            auth_mode="invalid",
            valid=False,
            source=str(auth_file),
            details=[f"auth.json found at {auth_file} but OAuth markers are absent."],
            next_step=(
                "Run `codex` interactively on elis-server to refresh OAuth, or set "
                "OPENAI_API_KEY as the fallback."
            ),
        )

    if api_key:
        preferred = auth_file_candidates()[0]
        return VerificationResult(
            auth_mode="api_key",
            valid=True,
            source="env:OPENAI_API_KEY",
            details=[
                f"WARN: OAuth credential file not found at {preferred}.",
                "WARN: Falling back to OPENAI_API_KEY.",
                f"OPENAI_API_KEY env present (length={len(api_key)})",
            ],
        )

    checked_paths = ", ".join(str(path) for path in auth_file_candidates())
    return VerificationResult(
        auth_mode="invalid",
        valid=False,
        source="missing",
        details=[f"OAuth credential file not found. Checked: {checked_paths}"],
        next_step=(
            "Run `codex` interactively on elis-server to refresh OAuth, or set "
            "OPENAI_API_KEY as the fallback."
        ),
    )


def verify_codex_cli(details: list[str]) -> tuple[bool, str | None]:
    codex_path = shutil.which("codex")
    if codex_path is None:
        details.append("INFO: local CLI not found on PATH (expected on elis-server).")
        return False, None

    details.append(f"local CLI: {codex_path}")
    result = subprocess.run(
        ["codex", "--version"],
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
    parser = argparse.ArgumentParser(description="Verify Codex authentication state.")
    parser.add_argument(
        "--json", action="store_true", help="Print JSON instead of text output."
    )
    args = parser.parse_args(argv)

    result = classify_auth()
    cli_details: list[str] = []
    cli_ok, cli_version = verify_codex_cli(cli_details)
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
