#!/usr/bin/env python3
"""
ELIS – JSON artefact validator (MVP)
====================================

Purpose
-------
Validate the three JSON artefacts (Appendix A/B/C) produced by the toy agent
against the minimal JSON Schemas under `schemas/`. Emit a small Markdown report
under `validation_reports/`. The CI workflow treats this step as non-blocking
by design, but the script can still exit with a non-zero code when asked.

Behaviour
---------
- Looks for:
    json_jsonl/ELIS_Appendix_A_Search_rows.json
    json_jsonl/ELIS_Appendix_B_Screening_rows.json
    json_jsonl/ELIS_Appendix_C_DataExtraction_rows.json
- Validates each list item against the corresponding schema.
- Writes a Markdown report with a short summary and any failures.

Flags
-----
--strict-exit   -> exit 1 when any validation error occurs (default: off)
--strict-dt     -> enable strict RFC3339 date-time checking (requires
                   jsonschema[format-nongpl] in requirements)

Notes
-----
Keep output deterministic and readable for CI diffs.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from jsonschema import Draft7Validator, FormatChecker  # type: ignore
except Exception as exc:  # pragma: no cover
    print(f"[validate] jsonschema import failed: {exc}", file=sys.stderr)
    sys.exit(2)

# --------------------------------------------------------------------------- #
# Repository layout
# --------------------------------------------------------------------------- #

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"
DATA_DIR = ROOT / "json_jsonl"
REPORTS_DIR = ROOT / "validation_reports"

A_PATH = DATA_DIR / "ELIS_Appendix_A_Search_rows.json"
B_PATH = DATA_DIR / "ELIS_Appendix_B_Screening_rows.json"
C_PATH = DATA_DIR / "ELIS_Appendix_C_DataExtraction_rows.json"

SCHEMA_A = SCHEMAS_DIR / "appendix_a.schema.json"
SCHEMA_B = SCHEMAS_DIR / "appendix_b.schema.json"
SCHEMA_C = SCHEMAS_DIR / "appendix_c.schema.json"

# --------------------------------------------------------------------------- #
# Utilities
# --------------------------------------------------------------------------- #


def load_json(path: Path) -> Any:
    """Load a JSON file if it exists; return None if missing."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"__error__": f"failed to parse JSON: {exc}"}


def load_schema(path: Path) -> Dict[str, Any]:
    """Load and return a JSON Schema."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"failed to load schema {path}: {exc}") from exc


def mk_validator(schema: Dict[str, Any], strict_dt: bool) -> Draft7Validator:
    """Build a Draft7 validator; optionally enable strict date-time."""
    if strict_dt:
        return Draft7Validator(schema, format_checker=FormatChecker())
    return Draft7Validator(schema)


def validate_rows(rows: Any, validator: Draft7Validator) -> Tuple[int, List[str]]:
    """
    Validate a JSON value expected to be a list of objects.

    Returns
    -------
    (error_count, messages)
    """
    messages: List[str] = []

    if rows is None:
        return 0, ["file missing (skipped)"]

    if isinstance(rows, dict) and "__error__" in rows:
        return 1, [rows["__error__"]]

    if not isinstance(rows, list):
        return 1, ["top-level JSON value is not an array"]

    err_count = 0
    for idx, item in enumerate(rows):
        errors = sorted(validator.iter_errors(item), key=lambda e: e.path)
        if not errors:
            continue
        err_count += len(errors)
        for e in errors:
            loc = "/".join(map(str, e.path)) or "<root>"
            messages.append(f"[{idx}] {loc}: {e.message}")

    return err_count, messages


def write_report(
    a_summary: Tuple[int, List[str]],
    b_summary: Tuple[int, List[str]],
    c_summary: Tuple[int, List[str]],
) -> Path:
    """Write a Markdown report and return its path."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    name = f"validation-report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    path = REPORTS_DIR / name

    def block(title: str, summary: Tuple[int, List[str]]) -> str:
        count, messages = summary
        lines = [f"### {title}", "", f"- errors: {count}"]
        if messages:
            lines.append("")
            lines.append("#### Details")
            lines.extend([f"- {m}" for m in messages])
        lines.append("")
        return "\n".join(lines)

    body = [
        "# ELIS – Validation Report",
        "",
        f"- generated: {ts}",
        "",
        block("Appendix A – Search", a_summary),
        block("Appendix B – Screening", b_summary),
        block("Appendix C – Data Extraction", c_summary),
        "",
        "_End of report._",
        "",
    ]

    path.write_text("\n".join(body), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate ELIS JSON artefacts.")
    parser.add_argument(
        "--strict-exit",
        action="store_true",
        help="exit with code 1 when any validation error occurs (default: off)",
    )
    parser.add_argument(
        "--strict-dt",
        action="store_true",
        help="enable strict RFC3339 'date-time' checking",
    )
    args = parser.parse_args(argv)

    schema_a = load_schema(SCHEMA_A)
    schema_b = load_schema(SCHEMA_B)
    schema_c = load_schema(SCHEMA_C)

    v_a = mk_validator(schema_a, args.strict_dt)
    v_b = mk_validator(schema_b, args.strict_dt)
    v_c = mk_validator(schema_c, args.strict_dt)

    rows_a = load_json(A_PATH)
    rows_b = load_json(B_PATH)
    rows_c = load_json(C_PATH)

    sum_a = validate_rows(rows_a, v_a)
    sum_b = validate_rows(rows_b, v_b)
    sum_c = validate_rows(rows_c, v_c)

    report = write_report(sum_a, sum_b, sum_c)
    print(f"[validate] wrote report: {report.relative_to(ROOT)}")

    total_errors = sum_a[0] + sum_b[0] + sum_c[0]
    if args.strict_exit and total_errors > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

