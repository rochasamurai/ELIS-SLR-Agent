"""ASTA pipeline integration wrappers (PE5)."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

from elis.agentic.evidence import validate_evidence_spans

AstaMCPAdapter = None

DEFAULT_CONFIG = "config/asta_config.yml"
DEFAULT_DISCOVER_LIMIT = 100
DEFAULT_ENRICH_LIMIT = 20


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _read_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    if text.startswith("["):
        payload = json.loads(text)
        if not isinstance(payload, list):
            raise ValueError(f"Expected JSON array in {path}")
        return [
            row for row in payload if isinstance(row, dict) and not row.get("_meta")
        ]

    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if isinstance(row, dict) and not row.get("_meta"):
            rows.append(row)
    return rows


def _load_config(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    import yaml  # type: ignore[import-untyped]

    cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
    return cfg if isinstance(cfg, dict) else {}


def _run_dir(run_id: str) -> Path:
    return Path("runs") / run_id / "agentic" / "asta"


def _default_discover_output(run_id: str) -> Path:
    return _run_dir(run_id) / "asta_discovery_report.json"


def _default_enrich_output(run_id: str) -> Path:
    return _run_dir(run_id) / "asta_outputs.jsonl"


def _record_id(record: dict[str, Any]) -> str:
    rid = record.get("id") or record.get("_stable_id")
    if rid:
        return str(rid)
    basis = (
        f"{record.get('title','')}|{record.get('year','')}|{record.get('source','')}"
    )
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
    return f"tmp:{digest}"


def _resolve_asta_adapter():
    """Resolve ASTA adapter class lazily with repo-local fallback."""
    global AstaMCPAdapter
    if AstaMCPAdapter is not None:
        return AstaMCPAdapter

    # Editable installs may not include top-level `sources`; fallback to repo root.
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.append(repo_root_str)

    for module_path in ("sources.asta_mcp.adapter", "elis.sources.asta_mcp.adapter"):
        try:
            module = importlib.import_module(module_path)
            AstaMCPAdapter = getattr(module, "AstaMCPAdapter")
            return AstaMCPAdapter
        except (ModuleNotFoundError, AttributeError):
            continue

    raise SystemExit(
        "ASTA adapter unavailable. Install/configure the ASTA sources package."
    )


def run_discover(
    *,
    query: str,
    run_id: str,
    output: str | None = None,
    config_path: str = DEFAULT_CONFIG,
    limit: int = DEFAULT_DISCOVER_LIMIT,
) -> Path:
    """
    Run ASTA discovery query and write sidecar report under runs/<run_id>/agentic/asta/.
    """
    cfg = _load_config(config_path)
    window_end = (
        cfg.get("asta_mcp", {}).get("evidence_window_end", "2025-01-31")
        if isinstance(cfg, dict)
        else "2025-01-31"
    )

    adapter_cls = _resolve_asta_adapter()
    adapter = adapter_cls(evidence_window_end=window_end, run_id=run_id)
    candidates = adapter.search_candidates(query=query, limit=limit)

    report = {
        "mode": "discover",
        "policy": "ASTA proposes, ELIS decides",
        "run_id": run_id,
        "query": query,
        "limit": limit,
        "candidate_count": len(candidates),
        "timestamp": _utc_now(),
        "outputs_path": str(_run_dir(run_id)),
        "candidates": candidates,
    }

    out_path = Path(output) if output else _default_discover_output(run_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return out_path


def run_enrich(
    *,
    input_path: str,
    run_id: str,
    output: str | None = None,
    config_path: str = DEFAULT_CONFIG,
    limit: int = DEFAULT_ENRICH_LIMIT,
) -> Path:
    """
    Run ASTA evidence enrichment for canonical records and write JSONL sidecar.
    """
    cfg = _load_config(config_path)
    window_end = (
        cfg.get("asta_mcp", {}).get("evidence_window_end", "2025-01-31")
        if isinstance(cfg, dict)
        else "2025-01-31"
    )

    adapter_cls = _resolve_asta_adapter()
    adapter = adapter_cls(evidence_window_end=window_end, run_id=run_id)
    records = _read_json_or_jsonl(Path(input_path))

    out_path = Path(output) if output else _default_enrich_output(run_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    for record in records:
        rid = _record_id(record)
        query = str(record.get("title") or "")

        paper_ids: list[str] = []
        for key in ("asta_id", "corpus_id", "paper_id", "paperId"):
            value = record.get(key)
            if value:
                paper_ids.append(str(value))

        snippets = adapter.find_snippets(
            query=query, paper_ids=paper_ids or None, limit=limit
        )
        spans = [
            str(s.get("snippet_text", "")) for s in snippets if s.get("snippet_text")
        ]
        validated = validate_evidence_spans(record, spans)
        valid_count = sum(1 for s in validated if s["valid"])
        confidence = round(min(0.99, 0.5 + (valid_count * 0.1)), 2)

        row = {
            "record_id": rid,
            "suggestion": "review",
            "confidence": confidence,
            "evidence_spans": validated,
            "model_id": "asta-mcp-v1",
            "prompt_hash": "",
            "run_id": run_id,
            "timestamp": _utc_now(),
        }
        lines.append(json.dumps(row, ensure_ascii=False))

    out_path.write_text(("\n".join(lines) + "\n") if lines else "", encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="elis agentic asta", description="ASTA sidecar integration"
    )
    sub = parser.add_subparsers(dest="asta_cmd", required=True)

    discover = sub.add_parser("discover", help="Run ASTA discovery")
    discover.add_argument("--query", required=True, help="Discovery query")
    discover.add_argument("--run-id", required=True, help="Run identifier")
    discover.add_argument("--output", default=None, help="Output report path")
    discover.add_argument(
        "--config", dest="config_path", default=DEFAULT_CONFIG, help="ASTA config path"
    )
    discover.add_argument(
        "--limit", type=int, default=DEFAULT_DISCOVER_LIMIT, help="Candidate limit"
    )

    enrich = sub.add_parser("enrich", help="Run ASTA evidence enrichment")
    enrich.add_argument(
        "--input",
        dest="input_path",
        required=True,
        help="Input Appendix A/B/C JSON or JSONL",
    )
    enrich.add_argument("--run-id", required=True, help="Run identifier")
    enrich.add_argument("--output", default=None, help="Output JSONL path")
    enrich.add_argument(
        "--config", dest="config_path", default=DEFAULT_CONFIG, help="ASTA config path"
    )
    enrich.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_ENRICH_LIMIT,
        help="Snippet limit per record",
    )

    args = parser.parse_args(argv)
    if args.asta_cmd == "discover":
        run_discover(
            query=args.query,
            run_id=args.run_id,
            output=args.output,
            config_path=args.config_path,
            limit=args.limit,
        )
    elif args.asta_cmd == "enrich":
        run_enrich(
            input_path=args.input_path,
            run_id=args.run_id,
            output=args.output,
            config_path=args.config_path,
            limit=args.limit,
        )
    return 0
