#!/usr/bin/env python3
"""
ELIS – Toy Agent (MVP)

Purpose
-------
Read Appendix A search rows and produce:
  - Appendix B Screening rows
  - Appendix C Data Extraction rows

Design notes
------------
- The agent reads A_FILE. It accepts either a top-level JSON array or an
  object with a `rows` array (backward compatible).
- It writes ONLY B_FILE and C_FILE, as requested for the MVP path.
- Module-level paths are overridable by tests (e.g., tests set A_FILE/B_FILE/C_FILE).
- Output is intentionally simple but valid for the minimal schemas.

Outputs (shape, minimal)
------------------------
Appendix B items:
  {
    "id": "B-0001",
    "source_id": "A-0001",
    "title": "…",
    "decision": "included",
    "reason": "MVP auto-include",
    "decided_at": "YYYY-MM-DDTHH:MM:SSZ"
  }

Appendix C items (one per B in this MVP):
  {
    "id": "C-0001",
    "screening_id": "B-0001",
    "key_findings": "MVP placeholder extraction",
    "extracted_at": "YYYY-MM-DDTHH:MM:SSZ",
    "notes": ""
  }
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Dict

# --------------------------------------------------------------------------- #
# Default locations (tests override these module variables)
# --------------------------------------------------------------------------- #

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "json_jsonl"

A_FILE = ART_DIR / "ELIS_Appendix_A_Search_rows.json"
B_FILE = ART_DIR / "ELIS_Appendix_B_Screening_rows.json"
# Default to the canonical MVP name. Tests may override this to *_Extraction_*.
C_FILE = ART_DIR / "ELIS_Appendix_C_DataExtraction_rows.json"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_appendix_a(path: Path) -> List[Dict[str, Any]]:
    """
    Load Appendix A search rows.

    Accepts:
      - a top-level JSON array
      - or an object with a 'rows' array
    """
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("rows"), list):
        return raw["rows"]
    return []


def _pick_title(a_row: Dict[str, Any], idx: int) -> str:
    # Use a reasonable title fallback hierarchy
    return (
        str(a_row.get("title"))
        or str(a_row.get("citation"))
        or str(a_row.get("search_query"))
        or f"Record {idx + 1}"
    )


# --------------------------------------------------------------------------- #
# Core
# --------------------------------------------------------------------------- #

def run() -> Dict[str, Any]:
    """
    Read Appendix A and write ONLY B and C outputs.

    Returns a small summary dict. Safe to ignore.
    """
    a_rows = _load_appendix_a(A_FILE)
    ts = _now_utc_iso()

    # Build B (Screening) rows
    b_rows: List[Dict[str, Any]] = []
    for i, row in enumerate(a_rows):
        source_id = str(row.get("id", f"A-{i + 1:04d}"))
        b_rows.append(
            {
                "id": f"B-{i + 1:04d}",
                "source_id": source_id,
                "title": _pick_title(row, i),
                "decision": "included",
                "reason": "MVP auto-include",
                "decided_at": ts,
            }
        )

    # Build C (Extraction) rows — one per included B for MVP
    c_rows: List[Dict[str, Any]] = []
    for j, b in enumerate(b_rows):
        c_rows.append(
            {
                "id": f"C-{j + 1:04d}",
                "screening_id": b["id"],
                "key_findings": "MVP placeholder extraction",
                "extracted_at": ts,
                "notes": "",
            }
        )

    # Write files
    _ensure_parent(B_FILE)
    _ensure_parent(C_FILE)

    B_FILE.write_text(json.dumps(b_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    C_FILE.write_text(json.dumps(c_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "written": {
            "B_FILE": str(B_FILE),
            "C_FILE": str(C_FILE),
        },
        "counts": {"b": len(b_rows), "c": len(c_rows)},
    }


if __name__ == "__main__":
    summary = run()
    print(json.dumps(summary, indent=2))
