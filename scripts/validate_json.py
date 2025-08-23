#!/usr/bin/env python3
"""
ELIS Agent — Validator (Rows/Config aware)
Validates JSON/JSONL files in ./json_jsonl against schemas in ./schemas.

Key features:
- Routes canonical execution artefacts (Rows) by filename patterns: *_rows.json
- Validates JSONL files line-by-line (Appendix D, Agent ValidationErrors)
- Codebook (Appendix E) as ARRAY supported; if the array schema is missing,
  falls back to validating EACH ITEM against the single-entry schema
- Auto-selects JSON Schema draft (draft-07 vs 2020-12) from schema["$schema"]
- Skips *_config.json by default (authoring files), with an option to include

Usage:
  python scripts/validate_json.py                 # validate all Rows/Logs
  python scripts/validate_json.py path/to/file    # validate a single file
  python scripts/validate_json.py --include-config
Exit codes: 0 = success, 1 = validation error, 2 = IO/config error
"""
import sys, os, re, json, argparse
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

# jsonschema imports (Draft selection handled dynamically)
from jsonschema import Draft7Validator, Draft202012Validator
try:
    # Present in jsonschema <5.x
    from jsonschema import Draft4Validator, Draft6Validator
except Exception:
    Draft4Validator = Draft6Validator = None

# RefResolver is deprecated but sufficient for our local file resolution
try:
    from jsonschema import RefResolver
except Exception:
    RefResolver = None

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "json_jsonl"
SCHEMA_DIR = REPO_ROOT / "schemas"

# -----------------------------------------------------------------------------
# Filename routing (Data Contract v1.0)
# -----------------------------------------------------------------------------
# Each entry: pattern -> dict(schema=..., mode=..., fallback=...)
# mode: "json" (validate whole JSON), "jsonl" (per-line)
# Special handling for Codebook (Appendix E) as ARRAY:
#   If ELIS_Appendix_E_CodebookArray.schema.json is absent, validate each item
#   against ELIS_Appendix_E_Codebook.schema.json
PATTERN_MAP: List[Tuple[re.Pattern, Dict[str, Any]]] = [
    # A/B/C Rows (execution artefacts)
    (re.compile(r"ELIS_Appendix_A_Search_rows\.json$"),
     {"schema": "ELIS_Appendix_A_Search.schema.json", "mode": "json"}),
    (re.compile(r"ELIS_Appendix_B_Screening_rows\.json$"),
     {"schema": "ELIS_Appendix_B_Screening.schema.json", "mode": "json"}),
    (re.compile(r"ELIS_Appendix_B_InclusionExclusion_rows\.json$"),
     {"schema": "ELIS_Appendix_B_InclusionExclusion.schema.json", "mode": "json"}),
    (re.compile(r"ELIS_Appendix_C_DataExtraction_rows\.json$"),
     {"schema": "ELIS_Appendix_C_DataExtraction.schema.json", "mode": "json"}),

    # Appendix E — Codebook as ARRAY (preferred)
    (re.compile(r"ELIS_Appendix_E_Codebook_\d{4}-\d{2}-\d{2}\.json$"),
     {"schema": "ELIS_Appendix_E_CodebookArray.schema.json",
      "mode": "json",
      "fallback_item_schema": "ELIS_Appendix_E_Codebook.schema.json"}),

    # Appendix F — Run Log & Policy (object)
    (re.compile(r"ELIS_Appendix_F_RunLogPolicy_\d{4}-\d{2}-\d{2}\.json$"),
     {"schema": "ELIS_Appendix_F_RunLogPolicy.schema.json", "mode": "json"}),

    # Appendix D — Audit Log (JSONL)
    (re.compile(r"ELIS_Appendix_D_AuditLog_\d{4}-\d{2}-\d{2}\.jsonl$"),
     {"schema": "ELIS_Appendix_D_AuditLog.schema.json", "mode": "jsonl"}),

    # Agent Validation Errors (JSONL)
    (re.compile(r"ELIS_Agent_ValidationErrors(_\d{4}-\d{2}-\d{2})?\.jsonl$"),
     {"schema": "ELIS_Agent_ValidationErrors.schema.json", "mode": "jsonl"}),

    # Agent Log Rotation Policy (object)
    (re.compile(r"ELIS_Agent_LogRotationPolicy\.json$"),
     {"schema": "ELIS_Agent_LogRotationPolicy.schema.json", "mode": "json"}),

    # Optional composite workbook dump (object)
    (re.compile(r"ELIS_Data_Sheets_\d{4}-\d{2}-\d{2}_v1\.0\.json$"),
     {"schema": "ELIS_Data_Sheets_2025-08-19_v1.0.schema.json", "mode": "json"}),
]

# Patterns to explicitly skip (authoring files) unless --include-config
SKIP_CONFIG_PATTERNS = [
    re.compile(r"_config\.json$"),
]

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_schema(schema_name: str) -> Dict[str, Any]:
    schema_path = SCHEMA_DIR / schema_name
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

def select_validator(schema: Dict[str, Any]):
    """Pick an appropriate Validator class based on $schema."""
    uri = str(schema.get("$schema", "")).lower()
    # Common identifiers
    if "2020-12" in uri or "202012" in uri:
        return Draft202012Validator
    if "2019-09" in uri or "201909" in uri:
        # Draft201909 not imported; Draft202012 can usually validate as superset
        return Draft202012Validator
    if "draft-07" in uri or "draft7" in uri or "draft07" in uri:
        return Draft7Validator
    if ("draft-06" in uri or "draft6" in uri) and Draft6Validator is not None:
        return Draft6Validator
    if ("draft-04" in uri or "draft4" in uri) and Draft4Validator is not None:
        return Draft4Validator
    # Default safely to Draft7 if not specified
    return Draft7Validator

