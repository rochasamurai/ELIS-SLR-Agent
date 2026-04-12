"""
verify_claude_auth.py — PE-AUTH-02

Verifies that the Claude Code CLI is ready for headless runner use via
CLAUDE_CREDENTIALS_JSON (written to ~/.claude/.credentials.json before
this script runs).

Exit codes:
    0 — claude CLI is available and credentials file is present
    1 — required environment or CLI preconditions are missing

Usage:
    python scripts/verify_claude_auth.py

Security rule §13: never prints credential values.
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys


def main() -> int:
    credentials_json = os.environ.get("CLAUDE_CREDENTIALS_JSON", "")
    if not credentials_json:
        print("FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.", file=sys.stderr)
        print(
            "Set it from the GitHub Secret before invoking this script.",
            file=sys.stderr,
        )
        return 1
    print(f"OK: CLAUDE_CREDENTIALS_JSON is set (length={len(credentials_json)})")

    creds_path = pathlib.Path.home() / ".claude" / ".credentials.json"
    if not creds_path.exists():
        print(
            f"FAIL: credentials file not found at {creds_path}",
            file=sys.stderr,
        )
        print(
            "The 'Write Claude credentials file' step must run before this script.",
            file=sys.stderr,
        )
        return 1
    print(f"OK: credentials file exists at {creds_path}")

    try:
        data = json.loads(creds_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"FAIL: credentials file is not valid JSON: {exc}", file=sys.stderr)
        return 1

    if "claudeAiOauth" not in data:
        print(
            "FAIL: credentials file missing 'claudeAiOauth' key.",
            file=sys.stderr,
        )
        return 1
    print("OK: credentials file contains claudeAiOauth entry")

    claude_path = shutil.which("claude")
    if claude_path is None:
        print("FAIL: 'claude' CLI not found on PATH.", file=sys.stderr)
        print(
            "Install Claude Code with the official Anthropic installer before retrying.",
            file=sys.stderr,
        )
        return 1
    print(f"OK: claude CLI found at {claude_path}")

    result = subprocess.run(
        ["claude", "--version"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        print(f"FAIL: 'claude --version' exited {result.returncode}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return 1

    version = result.stdout.strip() or result.stderr.strip()
    print(f"OK: claude --version -> {version}")
    print()
    print("claude auth verification PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
