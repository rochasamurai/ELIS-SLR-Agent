# scripts/elis/screen_mvp.py
# =============================================================================
# ELIS – Appendix B (Screening) MVP
# Purpose
#   Read the canonical Appendix A artefact and apply protocol screening rules
#   (years, languages, and optional per-topic preprint policy). Emit the
#   canonical Appendix B artefact containing ONLY the included records, with a
#   leading _meta block that captures counts and provenance.
#
# Inputs
#   - Canonical A file produced by search_mvp.py:
#       json_jsonl/ELIS_Appendix_A_Search_rows.json
#
# Output (canonical)
#   - json_jsonl/ELIS_Appendix_B_Screening_rows.json
#     * JSON array whose first element is a metadata object with "_meta": true.
#     * Remaining elements are the INCLUDED records only (not the excluded).
#
# Protocol alignment
#   - Years: default to A._meta.global.year_from .. year_to (Protocol §3.1),
#     unless overridden via CLI.
#   - Languages: default to A._meta.global.languages (Protocol §3.1), unless
#     overridden via CLI. By default, unknown language records are EXCLUDED.
#   - Preprints: if --enforce-preprint-policy is on (default), and A._meta
#     contains run_inputs.include_preprints_by_topic, then for any topic where
#     include_preprints=false, preprints (arXiv/doc_type=preprint) are excluded.
#
# Design notes
#   - This is a minimal, transparent filter: no mutation of the kept records.
#   - Each exclusion has a single reason so counts are easy to audit.
#   - We emit per-source and per-topic counts for the INCLUDED set in _meta.
#   - A concise Markdown Step Summary is appended in CI for reviewer UX.
#
# CLI (see main() for full help)
#   --input / --output:
#       Paths to A (in) and B (out). Defaults to canonical repo paths.
#   --year-from / --year-to:
#       Override the A._meta.global bounds.
#   --languages "en,fr,es,pt":
#       Override allowed languages (case-insensitive).
#   --keep-unknown-language:
#       If set, language=None records are allowed (default is exclude).
#   --enforce-preprint-policy:
#       Default: true. If A._meta.run_inputs.include_preprints_by_topic says a
#       topic should not include preprints, arXiv/doc_type=preprint rows are
#       excluded under "preprint_blocked".
#   --dry-run:
#       Run and print the meta summary without writing the B artefact.
#
# Exit codes
#   0 = ok, 2 = input not found/invalid, other non-zero = runtime error.
# =============================================================================

from __future__ import annotations

import datetime as dt
import json
import logging
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

# ----------------------------- Canonical paths --------------------------------
CANONICAL_A = "json_jsonl/ELIS_Appendix_A_Search_rows.json"
CANONICAL_B = "json_jsonl/ELIS_Appendix_B_Screening_rows.json"

# ----------------------------- Logging ---------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)


# ----------------------------- Small helpers ---------------------------------
def now_utc_iso() -> str:
    """Return UTC timestamp in ISO 8601 (no microseconds, trailing 'Z')."""
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_dirs(path: str) -> None:
    """Create parent directory for 'path' if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def read_json_array(path: str) -> List[dict]:
    """Read a UTF-8 JSON array file and return the parsed list."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Input JSON must be an array.")
    return data


def write_json_array(path: str, rows: List[dict]) -> None:
    """Write a UTF-8 JSON array with a trailing newline (human-friendly diffs)."""
    ensure_dirs(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
        f.write("\n")


def normalise_lang(lang: Optional[str]) -> Optional[str]:
    """Normalise a BCP-47-ish language string to lowercase 2-letter code when possible."""
    if not lang:
        return None
    return lang.strip().lower()


def within_years(year: Optional[int], y0: int, y1: int) -> bool:
    """Return True if 'year' is an int within [y0, y1]."""
    return isinstance(year, int) and (y0 <= year <= y1)


def is_preprint(rec: Dict[str, Any]) -> bool:
    """
    Heuristic: a record is a preprint when any of the following holds:
      - source == "arxiv"
      - venue contains "arxiv" (case-insensitive)
      - doc_type contains the substring "preprint" (case-insensitive)
    """
    src = (rec.get("source") or "").lower()
    if src == "arxiv":
        return True
    venue = (rec.get("venue") or "").lower()
    if "arxiv" in venue:
        return True
    dtype = (rec.get("doc_type") or "").lower()
    return "preprint" in dtype


def step_summary_append(lines: Iterable[str]) -> None:
    """
    If running in GitHub Actions, append lines to $GITHUB_STEP_SUMMARY so
    reviewers see counts without opening the artefact.
    """
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ----------------------------- Screening core --------------------------------
def screen_records(
    records: List[Dict[str, Any]],
    *,
    year_from: int,
    year_to: int,
    languages: List[str],
    keep_unknown_language: bool,
    enforce_preprint_policy: bool,
    include_preprints_by_topic: Dict[str, bool],
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Apply screening rules and return (included_records, excluded_by_reason_counts).

    Reasons used (keys of the second return value):
      - "out_of_year"
      - "language_blocked"
      - "preprint_blocked"
    """
    allowed_langs = {l.lower() for l in languages}
    excluded_by_reason: Dict[str, int] = defaultdict(int)
    included: List[Dict[str, Any]] = []

    for rec in records:
        # 1) Year filter
        if not within_years(rec.get("year"), year_from, year_to):
            excluded_by_reason["out_of_year"] += 1
            continue

        # 2) Language filter
        lang = normalise_lang(rec.get("language"))
        if lang is None:
            if not keep_unknown_language:
                excluded_by_reason["language_blocked"] += 1
                continue
        else:
            if allowed_langs and lang not in allowed_langs:
                excluded_by_reason["language_blocked"] += 1
                continue

        # 3) Preprint policy (per topic)
        if enforce_preprint_policy and is_preprint(rec):
            topic_id = rec.get("query_topic")
            allow_topic_preprints = include_preprints_by_topic.get(topic_id, True)
            if not allow_topic_preprints:
                excluded_by_reason["preprint_blocked"] += 1
                continue

        # Passed all checks
        included.append(rec)

    return included, dict(excluded_by_reason)


def build_counts(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """Compute per-source and per-topic counts for INCLUDED records."""
    per_source = Counter(r.get("source") for r in records if r.get("source"))
    per_topic = Counter(r.get("query_topic") for r in records if r.get("query_topic"))

    # Return plain dicts with stable ordering
    src_sorted = dict(sorted(per_source.items(), key=lambda x: (-x[1], x[0] or "")))
    tpc_sorted = dict(sorted(per_topic.items(), key=lambda x: (-x[1], x[0] or "")))
    return {"per_source": src_sorted, "per_topic": tpc_sorted}


def build_step_summary(
    *,
    included_count: int,
    excluded_count: int,
    excluded_by_reason: Dict[str, int],
    per_source: Dict[str, int],
    per_topic: Dict[str, int],
) ->
