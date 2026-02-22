"""check_status_packet.py — validate Status Packet section in HANDOFF.md.

Used by auto-assign-validator.yml (Gate 1).
Reads HANDOFF.md (or the path set in HANDOFF_PATH env var) and verifies
that the Status Packet section and all required subsections are present.

The Status Packet lives in HANDOFF.md — not in the PR body — so this script
reads the file directly from the checked-out working tree.

Exits 1 on any failure, 0 on success.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "## Status Packet",
    "### 6.1",
    "### 6.2",
    "### 6.3",
    "### 6.4",
    "### 6.5",
]


def main() -> int:
    handoff_path = Path(os.environ.get("HANDOFF_PATH", "HANDOFF.md"))

    if not handoff_path.exists():
        print(f"ERROR: {handoff_path} not found.")
        return 1

    content = handoff_path.read_text(encoding="utf-8")

    if not content.strip():
        print("ERROR: HANDOFF.md is empty.")
        return 1

    missing = [s for s in REQUIRED_SECTIONS if s not in content]
    if missing:
        for section in missing:
            print(f"Missing section: {section}")
        return 1

    print("Status Packet OK — all required sections present in HANDOFF.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
