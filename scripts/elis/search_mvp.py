# scripts/elis/search_mvp.py
# =============================================================================
# ELIS – Appendix A (Search) MVP
# Purpose:
#   Query multiple academic sources (Crossref, Semantic Scholar, arXiv) using
#   controlled queries defined in config/elis_search_queries.yml and produce a
#   canonical JSON array at:
#       json_jsonl/ELIS_Appendix_A_Search_rows.json
#
# Protocol Alignment:
#   - Years: 1990–2025  (Protocol §3.1)
#   - Languages: en, fr, es, pt  (Protocol §3.1)
#   - Phenomena: integrity, auditability, verifiability, trust (Protocol §2.2)
#   - Documentation: All searches and filters logged to metadata at file head.
#
# Design Notes:
#   - Minimal deps: PyYAML + requests (declared in workflows).
#   - Field mapping is "best effort" across sources; we record source + raw ids.
#   - Dedup strategy: prefer DOI; else normalised (title, year). First-hit wins.
#   - Rate limiting: small sleeps between calls; polite User-Agent for APIs.
#   - Determinism: no randomness; results may still vary across runs due to
#     upstream search backends updating/reshuffling.
#   - Safe on first run (creates canonical file); idempotent thereafter.
#
# Enhancements in this version:
#   - Adds a compact Search summary:
#       * _meta.summary.total
#       * _meta.summary.per_source: {"crossref": N, "semanticscholar": M, ...}
#       * _meta.summary.per_topic:  {"topic_id": N, ...}
#     and writes Markdown tables to $GITHUB_STEP_SUMMARY for PR reviewers.
#   - Records effective run-time inputs for provenance at _meta.run_inputs:
#       {
#         "year_from": <int>,
#         "year_to": <int>,
#         "job_result_cap": <int>,
#         "max_results_per_source": <int>,
#         "topics_selected": [<topic ids>],
#         "include_preprints_by_topic": {"topic_id": true/false, ...}
#       }
#     The values are derived from the *effective* configuration passed to this
#     script (which the workflow may patch from UI inputs).
#
# Environment (optional):
#   - SEMANTIC_SCHOLAR_API_KEY: increases S2 rate limits if present.
#   - ELIS_CONTACT: email shown in User-Agent for polite API usage (Crossref).
#   - ELIS_HTTP_SLEEP_S: seconds to sleep between pagination calls (default 0.5).
#
# Outputs:
#   - json_jsonl/ELIS_Appendix_A_Search_rows.json   (JSON array)
#       [
#         {
#           "_meta": true,
#           "protocol_version": "ELIS 2025 (MVP)",
#           "config_path": "...",
#           "retrieved_at": "YYYY-MM-DDTHH:MM:SSZ",
#           "global": {...},
#           "topics_enabled": [...],
#           "sources": [...],
#           "record_count": <int>,
#           "summary": {
#             "total": <int>,
#             "per_source": {...},
#             "per_topic":  {...}
#           },
#           "run_inputs": {
#             "year_from": <int>,
#             "year_to": <int>,
#             "job_result_cap": <int>,
#             "max_results_per_source": <int>,
#             "topics_selected": [...],
#             "include_preprints_by_topic": {...}
#           }
#         },
#         {
#           "id": "<stable id>",               # also present as _stable_id (BC)
#           "title": "...",
#           "authors": ["..."],
#           "year": 2021,
#           "doi": "10.1234/abcd",
#           "source": "crossref|semanticscholar|arxiv",
#           "source_id": "...",
#           "venue": "Journal / Conference",
#           "publisher": "...",
#           "abstract": "...",
#           "language": "en|fr|es|pt|null",
#           "url": "https://...",
#           "query_topic": "integrity_auditability_core",
#           "query_string": "<the exact string executed>",
#           "retrieved_at": "YYYY-MM-DDTHH:MM:SSZ",
#           "_stable_id": "<same as id>"       # kept temporarily for BC
#         },
#         ...
#       ]
#
# Exit codes:
#   0 = success; 2 = missing/invalid config; other nonzero = runtime error.
#
# Known limitations (MVP):
#   - Language is often unknown from S2/arXiv; screening (B) should enforce.
#   - Titles/years may vary across sources; dedup may keep one variant.
#   - arXiv parsed via lightweight regex (adequate for MVP).
# =============================================================================

