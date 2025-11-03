#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# ELIS – Imports → Appendix A (manual exports MVP)
#
# Purpose
#   Convert one or more CSV files exported from a bibliographic database
#   (currently: Scopus) into the canonical Appendix A JSON artefact:
#
#       json_jsonl/ELIS_Appendix_A_Search_rows.json
#
#   This allows manual UI exports (for example, via Imperial's Comet
#   browser) to feed the ELIS SLR Agent pipeline without going through
#   the live API integration.
#
# Scope (MVP)
#   - Supported provider: "scopus_csv"
#   - Supported format: UTF-8, comma-separated CSV, with Scopus-style
#     headers such as:
#       Title, Authors, Year, DOI, Source title, Publisher, Abstract,
#       Language of Original Document, EID, Link
#
# Protocol alignment
#   - The output JSON matches the Appendix A shape produced by
#     scripts/elis/search_mvp.py:
#       * JSON array
#       * First element is a `_meta` block with protocol + summary
#       * Subsequent elements are paper records
#
#   - We record provenance in `_meta.run_inputs` including:
#       * channel  = "manual_import"
#       * provider = "scopus"
#       * source_format = "csv"
#       * query_topic / query_string
#
# Design notes
#   - Standard library only (no external Python dependencies).
#   - Case-insensitive header handling to tolerate minor Scopus changes.
#   - Dedup strategy: prefer DOI; else hash of normalised title + year.
#   - Safe to run multiple times; each run overwrites the canonical
#     Appendix A JSON.
#   - If run inside GitHub Actions, the script writes a Step Summary
#     into $GITHUB_STEP_SUMMARY so reviewers see counts at a glance.
#
# Usage (example)
#   python scripts/elis/imports_to_appendix_a.py \
#     --provider scopus_csv \
#     --csv imports/scopus_export_2025-10-31.csv \
#     --config-path json_jsonl/config/ELIS_Appendix_A_Search_config.json \
#     --query-topic integrity_auditability_core \
#     --query-string 'TITLE-ABS-KEY("electoral integrity") AND PUBYEAR > 1990' \
#     --year-from 1990 --year-to 2025 --languages en,fr,es,pt
#
# Exit codes
#   0 = success
#   2 = bad arguments / unsupported provider
#   other non-zero = runtime error
# =============================================================================

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
from collections import Counter
from typing import Any, Dict, List, Optional, Set

CANONICAL_A = "json_jsonl/ELIS_Appendix_A_Search_rows.json"


# ---------------------------- helpers ----------------------------------------
def now_utc_iso() -> str:
    """Return UTC timestamp in ISO 8601 (no microseconds, trailing Z)."""
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_dirs() -> None:
    """Create output directories for the canonical Appendix A file."""
    os.makedirs(os.path.dirname(CANONICAL_A), exist_ok=True)


def norm(s: Optional[str]) -> Optional[str]:
    """Normalise a scalar string: strip whitespace, return None if empty."""
    if s is None:
        return None
    s = s.strip()
    return s or None


def normalise_title(title: Optional[str]) -> str:
    """
    Normalise title for deduplication:
    - lower-case
    - strip punctuation
    - collapse repeated whitespace
    """
    if not title:
        return ""
    t = re.sub(r"[^\w\s]", " ", title.lower())
    return re.sub(r"\s+", " ", t).strip()


def stable_id(doi: Optional[str], title: Optional[str], year: Optional[int]) -> str:
    """
    Produce a stable deterministic identifier for a record.

    Preferred form:
      - "doi:<doi>"  when DOI is present
      - "t:<hash>"   where hash is SHA256 of "<normalised_title>|<year>"
    """
    if doi:
        return "doi:" + doi.lower().strip()
    t = normalise_title(title)
    y = str(year or "")
    payload = f"{t}|{y}".encode("utf-8")
    return "t:" + hashlib.sha256(payload).hexdigest()[:20]


def split_authors(raw: Optional[str]) -> List[str]:
    """
    Split Scopus-style author lists into a list of names.

    Scopus often uses comma or semicolon as separators and may append
    affiliation markers like "(1)". We strip those trailing markers.
    """
    if not raw:
        return []
    parts = re.split(r"[;,]", raw)
    out: List[str] = []
    for p in parts:
        name = p.strip()
        # Remove trailing "(1)", "(2)", etc. used for affiliations.
        name = re.sub(r"\(\d+\)$", "", name).strip()
        if name:
            out.append(name)
    return out


