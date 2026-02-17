"""CLI entrypoint for ELIS."""

from __future__ import annotations

import argparse
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


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for ELIS CLI."""
    parser = argparse.ArgumentParser(prog="elis", description="ELIS SLR Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate",
        help="Validate JSON data against schema or run legacy full validation",
    )
    validate.add_argument("schema_path", nargs="?", help="Path to JSON schema")
    validate.add_argument("json_path", nargs="?", help="Path to JSON data file")
    validate.set_defaults(func=_run_validate)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI dispatcher."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
