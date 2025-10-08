#!/usr/bin/env python3
"""
ELIS – Validate artefacts against JSON Schemas (non-blocking).

Purpose
-------
Validate the three ELIS MVP artefacts produced under `json_jsonl/`:

  - ELIS_Appendix_A_Search_rows.json
  - ELIS_Appendix_B_Screening_rows.json
  - ELIS_Appendix_C_DataExtraction_rows.json

against minimal JSON Schemas in `schemas/`.

Behaviour
---------
- Generates a Markdown report at `validation_reports/validation-report.md`.
- Prints a short summary to STDOUT for CI logs.
- **Never blocks CI**: exits with code 0 even if validation errors are found.

Strict formats (post-MVP)
-------------------------
We default to *non-strict* JSON Schema format checking to keep MVP friction low.
When you are ready to tighten validation (e.g., enforce RFC 3339 “date-time”):

  1) Pin dependency:   jsonschema[format-nongpl]==4.23.0  (in requirements.txt)
  2) Run this script with --strict-formats or set ELIS_STRICT_FORMATS=1

Until then, --strict-formats is available but off by default (no behaviour change).
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator, FormatChecker

# -----------------------------------------------------------------------------
# Locations
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "json_jsonl"
A_PATH = DATA_DIR / "ELIS_Appendix_A_Search_rows.json"
B_PATH = DATA_DIR / "ELIS_Appendix_B_Screening_rows.json"
# FIX: align with agent/output naming (DataExtraction, not Extraction)
C_PATH = DATA_DIR / "ELIS_Appendix_C_DataExtraction_rows.json"

SCHEMA_DIR = ROOT / "schemas"
A_SCHEMA = SCHEMA_DIR / "appendix_a.schema.json"
B_SCHEMA = SCHEMA_DIR / "appendix_b.schema.json"
C_SCHEMA = SCHEMA_DIR / "appendix_c.schema.json"

REPORT_DIR = ROOT / "validation_reports"
REPORT_PATH = REPORT_DIR / "validation-report.md"

# How many individual row errors to include per section in the report.
ERROR_LIMIT_PER_SECTION = 50


# -----------------------------------------------------------------------------
# Data structures
# -----------------------------------------------------------------------------

@dataclass
class Result:
    """Container for per-appendix validation results."""

    name: str
    path: Path
    schema_path: Path
    ok: bool
    count: int
    errors: List[str]


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _load_json(path: Path) -> Any:
    """Load JSON from `path` (UTF-8). Raises on parse errors."""
    return json.loads(path.read_text(encoding="utf-8"))


def _load_schema(path: Path) -> Dict[str, Any]:
    """Load a JSON Schema from `path` (UTF-8)."""
    return json.loads(path.read_text(encoding="utf-8"))


def _make_validator(schema: Dict[str, Any], strict_formats: bool) -> Draft202012Validator:
    """
    Build a Draft 2020-12 validator.

    If `strict_formats` is true, attach a FormatChecker to enforce JSON-Schema
    "format" keywords (e.g., RFC 3339 'date-time'). For full strictness,
    ensure the environment installs `jsonschema[format-nongpl]`.
    """
    if strict_formats:
        return Draft202012Validator(schema, format_checker=FormatChecker())
    return Draft202012Validator(schema)


def _validate_rows(
    name: str, data_path: Path, schema_path: Path, strict_formats: bool
) -> Result:
    """
    Validate a JSON array of rows against `schema_path`.

    Returns
    -------
    Result
        ok=True when no validation errors were found.
    """
    if not data_path.exists():
        return Result(
            name=name,
            path=data_path,
            schema_path=schema_path,
            ok=False,
            count=0,
            errors=[f"Missing file: {data_path.name}"],
        )

    # Load data
    try:
        data = _load_json(data_path)
    except Exception as exc:  # pragma: no cover (robust logging)
        return Result(
            name=name,
            path=data_path,
            schema_path=schema_path,
            ok=False,
            count=0,
            errors=[f"JSON load failed: {exc!r}"],
        )

    if not isinstance(data, list):
        return Result(
            name=name,
            path=data_path,
            schema_path=schema_path,
            ok=False,
            count=0,
            errors=["File does not contain a JSON array"],
        )

    # Load schema
    try:
        schema = _load_schema(schema_path)
    except Exception as exc:  # pragma: no cover
        return Result(
            name=name,
            path=data_path,
            schema_path=schema_path,
            ok=False,
            count=len(data),
            errors=[f"Schema load failed: {exc!r}"],
        )

    validator = _make_validator(schema, strict_formats=strict_formats)

    errors: List[str] = []
    for idx, row in enumerate(data):
        for error in validator.iter_errors(row):
            loc = "/".join(str(p) for p in error.path) or "(root)"
            errors.append(f"row {idx}: {loc}: {error.message}")

    ok = not errors
    return Result(
        name=name,
        path=data_path,
        schema_path=schema_path,
        ok=ok,
        count=len(data),
        errors=errors,
    )


def _write_report(results: List[Result]) -> None:
    """Write a readable Markdown report to REPORT_PATH."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("# ELIS Validation Report (MVP)")
    lines.append("")
    for r in results:
        status = "✅ OK" if r.ok else "❌ Errors"
        lines.append(f"## {r.name} — {status}")
        lines.append("")
        lines.append(f"- File: `{r.path.relative_to(ROOT)}`")
        lines.append(f"- Schema: `{r.schema_path.relative_to(ROOT)}`")
        lines.append(f"- Row count: **{r.count}**")
        if r.ok:
            lines.append("- Findings: none")
        else:
            lines.append("- Findings:")
            for msg in r.errors[:ERROR_LIMIT_PER_SECTION]:
                lines.append(f"  - {msg}")
            if len(r.errors) > ERROR_LIMIT_PER_SECTION:
                lines.append(
                    f"  - ... and {len(r.errors) - ERROR_LIMIT_PER_SECTION} more"
                )
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# CLI / Main
# -----------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    """Parse optional CLI flags; defaults keep MVP behaviour."""
    parser = argparse.ArgumentParser(
        description="Validate ELIS artefacts against JSON Schemas (non-blocking)."
    )
    parser.add_argument(
        "--strict-formats",
        action="store_true",
        default=False,
        help=(
            "Enable strict JSON Schema 'format' checks (e.g., RFC 3339 date-time). "
            "Requires installing jsonschema[format-nongpl]."
        ),
    )
    return parser.parse_args()


def main() -> int:
    """
    Validate A/B/C artefacts and write a Markdown report.

    Always returns 0 (non-blocking by CI design).
    """
    args = _parse_args()
    strict_flag = (
        args.strict_formats or os.getenv("ELIS_STRICT_FORMATS", "0") in {"1", "true", "TRUE"}
    )

    results = [
        _validate_rows(
            "Appendix A (Search)", A_PATH, A_SCHEMA, strict_formats=strict_flag
        ),
        _validate_rows(
            "Appendix B (Screening)", B_PATH, B_SCHEMA, strict_formats=strict_flag
        ),
        _validate_rows(
            "Appendix C (Extraction)", C_PATH, C_SCHEMA, strict_formats=strict_flag
        ),
    ]

    # Emit a concise summary for CI logs.
    for r in results:
        status = "OK" if r.ok else "ERR"
        print(f"[{status}] {r.name}: rows={r.count} file={r.path.name}")

    _write_report(results)

    # Non-blocking by design (validate job must not fail merges).
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

