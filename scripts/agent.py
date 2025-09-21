#!/usr/bin/env python3
"""
ELIS Agent – Toy Run (A → B → C)

Goal
----
Minimal, deterministic agent that proves the repository is wired correctly.
It writes one JSON row to each of the three ELIS artefacts under `json_jsonl/`:

* ELIS_Appendix_A_Search_rows.json
* ELIS_Appendix_B_Screening_rows.json
* ELIS_Appendix_C_DataExtraction_rows.json

Each row is a small dict with stable keys so CI/test can assert structure.

Design notes
------------
- UK English comments and docstrings.
- No external dependencies; pure Python 3.11+.
- Deterministic content (only the timestamp changes) to keep diffs readable.
- Exits 0 on success and prints a concise summary to STDOUT.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

ROOT: Path = Path(__file__).resolve().parents[1]
DATA_DIR: Path = ROOT / "json_jsonl"

A_PATH: Path = DATA_DIR / "ELIS_Appendix_A_Search_rows.json"
B_PATH: Path = DATA_DIR / "ELIS_Appendix_B_Screening_rows.json"
C_PATH: Path = DATA_DIR / "ELIS_Appendix_C_DataExtraction_rows.json"


def now_iso_z() -> str:
    """Return the current UTC time as an ISO-8601 string with 'Z' suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dirs() -> None:
    """Create required directories if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def write_json_array(path: Path, rows: List[Dict]) -> None:
    """Serialise a list of dict rows to JSON with a trailing newline."""
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_row(stage: str, note: str) -> Dict:
    """
    Build a minimal, self-describing row used across A/B/C artefacts.

    Fields:
      - id:         stable identifier string
      - source:     which stage produced the row
      - created_at: ISO-8601 UTC timestamp (Z)
      - note:       human-readable explanation
    """
    return {
        "id": f"toy-{stage}-001",
        "source": stage,
        "created_at": now_iso_z(),
        "note": note,
    }


def make_toy_artefacts() -> None:
    """Write one minimal row to each ELIS artefact."""
    ensure_dirs()

    a_rows = [
        build_row(
            stage="A:search",
            note="Seed query issued by the Toy Agent to demonstrate pipeline wiring.",
        )
    ]
    b_rows = [
        build_row(
            stage="B:screening",
            note="Single record marked as 'included' by the Toy Agent for demo purposes.",
        )
    ]
    c_rows = [
        build_row(
            stage="C:data_extraction",
            note="Minimal extraction payload (placeholder fields only).",
        )
    ]

    write_json_array(A_PATH, a_rows)
    write_json_array(B_PATH, b_rows)
    write_json_array(C_PATH, c_rows)


def main() -> int:
    """Entry point used by CI and manual runs."""
    make_toy_artefacts()
    print("Toy run completed:")
    print(f"  - wrote: {A_PATH.relative_to(ROOT)}")
    print(f"  - wrote: {B_PATH.relative_to(ROOT)}")
    print(f"  - wrote: {C_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