def make_validator(schema: Dict[str, Any]):
    ValidatorClass = select_validator(schema)
    if RefResolver is not None:
        resolver = RefResolver(base_uri=SCHEMA_DIR.as_uri() + "/", referrer=schema)
        return ValidatorClass(schema, resolver=resolver)
    return ValidatorClass(schema)

def match_route(filename: str) -> Optional[Dict[str, Any]]:
    for pattern, cfg in PATTERN_MAP:
        if pattern.search(filename):
            return cfg
    return None

def is_config_file(filename: str) -> bool:
    return any(p.search(filename) for p in SKIP_CONFIG_PATTERNS)

def iter_targets(paths: List[str], include_config: bool):
    if paths:
        for p in paths:
            path = Path(p)
            if not path.exists():
                print(f"[IO] File not found: {path}")
                sys.exit(2)
            yield path
        return

    if not DATA_DIR.exists():
        print(f"[IO] Data directory not found: {DATA_DIR}")
        sys.exit(2)

    for root, _, files in os.walk(DATA_DIR):
        for name in files:
            if not (name.endswith(".json") or name.endswith(".jsonl")):
                continue
            if not include_config and is_config_file(name):
                print(f"[SKIP] {name} — authoring Config file")
                continue
            yield Path(root) / name

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
def validate_json_instance(instance: Any, schema: Dict[str, Any], label: str) -> List[str]:
    """Return a list of error messages (empty if valid)."""
    v = make_validator(schema)
    errors = sorted(v.iter_errors(instance), key=lambda e: (list(e.path), e.message))
    messages = []
    for e in errors:
        loc = "/".join(str(p) for p in e.path) or "(root)"
        messages.append(f"{label} {loc} → {e.message}")
    return messages

def validate_json_file(path: Path, route: Dict[str, Any]) -> bool:
    fname = path.name
    mode = route.get("mode", "json")
    schema_name = route.get("schema")

    # Special-case: Appendix E Codebook array with fallback to item schema
    if "Codebook" in fname and fname.endswith(".json"):
        try:
            schema = load_schema(schema_name)
            errs = validate_json_instance(load_json(path), schema, fname)
            if errs:
                for m in errs:
                    print(f"[FAIL] {m}")
                return False
            print(f"[OK]   {fname}")
            return True
        except FileNotFoundError:
            # Fallback: validate each array item against single-entry schema
            item_schema_name = route.get("fallback_item_schema")
            if not item_schema_name:
                print(f"[IO] Missing schema {schema_name} and no fallback item schema configured for {fname}")
                return False
            try:
                data = load_json(path)
                if not isinstance(data, list):
                    print(f"[FAIL] {fname} (root) → expected array for Codebook")
                    return False
                item_schema = load_schema(item_schema_name)
                ok = True
                for i, obj in enumerate(data, 1):
                    errs = validate_json_instance(obj, item_schema, f"{fname}[{i}]")
                    if errs:
                        ok = False
                        for m in errs:
                            print(f"[FAIL] {m}")
                if ok:
                    print(f"[OK]   {fname} (validated item-by-item against {item_schema_name})")
                return ok
            except Exception as e:
                print(f"[IO] {fname} → {e}")
                return False

    # Regular JSON / JSONL files
    try:
        schema = load_schema(schema_name)
    except FileNotFoundError as e:
        print(f"[IO] {e}")
        return False

    try:
        if mode == "jsonl":
            ok = True
            with open(path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as je:
                        print(f"[FAIL] {fname}:{i} invalid JSONL → {je}")
                        ok = False
                        continue
                    errs = validate_json_instance(obj, schema, f"{fname}:{i}")
                    if errs:
                        ok = False
                        for m in errs:
                            print(f"[FAIL] {m}")
            if ok:
                print(f"[OK]   {fname} (JSONL)")
            return ok

        else:
            obj = load_json(path)
            errs = validate_json_instance(obj, schema, fname)
            if errs:
                for m in errs:
                    print(f"[FAIL] {m}")
                return False
            print(f"[OK]   {fname}")
            return True

    except FileNotFoundError as e:
        print(f"[IO] {e}")
        return False
    except Exception as e:
        print(f"[IO] {fname} → {e}")
        return False

def main():
    ap = argparse.ArgumentParser(description="ELIS Agent Validator (Rows/Config aware)")
    ap.add_argument("paths", nargs="*", help="Specific files to validate (optional)")
    ap.add_argument("--include-config", action="store_true",
                    help="Also attempt to validate *_config.json (authoring files). Default: skip.")
    ap.add_argument("--strict", action="store_true",
                    help="Treat unmapped files as failures (default: skip with notice).")
    args = ap.parse_args()

    overall_ok = True
    for path in iter_targets(args.paths, include_config=args.include_config):
        fname = path.name
        route = match_route(fname)

        if route is None:
            if is_config_file(fname) and not args.include_config:
                # Already announced as [SKIP] earlier
                continue
            msg = f"[SKIP] {fname} → no schema mapping (use --strict to fail)"
            if args.strict:
                print(msg.replace("[SKIP]", "[FAIL]"))
                overall_ok = False
            else:
                print(msg)
            continue

        ok = validate_json_file(path, route)
        overall_ok = overall_ok and ok

    sys.exit(0 if overall_ok else 1)

if __name__ == "__main__":
    main()
