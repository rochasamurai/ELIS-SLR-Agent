"""Phase 2 ASTA screening workflow.

This script uses ASTA snippet search to pre-fill evidence support for
screening decisions. It does not make inclusion/exclusion decisions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sources.asta_mcp.adapter import AstaMCPAdapter


DEFAULT_SCREENING_QUERIES = [
    "audit mechanism",
    "verification protocol",
    "security threat model",
    "implementation case study",
    "effectiveness evaluation",
]


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Run ASTA Phase 2 screening support.")
    parser.add_argument(
        "--papers",
        required=True,
        help="Path to candidate papers file (json/jsonl/yml).",
    )
    parser.add_argument(
        "--config",
        default="config/asta_config.yml",
        help="Path to ASTA config file.",
    )
    parser.add_argument(
        "--output",
        default="runs/phase2_asta_screening_results.json",
        help="Output JSON path for screening snippets.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Override snippets per query.",
    )
    parser.add_argument(
        "--query",
        action="append",
        default=None,
        help="Screening query. May be passed multiple times.",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    """Load YAML config if available, otherwise return empty config."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


def load_records(path: Path) -> list[dict[str, Any]]:
    """Load JSON, JSONL, or YAML records from file."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        records: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if isinstance(data, dict):
                    records.append(data)
        return records

    if suffix in {".yaml", ".yml"}:
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
    else:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("records", "papers", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [payload]
    return []


def extract_paper_ids(records: list[dict[str, Any]]) -> list[str]:
    """Extract ASTA paper identifiers from candidate records."""
    paper_ids: list[str] = []
    seen: set[str] = set()
    fields = ("paper_id", "paperId", "asta_id", "corpus_id")
    for record in records:
        for field in fields:
            value = record.get(field)
            if value is None:
                continue
            paper_id = str(value).strip()
            if not paper_id or paper_id in seen:
                continue
            seen.add(paper_id)
            paper_ids.append(paper_id)
            break
    return paper_ids


def deduplicate_snippets(snippets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate snippets by paper_id + normalized snippet text."""
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for snippet in snippets:
        paper_id = str(snippet.get("paper_id", "")).strip().lower()
        text = str(snippet.get("snippet_text", "")).strip().lower()
        key = f"{paper_id}|{text}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(snippet)
    return deduped


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON output with stable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main() -> int:
    """Execute Phase 2 screening assistance workflow."""
    args = parse_args()
    config = load_config(Path(args.config))

    mcp_cfg = config.get("asta_mcp", {}) if isinstance(config, dict) else {}
    evidence_window_end = mcp_cfg.get("evidence_window_end", "2025-01-31")

    phase_cfg = config.get("phases", {}).get("phase2_screening", {})
    default_limit = int(phase_cfg.get("snippets_per_query", 100))
    limit = args.limit if args.limit is not None else default_limit

    queries = args.query if args.query else phase_cfg.get("snippet_queries", [])
    if not isinstance(queries, list) or not queries:
        queries = DEFAULT_SCREENING_QUERIES

    records = load_records(Path(args.papers))
    paper_ids = extract_paper_ids(records)
    adapter = AstaMCPAdapter(evidence_window_end=evidence_window_end)

    print("=" * 70)
    print("ELIS ASTA PHASE 2 - SCREENING ASSISTANCE")
    print("=" * 70)
    print(f"Evidence window end: {evidence_window_end}")
    print(f"Input records: {len(records)}")
    print(f"Paper IDs supplied to ASTA: {len(paper_ids)}")
    print(f"Queries: {len(queries)}")
    print(f"Snippets per query: {limit}")
    print()

    query_results: list[dict[str, Any]] = []
    all_snippets: list[dict[str, Any]] = []
    for idx, query in enumerate(queries, start=1):
        print(f"[{idx}/{len(queries)}] Query: {query}")
        try:
            snippets = adapter.find_snippets(
                query=query,
                paper_ids=paper_ids or None,
                limit=limit,
            )
            all_snippets.extend(snippets)
            query_results.append(
                {
                    "query": query,
                    "snippet_count": len(snippets),
                    "snippets": snippets,
                }
            )
            print(f"  Retrieved {len(snippets)} snippets")
        except Exception as exc:  # noqa: BLE001
            query_results.append(
                {
                    "query": query,
                    "snippet_count": 0,
                    "error": str(exc),
                    "snippets": [],
                }
            )
            print(f"  Error: {exc}")

    deduped_snippets = deduplicate_snippets(all_snippets)
    stats = adapter.get_stats()

    output = {
        "phase": "phase2_screening",
        "policy": "ASTA proposes, ELIS decides",
        "evidence_window_end": evidence_window_end,
        "input": {
            "papers_path": str(Path(args.papers)),
            "records_loaded": len(records),
            "paper_ids_used": len(paper_ids),
            "queries": queries,
            "snippet_limit_per_query": limit,
        },
        "results": {
            "total_snippets_raw": len(all_snippets),
            "total_snippets_deduped": len(deduped_snippets),
            "per_query": query_results,
        },
        "adapter_stats": stats,
        "run": {
            "run_id": adapter.run_id,
            "logs_dir": str(adapter.log_dir),
        },
    }

    output_path = Path(args.output)
    write_json(output_path, output)

    print()
    print(f"Total snippets (raw): {len(all_snippets)}")
    print(f"Total snippets (deduped): {len(deduped_snippets)}")
    print(f"Output: {output_path}")
    print(f"Logs: {adapter.log_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
