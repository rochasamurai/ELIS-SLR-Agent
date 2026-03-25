"""check_project_store_layout.py

Validates that a given directory is a correctly structured SLR project store.

Usage:
    python scripts/check_project_store_layout.py --path /opt/elis/projects/<review-id>

Checks:
    1. Path exists and is a directory
    2. MANIFEST.md is present
    3. All 5 phase subdirectories exist (harvest, screen, extract, synth, prisma)

Exits 0 on valid layout, 1 with error messages if not.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import List

REQUIRED_SUBDIRS = ["harvest", "screen", "extract", "synth", "prisma"]


def check_project_store(path: pathlib.Path) -> List[str]:
    errors: List[str] = []

    if not path.exists():
        return [f"path '{path}' does not exist"]
    if not path.is_dir():
        return [f"path '{path}' is not a directory"]

    if not (path / "MANIFEST.md").is_file():
        errors.append(f"MANIFEST.md missing in '{path}'")

    for subdir in REQUIRED_SUBDIRS:
        if not (path / subdir).is_dir():
            errors.append(f"phase subdirectory '{subdir}/' missing in '{path}'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an SLR project store layout."
    )
    parser.add_argument(
        "--path",
        type=pathlib.Path,
        required=True,
        help="Path to the project store directory",
    )
    args = parser.parse_args()

    errors = check_project_store(args.path)
    if errors:
        review_id = args.path.name
        print(f"FAIL: project store '{review_id}' has layout errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    review_id = args.path.name
    subdir_count = sum(1 for s in REQUIRED_SUBDIRS if (args.path / s).is_dir())
    print(
        f"OK: project store '{review_id}' is valid — "
        f"{subdir_count} subdirs, MANIFEST.md present"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
