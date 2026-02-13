"""
ELIS pipeline — JSON Validator

Importable module wrapping the MVP validation logic from scripts/validate_json.py.
Validates JSON artefacts (Appendix A/B/C) against JSON Schemas and generates
Markdown validation reports.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from jsonschema import Draft202012Validator

log = logging.getLogger(__name__)


def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load JSON file with UTF-8 encoding.

    Returns list of records with metadata records (_meta: true) filtered out.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected array, got {type(data).__name__}")

    records = [record for record in data if not record.get("_meta", False)]
    return records


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load JSON Schema file."""
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_records(
    records: List[Dict[str, Any]], schema: Dict[str, Any], file_name: str
) -> Tuple[bool, List[str]]:
    """
    Validate records against schema.

    Returns (is_valid, list_of_errors).
    """
    errors = []

    items_schema = schema.get("items", schema)

    if not items_schema or items_schema == {}:
        return True, []

    from jsonschema import Draft7Validator

    schema_version = items_schema.get("$schema", "")
    if "2020-12" in schema_version or "2019-09" in schema_version:
        validator = Draft202012Validator(items_schema)
    else:
        validator = Draft7Validator(items_schema)

    for idx, record in enumerate(records):
        validation_errors = list(validator.iter_errors(record))
        if validation_errors:
            for error in validation_errors:
                error_msg = f"row {idx}: {error.message}"
                if error.path:
                    field_path = ".".join(str(p) for p in error.path)
                    error_msg = f"row {idx}, field '{field_path}': {error.message}"
                errors.append(error_msg)

    return len(errors) == 0, errors


def validate_appendix(
    appendix_name: str, json_file: Path, schema_file: Path
) -> Tuple[bool, int, List[str]]:
    """
    Validate an appendix file.

    Returns (is_valid, record_count, errors).
    """
    try:
        records = load_json_file(json_file)
        schema = load_schema(schema_file)
        is_valid, errors = validate_records(records, schema, json_file.name)
        return is_valid, len(records), errors

    except FileNotFoundError as e:
        return False, 0, [f"File not found: {e}"]
    except json.JSONDecodeError as e:
        return False, 0, [f"Invalid JSON: {e}"]
    except Exception as e:
        return False, 0, [f"Unexpected error: {e}"]


def generate_report(results: Dict[str, Tuple[bool, int, List[str]]]) -> str:
    """Generate markdown validation report."""
    lines = ["# ELIS Validation Report (MVP)", ""]

    for appendix_name, (is_valid, count, errors) in results.items():
        status = "\u2705 Valid" if is_valid else "\u274c Errors"
        lines.append(f"## {appendix_name} \u2014 {status}")
        lines.append("")
        lines.append(f"- Row count: **{count}**")

        if errors:
            lines.append(f"- Error count: **{len(errors)}**")
            lines.append("- Errors:")
            for error in errors[:10]:
                lines.append(f"  - {error}")
            if len(errors) > 10:
                lines.append(f"  - ... and {len(errors) - 10} more errors")
        else:
            lines.append("- \u2705 All records valid")

        lines.append("")

    return "\n".join(lines)


# ------------------------- Canonical appendix map ---------------------------
CANONICAL_APPENDICES: Dict[str, Tuple[str, str]] = {
    "Appendix A (Search)": (
        "json_jsonl/ELIS_Appendix_A_Search_rows.json",
        "schemas/appendix_a.schema.json",
    ),
    "Appendix B (Screening)": (
        "json_jsonl/ELIS_Appendix_B_Screening_rows.json",
        "schemas/appendix_b.schema.json",
    ),
    "Appendix C (Extraction)": (
        "json_jsonl/ELIS_Appendix_C_Extraction_rows.json",
        "schemas/appendix_c.schema.json",
    ),
}

# Map filename fragments to their canonical schemas for auto-detection.
_SCHEMA_HINTS: Dict[str, str] = {
    "appendix_a": "schemas/appendix_a.schema.json",
    "search": "schemas/appendix_a.schema.json",
    "appendix_b": "schemas/appendix_b.schema.json",
    "screening": "schemas/appendix_b.schema.json",
    "appendix_c": "schemas/appendix_c.schema.json",
    "extraction": "schemas/appendix_c.schema.json",
}


