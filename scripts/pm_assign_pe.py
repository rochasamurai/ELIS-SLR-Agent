#!/usr/bin/env python
"""PM Agent PE assignment script.

Reads the Active PE Registry in CURRENT_PE.md, applies the alternation rule,
writes the new registry row, and creates the feature branch on the remote.

Usage:
    python scripts/pm_assign_pe.py \\
        --domain <domain> \\
        --pe <pe-id> \\
        [--description <text>] \\
        [--dry-run] \\
        [--current-pe <path>]

Examples:
    python scripts/pm_assign_pe.py --domain programs --pe PE-PROG-08 \\
        --description "PDF export" --dry-run
"""

from __future__ import annotations

import argparse
import datetime
import os
import pathlib
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Registry parsing (mirrored from scripts/check_role_registration.py)
# ---------------------------------------------------------------------------

VALID_STATUSES = {
    "planning",
    "implementing",
    "gate-1-pending",
    "validating",
    "gate-2-pending",
    "merged",
    "blocked",
}


def parse_active_registry(
    content: str,
) -> tuple[list[str], list[dict[str, str]]] | tuple[None, None]:
    lines = content.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == "## active pe registry":
            start = idx + 1
            break
    if start is None:
        return None, None

    table_lines: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            if table_lines:
                break
            continue
        if stripped.startswith("|"):
            table_lines.append(stripped)
            continue
        if table_lines:
            break

    if len(table_lines) < 3:
        return None, None

    header = [part.strip().lower() for part in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for row_line in table_lines[2:]:
        parts = [part.strip() for part in row_line.strip("|").split("|")]
        if len(parts) != len(header):
            return None, None
        rows.append(dict(zip(header, parts)))
    return header, rows


def extract_engine(agent_id: str) -> str | None:
    text = agent_id.strip().lower()
    if "codex" in text:
        return "codex"
    if "claude" in text:
        return "claude"
    return None


# ---------------------------------------------------------------------------
# Domain → agent-ID prefix mapping
# ---------------------------------------------------------------------------

DOMAIN_PREFIX: dict[str, str] = {
    "infra": "infra",
    "openclaw-infra": "prog",
    "programs": "prog",
    "slr": "slr",
}


def agent_prefix(domain: str) -> str:
    return DOMAIN_PREFIX.get(domain.lower(), domain.split("-")[0])


# ---------------------------------------------------------------------------
# Core alternation logic
# ---------------------------------------------------------------------------


def determine_engine(rows: list[dict[str, str]], domain: str) -> tuple[str, str | None]:
    """Return (new_engine, prev_engine) for the given domain.

    Scans all registry rows (any status) in order; the last row matching the
    domain determines the previous implementer engine.  If no prior row exists
    for the domain the first PE defaults to ``"codex"``.
    """
    prev_engine: str | None = None
    for row in rows:
        if row.get("domain", "").strip().lower() == domain.lower():
            engine = extract_engine(row.get("implementer-agentid", ""))
            if engine is not None:
                prev_engine = engine

    if prev_engine is None:
        return "codex", None

    new_engine = "claude" if prev_engine == "codex" else "codex"
    return new_engine, prev_engine


# ---------------------------------------------------------------------------
# Branch naming
# ---------------------------------------------------------------------------


def slug(description: str) -> str:
    s = description.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def make_branch_name(pe_id: str, description: str) -> str:
    base = f"feature/{pe_id.lower()}"
    if description:
        return f"{base}-{slug(description)}"
    return base


# ---------------------------------------------------------------------------
# Registry row construction
# ---------------------------------------------------------------------------


def make_registry_row(
    pe_id: str, domain: str, engine: str, branch: str, date: str
) -> str:
    prefix = agent_prefix(domain)
    other = "claude" if engine == "codex" else "codex"
    impl = f"{prefix}-impl-{engine}"
    val = f"{prefix}-val-{other}"
    return (
        f"| {pe_id:<11} | {domain:<15} | {impl:<19} | {val:<17}"
        f" | {branch:<54} | planning     | {date}   |"
    )


# ---------------------------------------------------------------------------
# CURRENT_PE.md in-place update
# ---------------------------------------------------------------------------


def insert_registry_row(content: str, new_row: str) -> str:
    """Return updated content with new_row appended inside the registry table."""
    lines = content.splitlines(keepends=True)
    in_registry = False
    last_table_idx: int | None = None

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower() == "## active pe registry":
            in_registry = True
            continue
        if in_registry:
            if stripped.startswith("|"):
                last_table_idx = idx
            elif last_table_idx is not None and not stripped.startswith("|"):
                break

    if last_table_idx is None:
        raise ValueError("Active PE Registry table not found in CURRENT_PE.md")

    lines.insert(last_table_idx + 1, new_row + "\n")
    return "".join(lines)


def get_base_branch(content: str) -> str:
    m = re.search(r"\|\s*Base branch\s*\|\s*([^|]+?)\s*\|", content)
    if m:
        return m.group(1).strip().strip("`")
    return "main"


# ---------------------------------------------------------------------------
# Git branch creation
# ---------------------------------------------------------------------------


def create_git_branch(branch: str, base_branch: str, repo_root: pathlib.Path) -> None:
    subprocess.run(
        ["git", "fetch", "origin", base_branch],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "push", "origin", f"origin/{base_branch}:refs/heads/{branch}"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assign a new PE to the Active PE Registry with alternation enforcement"
    )
    parser.add_argument(
        "--domain", required=True, help="PE domain (e.g. programs, infra)"
    )
    parser.add_argument("--pe", required=True, help="New PE ID (e.g. PE-PROG-08)")
    parser.add_argument(
        "--description", default="", help="Short description for branch slug"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without modifying files or creating branch",
    )
    parser.add_argument(
        "--current-pe",
        default=os.environ.get("CURRENT_PE_PATH", "CURRENT_PE.md"),
        help="Path to CURRENT_PE.md (default: CURRENT_PE_PATH env var or CURRENT_PE.md)",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.current_pe)
    if not path.exists():
        print(f"ERROR: {path} not found")
        return 1

    content = path.read_text(encoding="utf-8")
    _header, rows = parse_active_registry(content)
    if rows is None:
        print("ERROR: Active PE Registry table missing or malformed")
        return 1

    existing_ids = {r.get("pe-id", "").strip().lower() for r in rows}
    if args.pe.lower() in existing_ids:
        print(f"ERROR: PE '{args.pe}' already exists in the Active PE Registry")
        return 1

    new_engine, prev_engine = determine_engine(rows, args.domain)

    if prev_engine is not None:
        assert new_engine != prev_engine, (
            f"Alternation violation: domain '{args.domain}' previous implementer was "
            f"'{prev_engine}'; assigning '{new_engine}' would repeat the same engine."
        )

    base_branch = get_base_branch(content)
    branch = make_branch_name(args.pe, args.description)
    date = datetime.date.today().isoformat()
    new_row = make_registry_row(args.pe, args.domain, new_engine, branch, date)

    prefix = agent_prefix(args.domain)
    other_engine = "claude" if new_engine == "codex" else "codex"
    impl_id = f"{prefix}-impl-{new_engine}"
    val_id = f"{prefix}-val-{other_engine}"

    print(f"{args.pe.upper()} assigned.")
    print(f"Domain: {args.domain}")
    print(f"Implementer: {new_engine.upper()} ({impl_id})")
    print(f"Validator: {other_engine.upper()} ({val_id})")
    print(f"Branch: {branch}")
    print("Status: planning")

    if args.dry_run:
        print("[dry-run] CURRENT_PE.md would be updated (row appended).")
        print(f"[dry-run] Git branch '{branch}' would be created from '{base_branch}'.")
        return 0

    updated = insert_registry_row(content, new_row)
    path.write_text(updated, encoding="utf-8")
    print("CURRENT_PE.md updated.")

    repo_root = path.resolve().parent
    try:
        create_git_branch(branch, base_branch, repo_root)
        print(f"Branch '{branch}' created from '{base_branch}'.")
    except subprocess.CalledProcessError as exc:
        print(f"WARNING: Branch creation failed: {exc}")
        print("CURRENT_PE.md updated; create branch manually.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
