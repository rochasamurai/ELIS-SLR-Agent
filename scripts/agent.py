#!/usr/bin/env python3
"""
ELIS – Toy Agent (MVP)
----------------------

Reads Appendix A search rows and emits exactly two artefacts:

  - json_jsonl/ELIS_Appendix_B_Screening_rows.json
  - json_jsonl/ELIS_Appendix_C_DataExtraction_rows.json

It never modifies Appendix A. This is a placeholder pipeline that creates
one Screening row per A row, and one Extraction row per B row, using
deterministic, readable content suitable for CI and validation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Dict


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "json_jsonl"

A_FILE = DATA_DIR / "ELIS_Appendix_A_Search_rows.json"
B_FILE = DATA_DIR / "ELIS_Appendix_B_Screening_rows.json"
C_FILE = DATA_DIR / "ELIS_Appendix_C_DataExtraction_rows.json"


def _now_utc_iso() -> str:
    """RFC3339-ish timestamp with 'Z' (e.g., 2025-10-09T12:34:56Z)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> Any:
    """Read JSON with UTF-8; return None if missing."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_array(path: Path, rows: List[Dict[str, Any]]) -> None:
    """Write a JSON array with stable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _extract_rows_from_appendix_a(a_data: Any) -> List[Dict[str, Any]]:
    """
    Accept either:
      - {"rows": [...]} wrapper (current repo convention), or
      - a raw array of objects (legacy/toy).
    """
    if a_data is None:
        return []
    if isinstance(a_data, dict) and isinstance(a_data.get("rows"), list):
        return list(a_data["rows"])
    if isinstance(a_data, list):
        return list(a_data)
    # Unknown shape -> treat as no rows (robust)
    return []


def _mk_screening_row(i: int, a_row: Dict[str, Any], ts: str) -> Dict[str, Any]:
    """
    Minimal Screening row (Appendix B) for MVP schemas.
    """
    a_id = str(a_row.get("id") or f"A-{i+1:04d}")
    title_bits = []
    if "title" in a_row and a_row["title"]:
        title_bits.append(str(a_row["title"]))
    elif "search_query" in a_row and a_row["search_query"]:
        title_bits.append(f"Screened result from query: {a_row['search_query']}")
    else:
        title_bits.append("Screened result (toy)")

    if "source" in a_row and a_row["source"]:
        title_bits.append(f"[source: {a_row['source']}]")

    b_row = {
        "id": f"B-{i+1:04d}",
        "source_id": a_id,                     # FK to A
        "title": " ".join(title_bits),
        "decision": "included",                # toy decision
        "reason": "pilot include (MVP)",
        "decided_at": ts,
    }
    return b_row


def _mk_extraction_row(i: int, b_row: Dict[str, Any], ts: str, a_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal Extraction row (Appendix C) for MVP schemas.
    """
    notes_bits = []
    if "notes" in a_row and a_row["notes"]:
        notes_bits.append(str(a_row["notes"]))
    if "source" in a_row and a_row["source"]:
        notes_bits.append(f"source={a_row['source']}")
    if "search_query" in a_row and a_row["search_query"]:
        notes_bits.append(f"query={a_row['search_query']}")

    c_row = {
        "id": f"C-{i+1:04d}",
        "screening_id": b_row["id"],           # FK to B
        "key_findings": "pilot key finding (MVP)",
        "extracted_at": ts,
        "notes": "; ".join(notes_bits) if notes_bits else "n/a",
    }
    return c_row


def main() -> int:
    # Read Appendix A
    a_data = _read_json(A_FILE)
    a_rows = _extract_rows_from_appendix_a(a_data)

    # Prepare outputs
    ts = _now_utc_iso()
    b_rows: List[Dict[str, Any]] = []
    c_rows: List[Dict[str, Any]] = []

    for i, a_row in enumerate(a_rows):
        b = _mk_screening_row(i, a_row, ts)
        b_rows.append(b)
        c = _mk_extraction_row(i, b, ts, a_row)
        c_rows.append(c)

    # Write only B and C
    _write_json_array(B_FILE, b_rows)
    _write_json_array(C_FILE, c_rows)

    # Simple summary to STDOUT (used by the workflow log)
    summary = {
        "read": {
            "A_FILE": str(A_FILE),
        },
        "written": {
            "B_FILE": str(B_FILE),
            "C_FILE": str(C_FILE),
        },
        "counts": {
            "a": len(a_rows),
            "b": len(b_rows),
            "c": len(c_rows),
        },
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
