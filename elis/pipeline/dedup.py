"""ELIS pipeline - deterministic deduplication stage (PE4)."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CANONICAL_INPUT = "json_jsonl/ELIS_Appendix_A_Search_rows.json"
CANONICAL_OUTPUT = "dedup/appendix_a_deduped.json"
CANONICAL_REPORT = "dedup/dedup_report.json"
KEEPER_PRIORITY_CONFIG = "config/sources.yml"

# Code-default keeper priority (used only when config absent / unreadable)
_KEEPER_PRIORITY_DEFAULT = [
    "scopus",
    "wos",
    "semanticscholar",
    "crossref",
    "openalex",
    "ieee",
    "core",
    "sciencedirect",
    "google_scholar",
]


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------


def normalise_doi(doi: str | None) -> str:
    """Normalise a DOI to its bare lowercase form (no prefix)."""
    value = (doi or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix) :]
            break
    return value


def normalise_text(text: str | None) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    if not text:
        return ""
    s = text.lower()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------------------------------------------------------------------------
# Dedup key + cluster ID
# ---------------------------------------------------------------------------


def _dedup_key(record: dict[str, Any]) -> str:
    """
    Compute the deduplication key for a record.

    Priority:
      1. Normalised DOI (if present and non-empty after normalisation)
      2. normalise_text(title) + "|" + str(year) + "|" + normalise_text(first_author)
    """
    doi = normalise_doi(record.get("doi"))
    if doi:
        return doi

    title = normalise_text(record.get("title"))
    year = record.get("year")
    year_str = str(int(year)) if isinstance(year, (int, float)) and year else ""
    authors = record.get("authors") or []
    first_author = normalise_text(str(authors[0])) if authors else ""
    return f"{title}|{year_str}|{first_author}"


def _cluster_id(key: str) -> str:
    """Return a 12-char hex cluster ID derived from the dedup key."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------


def _load_keeper_priority(config_path: str = KEEPER_PRIORITY_CONFIG) -> list[str]:
    """
    Load keeper_priority from config/sources.yml.
    Returns the code default list if the file is absent or unreadable.
    """
    try:
        import yaml  # type: ignore[import-untyped]

        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh)
            priority = cfg.get("keeper_priority") if isinstance(cfg, dict) else None
            if isinstance(priority, list) and priority:
                return [str(s).lower() for s in priority]
    except Exception:
        pass
    return list(_KEEPER_PRIORITY_DEFAULT)


# ---------------------------------------------------------------------------
# Keeper selection
# ---------------------------------------------------------------------------


def _count_non_null(record: dict[str, Any]) -> int:
    """Count fields that are not None and not empty (string/list)."""
    count = 0
    for v in record.values():
        if v is None:
            continue
        if isinstance(v, str) and not v.strip():
            continue
        if isinstance(v, list) and not v:
            continue
        count += 1
    return count


def _pick_keeper_index(records: list[dict[str, Any]], priority: list[str]) -> int:
    """
    Return the index of the keeper in *records*.

    Tie-break rules (ascending = better):
      1. Fewer null/empty fields (more non-null = better → negate for sorting)
      2. Source priority position (lower index in *priority* = better)
    """

    def sort_key(idx: int) -> tuple[int, int]:
        rec = records[idx]
        non_null = _count_non_null(rec)
        source = str(rec.get("source", "")).lower()
        try:
            prio = priority.index(source)
        except ValueError:
            prio = len(priority)  # unknown → lowest priority
        return (-non_null, prio)

    return min(range(len(records)), key=sort_key)


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def _load_records(path: Path) -> list[dict[str, Any]]:
    """
    Load records from a JSON array or JSONL file, skipping any _meta header.
    """
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


def _load_meta(path: Path) -> dict[str, Any] | None:
    """Return the _meta header dict from a JSON array, or None."""
    text = path.read_text(encoding="utf-8").strip()
    if not text.startswith("["):
        return None
    payload = json.loads(text)
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        if payload[0].get("_meta"):
            return payload[0]
    return None


# ---------------------------------------------------------------------------
# Core dedup logic
# ---------------------------------------------------------------------------


