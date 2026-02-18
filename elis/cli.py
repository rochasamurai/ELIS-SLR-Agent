"""CLI entrypoint for ELIS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from elis.manifest import emit_run_manifest, manifest_path_for_output, now_utc_iso


def _count_data_rows(path: str | Path) -> int:
    """Count data rows in a JSON array/JSONL payload, skipping _meta headers."""
    target = Path(path)
    if not target.exists():
        return 0
    text = target.read_text(encoding="utf-8").strip()
    if not text:
        return 0
    if text.startswith("["):
        payload = json.loads(text)
        if isinstance(payload, list):
            return sum(
                1
                for item in payload
                if isinstance(item, dict) and not item.get("_meta")
            )
        return 0
    count = 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if isinstance(row, dict) and not row.get("_meta"):
            count += 1
    return count


def _load_inputs_from_manifest(manifest_path: str) -> list[str]:
    """Read merge input file list from a run manifest."""
    try:
        payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Manifest file not found: {manifest_path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Manifest payload must be a JSON object.")
    inputs = payload.get("input_paths")
    if isinstance(inputs, list) and inputs:
        return [str(item) for item in inputs if str(item).strip()]
    fallback = payload.get("output_path")
    if isinstance(fallback, str) and fallback.strip():
        return [fallback]
    raise ValueError("Manifest does not contain usable input_paths or output_path.")


def _resolve_merge_inputs(args: argparse.Namespace) -> list[str]:
    """Resolve merge inputs with --inputs taking precedence over --from-manifest."""
    if args.inputs:
        return [str(item) for item in args.inputs]
    if args.from_manifest:
        return _load_inputs_from_manifest(args.from_manifest)
    raise SystemExit("Provide --inputs or --from-manifest.")


def _run_validate(args: argparse.Namespace) -> int:
    """Run legacy validation via a thin wrapper for PE0a."""
    from scripts._archive.validate_json import (
        main as legacy_main,
        validate_appendix,
    )

    started_at = now_utc_iso()

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
        emit_run_manifest(
            stage="validate",
            source="system",
            input_paths=[str(Path(schema_path)), str(Path(json_path))],
            output_path=str(Path(json_path)),
            record_count=count,
            config_payload={
                "mode": "single",
                "schema_path": str(Path(schema_path)),
                "target_path": str(Path(json_path)),
            },
            started_at=started_at,
            finished_at=now_utc_iso(),
            manifest_path=manifest_path_for_output(Path(json_path)),
        )
        return 0

    if schema_path or json_path:
        raise SystemExit("Provide both <schema_path> and <json_path>, or neither.")

    code = 0
    try:
        legacy_main()
    except SystemExit as exc:
        if isinstance(exc.code, int):
            code = exc.code
    if code == 0:
        report_path = Path("validation_reports/validation-report.md")
        if report_path.exists():
            emit_run_manifest(
                stage="validate",
                source="system",
                input_paths=[],
                output_path=str(report_path),
                record_count=0,
                config_payload={"mode": "full"},
                started_at=started_at,
                finished_at=now_utc_iso(),
                manifest_path=manifest_path_for_output(report_path),
            )
    return code


# ---------------------------------------------------------------------------
# harvest subcommand (PE2)
# ---------------------------------------------------------------------------


def _run_harvest(args: argparse.Namespace) -> int:
    """Execute a harvest run for a single source."""
    from elis.sources import get_adapter
    from elis.sources.config import load_harvest_config

    started_at = now_utc_iso()

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

    config_source = (
        str(args.search_config)
        if getattr(args, "search_config", None)
        else "config/elis_search_queries.yml"
    )
    emit_run_manifest(
        stage="harvest",
        source=str(args.source),
        input_paths=[config_source],
        output_path=str(output_path),
        record_count=len(existing_results),
        config_payload={
            "search_config": config_source,
            "tier": getattr(args, "tier", None),
            "max_results": harvest_cfg.max_results,
            "output": str(output_path),
        },
        started_at=started_at,
        finished_at=now_utc_iso(),
        manifest_path=manifest_path_for_output(output_path),
    )

    return 0


def _run_merge(args: argparse.Namespace) -> int:
    """Execute PE3 canonical merge stage."""
    from elis.pipeline.merge import run_merge

    started_at = now_utc_iso()
    inputs = _resolve_merge_inputs(args)

    run_merge(inputs, args.output, args.report)
    print(f"[OK] Merged {len(inputs)} input file(s) -> {args.output}")
    print(f"[OK] Merge report -> {args.report}")
    emit_run_manifest(
        stage="merge",
        source="system",
        input_paths=inputs,
        output_path=str(args.output),
        record_count=_count_data_rows(args.output),
        config_payload={
            "report": str(args.report),
            "from_manifest": getattr(args, "from_manifest", None),
        },
        started_at=started_at,
        finished_at=now_utc_iso(),
        manifest_path=manifest_path_for_output(args.output),
    )
    return 0


def _run_dedup(args: argparse.Namespace) -> int:
    """Execute PE4 deterministic dedup stage."""
    from elis.pipeline.dedup import run_dedup

    started_at = now_utc_iso()
    run_dedup(
        args.input,
        args.output,
        args.report,
        duplicates_path=args.duplicates_path,
        fuzzy=args.fuzzy,
        threshold=args.threshold,
        config_path=args.config_path,
    )
    print(f"[OK] Dedup complete -> {args.output}")
    print(f"[OK] Dedup report  -> {args.report}")
    print(f"[OK] Duplicates    -> {args.duplicates_path}")
    emit_run_manifest(
        stage="dedup",
        source="system",
        input_paths=[str(args.input)],
        output_path=str(args.output),
        record_count=_count_data_rows(args.output),
        config_payload={
            "report": str(args.report),
            "duplicates_path": str(args.duplicates_path),
            "fuzzy": bool(args.fuzzy),
            "threshold": float(args.threshold),
            "config_path": str(args.config_path),
        },
        started_at=started_at,
        finished_at=now_utc_iso(),
        manifest_path=manifest_path_for_output(args.output),
    )
    return 0


def _run_screen(args: argparse.Namespace) -> int:
    """Execute PE0b screening stage via package pipeline."""
    from elis.pipeline.screen import main as screen_main

    started_at = now_utc_iso()
    cli_args: list[str] = ["--input", str(args.input), "--output", str(args.output)]
    if args.year_from is not None:
        cli_args.extend(["--year-from", str(args.year_from)])
    if args.year_to is not None:
        cli_args.extend(["--year-to", str(args.year_to)])
    if args.languages:
        cli_args.extend(["--languages", str(args.languages)])
    if args.allow_unknown_language:
        cli_args.append("--allow-unknown-language")
    if args.enforce_preprint_policy:
        cli_args.append("--enforce-preprint-policy")
    if args.dry_run:
        cli_args.append("--dry-run")

    rc = int(screen_main(cli_args))
    if rc == 0 and not args.dry_run and Path(args.output).exists():
        emit_run_manifest(
            stage="screen",
            source="system",
            input_paths=[str(args.input)],
            output_path=str(args.output),
            record_count=_count_data_rows(args.output),
            config_payload={
                "year_from": args.year_from,
                "year_to": args.year_to,
                "languages": args.languages,
                "allow_unknown_language": bool(args.allow_unknown_language),
                "enforce_preprint_policy": bool(args.enforce_preprint_policy),
                "dry_run": bool(args.dry_run),
            },
            started_at=started_at,
            finished_at=now_utc_iso(),
            manifest_path=manifest_path_for_output(args.output),
        )
    return rc


def _run_agentic_asta_discover(args: argparse.Namespace) -> int:
    """Execute PE5 ASTA discover sidecar stage."""
    from elis.agentic.asta import run_discover

    output = run_discover(
        query=args.query,
        run_id=args.run_id,
        output=args.output,
        config_path=args.config_path,
        limit=args.limit,
    )
    print(f"[OK] ASTA discover report -> {output}")
    return 0


def _run_agentic_asta_enrich(args: argparse.Namespace) -> int:
    """Execute PE5 ASTA enrich sidecar stage."""
    from elis.agentic.asta import run_enrich

    output = run_enrich(
        input_path=args.input_path,
        run_id=args.run_id,
        output=args.output,
        config_path=args.config_path,
        limit=args.limit,
    )
    print(f"[OK] ASTA enrich output -> {output}")
    return 0


def _run_export_latest(args: argparse.Namespace) -> int:
    """Copy canonical artefacts from runs/<run_id>/ to json_jsonl/ (PE6)."""
    import shutil

    runs_dir = Path(args.runs_dir)
    export_dir = Path(args.export_dir)
    latest_txt = export_dir / "LATEST_RUN_ID.txt"

    run_id = getattr(args, "run_id", None)
    if not run_id:
        if latest_txt.exists():
            run_id = latest_txt.read_text(encoding="utf-8").strip()
        if not run_id:
            print(
                "[ERROR] No --run-id provided and json_jsonl/LATEST_RUN_ID.txt not found."
            )
            return 1

    run_path = runs_dir / run_id
    if not run_path.exists():
        print(f"[ERROR] Run directory not found: {run_path}")
        return 1

    export_dir.mkdir(parents=True, exist_ok=True)

    # Copy all JSON/JSONL files from the run tree into json_jsonl/ (flat).
    copied = 0
    for src in sorted(run_path.rglob("*.json")) + sorted(run_path.rglob("*.jsonl")):
        if src.name.endswith("_manifest.json"):
            continue  # skip manifest sidecars
        dest = export_dir / src.name
        shutil.copy2(src, dest)
        copied += 1
        print(f"  copied: {src.relative_to(runs_dir)} → {dest}")

    # Write LATEST_RUN_ID.txt
    latest_txt.write_text(run_id + "\n", encoding="utf-8")
    print(f"\n[OK] Exported {copied} file(s) from run {run_id!r} → {export_dir}/")
    print(f"[OK] LATEST_RUN_ID.txt written: {run_id}")
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
        required=False,
        help="Input JSON/JSONL files to merge",
    )
    merge.add_argument(
        "--from-manifest",
        type=str,
        default=None,
        dest="from_manifest",
        help="Run manifest path to read input_paths from (used when --inputs is omitted)",
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
    dedup.add_argument(
        "--duplicates",
        type=str,
        default="dedup/duplicates.jsonl",
        dest="duplicates_path",
        help="JSONL sidecar for dropped records with cluster_id + duplicate_of",
    )
    dedup.set_defaults(func=_run_dedup)

    # screen --------------------------------------------------------------
    screen = subparsers.add_parser(
        "screen",
        help="Screen canonical Appendix A into Appendix B",
    )
    screen.add_argument(
        "--input",
        type=str,
        default="json_jsonl/ELIS_Appendix_A_Search_rows.json",
        help="Path to canonical Appendix A JSON array",
    )
    screen.add_argument(
        "--output",
        type=str,
        default="json_jsonl/ELIS_Appendix_B_Screening_rows.json",
        help="Path to write canonical Appendix B JSON array",
    )
    screen.add_argument(
        "--year-from",
        type=int,
        default=None,
        dest="year_from",
        help="Lower bound (inclusive). If omitted, read from Appendix A _meta.",
    )
    screen.add_argument(
        "--year-to",
        type=int,
        default=None,
        dest="year_to",
        help="Upper bound (inclusive). If omitted, read from Appendix A _meta.",
    )
    screen.add_argument(
        "--languages",
        type=str,
        default=None,
        help="Comma-separated ISO codes. If omitted, read from Appendix A _meta.",
    )
    screen.add_argument(
        "--allow-unknown-language",
        action="store_true",
        dest="allow_unknown_language",
        help="Keep records where language is missing/unknown.",
    )
    screen.add_argument(
        "--enforce-preprint-policy",
        action="store_true",
        dest="enforce_preprint_policy",
        help="Respect per-topic include_preprints flags.",
    )
    screen.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Compute screening but do not write output.",
    )
    screen.set_defaults(func=_run_screen)

    # agentic ------------------------------------------------------------
    agentic = subparsers.add_parser(
        "agentic",
        help="Agentic sidecar workflows (PE5)",
    )
    agentic_sub = agentic.add_subparsers(dest="agentic_command", required=True)

    asta = agentic_sub.add_parser("asta", help="ASTA sidecar workflows")
    asta_sub = asta.add_subparsers(dest="asta_command", required=True)

    asta_discover = asta_sub.add_parser(
        "discover",
        help="Run ASTA discovery sidecar",
    )
    asta_discover.add_argument("--query", required=True, help="Discovery query text")
    asta_discover.add_argument("--run-id", required=True, help="Run identifier")
    asta_discover.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output path (default under runs/<run_id>/agentic/asta/)",
    )
    asta_discover.add_argument(
        "--config",
        type=str,
        default="config/asta_config.yml",
        dest="config_path",
        help="Path to ASTA config",
    )
    asta_discover.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Candidate limit (default: 100)",
    )
    asta_discover.set_defaults(func=_run_agentic_asta_discover)

    asta_enrich = asta_sub.add_parser(
        "enrich",
        help="Run ASTA enrichment sidecar",
    )
    asta_enrich.add_argument(
        "--input",
        required=True,
        dest="input_path",
        help="Input records file (JSON/JSONL)",
    )
    asta_enrich.add_argument("--run-id", required=True, help="Run identifier")
    asta_enrich.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output path (default under runs/<run_id>/agentic/asta/)",
    )
    asta_enrich.add_argument(
        "--config",
        type=str,
        default="config/asta_config.yml",
        dest="config_path",
        help="Path to ASTA config",
    )
    asta_enrich.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Snippet limit per record (default: 20)",
    )
    asta_enrich.set_defaults(func=_run_agentic_asta_enrich)

    # export-latest ------------------------------------------------------
    export_latest = subparsers.add_parser(
        "export-latest",
        help="Copy canonical artefacts from runs/<run_id>/ to json_jsonl/ (backward-compat export)",
    )
    export_latest.add_argument(
        "--run-id",
        type=str,
        default=None,
        dest="run_id",
        help="Run ID to export. If omitted, reads json_jsonl/LATEST_RUN_ID.txt.",
    )
    export_latest.add_argument(
        "--runs-dir",
        type=str,
        default="runs",
        dest="runs_dir",
        help="Parent directory for run artefacts (default: runs)",
    )
    export_latest.add_argument(
        "--export-dir",
        type=str,
        default="json_jsonl",
        dest="export_dir",
        help="Export target directory (default: json_jsonl)",
    )
    export_latest.set_defaults(func=_run_export_latest)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI dispatcher."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
