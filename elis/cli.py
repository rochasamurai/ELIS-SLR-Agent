"""CLI entrypoint for ELIS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


def _run_validate(args: argparse.Namespace) -> int:
    """Run legacy validation via a thin wrapper for PE0a."""
    from scripts.validate_json import (
        main as legacy_main,
        validate_appendix,
    )

    schema_path = args.schema_path
    json_path = args.json_path

    if schema_path and json_path:
        is_valid, count, errors = validate_appendix(
            "Validation target", Path(json_path), Path(schema_path)
        )
        status = "[OK]" if is_valid else "[ERR]"
        print(f"{status} Validation target: rows={count} file={Path(json_path).name}")
        if errors:
            print("Errors:")
            for error in errors[:10]:
                print(f"- {error}")
            if len(errors) > 10:
                print(f"- ... and {len(errors) - 10} more errors")
        return 0

    if schema_path or json_path:
        raise SystemExit("Provide both <schema_path> and <json_path>, or neither.")

    try:
        legacy_main()
    except SystemExit as exc:
        if isinstance(exc.code, int):
            return exc.code
        return 0
    return 0


# ---------------------------------------------------------------------------
# harvest subcommand (PE2)
# ---------------------------------------------------------------------------


def _run_harvest(args: argparse.Namespace) -> int:
    """Execute a harvest run for a single source."""
    from elis.sources import get_adapter
    from elis.sources.config import load_harvest_config

    # Resolve configuration
    harvest_cfg = load_harvest_config(
        source_name=args.source,
        search_config=getattr(args, "search_config", None),
        tier=getattr(args, "tier", None),
        max_results_override=getattr(args, "max_results", None),
        output=getattr(args, "output", None),
    )

    if not harvest_cfg.queries:
        print(f"[ERROR] No queries found for source {args.source!r}")
        return 1

    # Print banner
    print(f"\n{'=' * 80}")
    print(f"{args.source.upper()} HARVEST — {harvest_cfg.config_mode} CONFIG")
    print(f"{'=' * 80}")
    print(f"Queries: {len(harvest_cfg.queries)}")
    print(f"Max results per query: {harvest_cfg.max_results}")
    print(f"Output: {harvest_cfg.output_path}")
    print(f"{'=' * 80}\n")

    # Load existing output for dedup
    output_path = Path(harvest_cfg.output_path)
    existing_results: list[dict] = []
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as fh:
            existing_results = json.load(fh)
        print(f"Loaded {len(existing_results)} existing results")

    # Build dedup index (DOI + source-specific ID)
    existing_dois: set[str] = {r["doi"] for r in existing_results if r.get("doi")}
    existing_ids: set[str] = set()
    for r in existing_results:
        for key in ("openalex_id", "crossref_id", "scopus_id"):
            val = r.get(key)
            if val:
                existing_ids.add(val)

    # Instantiate adapter and harvest
    adapter_cls = get_adapter(args.source)
    adapter = adapter_cls()

    new_count = 0
    for record in adapter.harvest(harvest_cfg.queries, harvest_cfg.max_results):
        doi = record.get("doi", "")
        # Check all ID fields for dedup
        is_dup = bool(doi and doi in existing_dois)
        if not is_dup:
            for key in ("openalex_id", "crossref_id", "scopus_id"):
                val = record.get(key)
                if val and val in existing_ids:
                    is_dup = True
                    break

        if not is_dup:
            existing_results.append(record)
            if doi:
                existing_dois.add(doi)
            for key in ("openalex_id", "crossref_id", "scopus_id"):
                val = record.get(key)
                if val:
                    existing_ids.add(val)
            new_count += 1

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(existing_results, fh, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'=' * 80}")
    print(f"[OK] {adapter.display_name} harvest complete")
    print(f"{'=' * 80}")
    print(f"New results added: {new_count}")
    print(f"Total records in dataset: {len(existing_results)}")
    print(f"Saved to: {harvest_cfg.output_path}")
    print(f"{'=' * 80}\n")

    return 0


def _run_merge(args: argparse.Namespace) -> int:
    """Execute PE3 canonical merge stage."""
    from elis.pipeline.merge import run_merge

    run_merge(args.inputs, args.output, args.report)
    print(f"[OK] Merged {len(args.inputs)} input file(s) -> {args.output}")
    print(f"[OK] Merge report -> {args.report}")
    return 0


def _run_dedup(args: argparse.Namespace) -> int:
    """Execute PE4 deterministic dedup stage."""
    from elis.pipeline.dedup import run_dedup

    run_dedup(
        args.input,
        args.output,
        args.report,
        fuzzy=args.fuzzy,
        threshold=args.threshold,
        config_path=args.config_path,
    )
    print(f"[OK] Dedup complete -> {args.output}")
    print(f"[OK] Dedup report  -> {args.report}")
    return 0


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for ELIS CLI."""
    parser = argparse.ArgumentParser(prog="elis", description="ELIS SLR Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate -----------------------------------------------------------
    validate = subparsers.add_parser(
        "validate",
        help="Validate JSON data against schema or run legacy full validation",
    )
    validate.add_argument("schema_path", nargs="?", help="Path to JSON schema")
    validate.add_argument("json_path", nargs="?", help="Path to JSON data file")
    validate.set_defaults(func=_run_validate)

    # harvest ------------------------------------------------------------
    harvest = subparsers.add_parser(
        "harvest",
        help="Harvest records from an academic source",
    )
    harvest.add_argument(
        "source",
        help="Source to harvest from (e.g. openalex, crossref, scopus)",
    )
    harvest.add_argument(
        "--search-config",
        type=str,
        dest="search_config",
        help="Path to search configuration YAML",
    )
    harvest.add_argument(
        "--tier",
        type=str,
        choices=["testing", "pilot", "benchmark", "production", "exhaustive"],
        help="Max-results tier",
    )
    harvest.add_argument(
        "--max-results",
        type=int,
        dest="max_results",
        help="Override max_results regardless of config or tier",
    )
    harvest.add_argument(
        "--output",
        type=str,
        default="json_jsonl/ELIS_Appendix_A_Search_rows.json",
        help="Output file path (default: json_jsonl/ELIS_Appendix_A_Search_rows.json)",
    )
    harvest.set_defaults(func=_run_harvest)

    # merge --------------------------------------------------------------
    merge = subparsers.add_parser(
        "merge",
        help="Merge per-source Appendix A outputs into canonical Appendix A",
    )
    merge.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Input JSON/JSONL files to merge",
    )
    merge.add_argument(
        "--output",
        type=str,
        default="json_jsonl/ELIS_Appendix_A_Search_rows.json",
        help="Merged Appendix A output file path",
    )
    merge.add_argument(
        "--report",
        type=str,
        default="json_jsonl/merge_report.json",
        help="Merge report output path",
    )
    merge.set_defaults(func=_run_merge)

    # dedup --------------------------------------------------------------
    dedup = subparsers.add_parser(
        "dedup",
        help="Deduplicate canonical Appendix A (PE4)",
    )
    dedup.add_argument(
        "--input",
        type=str,
        default="json_jsonl/ELIS_Appendix_A_Search_rows.json",
        help="Merged Appendix A input file",
    )
    dedup.add_argument(
        "--output",
        type=str,
        default="dedup/appendix_a_deduped.json",
        help="Deduped Appendix A output path",
    )
    dedup.add_argument(
        "--report",
        type=str,
        default="dedup/dedup_report.json",
        help="Dedup report output path",
    )
    dedup.add_argument(
        "--fuzzy",
        action="store_true",
        default=False,
        help="Enable fuzzy title-based deduplication (opt-in)",
    )
    dedup.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Similarity threshold for fuzzy mode (default: 0.85)",
    )
    dedup.add_argument(
        "--config",
        type=str,
        default="config/sources.yml",
        dest="config_path",
        help="Path to sources.yml for keeper priority",
    )
    dedup.set_defaults(func=_run_dedup)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI dispatcher."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
