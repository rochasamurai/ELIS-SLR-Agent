#!/usr/bin/env python3
"""
AGENTS.md compliance checks for PRs targeting release/2.0.

This enforces structural rules that can be validated automatically.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ALLOWED_BRANCH_PATTERNS = (
    r"^feature/pe[0-9]+[a-z]?-[-a-z0-9]+$",
    r"^hotfix/pe[0-9]+[a-z]?-[-a-z0-9]+$",
    r"^chore/[-a-z0-9]+$",
)


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def git_changed_files(base_ref: str) -> list[str]:
    # 3-dot comparison reflects PR diff against merge-base.
    out = run(["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"])
    if not out:
        return []
    return [
        line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()
    ]


def branch_matches_allowed(head_ref: str) -> bool:
    return any(re.match(pattern, head_ref) for pattern in ALLOWED_BRANCH_PATTERNS)


def extract_pe_id(head_ref: str) -> str | None:
    m = re.match(r"^(?:feature|hotfix)/pe([0-9]+[a-z]?)-", head_ref)
    return m.group(1) if m else None


def check_repo_prereqs() -> list[str]:
    errors: list[str] = []
    required_refs = [
        "AGENTS.md",
        "docs/_active/RELEASE_PLAN_v2.0.md",
        "docs/_active/INTEGRATION_PLAN_V2.md",
        "docs/_active/HARVEST_TEST_PLAN.md",
    ]
    for path in required_refs:
        if not Path(path).exists():
            errors.append(f"Missing canonical reference file: {path}")
    return errors


def check_pr_rules(
    base_ref: str, head_ref: str, changed_files: list[str]
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if base_ref != "release/2.0":
        errors.append(
            f"PR base must be 'release/2.0' per AGENTS.md. Found base='{base_ref}'."
        )

    if not branch_matches_allowed(head_ref):
        errors.append(
            "Head branch name does not match AGENTS.md patterns: "
            "feature/pe<id>-<scope>, hotfix/pe<id>-<scope>, or chore/<topic>."
        )

    pe_id = extract_pe_id(head_ref)
    if pe_id:
        if not Path("HANDOFF.md").exists():
            errors.append("PE branch must contain HANDOFF.md in branch head.")
        if "HANDOFF.md" not in changed_files:
            errors.append(
                "PE branch PR diff must include HANDOFF.md (must be committed before PR/open updates)."
            )

        # Prevent obvious cross-PE review contamination.
        for file in changed_files:
            m = re.match(r"^REVIEW_PE([0-9]+[a-z]?)\.md$", file)
            if m and m.group(1) != pe_id:
                errors.append(
                    f"Cross-PE contamination: {file} does not match branch PE id pe{pe_id}."
                )

    if head_ref.startswith("chore/"):
        if any(p.startswith("elis/") for p in changed_files):
            warnings.append(
                "Chore branch modifies product code under elis/. Confirm this is intentional."
            )
        if any(
            p.startswith("scripts/") and p != "scripts/agents_compliance_check.py"
            for p in changed_files
        ):
            warnings.append(
                "Chore branch modifies scripts/. Confirm scope is still non-PE housekeeping."
            )

    if not changed_files:
        errors.append("PR has no file changes against base branch.")

    return errors, warnings


def load_pr_event(path: str | None) -> tuple[str, str]:
    if not path:
        raise ValueError("Missing --event-path for pull_request metadata.")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    pr = payload.get("pull_request") or {}
    base = ((pr.get("base") or {}).get("ref")) or payload.get("base_ref")
    head = ((pr.get("head") or {}).get("ref")) or payload.get("head_ref")
    if not base or not head:
        raise ValueError("Could not resolve base/head refs from event payload.")
    return str(base), str(head)


def main() -> int:
    parser = argparse.ArgumentParser(description="AGENTS.md PR compliance checks")
    parser.add_argument(
        "--event-path", default=None, help="Path to GITHUB_EVENT_PATH JSON"
    )
    parser.add_argument("--base-ref", default=None, help="Optional override base ref")
    parser.add_argument("--head-ref", default=None, help="Optional override head ref")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(check_repo_prereqs())

    base_ref = args.base_ref
    head_ref = args.head_ref
    if not base_ref or not head_ref:
        try:
            base_ref, head_ref = load_pr_event(args.event_path)
        except Exception as exc:
            print(f"ERROR: {exc}")
            return 2

    changed = git_changed_files(base_ref)
    pr_errors, pr_warnings = check_pr_rules(base_ref, head_ref, changed)
    errors.extend(pr_errors)
    warnings.extend(pr_warnings)

    print("AGENTS compliance check")
    print(f"- base_ref: {base_ref}")
    print(f"- head_ref: {head_ref}")
    print(f"- changed_files: {len(changed)}")
    for file in changed:
        print(f"  - {file}")

    if warnings:
        print("\nWarnings:")
        for item in warnings:
            print(f"- {item}")

    if errors:
        print("\nBlocking errors:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("\nPASS: AGENTS.md structural compliance checks succeeded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