from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
import os
import re
import sys
import time
from collections import Counter
from typing import Any, Dict, List, Optional

import requests
import yaml

# ------------------------- Constants & runtime knobs -------------------------
CANONICAL_A = "json_jsonl/ELIS_Appendix_A_Search_rows.json"
CONFIG_PATH = "config/elis_search_queries.yml"

REQUEST_SLEEP_S = float(os.getenv("ELIS_HTTP_SLEEP_S", "0.5"))
CONTACT = os.getenv("ELIS_CONTACT", "")
UA = "ELIS-SLR-Agent/1.0"
if CONTACT:
    UA += f" (+mailto:{CONTACT})"
DEFAULT_HEADERS = {"User-Agent": UA}

# ------------------------- Logging configuration -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)


# ------------------------- Helpers ------------------------------------------
def now_utc_iso() -> str:
    """Return UTC timestamp in ISO 8601 (no microseconds, with trailing Z)."""
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_dirs() -> None:
    """Create output directories if missing."""
    os.makedirs(os.path.dirname(CANONICAL_A), exist_ok=True)


def load_yaml(path: str) -> dict:
    """Load a UTF-8 YAML file into a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_title(title: Optional[str]) -> str:
    """Normalise title for dedupe: lowercase, strip punctuation/extra spaces."""
    if not title:
        return ""
    t = re.sub(r"[^\w\s]", " ", title.lower())
    return re.sub(r"\s+", " ", t).strip()


def stable_id(doi: Optional[str], title: Optional[str], year: Optional[int]) -> str:
    """
    Produce a stable deterministic id for deduping.
    Prefer DOI; otherwise hash of normalised title + year.
    """
    if doi:
        return "doi:" + doi.lower().strip()
    t = normalize_title(title)
    y = str(year or "")
    return "t:" + hashlib.sha256((t + "|" + y).encode("utf-8")).hexdigest()[:20]


def within_years(year: Optional[int], y0: int, y1: int) -> bool:
    """Return True if year is an int within [y0, y1]."""
    if not isinstance(year, int):
        return False
    return y0 <= year <= y1


def lang_ok(language: Optional[str], allowed: List[str]) -> bool:
    """
    Accept record if language is allowed or unknown.
    We keep unknown languages for later screening.
    """
    if not allowed:
        return True
    if not language:
        return True
    return language.lower() in {x.lower() for x in allowed}


def polite_sleep() -> None:
    """Tiny sleep to avoid hammering public APIs (configurable via ELIS_HTTP_SLEEP_S)."""
    if REQUEST_SLEEP_S > 0:
        time.sleep(REQUEST_SLEEP_S)


def build_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute per-source and per-topic counts for the deduplicated record set.
    Returns a plain dict suitable for embedding in _meta.summary.
    """
    per_source = Counter(r.get("source") for r in records if r.get("source"))
    per_topic = Counter(r.get("query_topic") for r in records if r.get("query_topic"))

    # Convert Counters to vanilla dicts with stable ordering (desc by count)
    src_sorted = dict(sorted(per_source.items(), key=lambda x: (-x[1], x[0] or "")))
    tpc_sorted = dict(sorted(per_topic.items(), key=lambda x: (-x[1], x[0] or "")))

    return {"total": len(records), "per_source": src_sorted, "per_topic": tpc_sorted}


