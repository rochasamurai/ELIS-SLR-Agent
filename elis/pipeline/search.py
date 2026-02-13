"""
ELIS pipeline — Appendix A (Search)

Importable module wrapping the MVP search logic from scripts/elis/search_mvp.py.
Query multiple academic sources (Crossref, Semantic Scholar, arXiv) using
controlled queries and produce a canonical Appendix A JSON array.
"""

from __future__ import annotations

import argparse
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

log = logging.getLogger(__name__)


# ------------------------- Helpers ------------------------------------------
def now_utc_iso() -> str:
    """Return UTC timestamp in ISO 8601 (no microseconds, with trailing Z)."""
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_dirs(path: str = CANONICAL_A) -> None:
    """Create output directories if missing."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


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
    """Tiny sleep to avoid hammering public APIs."""
    if REQUEST_SLEEP_S > 0:
        time.sleep(REQUEST_SLEEP_S)


def build_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute per-source and per-topic counts for the deduplicated record set.
    Returns a plain dict suitable for embedding in _meta.summary.
    """
    per_source = Counter(r.get("source") for r in records if r.get("source"))
    per_topic = Counter(r.get("query_topic") for r in records if r.get("query_topic"))

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
    Derive a provenance snapshot of the *effective* knobs used for this run.
    """
    g = config.get("global") or {}
    year_from = int(g.get("year_from", 1990))
    year_to = int(g.get("year_to", dt.datetime.utcnow().year))
    job_result_cap = int(g.get("job_result_cap", 0))
    max_results_per_source = int(g.get("max_results_per_source", 100))

    topics = config.get("topics") or []
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
    """
    out: List[Dict[str, Any]] = []
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": 100,
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
            log.warning("Crossref error: %s", e)
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
                "abstract": (it.get("abstract") or None),
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
    headers = dict(DEFAULT_HEADERS)
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
            log.warning("Semantic Scholar error: %s", e)
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
                "language": None,
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
            log.warning("arXiv error: %s", e)
            break

        entries = re.findall(r"<entry>(.*?)</entry>", text, flags=re.DOTALL)
        if not entries:
            break

        for ent in entries:
            m_title = re.search(r"<title>(.*?)</title>", ent, flags=re.DOTALL)
            title = m_title.group(1).strip() if m_title else None
            m_pub = re.search(r"<published>(.*?)</published>", ent)
            year = None
            if m_pub:
                try:
                    year = int(m_pub.group(1)[:4])
                except Exception:
                    pass
            m_id = re.search(r"<id>(.*?)</id>", ent)
            entry_url = m_id.group(1) if m_id else None
            authors = re.findall(r"<name>(.*?)</name>", ent)
            m_doi = re.search(
                r'<arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">(.*?)</arxiv:doi>',
                ent,
            )
            doi = m_doi.group(1) if m_doi else None
            m_abs = re.search(r"<summary>(.*?)</summary>", ent, flags=re.DOTALL)
            abstract = m_abs.group(1).strip() if m_abs else None

            rec = {
                "title": title,
                "authors": authors,
                "year": year,
                "doi": doi,
                "venue": "arXiv",
                "publisher": None,
                "url": entry_url,
                "language": None,
                "abstract": abstract,
                "doc_type": "preprint",
                "source": "arxiv",
                "source_id": entry_url,
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

    seen: set[str] = set()

    def add_with_dedupe(rec: Dict[str, Any], topic_id: str, query_str: str) -> None:
        rec["query_topic"] = topic_id
        rec["query_string"] = query_str
        rec["retrieved_at"] = now_utc_iso()
        key = stable_id(rec.get("doi"), rec.get("title"), rec.get("year"))
        rec["id"] = key
        rec["_stable_id"] = key
        if key in seen:
            return
        seen.add(key)
        results.append(rec)

    for i, topic in enumerate(enabled_topics):
        topic_id = topic.get("id") or topic.get("name") or f"topic_{i}"
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
                log.info("Job result cap reached: %s", job_cap)
                return results
    return results


# ------------------------- Write JSON ----------------------------------------
def write_json_array(
    path: str, records: List[Dict[str, Any]], meta: Dict[str, Any]
) -> None:
    """Write records to a JSON array with a leading _meta element."""
    ensure_dirs(path)
    payload = [{"_meta": True, **meta}] + records
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ------------------------- CLI entrypoint ------------------------------------
def main(argv: List[str] | None = None) -> int:
    """CLI for Appendix A search."""
    if argv is None:
        argv = sys.argv[1:]

    ap = argparse.ArgumentParser(description="ELIS - Appendix A Search")
    ap.add_argument(
        "--config", default=CONFIG_PATH, help="YAML config with queries/topics"
    )
    ap.add_argument(
        "--dry-run", action="store_true", help="Run search but do not write file"
    )
    args = ap.parse_args(argv)

    if not os.path.isfile(args.config):
        log.error("Config not found: %s", args.config)
        return 2

    config = load_yaml(args.config)
    log.info("Starting search orchestrator...")
    records = orchestrate_search(config)
    log.info("Total records (pre-write, unique): %d", len(records))

    summary = build_summary(records)
    meta = {
        "protocol_version": "ELIS 2025 (MVP)",
        "config_path": args.config,
        "retrieved_at": now_utc_iso(),
        "global": config.get("global", {}),
        "topics_enabled": [
            t.get("id") or t.get("name") or f"topic_{i}"
            for i, t in enumerate(config.get("topics", []))
            if t.get("enabled", True)
        ],
        "sources": sorted(list({r["source"] for r in records})),
        "record_count": len(records),
        "summary": summary,
        "run_inputs": build_run_inputs(config),
    }

    write_step_summary(meta, summary)

    if args.dry_run:
        log.info("Dry-run: not writing canonical Appendix A file.")
        log.info(json.dumps(meta, indent=2))
        return 0

    write_json_array(CANONICAL_A, records, meta)
    log.info("Wrote canonical Appendix A JSON: %s", CANONICAL_A)
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout,
    )
    sys.exit(main())
