"""check_handoff.py — validate HANDOFF.md completeness.

Used by auto-assign-validator.yml (Gate 1).
Reads the path from the HANDOFF_PATH env var (default: HANDOFF.md at repo root).
Exits 1 if the file is missing or any required section is absent, 0 on success.
"""

import os
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "## Summary",
    "## Files Changed",
    "## Acceptance Criteria",
    "## Validation Commands",
]


def main() -> int:
    handoff_path = Path(os.environ.get("HANDOFF_PATH", "HANDOFF.md"))

    if not handoff_path.exists():
        print("ERROR: HANDOFF.md not found.")
        return 1

    content = handoff_path.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_SECTIONS if s not in content]
    if missing:
        for section in missing:
            print(f"Missing section: {section}")
        return 1

    print("HANDOFF.md OK — all required sections present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
