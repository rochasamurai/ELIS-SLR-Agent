#!/usr/bin/env python3
"""
ELIS – Toy Agent (MVP)
======================

Purpose
-------
Read Appendix A (Search rows) from ``json_jsonl/ELIS_Appendix_A_Search_rows.json``
and produce:
  • Appendix B (Screening rows)
  • Appendix C (Extraction rows)

This script **does not** write Appendix A. It only reads A and writes **B & C**.

Predictability
--------------
To keep downstream automation stable, this script **always writes Appendix C**,
even if there are zero "included" screening items (C will be an empty array).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# --------------------------------------------------------------------------- #
# Artefact locations (tests may override these module-level globals)
# --------------------------------------------------------------------------- #

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "json_jsonl"

A_FILE = ART_DIR / "ELIS_Appendix_A_Search_rows.json"
B_FILE = ART_DIR / "ELIS_Appendix_B_Screening_rows.json"
C_FILE = ART_DIR / "ELIS_Appendix_C_Extraction_rows.json"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _utc_now() -> str:
    """Return a UTC timestamp in RFC 3339 / ISO 8601 format with 'Z'."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json_array(path: Path) -> List[Dict[str, Any]]:
    """
    Load a JSON array from ``path``; return [] if the file is missing.

    We keep this tolerant for the MVP to simplify seeding Appendix A.
    """
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    # Allow both "array of rows" (recommended) and the older wrapper shape.
    if isinstance(data, dict) and "rows" in data and isinstance(data["rows"], list):
        return list(data["rows"])
    if isinstance(data, list):
        return list(data)
    raise ValueError(f"Expected a JSON array (or wrapper with 'rows') at {path}")


def _write_json_array(path: Path, rows: List[Dict[str, Any]]) -> None:
    """Write ``rows`` as pretty-printed JSON to ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", "utf-8")


# --------------------------------------------------------------------------- #
# Core
# --------------------------------------------------------------------------- #


def run() -> Dict[str, List[Dict[str, Any]]]:
    """
    Execute the toy agent logic:
      1) Read Appendix A rows.
      2) Create screening decisions (Appendix B) ensuring both 'included'
         and 'excluded' decisions appear in the output for predictability.
      3) Create extraction rows (Appendix C) **only** for 'included' items.
         C is **always written**, even if empty.

    Returns
    -------
    dict: {'a': [...], 'b': [...], 'c': [...]}
    """
    # 1) Load A (Search). The "array of objects" shape is the supported MVP shape.
    a_rows = _load_json_array(A_FILE)

    # 2) Build B (Screening).
    # Strategy:
    # - If we have 0 A rows → still produce B=[], and C will also be [].
    # - If we have 1 A row → produce two B decisions for the same source_id:
    #       one 'included' and one 'excluded' (keeps tests/pipeline predictable).
    # - If we have >=2 A rows → alternate included/excluded by index.
    b_rows: List[Dict[str, Any]] = []
    ts = _utc_now()

    if len(a_rows) == 0:
        b_rows = []
    elif len(a_rows) == 1:
        source_id = str(a_rows[0].get("id", "A-0001"))
        b_rows = [
            {
                "id": f"B-{source_id}-INC",
                "source_id": source_id,
                "title": a_rows[0].get("title", "N/A"),
                "decision": "included",
                "reason": "MVP toy include",
                "decided_at": ts,
            },
            {
                "id": f"B-{source_id}-EXC",
                "source_id": source_id,
                "title": a_rows[0].get("title", "N/A"),
                "decision": "excluded",
                "reason": "MVP toy exclude",
                "decided_at": ts,
            },
        ]
    else:
        for idx, row in enumerate(a_rows):
            source_id = str(row.get("id", f"A-{idx+1:04d}"))
            decision = "included" if idx % 2 == 0 else "excluded"
            b_rows.append(
                {
                    "id": f"B-{source_id}",
                    "source_id": source_id,
                    "title": row.get("title", "N/A"),
                    "decision": decision,
                    "reason": f"MVP toy {decision}",
                    "decided_at": ts,
                }
            )

    # 3) Build C (Extraction) for included screenings only.
    c_rows: List[Dict[str, Any]] = []
    for b in b_rows:
        if b.get("decision") != "included":
            continue
        c_rows.append(
            {
                "id": f"C-{b['id']}",
                "screening_id": b["id"],
                "key_findings": "MVP toy extraction placeholder",
                "extracted_at": ts,
                "notes": "Auto-generated by toy agent.",
            }
        )

    # 4) Write B and C. C is **always written**, even if empty.
    _write_json_array(B_FILE, b_rows)
    _write_json_array(C_FILE, c_rows)

    return {"a": a_rows, "b": b_rows, "c": c_rows}


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    result = run()
    # Print a concise summary for workflow logs.
    print(
        json.dumps(
            {
                "written": {
                    "B_FILE": str(B_FILE),
                    "C_FILE": str(C_FILE),
                },
                "counts": {
                    "a": len(result["a"]),
                    "b": len(result["b"]),
                    "c": len(result["c"]),
                },
            }
        )
    )