def run_dedup(
    input_path: str,
    output_path: str,
    report_path: str,
    *,
    fuzzy: bool = False,
    threshold: float = 0.85,
    config_path: str = KEEPER_PRIORITY_CONFIG,
) -> tuple[Path, Path]:
    """
    Deduplicate records from *input_path*, write keepers to *output_path*
    (JSON array with _meta header) and statistics to *report_path*.

    Returns (output_path, report_path) as Path objects.
    """
    if fuzzy:
        warnings.warn(
            "Fuzzy deduplication is enabled (--fuzzy). This may be slow for large datasets.",
            stacklevel=2,
        )
        logger.warning("Fuzzy dedup enabled with threshold=%.2f.", threshold)

    in_path = Path(input_path)
    out_path = Path(output_path)
    rep_path = Path(report_path)

    priority = _load_keeper_priority(config_path)
    config_source = config_path if Path(config_path).exists() else "default"

    # Preserve the upstream _meta so screen can use it
    upstream_meta = _load_meta(in_path)
    records = _load_records(in_path)
    total_input = len(records)

    # --- Build clusters (exact) ---
    clusters: dict[str, list[dict[str, Any]]] = {}
    cluster_methods: dict[str, str] = {}  # "doi" or "title"

    for rec in records:
        doi = normalise_doi(rec.get("doi"))
        if doi:
            key = doi
            method = "doi"
        else:
            title = normalise_text(rec.get("title"))
            year = rec.get("year")
            year_str = str(int(year)) if isinstance(year, (int, float)) and year else ""
            authors = rec.get("authors") or []
            first_author = normalise_text(str(authors[0])) if authors else ""
            key = f"{title}|{year_str}|{first_author}"
            method = "title"

        if key not in clusters:
            clusters[key] = []
            cluster_methods[key] = method
        clusters[key].append(rec)

    # --- Optional fuzzy merge of clusters ---
    fuzzy_count = 0
    if fuzzy:
        from difflib import SequenceMatcher

        keys = list(clusters.keys())
        absorbed: set[str] = set()

        for i in range(len(keys)):
            ki = keys[i]
            if ki in absorbed:
                continue
            for j in range(i + 1, len(keys)):
                kj = keys[j]
                if kj in absorbed:
                    continue
                ratio = SequenceMatcher(None, ki, kj).ratio()
                if ratio >= threshold:
                    # Merge kj into ki
                    before = len(clusters[ki])
                    clusters[ki].extend(clusters.pop(kj))
                    fuzzy_count += len(clusters[ki]) - before
                    absorbed.add(kj)

    # --- Pick keepers and annotate ---
    keepers: list[dict[str, Any]] = []

    for key, recs in clusters.items():
        cid = _cluster_id(key)
        cluster_size = len(recs)
        cluster_sources = sorted(
            {str(r.get("source", "")).lower() for r in recs if r.get("source")}
        )

        keeper_idx = _pick_keeper_index(recs, priority)
        keeper = dict(recs[keeper_idx])
        keeper["cluster_id"] = cid
        keeper["cluster_size"] = cluster_size
        keeper["cluster_sources"] = cluster_sources
        keepers.append(keeper)

    # Deterministic sort
    keepers.sort(
        key=lambda r: (
            str(r.get("source", "")),
            str(r.get("query_topic", "")),
            str(r.get("title", "")),
        )
    )

    # --- Stats ---
    duplicates_removed = total_input - len(keepers)
    doi_based_dedup = sum(
        len(v) - 1
        for k, v in clusters.items()
        if len(v) > 1 and cluster_methods.get(k) == "doi"
    )
    title_year_author_dedup = sum(
        len(v) - 1
        for k, v in clusters.items()
        if len(v) > 1 and cluster_methods.get(k) == "title"
    )
    top_collisions = sorted(
        (
            {
                "cluster_id": _cluster_id(k),
                "size": len(v),
                "sources": sorted(
                    {str(r.get("source", "")).lower() for r in v if r.get("source")}
                ),
            }
            for k, v in clusters.items()
            if len(v) > 1
        ),
        key=lambda x: -x["size"],
    )[:10]

    # --- Build output _meta ---
    _meta: dict[str, Any] = {
        "_meta": True,
        "stage": "dedup",
        "input_records": total_input,
        "unique_clusters": len(keepers),
        "duplicates_removed": duplicates_removed,
        "fuzzy_enabled": fuzzy,
        "keeper_priority_source": config_source,
    }
    if upstream_meta:
        # Forward useful upstream fields
        for field in ("protocol_version", "topics_enabled", "sources", "run_inputs"):
            if field in upstream_meta:
                _meta[field] = upstream_meta[field]

    # --- Write outputs ---
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rep_path.parent.mkdir(parents=True, exist_ok=True)

    payload = [_meta] + keepers
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report: dict[str, Any] = {
        "input_records": total_input,
        "unique_clusters": len(keepers),
        "duplicates_removed": duplicates_removed,
        "doi_based_dedup": doi_based_dedup,
        "title_year_author_dedup": title_year_author_dedup,
        "fuzzy_dedup": fuzzy_count,
        "keeper_priority_source": config_source,
        "top_10_collisions": top_collisions,
    }
    rep_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return out_path, rep_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="elis dedup", description="Deduplicate canonical Appendix A"
    )
    parser.add_argument(
        "--input",
        default=CANONICAL_INPUT,
        help=f"Merged Appendix A JSON file (default: {CANONICAL_INPUT})",
    )
    parser.add_argument(
        "--output",
        default=CANONICAL_OUTPUT,
        help=f"Deduped output path (default: {CANONICAL_OUTPUT})",
    )
    parser.add_argument(
        "--report",
        default=CANONICAL_REPORT,
        help=f"Dedup report path (default: {CANONICAL_REPORT})",
    )
    parser.add_argument(
        "--fuzzy",
        action="store_true",
        default=False,
        help="Enable fuzzy title-based deduplication (opt-in, slow on large datasets)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Similarity threshold for fuzzy mode (default: 0.85)",
    )
    parser.add_argument(
        "--config",
        default=KEEPER_PRIORITY_CONFIG,
        dest="config_path",
        help=f"Path to sources.yml for keeper priority (default: {KEEPER_PRIORITY_CONFIG})",
    )
    args = parser.parse_args(argv)

    run_dedup(
        args.input,
        args.output,
        args.report,
        fuzzy=args.fuzzy,
        threshold=args.threshold,
        config_path=args.config_path,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
