#!/usr/bin/env python3
# Minimal ELIS Agent stub for MVP: writes a valid A/rows file and exits 0.
import json, pathlib, datetime as dt

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "json_jsonl"
OUT.mkdir(parents=True, exist_ok=True)

payload = {
    "appendix": "Appendix_A",
    "generated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "rows": [
        {"field_a": "value1", "field_b": 123},
        {"field_a": "value2", "field_b": 456}
    ]
}

target = OUT / "ELIS_Appendix_A_Search_rows.json"
target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[WRITE] {target.relative_to(ROOT)}")
