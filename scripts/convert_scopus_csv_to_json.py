"""
convert_scopus_csv_to_json.py
Convert a Scopus CSV export into Appendix A JSON array format.

Usage:
  python scripts/convert_scopus_csv_to_json.py --in imports/raw/scopus.csv --out imports/staging/scopus.json \
    --query-topic "<topic_id>" --query-string "<query>"
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


SCOPUS_SOURCE = "Scopus"


def normalize_header(header: str) -> str:
    return header.strip().lower()


def pick_field(row: Dict[str, str], candidates: List[str]) -> str:
    for key in candidates:
        if key in row and row[key]:
            return row[key]
    return ""


def split_authors(raw: str) -> List[str]:
    if not raw:
        return []
    # Scopus usually uses "; " between authors. Fall back to comma.
    if "; " in raw:
        parts = [p.strip() for p in raw.split(";")]
    else:
        parts = [p.strip() for p in raw.split(",")]
    return [p for p in parts if p]


def safe_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def make_id(doi: str, eid: str, title: str, year: Optional[int], authors: List[str]) -> str:
    if doi:
        return f"doi:{doi.lower().strip()}"
    if eid:
        return f"eid:{eid.strip()}"
    base = f"{title}|{year or ''}|{'|'.join(authors)}"
    return "sha1:" + hashlib.sha1(base.encode("utf-8")).hexdigest()


def build_meta(config_path: str, retrieved_at: str, record_count: int, query_topic: str) -> Dict:
    return {
        "_meta": True,
        "protocol_version": "ELIS 2025 (MVP)",
        "config_path": config_path,
        "retrieved_at": retrieved_at,
        "global": {},
        "topics_enabled": [query_topic],
        "sources": [SCOPUS_SOURCE],
        "record_count": record_count,
        "summary": {"total": record_count, "per_source": {SCOPUS_SOURCE: record_count}},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Scopus CSV export to Appendix A JSON.")
    parser.add_argument("--in", dest="input_path", required=True, help="Input CSV file path")
    parser.add_argument("--out", dest="output_path", required=True, help="Output JSON file path")
    parser.add_argument("--query-topic", required=True, help="Query topic identifier")
    parser.add_argument("--query-string", required=True, help="Original query string")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_path = Path(args.output_path)

    if not input_path.exists():
        print(f"Input not found: {input_path}")
        return 2

    retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with input_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("CSV has no header row.")
            return 2

        # Normalize header keys for case-insensitive access
        field_map = {normalize_header(h): h for h in reader.fieldnames}

        def get(row: Dict[str, str], keys: List[str]) -> str:
            normalized_row = {normalize_header(k): v for k, v in row.items()}
            return pick_field(normalized_row, keys)

        records = []
        for row in reader:
            normalized_row = {normalize_header(k): v for k, v in row.items()}

            title = pick_field(
                normalized_row,
                ["title", "document title"],
            )
            authors_raw = pick_field(
                normalized_row,
                ["authors", "author(s)", "author"],
            )
            authors = split_authors(authors_raw)
            year_raw = pick_field(normalized_row, ["year", "cover date"])
            year = safe_int(year_raw[:4] if year_raw else year_raw)
            doi = pick_field(normalized_row, ["doi"])
            abstract = pick_field(normalized_row, ["abstract"])
            url = pick_field(normalized_row, ["link", "url"])
            eid = pick_field(normalized_row, ["eid"])
            source_title = pick_field(
                normalized_row,
                ["source title", "publication title", "source"],
            )
            publisher = pick_field(normalized_row, ["publisher"])
            language = pick_field(normalized_row, ["language of original document", "language"])

            record_id = make_id(doi, eid, title, year, authors)

            record = {
                "id": record_id,
                "source": SCOPUS_SOURCE,
                "source_id": eid or None,
                "scopus_id": eid or None,
                "title": title or None,
                "authors": authors,
                "year": year,
                "doi": doi or None,
                "venue": source_title or None,
                "publisher": publisher or None,
                "abstract": abstract or None,
                "language": language or None,
                "url": url or None,
                "query_topic": args.query_topic,
                "query_string": args.query_string,
                "retrieved_at": retrieved_at,
            }

            records.append(record)

    meta = build_meta(str(input_path), retrieved_at, len(records), args.query_topic)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        import json

        json.dump([meta] + records, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(records)} records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
