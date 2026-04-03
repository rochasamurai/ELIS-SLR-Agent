"""check_handoff.py — validate HANDOFF.md completeness.

Used by auto-assign-validator.yml (Gate 1).

Resolution order (PE-AUTO-03 namespacing):
  1. HANDOFF_PATH env var — explicit override, used in tests
  2. handoffs/HANDOFF_{PE_ID}.md — namespaced path derived from CURRENT_PE.md
  3. HANDOFF.md at repo root — legacy fallback (migration period)

Exits 1 if the file is missing or any required section is absent, 0 on success.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "## Summary",
    "## Files Changed",
    "## Acceptance Criteria",
    "## Validation Commands",
]


def _resolve_path() -> Path:
    explicit = os.environ.get("HANDOFF_PATH")
    if explicit:
        return Path(explicit)

    current_pe_path = Path(os.environ.get("CURRENT_PE_PATH", "CURRENT_PE.md"))
    if current_pe_path.exists():
        content = current_pe_path.read_text(encoding="utf-8")
        match = re.search(
            r"^\|\s*PE\s*\|\s*(PE-[A-Z]+-[0-9]+)\s*\|",
            content,
            re.MULTILINE,
        )
        if match:
            pe_id = match.group(1)
            namespaced = Path("handoffs") / f"HANDOFF_{pe_id}.md"
            if namespaced.exists():
                return namespaced

    return Path("HANDOFF.md")


def main() -> int:
    path = _resolve_path()

    if not path.exists():
        print(f"ERROR: {path} not found.")
        return 1

    content = path.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_SECTIONS if s not in content]
    if missing:
        for section in missing:
            print(f"Missing section: {section}")
        return 1

    print(f"HANDOFF OK ({path}) — all required sections present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
