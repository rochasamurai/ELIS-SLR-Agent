"""
verify_codex_auth.py — PE-AUTH-01

Verifies that the Codex CLI is configured with an OAuth-backed auth.json in the
current environment.
Intended for use in GitHub Actions runners after ~/.codex/auth.json is written
from a GitHub Secret.

Exit codes:
    0 — codex is available and an OAuth auth.json is present
    1 — codex CLI not found or auth.json missing/invalid

Usage:
    python scripts/verify_codex_auth.py

Security rule §13: never prints token values.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys


def find_auth_file() -> pathlib.Path | None:
    candidates = [
        pathlib.Path.home() / ".codex" / "auth.json",
        pathlib.Path.home() / ".config" / "openai" / "auth.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def main() -> int:
    auth_file = find_auth_file()
    if auth_file is None:
        print("FAIL: Codex auth.json not found in ~/.codex or ~/.config/openai.", file=sys.stderr)
        print(
            "Write an OAuth-backed auth.json from the GitHub Secret before invoking this script.",
            file=sys.stderr,
        )
        return 1

    try:
        with auth_file.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"FAIL: Could not parse auth.json: {exc}", file=sys.stderr)
        return 1

    auth_mode = data.get("auth_mode", "<absent>")
    print(f"auth.json location : {auth_file}")
    print(f"auth_mode          : {auth_mode}")

    tokens = data.get("tokens")
    if isinstance(tokens, dict):
        print(f"tokens sub-keys    : {list(tokens.keys())}")
        print(f"access_token present : {bool(tokens.get('access_token'))}")
        print(f"refresh_token present: {bool(tokens.get('refresh_token'))}")
    else:
        print("tokens             : <absent or not an object>")
        return 1

    if auth_mode not in {"chatgpt", "oauth"}:
        print(
            "FAIL: auth.json is present but does not look OAuth-backed (expected auth_mode chatgpt/oauth).",
            file=sys.stderr,
        )
        return 1

    # Check codex CLI is on PATH.
    codex_path = shutil.which("codex")
    if codex_path is None:
        print("FAIL: 'codex' CLI not found on PATH.", file=sys.stderr)
        print("Install with: npm install -g @openai/codex", file=sys.stderr)
        return 1
    print(f"OK: codex CLI found at {codex_path}")

    # Run codex --version as a smoke-test (no auth required, confirms binary works).
    result = subprocess.run(
        ["codex", "--version"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        print(f"FAIL: 'codex --version' exited {result.returncode}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return 1
    version = result.stdout.strip() or result.stderr.strip()
    print(f"OK: codex --version → {version}")

    print()
    print("codex OAuth auth verification PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
