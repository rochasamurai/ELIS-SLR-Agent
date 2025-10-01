"""
Toy ELIS SLR Agent runner.

Purpose
-------
Produce minimal, schema-aligned artefacts for Appendices A, B, and C so CI can
smoke-test the pipeline. If an Appendix A JSON file exists (from a prior step),
use its content as input; otherwise generate a dummy search query entry. Then
produce screening decisions (Step B) with a placeholder reason for each
decision, and a minimal extraction record for included items. Files are written
under `json_jsonl/` as pretty-printed JSON arrays.
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


def _now() -> str:
    """Return current UTC timestamp in ISO-8601 with trailing 'Z'."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data) -> None:
    """Write `data` to `path` as deterministic UTF-8 JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------------- #
# Core run
# --------------------------------------------------------------------------- #


def run():
    """
    Execute the toy agent logic: read Appendix A input (if available), generate
    screening decisions (Appendix B) and extraction records (Appendix C), and
    write them to disk.

    Returns
    -------
    dict: with keys 'a', 'b', 'c' corresponding to the lists of records for
    Appendices A, B, and C.
    """
    # Appendix A — Search (use existing input if available, else create a dummy)
    a_rows = []
    if A_FILE.exists():
        try:
            with A_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    a_rows = data
        except Exception:
            a_rows = []
    if not a_rows:
        a_rows = [
            {
                "id": "A-0001",
                "search_query": "electronic voting integrity",
                "source": "DemoEngine",
                "executed_at": _now(),
                "notes": "toy run",
            }
        ]

    # Appendix B — Screening (one included and one excluded decision)
    first_search_id = a_rows[0]["id"] if a_rows else "A-0001"
    b_rows = [
        {
            "id": "B-0001",
            "source_id": first_search_id,
            "title": "Pilot study on electronic voting",
            "decision": "included",
            "reason": "No reason required (included)",
            "decided_at": _now(),
        },
        {
            "id": "B-0002",
            "source_id": first_search_id,
            "title": "Blog post without methodology",
            "decision": "excluded",
            "reason": "Not peer-reviewed / out of scope",
            "decided_at": _now(),
        },
    ]

    # Appendix C — Extraction (only for included items)
    c_rows = []
    included_entry = next(
        (entry for entry in b_rows if entry["decision"] == "included"),
        None,
    )
    if included_entry:
        c_rows = [
            {
                "id": "C-0001",
                "screening_id": included_entry["id"],
                "key_findings": "Example extraction placeholder.",
                "extracted_at": _now(),
                "notes": "toy run",
            }
        ]

    # Persist all artefacts to JSON files
    _write_json(A_FILE, a_rows)
    _write_json(B_FILE, b_rows)
    _write_json(C_FILE, c_rows)

    return {"a": a_rows, "b": b_rows, "c": c_rows}


# --------------------------------------------------------------------------- #
# CLI entrypoint
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
                "counts": {key: len(val) for key, val in output.items()},
            },
            ensure_ascii=False,
            indent=2,
        )
    )