def get_col(row: Dict[str, str], *candidates: str) -> Optional[str]:
    """
    Fetch the first present candidate column from a CSV row,
    in a case-insensitive way.

    Returns normalised string or None.
    """
    lower_map = {k.lower(): k for k in row.keys()}
    for cand in candidates:
        key = lower_map.get(cand.lower())
        if key is not None:
            return norm(row.get(key))
    return None


def to_int(s: Optional[str]) -> Optional[int]:
    """Robustly coerce a string to int, returning None on failure."""
    try:
        return int(s) if s is not None and s != "" else None
    except Exception:
        return None


# ----------------------- Scopus CSV conversion -------------------------------
def convert_scopus_csv(
    csv_paths: List[str],
    topic: str,
    query: Optional[str],
) -> List[Dict[str, Any]]:
    """
    Convert one or more Scopus CSV exports into ELIS Appendix A records.

    Each CSV is expected to be UTF-8, comma-separated, with Scopus-style
    headers. The function:
      - maps common Scopus columns to ELIS fields
      - deduplicates across all files
      - returns a list of record dictionaries
    """
    results: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    for path in csv_paths:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                title = get_col(row, "Title", "Document Title")
                authors_raw = get_col(row, "Authors", "Author(s)")
                authors = split_authors(authors_raw)
                year = to_int(get_col(row, "Year"))
                doi = get_col(row, "DOI")
                venue = get_col(
                    row,
                    "Source title",
                    "Publication Title",
                    "Source Title",
                )
                publisher = get_col(row, "Publisher")
                abstract = get_col(row, "Abstract")
                language = get_col(
                    row,
                    "Language of Original Document",
                    "Language",
                )
                url = get_col(row, "Link", "URL")
                eid = get_col(row, "EID")

                rec: Dict[str, Any] = {
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "doi": doi,
                    "venue": venue,
                    "publisher": publisher,
                    "abstract": abstract,
                    # Normalise language to lower-case if present; keep full name.
                    "language": language.lower() if language else None,
                    "url": url,
                    "doc_type": None,  # Scopus UI CSV does not always expose this cleanly.
                    "source": "scopus",
                    "source_id": eid or doi or url,
                    "query_topic": topic,
                    "query_string": query,
                    "retrieved_at": now_utc_iso(),
                }

                key = stable_id(doi, title, year)
                if key in seen:
                    continue
                seen.add(key)
                rec["id"] = key
                # Temporary backwards-compatibility field until all consumers
                # are migrated to the canonical "id".
                rec["_stable_id"] = key
                results.append(rec)

    return results


