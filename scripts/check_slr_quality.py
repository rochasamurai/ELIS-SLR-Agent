#!/usr/bin/env python
"""SLR artifact quality gate for PE-OC-05."""

from __future__ import annotations

import argparse
import json
import pathlib


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def ok(message: str) -> int:
    print(f"OK: {message}")
    return 0


def require_fields(obj: dict, fields: list[str], ctx: str) -> str | None:
    for field in fields:
        if field not in obj:
            return f"{ctx}: missing field '{field}'"
    return None


def load_json(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Root must be a JSON object")
    return data


def validate(data: dict) -> str | None:
    top_required = [
        "screening_decisions",
        "data_extraction",
        "prisma_record",
        "synthesis_notes",
        "agreement",
    ]
    missing = require_fields(data, top_required, "root")
    if missing:
        return missing

    if (
        not isinstance(data["screening_decisions"], list)
        or not data["screening_decisions"]
    ):
        return "screening_decisions must be a non-empty list"
    if not isinstance(data["data_extraction"], list) or not data["data_extraction"]:
        return "data_extraction must be a non-empty list"
    if not isinstance(data["synthesis_notes"], list) or not data["synthesis_notes"]:
        return "synthesis_notes must be a non-empty list"

    for idx, row in enumerate(data["screening_decisions"]):
        if not isinstance(row, dict):
            return f"screening_decisions[{idx}] must be an object"
        missing = require_fields(
            row, ["study_id", "decision", "reason_code"], f"screening_decisions[{idx}]"
        )
        if missing:
            return missing
        if row["decision"] not in {"include", "exclude"}:
            return f"screening_decisions[{idx}].decision must be include|exclude"

    for idx, row in enumerate(data["data_extraction"]):
        if not isinstance(row, dict):
            return f"data_extraction[{idx}] must be an object"
        missing = require_fields(
            row,
            ["study_id", "country", "design", "sample_size", "outcomes"],
            f"data_extraction[{idx}]",
        )
        if missing:
            return missing

    prisma = data["prisma_record"]
    if not isinstance(prisma, dict):
        return "prisma_record must be an object"
    missing = require_fields(
        prisma,
        ["identified", "screened", "eligible", "included"],
        "prisma_record",
    )
    if missing:
        return missing

    for key in ["identified", "screened", "eligible", "included"]:
        if not isinstance(prisma[key], int) or prisma[key] < 0:
            return f"prisma_record.{key} must be a non-negative integer"

    if not (
        prisma["identified"]
        >= prisma["screened"]
        >= prisma["eligible"]
        >= prisma["included"]
    ):
        return "prisma_record counts must be monotonic: identified>=screened>=eligible>=included"

    agreement = data["agreement"]
    if not isinstance(agreement, dict):
        return "agreement must be an object"
    missing = require_fields(agreement, ["metric", "value", "threshold"], "agreement")
    if missing:
        return missing
    if not isinstance(agreement["value"], (int, float)) or not isinstance(
        agreement["threshold"], (int, float)
    ):
        return "agreement value/threshold must be numeric"
    if agreement["value"] < agreement["threshold"]:
        return "dual-reviewer agreement below threshold"

    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate SLR artifact quality payload"
    )
    parser.add_argument("--input", required=True, help="Path to SLR artifact JSON")
    args = parser.parse_args()

    path = pathlib.Path(args.input)
    if not path.exists():
        return fail(f"input not found: {path}")

    try:
        data = load_json(path)
    except Exception as exc:  # pragma: no cover - defensive parse handling
        return fail(f"invalid JSON: {exc}")

    problem = validate(data)
    if problem:
        return fail(problem)

    return ok("SLR artifact set is compliant")


if __name__ == "__main__":
    raise SystemExit(main())
