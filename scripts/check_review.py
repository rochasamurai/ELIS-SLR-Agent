"""check_review.py — validate REVIEW file evidence completeness.

Used by auto-merge-on-pass.yml (Gate 2b) and ci.yml (review-evidence-check).
Exits 1 if required sections are missing or Evidence section has no code block.
Exits 0 on a valid REVIEW file.

File selection: same priority as parse_verdict.py:
  1. REVIEW_FILE env var — exact path.
  2. REVIEW_PATH env var — directory scan by mtime. Default ".".
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "### Verdict",
    "### Gate results",
    "### Scope",
    "### Required fixes",
    "### Evidence",
]


_VERDICT_RE = re.compile(r"^(PASS|FAIL|IN PROGRESS)\b")


def _find_review_file(search_dir: Path) -> Path | None:
    """Return most-recent REVIEW_PE*.md by mtime, or None if none found."""
    files = sorted(
        search_dir.glob("REVIEW_PE*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def _last_header_index(lines: list[str], header: str) -> int | None:
    index: int | None = None
    for i, line in enumerate(lines):
        if line.strip() == header:
            index = i
    return index


def _section_body(lines: list[str], start_index: int) -> list[str]:
    body: list[str] = []
    for i in range(start_index + 1, len(lines)):
        current = lines[i]
        if current.strip().startswith("### "):
            break
        body.append(current)
    return body


def _extract_verdict(lines: list[str]) -> str | None:
    idx = _last_header_index(lines, "### Verdict")
    if idx is None:
        return None

    body = _section_body(lines, idx)
    for line in body:
        candidate = line.strip()
        if not candidate:
            continue
        match = _VERDICT_RE.match(candidate)
        if match:
            return match.group(1)
        return None
    return None


def _has_fenced_code_block(lines: list[str]) -> bool:
    return any(line.strip().startswith("```") for line in lines)


def _required_fixes_missing(lines: list[str]) -> bool:
    meaningful: list[str] = []
    for raw in lines:
        text = raw.strip()
        if not text:
            continue
        text = text.lstrip("-* ").strip().rstrip(".")
        if text:
            meaningful.append(text.lower())

    if not meaningful:
        return True

    return all(value == "none" for value in meaningful)


def main() -> int:
    review_file_env = os.environ.get("REVIEW_FILE", "").strip()
    if review_file_env:
        review_file = Path(review_file_env)
        if not review_file.exists():
            print("ERROR: REVIEW file not found.")
            return 1
    else:
        search_dir = Path(os.environ.get("REVIEW_PATH", "."))
        review_file = _find_review_file(search_dir)
        if review_file is None:
            print("ERROR: REVIEW file not found.")
            return 1

    content = review_file.read_text(encoding="utf-8")
    missing = [section for section in REQUIRED_SECTIONS if section not in content]
    if missing:
        for section in missing:
            print(f"ERROR: Missing section: {section}")
        return 1

    lines = content.splitlines()

    verdict = _extract_verdict(lines)
    if verdict is None:
        print("ERROR: Verdict field missing or unrecognised.")
        return 1

    evidence_idx = _last_header_index(lines, "### Evidence")
    if evidence_idx is None:
        print("ERROR: Missing section: ### Evidence")
        return 1

    evidence_body = _section_body(lines, evidence_idx)
    if not _has_fenced_code_block(evidence_body):
        print("ERROR: Evidence section must include at least one fenced code block.")
        return 1

    if verdict == "FAIL":
        fixes_idx = _last_header_index(lines, "### Required fixes")
        if fixes_idx is None:
            print("ERROR: Missing section: ### Required fixes")
            return 1

        fixes_body = _section_body(lines, fixes_idx)
        if _required_fixes_missing(fixes_body):
            print("ERROR: FAIL verdict requires at least one required fix.")
            return 1

    print(f"REVIEW evidence check PASS ({review_file.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
