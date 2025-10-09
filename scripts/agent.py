#!/usr/bin/env python3
"""
ELIS – Toy Agent (MVP)

Reads Appendix A (Search) and produces ONLY:
  - Appendix B (Screening) rows
  - Appendix C (Data Extraction) rows

Notes
-----
- Accepts Appendix A as either a top-level list or {"rows": [...]}.
- Writes *only* B_FILE and C_FILE (MVP path).
- Tests may override ART_DIR / A_FILE / B_FILE / C_FILE module variables.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# --------------------------------------------------------------------------- #
# Locations (tests can override these module variables)
# --------------------------------------------------------------------------- #

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "json_jsonl"

A_FILE = ART_DIR / "ELIS_Appendix_A_Search_rows.json"
B_FILE = ART_DIR / "ELIS_Appendix_B_Screening_rows.json"
# Default is DataExtraction (repo canonical); tests may override to *_Extraction_*.
C_FILE = ART_DIR / "ELIS_Appendix_C_DataExtraction_rows.json"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_appendix_a(path: Path) -> List[Dict[str, Any]]:
    """Load Appendix A rows; support list or {'rows': [...]}."""
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("rows"), list):
        return raw["rows"]
    return []


def _pick_title(a_row: Dict[str, Any], idx: int) -> str:
    title = a_row.get("title")
    if title:
        return str(title)
    citation = a_row.get("citation")
    if citation:
        return str(citation)
    query = a_row.get("search_query")
    if query:
        return str(query)
    return f"Record {idx + 1}"


# --------------------------------------------------------------------------- #
# Core
# --------------------------------------------------------------------------- #

def run() -> Dict[str, Any]:
    """
    Read Appendix A and write ONLY B and C outputs.

    Returns a dict:
      {
        "a": [...], "b": [...], "c": [...],
        "counts": {"a": int, "b": int, "c": int},
        "written": {"B_FILE": "...", "C_FILE": "..."}
      }
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

    # Build C (Extraction) rows — one per B in this MVP
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

    # Write outputs (only B and C)
    _ensure_parent(B_FILE)
    _ensure_parent(C_FILE)
    B_FILE.write_text(
        json.dumps(b_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    C_FILE.write_text(
        json.dumps(c_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    return {
        "a": a_rows,
        "b": b_rows,
        "c": c_rows,
        "counts": {"a": len(a_rows), "b": len(b_rows), "c": len(c_rows)},
        "written": {"B_FILE": str(B_FILE), "C_FILE": str(C_FILE)},
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