# ----------------------- meta & summary --------------------------------------
def build_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Summarise the record set:
      - total count
      - counts per source
      - counts per topic
    """
    per_source = Counter(r.get("source") for r in records if r.get("source"))
    per_topic = Counter(r.get("query_topic") for r in records if r.get("query_topic"))

    return {
        "total": len(records),
        "per_source": dict(
            sorted(per_source.items(), key=lambda x: (-x[1], x[0] or ""))
        ),
        "per_topic": dict(
            sorted(per_topic.items(), key=lambda x: (-x[1], x[0] or ""))
        ),
    }


def write_json_array(path: str, records: List[Dict[str, Any]], meta: Dict[str, Any]) -> None:
    """
    Write a JSON array with a leading _meta element followed by records.

    The file is encoded as UTF-8 with indentation for readability.
    """
    ensure_dirs()
    payload: List[Dict[str, Any]] = [{"_meta": True, **meta}] + records
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_step_summary(meta: Dict[str, Any]) -> None:
    """
    If running under GitHub Actions, append a compact summary of the
    import conversion to $GITHUB_STEP_SUMMARY.

    This is intentionally read-only and safe; it does not affect exit
    codes.
    """
    summary = meta.get("summary") or {}
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return

    total = summary.get("total", 0)
    provider = meta.get("run_inputs", {}).get("provider", "unknown")
    channel = meta.get("run_inputs", {}).get("channel", "manual_import")
    topic_ids = meta.get("topics_enabled", [])

    lines: List[str] = []
    lines.append("## Imports → Appendix A summary")
    lines.append("")
    lines.append(f"- Channel: **{channel}**")
    lines.append(f"- Provider: **{provider}**")
    lines.append(f"- Output file: `{CANONICAL_A}`")
    lines.append(f"- Total unique records: **{total}**")
    lines.append("")
    if topic_ids:
        lines.append("### Topics")
        for t in topic_ids:
            lines.append(f"- `{t}`")
        lines.append("")
    lines.append("### Per source")
    lines.append("| Source | Records |")
    lines.append("|--------|---------|")
    for src, count in (summary.get("per_source") or {}).items():
        label = src or "(unknown)"
        lines.append(f"| {label} | {count} |")
    lines.append("")
    lines.append("### Per topic")
    lines.append("| Topic ID | Records |")
    lines.append("|----------|---------|")
    for topic_id, count in (summary.get("per_topic") or {}).items():
        label = topic_id or "(unknown)"
        lines.append(f"| {label} | {count} |")
    lines.append("")

    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------- CLI -------------------------------------------
def main(argv: List[str]) -> int:
    """CLI entrypoint for manual imports → Appendix A conversion."""
    import argparse

    ap = argparse.ArgumentParser(
        description="Convert manual database exports into Appendix A JSON (MVP)",
    )
    ap.add_argument(
        "--provider",
        required=True,
        help="Provider/format identifier (currently: scopus_csv)",
    )
    ap.add_argument(
        "--csv",
        action="append",
        dest="csv_paths",
        help="Path to a Scopus CSV export (repeatable)",
    )
    ap.add_argument(
        "--config-path",
        default="json_jsonl/config/ELIS_Appendix_A_Search_config.json",
        help="Path to the search config used (for metadata only)",
    )
    ap.add_argument(
        "--query-topic",
        default="scopus_ui_manual",
        help="Topic identifier for provenance (e.g., integrity_auditability_core)",
    )
    ap.add_argument(
        "--query-string",
        default=None,
        help="Exact search string used in the provider UI (optional but recommended)",
    )
    ap.add_argument(
        "--year-from",
        type=int,
        default=1990,
        help="Lower bound year used for the search (for metadata only)",
    )
    ap.add_argument(
        "--year-to",
        type=int,
        default=dt.datetime.utcnow().year,
        help="Upper bound year used for the search (for metadata only)",
    )
    ap.add_argument(
        "--languages",
        default="en,fr,es,pt",
        help="Comma-separated list of languages (for metadata only)",
    )

    args = ap.parse_args(argv)

    provider = args.provider.strip().lower()
    if provider != "scopus_csv":
        sys.stderr.write(f"Unsupported provider: {provider!r} (MVP only handles scopus_csv)\n")
        return 2

    csv_paths = args.csv_paths or []
    if not csv_paths:
        sys.stderr.write("At least one --csv path is required for scopus_csv.\n")
        return 2

    records = convert_scopus_csv(csv_paths, args.query_topic, args.query_string)
    summary = build_summary(records)

    languages = [
        s.strip()
        for s in (args.languages or "").split(",")
        if s.strip()
    ]

    meta: Dict[str, Any] = {
        "protocol_version": "ELIS 2025 (MVP)",
        "config_path": args.config_path,
        "retrieved_at": now_utc_iso(),
        "global": {
            "year_from": args.year_from,
            "year_to": args.year_to,
            "languages": languages,
            "max_results_per_source": None,
            "job_result_cap": None,
        },
        "topics_enabled": [args.query_topic],
        "sources": ["scopus"] if records else [],
        "record_count": len(records),
        "summary": summary,
        "run_inputs": {
            "channel": "manual_import",
            "provider": "scopus",
            "source_format": "csv",
            "workflow": os.environ.get("GITHUB_WORKFLOW"),
            "query_topic": args.query_topic,
            "query_string": args.query_string,
        },
    }

    write_json_array(CANONICAL_A, records, meta)
    write_step_summary(meta)
    print(f"Wrote {CANONICAL_A} with {len(records)} records.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
