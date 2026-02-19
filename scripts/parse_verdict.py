"""parse_verdict.py — extract verdict from a REVIEW_PE*.md file.

Used by auto-merge-on-pass.yml (Gate 2).
Sets GitHub Actions outputs: verdict=PASS|FAIL|IN_PROGRESS, review_file=<name>.

File selection (in priority order):
  1. REVIEW_FILE env var — path to the exact REVIEW file to parse.
  2. REVIEW_PATH env var — directory to scan for REVIEW_PE*.md (mtime-sorted).
     Defaults to repo root ".".

Verdict matching tolerates trailing annotations, e.g. "PASS (with 1 warning)".
Exits 1 only on an unrecognised verdict; exits 0 in all other cases.
"""

import os
import re
import sys
from pathlib import Path

# Regex that matches valid verdict prefixes (anchored at start of line).
_VERDICT_RE = re.compile(r"^(PASS|FAIL|IN PROGRESS)\b")

GITHUB_OUTPUT = os.environ.get("GITHUB_OUTPUT", "")


def _set_output(key: str, value: str) -> None:
    """Write a GitHub Actions step output, or print to stdout in local mode."""
    if GITHUB_OUTPUT:
        with open(GITHUB_OUTPUT, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")
    else:
        print(f"{key}={value}")


def _find_review_file(search_dir: Path) -> Path | None:
    """Return most-recent REVIEW_PE*.md by mtime, or None if none found."""
    files = sorted(
        search_dir.glob("REVIEW_PE*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def main() -> int:
    # Priority 1: explicit REVIEW_FILE env var
    review_file_env = os.environ.get("REVIEW_FILE", "").strip()
    if review_file_env:
        review_file = Path(review_file_env)
        if not review_file.exists():
            _set_output("verdict", "IN_PROGRESS")
            _set_output("review_file", "")
            print(
                f"REVIEW_FILE={review_file_env!r} not found — verdict set to IN_PROGRESS."
            )
            return 0
    else:
        # Priority 2: scan REVIEW_PATH directory by mtime
        search_dir = Path(os.environ.get("REVIEW_PATH", "."))
        review_file = _find_review_file(search_dir)
        if review_file is None:
            _set_output("verdict", "IN_PROGRESS")
            _set_output("review_file", "")
            print("No REVIEW_PE*.md file found — verdict set to IN_PROGRESS.")
            return 0

    _set_output("review_file", review_file.name)

    lines = review_file.read_text(encoding="utf-8").splitlines()

    # Scan all sections; keep the last match (iterative re-validations append new sections).
    verdict_line = None
    for i, line in enumerate(lines):
        if line.strip() == "### Verdict":
            for j in range(i + 1, len(lines)):
                candidate = lines[j].strip()
                if candidate:
                    verdict_line = candidate
                    break

    if verdict_line is None:
        print("ERROR: Verdict field missing or unrecognised.")
        return 1

    # Tolerate trailing annotations: "PASS (with 1 warning)" → "PASS"
    m = _VERDICT_RE.match(verdict_line)
    if not m:
        print(f"ERROR: Verdict field missing or unrecognised: {verdict_line!r}")
        return 1

    canonical = m.group(1)  # "PASS", "FAIL", or "IN PROGRESS"
    normalised = canonical.replace(" ", "_")  # "IN_PROGRESS"

    _set_output("verdict", normalised)
    print(f"Verdict: {canonical} (file: {review_file.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
