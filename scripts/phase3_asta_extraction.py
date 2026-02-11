"""Phase 3 ASTA evidence localization workflow.

This script retrieves construct-focused snippets to assist data extraction.
It does not finalize extracted values; human validation is required.
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


DEFAULT_CONSTRUCT_QUERIES = [
    "auditability mechanism evidence",
    "verification protocol evidence",
    "security threat model evidence",
    "implementation context evidence",
    "effectiveness outcome evidence",
]


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run ASTA Phase 3 evidence localization."
    )
    parser.add_argument(
        "--papers",
        required=True,
        help="Path to included papers file (json/jsonl/yml).",
    )
    parser.add_argument(
        "--config",
        default="config/asta_config.yml",
        help="Path to ASTA config file.",
    )
    parser.add_argument(
        "--output",
        default="runs/phase3_asta_extraction_results.json",
        help="Output JSON path for extraction snippets.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Snippets per construct query.",
    )
    parser.add_argument(
        "--construct",
        action="append",
        default=None,
        help="Construct-focused query. May be passed multiple times.",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    """Load YAML config if present."""
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

    if suffix in {".yml", ".yaml"}:
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
    """Extract unique paper identifiers from records."""
    ids: list[str] = []
    seen: set[str] = set()
    for record in records:
        for field in ("paper_id", "paperId", "asta_id", "corpus_id"):
            value = record.get(field)
            if value is None:
                continue
            paper_id = str(value).strip()
            if not paper_id or paper_id in seen:
                continue
            seen.add(paper_id)
            ids.append(paper_id)
            break
    return ids


def group_by_paper_id(
    snippets: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """Group snippets for one construct by paper id."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for snippet in snippets:
        paper_id = str(snippet.get("paper_id", "")).strip() or "unknown"
        grouped.setdefault(paper_id, []).append(snippet)
    return grouped


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON output."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main() -> int:
    """Execute Phase 3 extraction assistance workflow."""
    args = parse_args()
    config = load_config(Path(args.config))

    mcp_cfg = config.get("asta_mcp", {}) if isinstance(config, dict) else {}
    evidence_window_end = mcp_cfg.get("evidence_window_end", "2025-01-31")

    records = load_records(Path(args.papers))
    paper_ids = extract_paper_ids(records)
    constructs = args.construct if args.construct else DEFAULT_CONSTRUCT_QUERIES

    adapter = AstaMCPAdapter(evidence_window_end=evidence_window_end)

    print("=" * 70)
    print("ELIS ASTA PHASE 3 - EVIDENCE LOCALIZATION")
    print("=" * 70)
    print(f"Evidence window end: {evidence_window_end}")
    print(f"Input records: {len(records)}")
    print(f"Paper IDs supplied to ASTA: {len(paper_ids)}")
    print(f"Construct queries: {len(constructs)}")
    print(f"Snippets per construct: {args.limit}")
    print()

    per_construct: list[dict[str, Any]] = []
    total_snippets = 0
    for idx, construct in enumerate(constructs, start=1):
        print(f"[{idx}/{len(constructs)}] Construct query: {construct}")
        try:
            snippets = adapter.find_snippets(
                query=construct,
                paper_ids=paper_ids or None,
                limit=args.limit,
            )
            total_snippets += len(snippets)
            per_construct.append(
                {
                    "construct_query": construct,
                    "snippet_count": len(snippets),
                    "by_paper_id": group_by_paper_id(snippets),
                }
            )
            print(f"  Retrieved {len(snippets)} snippets")
        except Exception as exc:  # noqa: BLE001
            per_construct.append(
                {
                    "construct_query": construct,
                    "snippet_count": 0,
                    "error": str(exc),
                    "by_paper_id": {},
                }
            )
            print(f"  Error: {exc}")

    stats = adapter.get_stats()
    output = {
        "phase": "phase3_extraction",
        "policy": "ASTA proposes, ELIS decides",
        "evidence_window_end": evidence_window_end,
        "input": {
            "papers_path": str(Path(args.papers)),
            "records_loaded": len(records),
            "paper_ids_used": len(paper_ids),
            "construct_queries": constructs,
            "snippet_limit_per_construct": args.limit,
        },
        "results": {
            "total_snippets_raw": total_snippets,
            "per_construct": per_construct,
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
    print(f"Total snippets: {total_snippets}")
    print(f"Output: {output_path}")
    print(f"Logs: {adapter.log_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
