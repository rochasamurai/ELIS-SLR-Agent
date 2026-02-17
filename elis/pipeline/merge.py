"""ELIS pipeline - canonical Appendix A merge stage (PE3)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

CANONICAL_OUTPUT = "json_jsonl/ELIS_Appendix_A_Search_rows.json"
CANONICAL_REPORT = "json_jsonl/merge_report.json"
_EPOCH_ISO = "1970-01-01T00:00:00Z"


def _collapse_ws(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip())


def normalise_doi(doi: str | None) -> str:
    value = (doi or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix) :]
            break
    return value


def normalise_year(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _stable_id(record: dict[str, Any]) -> str:
    doi = normalise_doi(record.get("doi"))
    if doi:
        return f"doi:{doi}"

    title = _collapse_ws(record.get("title")).lower()
    year = normalise_year(record.get("year"))
    source = str(record.get("source", "")).strip().lower()
    source_id = str(record.get("source_id", "")).strip().lower()
    key = f"{title}|{year or ''}|{source}|{source_id}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
    return f"t:{digest}"


def _load_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    if text.startswith("["):
        payload = json.loads(text)
        if not isinstance(payload, list):
            raise ValueError(f"Expected JSON array in {path}")
        return [
            item
            for item in payload
            if isinstance(item, dict) and not bool(item.get("_meta"))
        ]

    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if isinstance(row, dict) and not bool(row.get("_meta")):
            rows.append(row)
    return rows


def _normalise_record(
    record: dict[str, Any], *, source_file: str, merge_position: int
) -> dict[str, Any]:
    source = _collapse_ws(str(record.get("source", "") or source_file)).lower()
    title = _collapse_ws(record.get("title"))
    authors = [
        _collapse_ws(str(author))
        for author in (record.get("authors") or [])
        if _collapse_ws(str(author))
    ]
    year = normalise_year(record.get("year"))
    doi = normalise_doi(record.get("doi"))

    query_topic = _collapse_ws(str(record.get("query_topic", "") or "unknown"))
    query_string = _collapse_ws(str(record.get("query_string", "") or ""))
    retrieved_at = _collapse_ws(str(record.get("retrieved_at", "") or _EPOCH_ISO))
    source_id = _collapse_ws(str(record.get("source_id", "") or ""))

    merged = dict(record)
    merged.update(
        {
            "title": title,
            "authors": authors,
            "year": year,
            "doi": doi or None,
            "source": source,
            "source_id": source_id or None,
            "query_topic": query_topic,
            "query_string": query_string,
            "retrieved_at": retrieved_at,
            "source_file": source_file,
            "merge_position": merge_position,
        }
    )
    merged["id"] = str(record.get("id") or _stable_id(merged))
    merged["_stable_id"] = _stable_id(merged)
    return merged


def _sort_key(record: dict[str, Any]) -> tuple[str, str, str, int, int]:
    year = record.get("year")
    year_sort = year if isinstance(year, int) else -1
    return (
        str(record.get("source", "")),
        str(record.get("query_topic", "")),
        str(record.get("title", "")),
        year_sort,
        int(record.get("merge_position", 0)),
    )


def merge_inputs(input_paths: list[Path]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    position = 0

    for input_path in input_paths:
        for record in _load_records(input_path):
            position += 1
            merged.append(
                _normalise_record(
                    record,
                    source_file=input_path.name,
                    merge_position=position,
                )
            )

    merged.sort(key=_sort_key)
    return merged


def build_meta(
    records: list[dict[str, Any]], input_paths: list[Path]
) -> dict[str, Any]:
    per_source = Counter(
        str(record.get("source", "")) for record in records if record.get("source")
    )
    per_topic = Counter(
        str(record.get("query_topic", ""))
        for record in records
        if record.get("query_topic")
    )

    return {
        "_meta": True,
        "protocol_version": "ELIS 2025 (MVP)",
        "config_path": "elis merge --inputs",
        "retrieved_at": _EPOCH_ISO,
        "global": {},
        "topics_enabled": sorted(per_topic.keys()),
        "sources": sorted(per_source.keys()),
        "record_count": len(records),
        "summary": {
            "total": len(records),
            "per_source": dict(sorted(per_source.items(), key=lambda kv: kv[0])),
            "per_topic": dict(sorted(per_topic.items(), key=lambda kv: kv[0])),
        },
        "run_inputs": {"input_files": [str(path) for path in input_paths]},
    }


def build_report(
    records: list[dict[str, Any]], input_paths: list[Path]
) -> dict[str, Any]:
    per_source = Counter(
        str(record.get("source", "")) for record in records if record.get("source")
    )
    total = len(records)
    with_doi = sum(1 for record in records if record.get("doi"))
    doi_coverage_pct = round((with_doi / total) * 100, 1) if total else 0.0

    null_ratios = {}
    for field in ("title", "abstract", "language"):
        null_count = sum(1 for record in records if not record.get(field))
        null_ratios[field] = round((null_count / total), 4) if total else 0.0

    return {
        "total_records": total,
        "per_source_counts": dict(sorted(per_source.items(), key=lambda kv: kv[0])),
        "doi_coverage_pct": doi_coverage_pct,
        "null_field_ratios": null_ratios,
        "input_files": [str(path) for path in input_paths],
    }


def write_json_array(
    path: Path, records: list[dict[str, Any]], meta: dict[str, Any]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [meta] + records
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def run_merge(inputs: list[str], output: str, report: str) -> tuple[Path, Path]:
    input_paths = [Path(item) for item in inputs]
    records = merge_inputs(input_paths)
    meta = build_meta(records, input_paths)
    merge_report = build_report(records, input_paths)

    output_path = Path(output)
    report_path = Path(report)
    write_json_array(output_path, records, meta)
    write_json(report_path, merge_report)
    return output_path, report_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="elis merge", description="Merge Appendix A inputs"
    )
    parser.add_argument(
        "--inputs", nargs="+", required=True, help="Input JSON/JSONL files"
    )
    parser.add_argument(
        "--output", default=CANONICAL_OUTPUT, help="Merged Appendix A output path"
    )
    parser.add_argument("--report", default=CANONICAL_REPORT, help="Merge report path")
    args = parser.parse_args(argv)

    run_merge(args.inputs, args.output, args.report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
