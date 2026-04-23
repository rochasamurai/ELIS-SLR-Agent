"""
extract_codex_token.py — PE-AUTH-01

Reads the local Codex CLI auth file and prints ONLY metadata (key names,
auth_mode, last_refresh timestamp). Never prints token values.

Usage (PO runs once on local machine to verify what is available):
    python scripts/extract_codex_token.py

Security rule §13: token values must never appear in any output.
"""

import json
import pathlib
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
        print(
            "ERROR: auth.json not found. Run 'codex auth login' first.", file=sys.stderr
        )
        return 1

    with auth_file.open() as fh:
        data = json.load(fh)

    print(f"auth.json location : {auth_file}")
    print(f"auth_mode          : {data.get('auth_mode', '<absent>')}")
    print(f"last_refresh       : {data.get('last_refresh', '<absent>')}")
    print()

    top_keys = [k for k in data if k != "tokens"]
    print(f"Top-level keys     : {top_keys}")

    tokens = data.get("tokens")
    if isinstance(tokens, dict):
        print(f"tokens sub-keys    : {list(tokens.keys())}")
    else:
        print("tokens             : <absent or not an object>")

    has_api_key = bool(data.get("OPENAI_API_KEY"))
    has_refresh = isinstance(tokens, dict) and bool(tokens.get("refresh_token"))
    print()
    print(f"OPENAI_API_KEY present : {has_api_key}")
    print(f"refresh_token present  : {has_refresh}")

    if has_api_key:
        print()
        print(
            "Recommended mechanism: store OPENAI_API_KEY as GitHub Secret 'OPENAI_API_KEY'."
        )
        print("Runners set: export OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}")
    elif has_refresh:
        print()
        print("Fallback mechanism: store refresh_token as 'CODEX_REFRESH_TOKEN'.")
        print("Runner must exchange it for an access_token before invoking codex.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
