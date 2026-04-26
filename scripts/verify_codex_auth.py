"""
verify_codex_auth.py — PE-AUTH-01

Verifies whether the Codex CLI is authenticated in the current environment.
Primary mechanism: OAuth-backed auth.json.
Fallback mechanism: OPENAI_API_KEY.

Exit codes:
    0 — valid OAuth or API key authentication
    1 — invalid or missing authentication / CLI prerequisites

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
from dataclasses import dataclass, asdict


@dataclass
class VerificationResult:
    auth_mode: str
    valid: bool
    source: str
    details: list[str]
    next_step: str | None = None


def find_auth_file() -> pathlib.Path | None:
    candidates = [
        pathlib.Path.home() / ".codex" / "auth.json",
        pathlib.Path.home() / ".config" / "openai" / "auth.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def classify_auth() -> VerificationResult:
    auth_file = find_auth_file()
    api_key = os.environ.get("OPENAI_API_KEY", "")

    details: list[str] = []
    source = "missing"

    if auth_file is not None:
        try:
            data = json.loads(auth_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            return VerificationResult(
                auth_mode="invalid",
                valid=False,
                source=str(auth_file),
                details=[f"credentials file unreadable: {exc}"],
                next_step="Ask PO to re-run 'codex auth login' on a terminal with browser access.",
            )

        auth_mode = str(data.get("auth_mode", "")).strip().lower()
        tokens = data.get("tokens")
        has_refresh_token = isinstance(tokens, dict) and bool(
            tokens.get("refresh_token")
        )
        has_access_token = isinstance(tokens, dict) and bool(tokens.get("access_token"))
        has_top_level_api_key = bool(data.get("OPENAI_API_KEY"))

        if auth_mode in {"chatgpt", "oauth"} or has_refresh_token or has_access_token:
            details.append(f"auth.json location: {auth_file}")
            if auth_mode:
                details.append(f"auth_mode: {auth_mode}")
            if has_refresh_token:
                details.append("refresh_token present: yes")
            if has_access_token:
                details.append("access_token present: yes")
            if has_top_level_api_key:
                details.append("OPENAI_API_KEY field present: yes")
            if api_key:
                details.append("OPENAI_API_KEY env fallback present: yes")
            return VerificationResult(
                auth_mode="oauth",
                valid=True,
                source=str(auth_file),
                details=details,
            )

        if auth_mode in {"apikey", "api_key"} or has_top_level_api_key or api_key:
            details.append(f"auth.json location: {auth_file}")
            if auth_mode:
                details.append(f"auth_mode: {auth_mode}")
            if has_top_level_api_key:
                details.append("OPENAI_API_KEY field present: yes")
            if api_key:
                details.append("OPENAI_API_KEY env fallback present: yes")
            return VerificationResult(
                auth_mode="api_key",
                valid=True,
                source=str(auth_file) if auth_file else "env:OPENAI_API_KEY",
                details=details,
            )

        details.append(f"auth.json location: {auth_file}")
        details.append("No supported auth markers found in auth.json")
        source = str(auth_file)
    elif api_key:
        return VerificationResult(
            auth_mode="api_key",
            valid=True,
            source="env:OPENAI_API_KEY",
            details=[f"OPENAI_API_KEY env present (length={len(api_key)})"],
        )
    else:
        details.append("auth.json not found")

    return VerificationResult(
        auth_mode="invalid",
        valid=False,
        source=source,
        details=details,
        next_step="Ask PO to run 'codex auth login' on a machine with browser access, or set OPENAI_API_KEY as the fallback.",
    )


def verify_codex_cli(details: list[str]) -> tuple[bool, str | None]:
    codex_path = shutil.which("codex")
    if codex_path is None:
        details.append("FAIL: 'codex' CLI not found on PATH.")
        details.append("Install with: npm install -g @openai/codex")
        return False, None

    details.append(f"codex CLI: {codex_path}")
    result = subprocess.run(
        ["codex", "--version"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    if result.returncode != 0:
        details.append(f"FAIL: 'codex --version' exited {result.returncode}")
        stderr = result.stderr.strip()
        if stderr:
            details.append(stderr)
        return False, None

    version = result.stdout.strip() or result.stderr.strip() or "<unknown>"
    details.append(f"codex --version: {version}")
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
    elif result.valid and not cli_ok:
        lines.append("RESULT: Invalid authentication")
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

    if result.valid and cli_ok:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
