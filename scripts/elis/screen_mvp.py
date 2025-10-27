# scripts/elis/screen_mvp.py
# =============================================================================
# ELIS – Appendix B (Screening) MVP
# Purpose
#   Read canonical Appendix A (Search results), apply protocol-aligned screening
#   filters, and write canonical Appendix B with the INCLUDED records only.
#
# Canonical paths
#   - Input (A):  json_jsonl/ELIS_Appendix_A_Search_rows.json
#   - Output (B): json_jsonl/ELIS_Appendix_B_Screening_rows.json
#
# What we screen (MVP)
#   - Publication year ∈ [year_from, year_to]
#   - Language must be one of the allowed ISO 639-1 codes
#     (unknown language is excluded in this MVP; see note below)
#   - Optional: enforce per-topic preprint policy
#       • If a topic has include_preprints=false (from A._meta.run_inputs or
#         topic defaults) AND a record is detected as a preprint (arXiv or
#         doc_type contains "preprint"), the record is excluded.
#
# Metadata we write at the head of the JSON array (_meta)
#   - protocol_version, input_path, output_path, retrieved_at
#   - run_inputs (effective knobs used this run)
#   - topics_enabled, sources_touched (for included set)
#   - counts: included_count, excluded_count, excluded_by_reason{reason: n}
#   - summary: total (included), per_source, per_topic (included only)
#
# Notes / limitations
#   - Language: Semantic Scholar and arXiv often omit language; in this MVP we
#     EXCLUDE unknown language with reason "language_unknown". If you prefer to
#     keep them for human screening, run with --allow-unknown-language.
#   - Field names follow Appendix A; we do not re-map or normalise beyond what
#     A already produced.
#   - Deterministic and side-effect free; output only differs with inputs.
#
# CI usage (recommended)
#   - Expose the flags below as workflow_dispatch inputs and call:
#       python scripts/elis/screen_mvp.py \
#         --input json_jsonl/ELIS_Appendix_A_Search_rows.json \
#         --output json_jsonl/ELIS_Appendix_B_Screening_rows.json \
#         --year-from 1990 --year-to 2025 \
#         --languages en,fr,es,pt \
#         --enforce-preprint-policy \
#         [--allow-unknown-language] \
#         [--dry-run]
#   - Always append the Step Summary produced to $GITHUB_STEP_SUMMARY.
# =============================================================================

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

# ------------------------- Canonical paths -----------------------------------
CANONICAL_A = "json_jsonl/ELIS_Appendix_A_Search_rows.json"
CANONICAL_B = "json_jsonl/ELIS_Appendix_B_Screening_rows.json"

# ------------------------- Logging -------------------------------------------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout
)

# ------------------------- Small helpers -------------------------------------


def now_utc_iso() -> str:
    """Return an ISO-8601 UTC timestamp without microseconds and with trailing Z."""
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_parent_dir(path: str) -> None:
    """Create the parent directory for `path` if it does not exist."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


def load_json_array(path: str) -> List[dict]:
    """Load a UTF-8 JSON array file and return the Python list."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array at {path}")
    return data


