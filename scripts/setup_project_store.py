"""setup_project_store.py

Creates a canonical SLR project store directory layout under a given base path.

Usage:
    python scripts/setup_project_store.py --review-id <id> --title "<title>" \
        [--protocol-ref <ref>] [--base-path /opt/elis/projects]

Layout created:
    <base-path>/<review-id>/
        MANIFEST.md
        harvest/
        screen/
        extract/
        synth/
        prisma/

Idempotent — safe to re-run. Existing files and directories are not overwritten.
Exits 0 on success, 1 on error.
"""

from __future__ import annotations

import argparse
import datetime
import pathlib
import sys

PHASE_SUBDIRS = ["harvest", "screen", "extract", "synth", "prisma"]

DEFAULT_BASE_PATH = pathlib.Path("/opt/elis/projects")


def _build_manifest(review_id: str, title: str, protocol_ref: str) -> str:
    today = datetime.date.today().isoformat()
    phase_rows = "\n".join(
        [
            "| harvest | pending | harvest-impl-codex / harvest-val-claude  |",
            "| screen  | pending | screen-impl-claude / screen-val-codex    |",
            "| extract | pending | extract-impl-codex / extract-val-claude  |",
            "| synth   | pending | synth-impl-claude / synth-val-codex      |",
            "| prisma  | pending | prisma-impl-claude / prisma-val-codex    |",
        ]
    )
    return f"""# Review Manifest

review_id: {review_id}
title: {title}
created: {today}
protocol_ref: {protocol_ref}
status: active

## Phase Status

| Phase   | Status  | Agent pair                              |
|---------|---------|------------------------------------------|
{phase_rows}
"""


def create_project_store(
    review_id: str,
    title: str,
    protocol_ref: str,
    base_path: pathlib.Path,
) -> int:
    if not review_id or not review_id.replace("-", "").isalnum():
        print(
            f"ERROR: review-id '{review_id}' must be alphanumeric with hyphens only",
            file=sys.stderr,
        )
        return 1

    store = base_path / review_id

    try:
        store.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"ERROR: cannot create {store}: {exc}", file=sys.stderr)
        return 1

    for subdir in PHASE_SUBDIRS:
        (store / subdir).mkdir(exist_ok=True)

    manifest_path = store / "MANIFEST.md"
    if not manifest_path.exists():
        manifest_path.write_text(
            _build_manifest(review_id, title, protocol_ref), encoding="utf-8"
        )
        print(f"Created: {manifest_path}")
    else:
        print(f"Exists (skipped): {manifest_path}")

    for subdir in PHASE_SUBDIRS:
        path = store / subdir
        created = not (path / ".gitkeep").exists()
        if created:
            (path / ".gitkeep").write_text("", encoding="utf-8")
            print(f"Created: {path}/")
        else:
            print(f"Exists (skipped): {path}/")

    print(f"OK: project store '{review_id}' ready at {store}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a canonical SLR project store."
    )
    parser.add_argument(
        "--review-id", required=True, help="Slug identifier for the review"
    )
    parser.add_argument(
        "--title", default="Untitled Review", help="Human-readable review title"
    )
    parser.add_argument(
        "--protocol-ref", default="TBD", help="URL or path to protocol document"
    )
    parser.add_argument(
        "--base-path",
        type=pathlib.Path,
        default=DEFAULT_BASE_PATH,
        help=f"Base directory for project stores (default: {DEFAULT_BASE_PATH})",
    )
    args = parser.parse_args()
    return create_project_store(
        args.review_id, args.title, args.protocol_ref, args.base_path
    )


if __name__ == "__main__":
    sys.exit(main())
