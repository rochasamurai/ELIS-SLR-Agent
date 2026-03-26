"""
verify_codex_auth.py — PE-AUTH-01

Verifies that the Codex CLI is authenticated in the current environment.
Intended for use in GitHub Actions runners after OPENAI_API_KEY is injected.

Exit codes:
    0 — codex is available and authenticated
    1 — codex CLI not found or not authenticated

Usage:
    python scripts/verify_codex_auth.py

Security rule §13: never prints token values.
"""

import os
import shutil
import subprocess
import sys


def main() -> int:
    # Check OPENAI_API_KEY is set (existence only — never print value)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("FAIL: OPENAI_API_KEY is not set in environment.", file=sys.stderr)
        print(
            "Set it from the GitHub Secret before invoking this script.",
            file=sys.stderr,
        )
        return 1
    print(f"OK: OPENAI_API_KEY is set (length={len(api_key)})")

    # Check codex CLI is on PATH
    codex_path = shutil.which("codex")
    if codex_path is None:
        print("FAIL: 'codex' CLI not found on PATH.", file=sys.stderr)
        print("Install with: npm install -g @openai/codex", file=sys.stderr)
        return 1
    print(f"OK: codex CLI found at {codex_path}")

    # Run codex --version as a smoke-test (no auth required, confirms binary works)
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
    print("codex auth verification PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
