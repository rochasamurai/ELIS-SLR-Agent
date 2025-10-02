"""
Toy ELIS SLR Agent runner.

Goal
----
Generate minimal, schema-like artefacts for Appendices A, B, and C so CI can
smoke-test the pipeline. If an Appendix A JSON file already exists, reuse it;
otherwise, create a small dummy input. Then produce:

- Appendix B (screening): one "included" and one "excluded" item with reasons.
- Appendix C (extraction): a tiny extraction row for the included item.

Files are written to `json_jsonl/` as pretty-printed JSON arrays.  The exact
field names are placeholders compatible with the MVP smoke tests.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


# --------------------------------------------------------------------------- #
# Artefact locations (tests may override these module-level globals)
# --------------------------------------------------------------------------- #

ART_DIR = Path("json_jsonl")
A_FILE = ART_DIR / "ELIS_Appendix_A_Search_rows.json"
B_FILE = ART_DIR / "ELIS_Appendix_B_Screening_rows.json"
C_FILE = ART_DIR / "ELIS_Appendix_C_Extraction_rows.json"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _now_iso_z() -> str:
    """Return current UTC time in ISO-8601 with trailing 'Z' (no offset)."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data) -> None:
    """
    Write `data` to `path` as deterministic UTF-8 JSON.

    Notes
    -----
    - Creates parent directories as needed.
    - Uses indent=2 and ensure_ascii=False for readability.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# --------------------------------------------------------------------------- #
# Core run
# --------------------------------------------------------------------------- #


def run():
    """
    Build A/B/C rows in memory and persist them to disk.

    Returns
    -------
    dict
        Mapping with keys 'a', 'b', 'c' (lists of dicts) representing
        Appendices A, B, and C respectively.
    """
    # Appendix A — reuse if present, otherwise create a single dummy row.
    a_rows = []
    if A_FILE.exists():
        try:
            loaded = json.loads(A_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                a_rows = loaded
        except Exception:
            # If input is malformed, fall back to a fresh dummy row.
            a_rows = []

    if not a_rows:
        a_rows = [
            {
                "id": "A-0001",
                "search_query": "electronic voting integrity",
                "source": "DemoEngine",
                "executed_at": _now_iso_z(),
                "notes": "toy run",
            }
        ]

    # Appendix B — one included and one excluded screening decision.
    first_search_id = a_rows[0]["id"] if a_rows else "A-0001"
    b_rows = [
        {
            "id": "B-0001",
            "source_id": first_search_id,
            "title": "Pilot study on electronic voting",
            "decision": "included",
            "reason": "No reason required (included)",
            "decided_at": _now_iso_z(),
        },
        {
            "id": "B-0002",
            "source_id": first_search_id,
            "title": "Blog post without methodology",
            "decision": "excluded",
            "reason": "Not peer-reviewed / out of scope",
            "decided_at": _now_iso_z(),
        },
    ]

    # Appendix C — minimal extraction for the included item.
    c_rows = []
    included = next((row for row in b_rows if row["decision"] == "included"), None)
    if included:
        c_rows = [
            {
                "id": "C-0001",
                "screening_id": included["id"],
                "key_findings": "Example extraction placeholder.",
                "extracted_at": _now_iso_z(),
                "notes": "toy run",
            }
        ]

    # Persist all artefacts.
    _write_json(A_FILE, a_rows)
    _write_json(B_FILE, b_rows)
    _write_json(C_FILE, c_rows)

    return {"a": a_rows, "b": b_rows, "c": c_rows}


# --------------------------------------------------------------------------- #
# CLI entry point
# --------------------------------------------------------------------------- #


if __name__ == "__main__":
    # Allow `python scripts/agent.py` for ad-hoc runs.
    output = run()
    print(
        json.dumps(
            {
                "written": {
                    "A_FILE": str(A_FILE),
                    "B_FILE": str(B_FILE),
                    "C_FILE": str(C_FILE),
                },
                "counts": {k: len(v) for k, v in output.items()},
            },
            ensure_ascii=False,
            indent=2,
        )
    )
