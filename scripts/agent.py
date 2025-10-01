"""
Toy ELIS SLR Agent runner.

Produces minimal, schema-aligned artefacts for Appendices A, B, and C so CI can
smoke-test the pipeline. If an Appendix A JSON file exists (from a prior step),
use it; otherwise create a dummy search entry. Then emit Step B screening rows
(included + excluded with reason) and a minimal Step C extraction for included
items. Files are written under `json_jsonl/` as pretty-printed JSON arrays.
"""

import datetime
import json
import pathlib


# --------------------------------------------------------------------------- #
# Artefact locations (tests may override these module-level globals)
# --------------------------------------------------------------------------- #

ART_DIR = pathlib.Path("json_jsonl")
A_FILE = ART_DIR / "ELIS_Appendix_A_Search_rows.json"
B_FILE = ART_DIR / "ELIS_Appendix_B_Screening_rows.json"
C_FILE = ART_DIR / "ELIS_Appendix_C_Extraction_rows.json"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _now() -> str:
    """Return current UTC timestamp in ISO-8601 with trailing 'Z'."""
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _write_json(path: pathlib.Path, data) -> None:
    """Write `data` to `path` as deterministic UTF-8 JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------------- #
# Core run
# --------------------------------------------------------------------------- #


def run():
    """
    Read Appendix A input (if present), generate Appendix B decisions and
    Appendix C extraction, and persist them to disk.

    Returns
    -------
    dict: keys 'a', 'b', 'c' with the lists written to disk.
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
