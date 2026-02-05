"""
archive_old_reports.py
Archive older validation reports under validation_reports/archive/YYYY/.

Usage:
  python scripts/archive_old_reports.py --keep 10
  python scripts/archive_old_reports.py --keep 10 --dry-run
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


REPORTS_DIR = Path("validation_reports")
ARCHIVE_DIR = REPORTS_DIR / "archive"


DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def parse_date_from_name(name: str) -> Optional[datetime]:
    match = DATE_PREFIX_RE.match(name)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y-%m-%d")
    except ValueError:
        return None


def report_sort_key(path: Path) -> Tuple[int, float]:
    # Primary: date prefix if present, else 0.
    date = parse_date_from_name(path.name)
    if date:
        return (1, date.timestamp())
    # Fallback: file mtime for unparseable names
    return (0, path.stat().st_mtime)


def is_report_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name in (".gitkeep", "validation-report.md"):
        return False
    if "validation_report" in path.name or "validation-report" in path.name:
        return True
    # Also include timestamped reports that end with .md
    if DATE_PREFIX_RE.match(path.name) and path.suffix.lower() == ".md":
        return True
    return False


def archive_reports(keep: int, dry_run: bool) -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    reports = [p for p in REPORTS_DIR.iterdir() if is_report_file(p)]
    if not reports:
        print("No report files found to archive.")
        return 0

    # Sort newest first
    reports_sorted = sorted(reports, key=report_sort_key, reverse=True)
    to_keep = reports_sorted[:keep]
    to_archive = reports_sorted[keep:]

    print(f"Found {len(reports_sorted)} report files.")
    print(f"Keeping {len(to_keep)} most recent.")
    print(f"Archiving {len(to_archive)} older files.")

    moved = 0
    for path in to_archive:
        date = parse_date_from_name(path.name)
        year = date.strftime("%Y") if date else "unknown"
        target_dir = ARCHIVE_DIR / year
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / path.name

        if dry_run:
            print(f"[DRY-RUN] {path} -> {target_path}")
            continue

        path.replace(target_path)
        moved += 1
        print(f"Moved {path} -> {target_path}")

    return moved


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive older validation reports.")
    parser.add_argument("--keep", type=int, default=10, help="How many recent reports to keep")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without moving files")
    args = parser.parse_args()

    if args.keep < 0:
        print("--keep must be >= 0")
        return 2

    archive_reports(keep=args.keep, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
