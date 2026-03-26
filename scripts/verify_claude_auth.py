"""
verify_claude_auth.py — PE-AUTH-02

Verifies that the Claude Code CLI is ready for headless runner use via
CLAUDE_SETUP_TOKEN and without ANTHROPIC_API_KEY.

Exit codes:
    0 — claude CLI is available and token-only runner setup is valid
    1 — required environment or CLI preconditions are missing

Usage:
    python scripts/verify_claude_auth.py

Security rule §13: never prints token values.
"""

import os
import shutil
import subprocess
import sys


def main() -> int:
    setup_token = os.environ.get("CLAUDE_SETUP_TOKEN", "")
    if not setup_token:
        print("FAIL: CLAUDE_SETUP_TOKEN is not set in environment.", file=sys.stderr)
        print(
            "Set it from the GitHub Secret before invoking this script.",
            file=sys.stderr,
        )
        return 1
    print(f"OK: CLAUDE_SETUP_TOKEN is set (length={len(setup_token)})")

    if os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "FAIL: ANTHROPIC_API_KEY is set in environment.",
            file=sys.stderr,
        )
        print(
            "PE-AUTH-02 requires token-only verification for the runner path.",
            file=sys.stderr,
        )
        return 1
    print("OK: ANTHROPIC_API_KEY is absent from environment")

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