def write_step_summary(meta: Dict[str, Any], summary: Dict[str, Any]) -> None:
    """
    If running in GitHub Actions, append a compact Markdown summary to
    $GITHUB_STEP_SUMMARY so reviewers get counts without opening the JSON.
    """
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return

    def md_table(mapping: Dict[str, int], header_a: str, header_b: str) -> str:
        lines = [f"| {header_a} | {header_b} |", "|---|---|"]
        for k, v in mapping.items():
            lines.append(f"| {k or '(unknown)'} | {v} |")
        return "\n".join(lines)

    lines: List[str] = []
    lines.append("## Search summary")
    lines.append("")
    lines.append(f"- Timestamp: **{meta.get('retrieved_at', '')}**")
    lines.append(f"- Total unique records: **{summary.get('total', 0)}**")
    lines.append("")
    lines.append("### Per source")
    lines.append(md_table(summary.get("per_source", {}), "Source", "Records"))
    lines.append("")
    lines.append("### Per topic")
    lines.append(md_table(summary.get("per_topic", {}), "Topic ID", "Records"))
    lines.append("")

    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def build_run_inputs(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Derive a provenance snapshot of the *effective* knobs used for this run,
    based solely on the configuration loaded by this script (which may have
    been patched by CI UI inputs before execution).
    """
    g = (config.get("global") or {})
    year_from = int(g.get("year_from", 1990))
    year_to = int(g.get("year_to", dt.datetime.utcnow().year))
    job_result_cap = int(g.get("job_result_cap", 0))
    max_results_per_source = int(g.get("max_results_per_source", 100))

    topics = (config.get("topics") or [])
    enabled = [t for t in topics if t.get("enabled", True)]

    topics_selected = [t.get("id") for t in enabled if t.get("id")]
    include_preprints_by_topic = {
        t.get("id"): bool(t.get("include_preprints", True))
        for t in enabled
        if t.get("id")
    }

    return {
        "year_from": year_from,
        "year_to": year_to,
        "job_result_cap": job_result_cap,
        "max_results_per_source": max_results_per_source,
        "topics_selected": topics_selected,
        "include_preprints_by_topic": include_preprints_by_topic,
    }


# ------------------------- Source: Crossref ----------------------------------
def search_crossref(
    query: str, year_from: int, year_to: int, languages: List[str], cap: int
) -> List[Dict[str, Any]]:
    """
    Crossref REST: https://api.crossref.org/works
    We use 'query' and filter by 'from-pub-date'/'until-pub-date'.
    """
    out: List[Dict[str, Any]] = []
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": 100,  # paginate
        "select": "title,author,issued,DOI,container-title,publisher,URL,language,abstract,type",
        "filter": f"from-pub-date:{year_from}-01-01,until-pub-date:{year_to}-12-31",
        "sort": "relevance",
        "order": "desc",
    }
    cursor = "*"
    got = 0
    while got < cap:
        try:
            r = requests.get(
                url,
                params={**params, "cursor": cursor},
                headers=DEFAULT_HEADERS,
                timeout=30,
            )
            r.raise_for_status()
        except Exception as e:
            logging.warning(f"Crossref error: {e}")
            break
        data = r.json()
        items = (data.get("message") or {}).get("items") or []
        for it in items:
            title = " ".join(it.get("title") or []) or None
            authors = []
            for a in it.get("author") or []:
                nm = " ".join([a.get("given", ""), a.get("family", "")]).strip()
                if nm:
                    authors.append(nm)
            # Extract year
            year = None
            issued = it.get("issued", {})
            parts = issued.get("date-parts") or []
            if parts and parts[0]:
                y = parts[0][0]
                if isinstance(y, int):
                    year = y

            rec = {
                "title": title,
                "authors": authors,
                "year": year,
                "doi": (it.get("DOI") or None),
                "venue": ((it.get("container-title") or [None])[0]),
                "publisher": (it.get("publisher") or None),
                "url": (it.get("URL") or None),
                "language": (it.get("language") or None),
                "abstract": (it.get("abstract") or None),  # may include HTML
                "doc_type": (it.get("type") or None),
                "source": "crossref",
                "source_id": (it.get("DOI") or it.get("URL") or None),
            }
            if within_years(rec["year"], year_from, year_to) and lang_ok(
                rec["language"], languages
            ):
                out.append(rec)
                got += 1
                if got >= cap:
                    break
        cursor = (data.get("message") or {}).get("next-cursor") or None
        if not cursor:
            break
        polite_sleep()
    return out


# ------------------------- Source: Semantic Scholar --------------------------
def search_semantic_scholar(
    query: str, year_from: int, year_to: int, languages: List[str], cap: int
) -> List[Dict[str, Any]]:
    """
    Semantic Scholar API v1:
    https://api.semanticscholar.org/
    """
    out: List[Dict[str, Any]] = []
    fields = (
        "title,authors,year,venue,externalIds,publicationTypes,abstract,url,"
        "journal,publicationVenue"
    )
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = dict(DEFAULT_HEADERS)  # include UA alongside the API key
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    offset = 0
    pagesize = 100
    while len(out) < cap:
        params = {
            "query": query,
            "yearFilter": f"{year_from}-{year_to}",
            "limit": min(pagesize, cap - len(out)),
            "offset": offset,
            "fields": fields,
        }
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            r.raise_for_status()
        except Exception as e:
            logging.warning(f"Semantic Scholar error: {e}")
            break
        data = r.json()
        for it in data.get("data", []):
            ext = it.get("externalIds") or {}
            doi = ext.get("DOI") or None
            rec = {
                "title": it.get("title"),
                "authors": [
                    a.get("name") for a in (it.get("authors") or []) if a.get("name")
                ],
                "year": it.get("year"),
                "doi": doi,
                "venue": it.get("venue")
                or (it.get("journal") or {}).get("name")
                or (it.get("publicationVenue") or {}).get("name"),
                "publisher": None,
                "url": it.get("url"),
                "language": None,  # unknown: we keep and screen later
                "abstract": it.get("abstract"),
                "doc_type": (",".join(it.get("publicationTypes") or []) or None),
                "source": "semanticscholar",
                "source_id": it.get("paperId"),
            }
            if within_years(rec["year"], year_from, year_to) and lang_ok(
                rec["language"], languages
            ):
                out.append(rec)
                if len(out) >= cap:
                    break
        if not data.get("data"):
            break
        offset += params["limit"]
        polite_sleep()
    return out


# ------------------------- Source: arXiv -------------------------------------
def search_arxiv(
    query: str, year_from: int, year_to: int, languages: List[str], cap: int
) -> List[Dict[str, Any]]:
    """
    arXiv Atom API via export.arxiv.org.
    Language not provided; treat as unknown and keep for screening.
    """
    out: List[Dict[str, Any]] = []
    base = "http://export.arxiv.org/api/query"
    start = 0
    pagesize = 100
    while len(out) < cap:
        params = {
            "search_query": f"all:{query}",
            "start": start,
            "max_results": min(pagesize, cap - len(out)),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        try:
            r = requests.get(base, params=params, headers=DEFAULT_HEADERS, timeout=30)
            r.raise_for_status()
            text = r.text
        except Exception as e:
            logging.warning(f"arXiv error: {e}")
            break

        # Lightweight parsing (avoid external XML deps)
        entries = re.findall(r"<entry>(.*?)</entry>", text, flags=re.DOTALL)
        if not entries:
            break

        for ent in entries:
            # Title
            m_title = re.search(r"<title>(.*?)</title>", ent, flags=re.DOTALL)
            title = m_title.group(1).strip() if m_title else None
            # Year from <published>
            m_pub = re.search(r"<published>(.*?)</published>", ent)
            year = None
            if m_pub:
                try:
                    year = int(m_pub.group(1)[:4])
                except Exception:
                    pass
            # URL/ID
            m_id = re.search(r"<id>(.*?)</id>", ent)
            url = m_id.group(1) if m_id else None
            # Authors
            authors = re.findall(r"<name>(.*?)</name>", ent)
            # DOI (if provided)
            m_doi = re.search(
                r'<arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">(.*?)</arxiv:doi>',
                ent,
            )
            doi = m_doi.group(1) if m_doi else None
            # Abstract
            m_abs = re.search(r"<summary>(.*?)</summary>", ent, flags=re.DOTALL)
            abstract = m_abs.group(1).strip() if m_abs else None

            rec = {
                "title": title,
                "authors": authors,
                "year": year,
                "doi": doi,
                "venue": "arXiv",
                "publisher": None,
                "url": url,
                "language": None,  # unknown
                "abstract": abstract,
                "doc_type": "preprint",
                "source": "arxiv",
                "source_id": url,
            }
            if within_years(rec["year"], year_from, year_to) and lang_ok(
                rec["language"], languages
            ):
                out.append(rec)
                if len(out) >= cap:
                    break
        start += params["max_results"]
        polite_sleep()
    return out


# ------------------------- Orchestrator --------------------------------------
def orchestrate_search(config: dict) -> List[Dict[str, Any]]:
    """Run configured topics/queries across sources and return de-duplicated results."""
    y0 = int(config.get("global", {}).get("year_from", 1990))
    y1 = int(config.get("global", {}).get("year_to", dt.datetime.utcnow().year))
    langs = config.get("global", {}).get("languages", ["en"])
    topic_cap = int(config.get("global", {}).get("max_results_per_source", 100))
    job_cap = int(config.get("global", {}).get("job_result_cap", 0))

    enabled_topics = [t for t in (config.get("topics") or []) if t.get("enabled", True)]
    results: List[Dict[str, Any]] = []

    # Dedup tracking
    seen: set[str] = set()

    def add_with_dedupe(rec: Dict[str, Any], topic_id: str, query_str: str) -> None:
        rec["query_topic"] = topic_id
        rec["query_string"] = query_str
        rec["retrieved_at"] = now_utc_iso()
        key = stable_id(rec.get("doi"), rec.get("title"), rec.get("year"))
        rec["id"] = key
        rec["_stable_id"] = key  # kept for backward compatibility
        if key in seen:
            return
        seen.add(key)
        results.append(rec)

    for topic in enabled_topics:
        topic_id = topic["id"]
        include_preprints = bool(topic.get("include_preprints", True))
        sources = topic.get("sources", ["crossref", "semanticscholar"])
        for q in topic.get("queries") or []:
            if "crossref" in sources:
                for rec in search_crossref(q, y0, y1, langs, cap=topic_cap):
                    add_with_dedupe(rec, topic_id, q)
            if "semanticscholar" in sources:
                for rec in search_semantic_scholar(q, y0, y1, langs, cap=topic_cap):
                    add_with_dedupe(rec, topic_id, q)
            if include_preprints and "arxiv" in sources:
                for rec in search_arxiv(q, y0, y1, langs, cap=min(50, topic_cap)):
                    add_with_dedupe(rec, topic_id, q)
            if job_cap and len(results) >= job_cap:
                logging.info(f"Job result cap reached: {job_cap}")
                return results
    return results


# ------------------------- Write JSON ----------------------------------------
def write_json_array(path: str, records: List[Dict[str, Any]], meta: Dict[str, Any]) -> None:
    """Write records to a JSON array with a leading _meta element."""
    ensure_dirs()
    payload = [{"_meta": True, **meta}] + records
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ------------------------- CLI entrypoint ------------------------------------
def main(argv: List[str]) -> int:
    """CLI for Appendix A search MVP."""
    import argparse

    ap = argparse.ArgumentParser(description="ELIS – Appendix A Search (MVP)")
    ap.add_argument("--config", default=CONFIG_PATH, help="YAML config with queries/topics")
    ap.add_argument("--dry-run", action="store_true", help="Run search but do not write file")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.config):
        logging.error(f"Config not found: {args.config}")
        return 2

    config = load_yaml(args.config)
    logging.info("Starting search orchestrator…")
    records = orchestrate_search(config)
    logging.info(f"Total records (pre-write, unique): {len(records)}")

    # Build meta (with summary + run_inputs) for provenance and quick review.
    summary = build_summary(records)
    meta = {
        "protocol_version": "ELIS 2025 (MVP)",
        "config_path": args.config,
        "retrieved_at": now_utc_iso(),
        "global": config.get("global", {}),
        "topics_enabled": [t["id"] for t in config.get("topics", []) if t.get("enabled", True)],
        "sources": sorted(list({r["source"] for r in records})),
        "record_count": len(records),
        "summary": summary,
        "run_inputs": build_run_inputs(config),
    }

    # Emit a nice table into the GitHub Actions "Step Summary", if available.
    write_step_summary(meta, summary)

    if args.dry_run:
        logging.info("Dry-run: not writing canonical Appendix A file.")
        logging.info(json.dumps(meta, indent=2))
        return 0

    write_json_array(CANONICAL_A, records, meta)
    logging.info(f"Wrote canonical Appendix A JSON: {CANONICAL_A}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
