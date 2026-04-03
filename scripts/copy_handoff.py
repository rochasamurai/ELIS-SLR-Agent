"""copy_handoff.py — copy the active PE's namespaced HANDOFF to the repo root.

Reads the current PE identifier from CURRENT_PE.md, then copies
``handoffs/HANDOFF_{PE_ID}.md`` to ``HANDOFF.md`` at the repo root.

This makes root ``HANDOFF.md`` a reproducible, script-generated artefact rather
than a hand-maintained file or a symlink (symlinks are unreliable on Windows
with ``core.symlinks=false``).

Intended callers:
  - Manually, after writing a new namespaced HANDOFF file.
  - PE-AUTO-06 Sequencer — will invoke this automatically at each PE advance.

Usage::

    python scripts/copy_handoff.py

Environment variables (optional, for testing):
  CURRENT_PE_PATH — override path to CURRENT_PE.md (default: ``CURRENT_PE.md``)
  HANDOFFS_DIR    — override the handoffs directory   (default: ``handoffs``)
  ROOT_HANDOFF    — override the root output path     (default: ``HANDOFF.md``)

Exits 0 on success, 1 on any error.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path


def main() -> int:
    current_pe_path = Path(os.environ.get("CURRENT_PE_PATH", "CURRENT_PE.md"))
    handoffs_dir = Path(os.environ.get("HANDOFFS_DIR", "handoffs"))
    root_handoff = Path(os.environ.get("ROOT_HANDOFF", "HANDOFF.md"))

    if not current_pe_path.exists():
        print(f"ERROR: {current_pe_path} not found.")
        return 1

    content = current_pe_path.read_text(encoding="utf-8")
    match = re.search(
        r"^\|\s*PE\s*\|\s*(PE-[A-Z]+-[0-9]+)\s*\|",
        content,
        re.MULTILINE,
    )
    if not match:
        print("ERROR: PE field not found in CURRENT_PE.md.")
        return 1

    pe_id = match.group(1)
    source = handoffs_dir / f"HANDOFF_{pe_id}.md"

    if not source.exists():
        print(f"ERROR: {source} not found.")
        return 1

    shutil.copy2(source, root_handoff)
    print(f"Copied {source} -> {root_handoff}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
