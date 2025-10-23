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
#   - No external dependencies beyond PyYAML and requests (use requirements.txt).
#   - “Best effort” mapping of fields across sources. We record source + raw ids.
#   - Dedup strategy: prefer DOI; else normalized (title, year). First-win keep.
#   - Rate limiting: simple sleep between calls to be polite.
#   - Safe on first run (creates canonical file); idempotent thereafter.
#
# Environment (optional):
#   - SEMANTIC_SCHOLAR_API_KEY: increases S2 rate limits if present.
#
# Outputs:
#   - json_jsonl/ELIS_Appendix_A_Search_rows.json   (JSON array)
#       [
#         {
#           "id": "<stable hash>",
#           "title": "...",
#           "authors": ["..."],
#           "year": 2021,
#           "doi": "10.1234/abcd",
#           "source": "crossref|semanticscholar|arxiv",
#           "source_id": "...",
#           "venue": "Journal / Conference",
#           "publisher": "...",
#           "abstract": "...",
#           "language": "en",
#           "url": "https://...",
#           "query_topic": "integrity_auditability_core",
#           "query_string": "<the exact string executed>",
#           "retrieved_at": "YYYY-MM-DDTHH:MM:SSZ"
#         },
#         ...
#       ]
#   - Also writes a small run metadata block as first element with "_meta": true.
# =============================================================================

from __future__ import annotations
import os
import re
import sys
import json
import time
import math
import uuid
import hashlib
import logging
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml

CANONICAL_A = "json_jsonl/ELIS_Appendix_A_Search_rows.json"
CONFIG_PATH = "config/elis_search_queries.yml"

# ------------------------- Logging configuration -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

# ------------------------- Helpers ------------------------------------------
def now_utc_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def ensure_dirs():
    os.makedirs(os.path.dirname(CANONICAL_A), exist_ok=True)

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def normalize_title(title: Optional[str]) -> str:
    if not title:
        return ""
    # Lowercase, remove punctuation & extra spaces
    t = re.sub(r"[^\w\s]", " ", title.lower())
    return re.sub(r"\s+", " ", t).strip()

def stable_id(doi: Optional[str], title: Optional[str], year: Optional[int]) -> str:
    """
    Produce a stable deterministic id for deduping. Prefer DOI; else title+year.
    """
    if doi:
        return "doi:" + doi.lower().strip()
    t = normalize_title(title)
    y = str(year or "")
    return "t:"+hashlib.sha256((t+"|"+y).encode("utf-8")).hexdigest()[:20]

def within_years(year: Optional[int], y0: int, y1: int) -> bool:
    if not isinstance(year, int):
        return False
    return y0 <= year <= y1

def lang_ok(language: Optional[str], allowed: List[str]) -> bool:
    if not allowed:
        return True
    if not language:
        # We keep items with unknown language; screening can exclude later.
        return True
    return language.lower() in {x.lower() for x in allowed}

def polite_sleep(seconds: float):
    time.sleep(seconds)

# ------------------------- Source: Crossref ----------------------------------
def search_crossref(query: str, year_from: int, year_to: int, languages: List[str], cap: int) -> List[Dict[str, Any]]:
    """
    Crossref REST: https://api.crossref.org/works
    We use 'query' and filter by 'from-pub-date'/'until-pub-date' where possible.
    """
    out = []
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
            r = requests.get(url, params={**params, "cursor": cursor}, timeout=30)
            r.raise_for_status()
        except Exception as e:
            logging.warning(f"Crossref error: {e}")
            break
        data = r.json()
        items = (data.get("message") or {}).get("items") or []
        for it in items:
            # Map fields with best-effort parsing
            title = " ".join(it.get("title") or []) or None
            authors = []
            for a in it.get("author") or []:
                nm = " ".join([a.get("given",""), a.get("family","")]).strip()
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
            if within_years(rec["year"], year_from, year_to) and lang_ok(rec["language"], languages):
                out.append(rec)
                got += 1
                if got >= cap:
                    break
        cursor = (data.get("message") or {}).get("next-cursor") or None
        if not cursor:
            break
        polite_sleep(0.5)
    return out

# ------------------------- Source: Semantic Scholar --------------------------
def search_semantic_scholar(query: str, year_from: int, year_to: int, languages: List[str], cap: int) -> List[Dict[str, Any]]:
    """
    Semantic Scholar API v1 (Graph-like REST):
    https://api.semanticscholar.org/ (free tier; API key optional)
    """
    out = []
    fields = "title,authors,year,venue,externalIds,publicationTypes,abstract,url,journal,publicationVenue"
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {}
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
            doi = None
            ext = it.get("externalIds") or {}
            if "DOI" in ext and ext["DOI"]:
                doi = ext["DOI"]
            # crude language guess (S2 doesn’t provide lang reliably) -> keep
            rec = {
                "title": it.get("title"),
                "authors": [a.get("name") for a in (it.get("authors") or []) if a.get("name")],
                "year": it.get("year"),
                "doi": doi,
                "venue": it.get("venue") or (it.get("journal") or {}).get("name") or (it.get("publicationVenue") or {}).get("name"),
                "publisher": None,
                "url": it.get("url"),
                "language": None,  # unknown: we keep and screen later
                "abstract": it.get("abstract"),
                "doc_type": (",".join(it.get("publicationTypes") or []) or None),
                "source": "semanticscholar",
                "source_id": it.get("paperId"),
            }
            if within_years(rec["year"], year_from, year_to) and lang_ok(rec["language"], languages):
                out.append(rec)
                if len(out) >= cap:
                    break
        if not data.get("data"):
            break
        offset += params["limit"]
        polite_sleep(0.5)
    return out