def write_json_array(path: str, arr: List[dict]) -> None:
    """Write a JSON array with trailing newline (git-friendly)."""
    ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(arr, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def is_preprint(rec: Dict[str, Any]) -> bool:
    """
    Heuristic preprint detection suitable for MVP:
      - source == "arxiv" OR
      - venue contains "arXiv" (case-insensitive) OR
      - doc_type contains "preprint"
    """
    src = (rec.get("source") or "").lower()
    if src == "arxiv":
        return True
    venue = (rec.get("venue") or "")
    if isinstance(venue, str) and "arxiv" in venue.lower():
        return True
    doc_type = (rec.get("doc_type") or "")
    if isinstance(doc_type, str) and "preprint" in doc_type.lower():
        return True
    return False


def within_years(year: Optional[int], y0: int, y1: int) -> bool:
    """Return True if year is an int within [y0, y1]."""
    if not isinstance(year, int):
        return False
    return y0 <= year <= y1


def lang_allowed(lang: Optional[str], allowed: Iterable[str], allow_unknown: bool) -> bool:
    """
    Whether `lang` is allowed given a set of ISO codes. Unknown language passes
    only if allow_unknown=True.
    """
    if not lang:
        return bool(allow_unknown)
    return lang.lower() in {x.lower() for x in allowed}


def md_table(rows: List[Tuple[str, int]], header_a: str, header_b: str) -> str:
    """Render a simple Markdown table for step summaries."""
    out = [f"| {header_a} | {header_b} |", "|---|---|"]
    for k, v in rows:
        out.append(f"| {k} | {v} |")
    return "\n".join(out)


# ------------------------- Screening core ------------------------------------


def screen_records(
    records: List[Dict[str, Any]],
    *,
    year_from: int,
    year_to: int,
    languages: List[str],
    allow_unknown_language: bool,
    enforce_preprint_policy: bool,
    include_preprints_by_topic: Dict[str, bool],
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Apply screening rules and return (included_records, excluded_by_reason).

    excluded_by_reason counts:
      - out_of_year
      - language_blocked
      - language_unknown
      - preprint_blocked
    """
    included: List[Dict[str, Any]] = []
    excluded: Dict[str, int] = defaultdict(int)

    for rec in records:
        reasons: List[str] = []

        # 1) Year window
        if not within_years(rec.get("year"), year_from, year_to):
            reasons.append("out_of_year")

        # 2) Language
        lang = rec.get("language")
        if not lang_allowed(lang, languages, allow_unknown_language):
            reasons.append("language_unknown" if not lang else "language_blocked")

        # 3) Optional topic-level preprint policy
        if enforce_preprint_policy:
            topic = rec.get("query_topic") or ""
            allow_preprints = include_preprints_by_topic.get(topic, True)
            if not allow_preprints and is_preprint(rec):
                reasons.append("preprint_blocked")

        if reasons:
            for r in reasons:
                excluded[r] += 1
        else:
            included.append(rec)

    return included, dict(sorted(excluded.items(), key=lambda kv: (-kv[1], kv[0])))


def build_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute per-source and per-topic counts for INCLUDED records."""
    per_source = Counter(r.get("source") for r in records if r.get("source"))
    per_topic = Counter(r.get("query_topic") for r in records if r.get("query_topic"))
    src_rows = sorted(((k or "(unknown)", v) for k, v in per_source.items()), key=lambda x: (-x[1], x[0]))
    tpc_rows = sorted(((k or "(unknown)", v) for k, v in per_topic.items()), key=lambda x: (-x[1], x[0]))
    return {
        "total": len(records),
        "per_source": dict(src_rows),
        "per_topic": dict(tpc_rows),
    }


def write_step_summary(
    *,  # force keyword use for readability
    retrieved_at: str,
    included_count: int,
    excluded_count: int,
    excluded_by_reason: Dict[str, int],
    per_source: Dict[str, int],
    per_topic: Dict[str, int],
) -> None:
    """
    Append a compact Markdown overview to the Actions Step Summary so reviewers
    do not need to download the artefact to understand the result.
    """
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return

    def rows(d: Dict[str, int]) -> List[Tuple[str, int]]:
        return sorted(((k or "(unknown)", v) for k, v in d.items()), key=lambda x: (-x[1], x[0]))

    lines: List[str] = []
    lines.append("## Screening summary (Appendix B)")
    lines.append("")
    lines.append(f"- Timestamp: **{retrieved_at}**")
    lines.append(f"- Included: **{included_count}**")
    lines.append(f"- Excluded: **{excluded_count}**")
    lines.append("")
    lines.append("### Excluded by reason")
    lines.append(md_table(rows(excluded_by_reason), "Reason", "Records"))
    lines.append("")
    lines.append("### Included – per source")
    lines.append(md_table(rows(per_source), "Source", "Records"))
    lines.append("")
    lines.append("### Included – per topic")
    lines.append(md_table(rows(per_topic), "Topic ID", "Records"))
    lines.append("")

    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ------------------------- CLI / Orchestrator --------------------------------


def main(argv: List[str]) -> int:
    """CLI entrypoint for Appendix B screening (MVP)."""
    ap = argparse.ArgumentParser(description="ELIS – Appendix B (Screening) MVP")
    ap.add_argument("--input", default=CANONICAL_A, help="Path to canonical Appendix A JSON array")
    ap.add_argument("--output", default=CANONICAL_B, help="Path to write canonical Appendix B JSON array")
    ap.add_argument(
        "--year-from",
        type=int,
        default=None,
        help="Lower bound (inclusive). If omitted, take from A._meta.global.year_from",
    )
    ap.add_argument(
        "--year-to",
        type=int,
        default=None,
        help="Upper bound (inclusive). If omitted, take from A._meta.global.year_to",
    )
    ap.add_argument(
        "--languages",
        default=None,
        help="Comma-separated ISO 639-1 codes. If omitted, take from A._meta.global.languages",
    )
    ap.add_argument(
        "--allow-unknown-language",
        action="store_true",
        help="Keep records where language is missing/unknown (default: exclude).",
    )
    ap.add_argument(
        "--enforce-preprint-policy",
        action="store_true",
        help="Respect per-topic include_preprints flags (default: off).",
    )
    ap.add_argument("--dry-run", action="store_true", help="Compute but do not write B to disk.")
    args = ap.parse_args(argv)

    # 1) Load Appendix A
    data_a = load_json_array(args.input)
    if not data_a or not isinstance(data_a[0], dict) or not data_a[0].get("_meta"):
        logging.error("Appendix A file does not start with a _meta object.")
        return 2

    meta_a = data_a[0]
    records_a = data_a[1:]

    # 2) Resolve effective knobs (defaults from A, override via CLI)
    g = meta_a.get("global") or {}
    year_from = int(args.year_from if args.year_from is not None else g.get("year_from", 1990))
    year_to = int(args.year_to if args.year_to is not None else g.get("year_to", dt.datetime.utcnow().year))

    if args.languages:
        languages = [x.strip() for x in args.languages.split(",") if x.strip()]
    else:
        languages = list(g.get("languages") or ["en", "fr", "es", "pt"])

    # Topic-level preprint policy: from A._meta.run_inputs if present, else default True.
    include_preprints_by_topic: Dict[str, bool] = {}
    run_inputs_a = (meta_a.get("run_inputs") or {})
    ipbt = run_inputs_a.get("include_preprints_by_topic") or {}
    if isinstance(ipbt, dict):
        include_preprints_by_topic = {str(k): bool(v) for k, v in ipbt.items()}

    # Fallback – if A didn't record per-topic flags, assume True for all topics seen.
    if not include_preprints_by_topic:
        topic_ids = {rec.get("query_topic") for rec in records_a if rec.get("query_topic")}
        include_preprints_by_topic = {tid: True for tid in topic_ids}

    # 3) Run screening
    logging.info(
        "Screening with year=[%s..%s], languages=%s, allow_unknown_language=%s, enforce_preprint_policy=%s",
        year_from,
        year_to,
        ",".join(languages),
        args.allow_unknown_language,
        args.enforce_preprint_policy,
    )

    included, excluded_by_reason = screen_records(
        records_a,
        year_from=year_from,
        year_to=year_to,
        languages=languages,
        allow_unknown_language=args.allow_unknown_language,
        enforce_preprint_policy=args.enforce_preprint_policy,
        include_preprints_by_topic=include_preprints_by_topic,
    )

    # 4) Summaries and _meta for B
    summary = build_summary(included)
    included_count = len(included)
    excluded_count = sum(excluded_by_reason.values())
    retrieved_at = now_utc_iso()

    topics_enabled = meta_a.get("topics_enabled") or []
    sources_touched = sorted({r.get("source") for r in included if r.get("source")})

    run_inputs_b = {
        "year_from": year_from,
        "year_to": year_to,
        "languages": languages,
        "allow_unknown_language": bool(args.allow_unknown_language),
        "enforce_preprint_policy": bool(args.enforce_preprint_policy),
    }

    meta_b = {
        "_meta": True,
        "protocol_version": meta_a.get("protocol_version", "ELIS 2025 (MVP)"),
        "input_path": os.path.abspath(args.input),
        "output_path": os.path.abspath(args.output),
        "retrieved_at": retrieved_at,
        "topics_enabled": topics_enabled,
        "sources_touched": sources_touched,
        "counts": {
            "included_count": included_count,
            "excluded_count": excluded_count,
            "excluded_by_reason": excluded_by_reason,
        },
        "summary": summary,  # totals for INCLUDED only
        "run_inputs": run_inputs_b,
    }

    # 5) Step Summary for reviewers
    write_step_summary(
        retrieved_at=retrieved_at,
        included_count=included_count,
        excluded_count=excluded_count,
        excluded_by_reason=excluded_by_reason,
        per_source=summary.get("per_source", {}),
        per_topic=summary.get("per_topic", {}),
    )

    # 6) Persist or dry-run
    if args.dry_run:
        logging.info("Dry-run: not writing Appendix B. Meta follows:")
        logging.info(json.dumps(meta_b, indent=2))
        return 0

    payload_b = [meta_b] + included
    write_json_array(args.output, payload_b)
    logging.info("Wrote canonical Appendix B JSON: %s", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
