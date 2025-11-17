#!/usr/bin/env python3
"""
ELIS SLR Agent - JSON Validator
Validates JSON artefacts against schemas, skipping metadata records.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
from jsonschema import Draft202012Validator


def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load JSON file with UTF-8 encoding.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of records (metadata records filtered out)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Ensure we have a list
    if not isinstance(data, list):
        raise ValueError(f"Expected array, got {type(data).__name__}")
    
    # Filter out metadata records (records with "_meta": true)
    records = [record for record in data if not record.get('_meta', False)]
    
    return records


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """
    Load JSON Schema file.
    
    Args:
        schema_path: Path to schema file
        
    Returns:
        Schema dictionary
    """
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_records(
    records: List[Dict[str, Any]], 
    schema: Dict[str, Any],
    file_name: str
) -> Tuple[bool, List[str]]:
    """
    Validate records against schema.
    
    Args:
        records: List of data records
        schema: JSON Schema (either full schema with 'items', or item schema directly)
        file_name: Name of file being validated (for error messages)
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # If schema has "items", extract it (it's a full array schema)
    # Otherwise, treat the schema as the item schema itself
    items_schema = schema.get("items", schema)
    
    if not items_schema or items_schema == {}:
        return True, []
    
    # Use appropriate validator based on schema version
    from jsonschema import Draft7Validator
    
    # Check schema version to use correct validator
    schema_version = items_schema.get("$schema", "")
    if "2020-12" in schema_version or "2019-09" in schema_version:
        validator = Draft202012Validator(items_schema)
    else:
        validator = Draft7Validator(items_schema)
    
    # Validate each record
    for idx, record in enumerate(records):
        validation_errors = list(validator.iter_errors(record))
        if validation_errors:
            for error in validation_errors:
                error_msg = f"row {idx}: {error.message}"
                if error.path:
                    field_path = '.'.join(str(p) for p in error.path)
                    error_msg = f"row {idx}, field '{field_path}': {error.message}"
                errors.append(error_msg)
    
    return len(errors) == 0, errors


def validate_appendix(
    appendix_name: str,
    json_file: Path,
    schema_file: Path
) -> Tuple[bool, int, List[str]]:
    """
    Validate an appendix file.
    
    Args:
        appendix_name: Human-readable name (e.g., "Appendix A (Search)")
        json_file: Path to JSON data file
        schema_file: Path to schema file
        
    Returns:
        Tuple of (is_valid, record_count, errors)
    """
    try:
        # Load data and schema
        records = load_json_file(json_file)
        schema = load_schema(schema_file)
        
        # Validate
        is_valid, errors = validate_records(records, schema, json_file.name)
        
        return is_valid, len(records), errors
        
    except FileNotFoundError as e:
        return False, 0, [f"File not found: {e}"]
    except json.JSONDecodeError as e:
        return False, 0, [f"Invalid JSON: {e}"]
    except Exception as e:
        return False, 0, [f"Unexpected error: {e}"]


def generate_report(results: Dict[str, Tuple[bool, int, List[str]]]) -> str:
    """
    Generate markdown validation report.
    
    Args:
        results: Dictionary of appendix results
        
    Returns:
        Markdown formatted report
    """
    lines = ["# ELIS Validation Report (MVP)", ""]
    
    for appendix_name, (is_valid, count, errors) in results.items():
        status = "✅ Valid" if is_valid else "❌ Errors"
        lines.append(f"## {appendix_name} — {status}")
        lines.append("")
        lines.append(f"- Row count: **{count}**")
        
        if errors:
            lines.append(f"- Error count: **{len(errors)}**")
            lines.append("- Errors:")
            for error in errors[:10]:  # Show first 10 errors
                lines.append(f"  - {error}")
            if len(errors) > 10:
                lines.append(f"  - ... and {len(errors) - 10} more errors")
        else:
            lines.append("- ✅ All records valid")
        
        lines.append("")
    
    return "\n".join(lines)


def main():
    """Main validation function."""
    # Define appendices to validate
    appendices = {
        "Appendix A (Search)": (
            Path("json_jsonl/ELIS_Appendix_A_Search_rows.json"),
            Path("schemas/appendix_a.schema.json")
        ),
        "Appendix B (Screening)": (
            Path("json_jsonl/ELIS_Appendix_B_Screening_rows.json"),
            Path("schemas/appendix_b.schema.json")
        ),
        "Appendix C (Extraction)": (
            Path("json_jsonl/ELIS_Appendix_C_Extraction_rows.json"),
            Path("schemas/appendix_c.schema.json")
        ),
    }
    
    # Validate each appendix
    results = {}
    
    for name, (json_file, schema_file) in appendices.items():
        # Skip if files don't exist
        if not json_file.exists():
            print(f"[SKIP] {name}: file not found")
            continue
        if not schema_file.exists():
            print(f"[SKIP] {name}: schema not found")
            continue
        
        is_valid, count, errors = validate_appendix(name, json_file, schema_file)
        results[name] = (is_valid, count, errors)
        
        # Print status
        status = "[OK]" if is_valid else "[ERR]"
        print(f"{status} {name}: rows={count} file={json_file.name}")
    
    # Generate and save reports
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    # Save timestamped report
    report = generate_report(results)
    report_dir = Path("validation_reports")
    report_dir.mkdir(exist_ok=True)
    
    timestamped_report = report_dir / f"{timestamp}_validation_report.md"
    timestamped_report.write_text(report, encoding='utf-8')
    
    # Also save as latest (for easy reference)
    latest_report = report_dir / "validation-report.md"
    latest_report.write_text(report, encoding='utf-8')
    
    print("\nReports saved:")
    print(f"  - Latest: {latest_report}")
    print(f"  - Timestamped: {timestamped_report}")
    
    # Exit with appropriate code (but don't fail CI)
    # We treat validation as informational, not blocking
    sys.exit(0)


if __name__ == "__main__":
    main()
    