def _infer_schema(data_path: Path) -> Path | None:
    """Try to guess the schema from the data filename."""
    stem = data_path.stem.lower()
    for hint, schema_rel in _SCHEMA_HINTS.items():
        if hint in stem:
            return Path(schema_rel)
    return None


def run_full_validation() -> int:
    """Legacy behaviour: validate all canonical appendices, write reports.

    Returns 0 always (informational, not blocking).
    """
    results: Dict[str, Tuple[bool, int, List[str]]] = {}

    for name, (json_rel, schema_rel) in CANONICAL_APPENDICES.items():
        json_file = Path(json_rel)
        schema_file = Path(schema_rel)
        if not json_file.exists():
            print(f"[SKIP] {name}: file not found")
            continue
        if not schema_file.exists():
            print(f"[SKIP] {name}: schema not found")
            continue

        is_valid, count, errors = validate_appendix(name, json_file, schema_file)
        results[name] = (is_valid, count, errors)

        status = "[OK]" if is_valid else "[ERR]"
        print(f"{status} {name}: rows={count} file={json_file.name}")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    report = generate_report(results)
    report_dir = Path("validation_reports")
    report_dir.mkdir(exist_ok=True)

    timestamped_report = report_dir / f"{timestamp}_validation_report.md"
    timestamped_report.write_text(report, encoding="utf-8")

    latest_report = report_dir / "validation-report.md"
    latest_report.write_text(report, encoding="utf-8")

    print("\nReports saved:")
    print(f"  - Latest: {latest_report}")
    print(f"  - Timestamped: {timestamped_report}")

    return 0


# ------------------------- CLI entrypoint ------------------------------------
def main(argv: List[str] | None = None) -> int:
    """CLI for ELIS JSON validation.

    Modes:
      elis validate                        Legacy full validation (all appendices)
      elis validate --data F --schema S    Validate data file against explicit schema
      elis validate <data.json>            Validate data file; schema inferred from name
    """
    import argparse

    if argv is None:
        argv = sys.argv[1:]

    ap = argparse.ArgumentParser(
        prog="elis validate",
        description="Validate ELIS JSON artefacts against schemas.",
    )
    ap.add_argument(
        "data_pos",
        nargs="?",
        default=None,
        metavar="DATA",
        help="JSON data file to validate (positional shorthand for --data)",
    )
    ap.add_argument(
        "--data",
        default=None,
        dest="data_flag",
        metavar="FILE",
        help="JSON data file to validate",
    )
    ap.add_argument(
        "--schema",
        default=None,
        metavar="FILE",
        help="JSON Schema file (inferred from data filename when omitted)",
    )
    args = ap.parse_args(argv)

    data_path_str = args.data_flag or args.data_pos

    # No explicit data → legacy full validation run.
    if data_path_str is None:
        return run_full_validation()

    # Explicit data file supplied → single-file validation mode.
    data_path = Path(data_path_str)
    if not data_path.exists():
        print(f"Error: data file not found: {data_path}", file=sys.stderr)
        return 1

    if args.schema:
        schema_path = Path(args.schema)
    else:
        schema_path = _infer_schema(data_path)
        if schema_path is None:
            print(
                f"Error: cannot infer schema for '{data_path.name}'. "
                "Use --schema to specify explicitly.",
                file=sys.stderr,
            )
            return 2

    if not schema_path.exists():
        print(f"Error: schema file not found: {schema_path}", file=sys.stderr)
        return 1

    is_valid, count, errors = validate_appendix(data_path.name, data_path, schema_path)

    status = "[OK]" if is_valid else "[ERR]"
    print(f"{status} {data_path.name}: rows={count}")
    for err in errors[:10]:
        print(f"  - {err}")
    if len(errors) > 10:
        print(f"  - ... and {len(errors) - 10} more errors")

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