# ------------------------- Source: arXiv -------------------------------------
def search_arxiv(query: str, year_from: int, year_to: int, languages: List[str], cap: int) -> List[Dict[str, Any]]:
    """
    arXiv Atom API via export.arxiv.org
    Language not provided; treat as unknown and keep for screening.
    """
    out = []
    # arXiv query syntax is different; we do a simple all: query with URL encoding.
    # Note: arXiv is preprint; allow via include_preprints flag at topic level.
    base = "http://export.arxiv.org/api/query"
    start = 0
    pagesize = 100
    while len(out) < cap:
        params = {
            "search_query": f'all:{query}',
            "start": start,
            "max_results": min(pagesize, cap - len(out)),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        try:
            r = requests.get(base, params=params, timeout=30)
            r.raise_for_status()
            text = r.text
        except Exception as e:
            logging.warning(f"arXiv error: {e}")
            break

        # Very light parsing to get entries (avoid external deps)
        entries = re.findall(r"<entry>(.*?)</entry>", text, flags=re.DOTALL)
        if not entries:
            break

        for ent in entries:
            # Title
            m_title = re.search(r"<title>(.*?)</title>", ent, flags=re.DOTALL)
            title = (m_title.group(1).strip() if m_title else None)
            # Year from published
            m_pub = re.search(r"<published>(.*?)</published>", ent)
            year = None
            if m_pub:
                try:
                    year = int(m_pub.group(1)[:4])
                except Exception:
                    pass
            # URL/ID
            m_id = re.search(r"<id>(.*?)</id>", ent)
            url = (m_id.group(1) if m_id else None)
            # Authors
            authors = re.findall(r"<name>(.*?)</name>", ent)
            # DOI if present in links
            m_doi = re.search(r"<arxiv:doi xmlns:arxiv=\"http://arxiv.org/schemas/atom\">(.*?)</arxiv:doi>", ent)
            doi = m_doi.group(1) if m_doi else None
            # Abstract
            m_abs = re.search(r"<summary>(.*?)</summary>", ent, flags=re.DOTALL)
            abstract = (m_abs.group(1).strip() if m_abs else None)

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
            if within_years(rec["year"], year_from, year_to) and lang_ok(rec["language"], languages):
                out.append(rec)
                if len(out) >= cap:
                    break
        start += params["max_results"]
        polite_sleep(0.5)
    return out

# ------------------------- Orchestrator --------------------------------------
def orchestrate_search(config: dict) -> List[Dict[str, Any]]:
    y0 = int(config.get("global", {}).get("year_from", 1990))
    y1 = int(config.get("global", {}).get("year_to", dt.datetime.utcnow().year))
    langs = config.get("global", {}).get("languages", ["en"])
    topic_cap = int(config.get("global", {}).get("max_results_per_source", 100))
    job_cap = int(config.get("global", {}).get("job_result_cap", 0))

    enabled_topics = [t for t in (config.get("topics") or []) if t.get("enabled", True)]
    results: List[Dict[str, Any]] = []

    # Dedup tracking
    seen: set[str] = set()

    def add_with_dedupe(rec: Dict[str, Any], topic_id: str, query_str: str):
        rec["query_topic"] = topic_id
        rec["query_string"] = query_str
        rec["retrieved_at"] = now_utc_iso()
        key = stable_id(rec.get("doi"), rec.get("title"), rec.get("year"))
        rec["_stable_id"] = key  # internal
        if key in seen:
            return
        seen.add(key)
        results.append(rec)

    for topic in enabled_topics:
        topic_id = topic["id"]
        include_preprints = bool(topic.get("include_preprints", True))
        sources = topic.get("sources", ["crossref", "semanticscholar"])
        for q in (topic.get("queries") or []):
            # Crossref
            if "crossref" in sources:
                for rec in search_crossref(q, y0, y1, langs, cap=topic_cap):
                    add_with_dedupe(rec, topic_id, q)
            # Semantic Scholar
            if "semanticscholar" in sources:
                for rec in search_semantic_scholar(q, y0, y1, langs, cap=topic_cap):
                    add_with_dedupe(rec, topic_id, q)
            # arXiv (preprints)
            if include_preprints and "arxiv" in sources:
                for rec in search_arxiv(q, y0, y1, langs, cap=min(50, topic_cap)):  # keep arXiv modest
                    add_with_dedupe(rec, topic_id, q)
            # Job-level cap (if set)
            if job_cap and len(results) >= job_cap:
                logging.info(f"Job result cap reached: {job_cap}")
                return results
    return results

# ------------------------- Write JSON ----------------------------------------
def write_json_array(path: str, records: List[Dict[str, Any]], meta: Dict[str, Any]):
    ensure_dirs()
    payload = [{"_meta": True, **meta}] + records
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

# ------------------------- CLI entrypoint ------------------------------------
def main(argv: List[str]) -> int:
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

    meta = {
        "protocol_version": "ELIS 2025 (MVP)",
        "config_path": args.config,
        "retrieved_at": now_utc_iso(),
        "global": config.get("global", {}),
        "topics_enabled": [t["id"] for t in config.get("topics", []) if t.get("enabled", True)],
        "sources": list({r["source"] for r in records}),
        "record_count": len(records),
    }

    if args.dry_run:
        logging.info("Dry-run: not writing canonical Appendix A file.")
        logging.info(json.dumps(meta, indent=2))
        return 0

    write_json_array(CANONICAL_A, records, meta)
    logging.info(f"Wrote canonical Appendix A JSON: {CANONICAL_A}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
