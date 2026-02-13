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


def main(argv: List[str] | None = None) -> int:
    """Main validation function. Returns 0 always (informational, not blocking)."""
    appendices = {
        "Appendix A (Search)": (
            Path("json_jsonl/ELIS_Appendix_A_Search_rows.json"),
            Path("schemas/appendix_a.schema.json"),
        ),
        "Appendix B (Screening)": (
            Path("json_jsonl/ELIS_Appendix_B_Screening_rows.json"),
            Path("schemas/appendix_b.schema.json"),
        ),
        "Appendix C (Extraction)": (
            Path("json_jsonl/ELIS_Appendix_C_Extraction_rows.json"),
            Path("schemas/appendix_c.schema.json"),
        ),
    }

    results = {}

    for name, (json_file, schema_file) in appendices.items():
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


if __name__ == "__main__":
    sys.exit(main())
