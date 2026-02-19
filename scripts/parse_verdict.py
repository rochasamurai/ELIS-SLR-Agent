"""parse_verdict.py — extract verdict from the most recent REVIEW_PE*.md file.

Used by auto-merge-on-pass.yml (Gate 2).
Sets GitHub Actions outputs: verdict=PASS|FAIL|IN_PROGRESS, review_file=<name>.
REVIEW_PATH env var overrides the directory to search (default: repo root ".").
Exits 1 only on unrecognised/missing verdict line; exits 0 in all other cases.
"""

import os
import sys
from pathlib import Path

VALID_VERDICTS = {"PASS", "FAIL", "IN PROGRESS"}
GITHUB_OUTPUT = os.environ.get("GITHUB_OUTPUT", "")


def _set_output(key: str, value: str) -> None:
    """Write a GitHub Actions step output, or print to stdout in local mode."""
    if GITHUB_OUTPUT:
        with open(GITHUB_OUTPUT, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")
    else:
        print(f"{key}={value}")


def main() -> int:
    search_dir = Path(os.environ.get("REVIEW_PATH", "."))

    review_files = sorted(
        search_dir.glob("REVIEW_PE*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not review_files:
        _set_output("verdict", "IN_PROGRESS")
        _set_output("review_file", "")
        print("No REVIEW_PE*.md file found — verdict set to IN_PROGRESS.")
        return 0

    review_file = review_files[0]
    _set_output("review_file", review_file.name)

    lines = review_file.read_text(encoding="utf-8").splitlines()

    verdict_line = None
    for i, line in enumerate(lines):
        if line.strip() == "### Verdict":
            # The verdict is on the next non-blank line
            for j in range(i + 1, len(lines)):
                candidate = lines[j].strip()
                if candidate:
                    verdict_line = candidate
                    break
            break

    if verdict_line is None:
        print("ERROR: Verdict field missing or unrecognised.")
        return 1

    # Normalise "IN PROGRESS" → "IN_PROGRESS" for Actions output compatibility
    normalised = verdict_line.replace(" ", "_")

    if verdict_line not in VALID_VERDICTS:
        print(f"ERROR: Verdict field missing or unrecognised: {verdict_line!r}")
        return 1

    _set_output("verdict", normalised)
    print(f"Verdict: {verdict_line} (file: {review_file.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
