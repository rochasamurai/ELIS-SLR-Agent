# scripts/agent.py
import argparse, json, os
from pathlib import Path
from datetime import datetime, date

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
OUT_DIR = REPO_ROOT / "json_jsonl"
TODAY = date.today().strftime("%Y-%m-%d")

def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def pick_enum(schema):
    enum = schema.get("enum")
    if enum:
        return enum[0]
    return None

def stub_for_format(fmt):
    if fmt == "date-time":
        return now_iso()
    if fmt == "date":
        return date.today().isoformat()
    if fmt == "uri":
        return "https://example.org/resource"
    if fmt == "email":
        return "example@example.com"
    if fmt in ("uuid", "id"):
        return "00000000-0000-0000-0000-000000000000"
    return "stub"

def number_with_min(schema):
    if "minimum" in schema:
        return max(schema.get("minimum", 0), 0)
    if "exclusiveMinimum" in schema:
        return max(schema.get("exclusiveMinimum", 0) + 1, 0)
    return 0

def integer_with_min(schema):
    n = number_with_min(schema)
    return int(n)

def string_with_min_len(schema):
    n = schema.get("minLength", 0)
    if n <= 0:
        return "stub"
    return "x" * n

def stub_from_schema(schema):
    # Handle $ref/oneOf/anyOf quickly (choose first)
    if "$ref" in schema:
        # Best effort: if definitions provided inline, ignore and fallback to generic
        pass
    if "oneOf" in schema and isinstance(schema["oneOf"], list) and schema["oneOf"]:
        return stub_from_schema(schema["oneOf"][0])
    if "anyOf" in schema and isinstance(schema["anyOf"], list) and schema["anyOf"]:
        return stub_from_schema(schema["anyOf"][0])

    t = schema.get("type")
    if isinstance(t, list):
        # choose first non-null
        t = [x for x in t if x != "null"][0] if t else None

    # Enum dominates type
    v = pick_enum(schema)
    if v is not None:
        return v

    if t == "object" or ("properties" in schema or "required" in schema):
        obj = {}
        props = schema.get("properties", {})
        required = schema.get("required", [])
        # prefill required fields
        for key in required:
            subschema = props.get(key, {})
            obj[key] = stub_from_schema(subschema) if subschema else "stub"
        # fill optional few fields (light touch)
        for key, subschema in props.items():
            if key not in obj:
                # keep small objects compact
                continue
        # additionalProperties: ignore for stub
        return obj

    if t == "array" or "items" in schema:
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 1)
        if isinstance(items_schema, list) and items_schema:
            # tuple validation — take the first position
            return [stub_from_schema(items_schema[0])]
        # normal homogeneous array
        count = max(1, min_items)
        return [stub_from_schema(items_schema) for _ in range(count)]

    if t == "number":
        return float(number_with_min(schema))
    if t == "integer":
        return int(integer_with_min(schema))
    if t == "boolean":
        return True
    if t == "string" or t is None:
        fmt = schema.get("format")
        if fmt:
            return stub_for_format(fmt)
        return string_with_min_len(schema)

    # Fallback
    return "stub"

def load_schema(name):
    path = SCHEMA_DIR / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[WRITE] {path.relative_to(REPO_ROOT)}")

def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for obj in rows:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"[WRITE] {path.relative_to(REPO_ROOT)} (JSONL)")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schemas", default=str(SCHEMA_DIR))
    parser.add_argument("--out", default=str(OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out)

    # Map schemas -> filenames que o validador espera
    targets = [
        ("ELIS_Appendix_A_Search.schema.json",            out_dir / "ELIS_Appendix_A_Search_rows.json", "json"),
        ("ELIS_Appendix_B_Screening.schema.json",         out_dir / "ELIS_Appendix_B_Screening_rows.json", "json"),
        ("ELIS_Appendix_B_InclusionExclusion.schema.json",out_dir / "ELIS_Appendix_B_InclusionExclusion_rows.json", "json"),
        ("ELIS_Appendix_C_DataExtraction.schema.json",    out_dir / "ELIS_Appendix_C_DataExtraction_rows.json", "json"),
        ("ELIS_Appendix_D_AuditLog.schema.json",          out_dir / f"ELIS_Appendix_D_AuditLog_{TODAY}.jsonl", "jsonl"),
        ("ELIS_Appendix_E_CodebookArray.schema.json",     out_dir / f"ELIS_Appendix_E_Codebook_{TODAY}.json", "json"),
        ("ELIS_Appendix_F_RunLogPolicy.schema.json",      out_dir / f"ELIS_Appendix_F_RunLogPolicy_{TODAY}.json", "json"),
    ]

    # Se não existir CodebookArray, tentar o fallback por item
    codebook_array_schema = load_schema("ELIS_Appendix_E_CodebookArray.schema.json")
    codebook_item_schema  = load_schema("ELIS_Appendix_E_Codebook.schema.json")
    if codebook_array_schema is None and codebook_item_schema is not None:
        # manter o mesmo nome de arquivo; validator tem fallback item-a-item
        pass

    for schema_name, outfile, mode in targets:
        schema = load_schema(schema_name)
        if schema is None:
            # tolerante: apenas informa
            print(f"[SKIP] Missing schema: {schema_name}")
            continue

        if mode == "jsonl":
            # gera ao menos uma linha válida
            row = stub_from_schema(schema)
            rows = [row]
            write_jsonl(outfile, rows)
        else:
            # caso especial E_Codebook com array
            if "Appendix_E_Codebook" in str(outfile.name) and codebook_array_schema is None and codebook_item_schema is not None:
                # gerar array de itens com base no schema de item
                item = stub_from_schema(codebook_item_schema)
                data = [item]  # o validator faz fallback item-a-item
                write_json(outfile, data)
            else:
                data = stub_from_schema(schema)
                write_json(outfile, data)

    print("[DONE] Agent stubs generated in json_jsonl/")

if __name__ == "__main__":
    main()
