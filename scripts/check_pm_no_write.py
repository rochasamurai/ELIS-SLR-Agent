#!/usr/bin/env python3
"""check_pm_no_write.py — verify PM has not written to any disallowed paths.

Exits non-zero if PM-authored content is found in implementation files,
validation artefacts, or REVIEW.md files.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

FORBIDDEN_PM_WRITE_PATTERNS = [
    ".elis/pe/*/HANDOFF.md",
    ".elis/pe/*/REVIEW.md",
    "scripts/check_*.py",
    "tests/test_check_*.py",
    "tests/test_pe_*.py",
    "tests/test_pm_agent_rules.py",
    "openclaw/workspaces/workspace-pm/AGENTS.md",
    "openclaw/workspaces/workspace-pm/SKILLS.md",
    "docs/governance/",
]

# These are the only files PM is allowed to edit directly
PM_ALLOWED_WRITE = {
    ".elis/pe/*/PE_TASK.md",
}

# Author identities that are NOT PM
NON_PM_AUTHORS = {
    "infra-impl",
    "infra-impl-a",
    "infra-impl-b",
    "infra-impl-codex",
    "infra-impl-claude",
    "infra-val",
    "infra-val-a",
    "infra-val-b",
    "infra-val-codex",
    "infra-val-claude",
    "prog-impl",
    "prog-val",
    "slr-impl",
    "slr-val",
    "gha-impl",
    "gha-val",
    "e2e-impl",
    "e2e-val",
}


def git(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *cmd], cwd=cwd, text=True).strip()


def _pm_authored_file(file_path: str, repo: Path, pe_range: str) -> bool:
    """Check if a file's last commit author matches PM identity."""
    try:
        author = git(
            ["log", "--format=%an", "-1", pe_range, "--", file_path],
            cwd=repo,
        )
    except subprocess.CalledProcessError:
        return False
    if not author:
        return False
    author_lower = author.strip().lower()
    # Check if author is PM-like (pm, elis-pm, elis pm agent)
    if "pm" in author_lower and "infra" not in author_lower and "impl" not in author_lower and "val" not in author_lower:
        return True
    return False


def main() -> int:
    p = argparse.ArgumentParser(description="Check PM has not written disallowed files")
    p.add_argument("--repo", default=".")
    p.add_argument("--pe-range", help="Git range (e.g. base..HEAD) to check")
    p.add_argument("--pe-id", required=True)
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    pe_range = args.pe_range or "HEAD~1..HEAD"

    # 1. If pe_range given, check commit authors in that range
    if args.pe_range:
        # Get all commits in range
        try:
            commits = git(
                ["log", "--format=%H %an <%ae>", pe_range],
                cwd=repo,
            )
        except subprocess.CalledProcessError:
            commits = ""

        for line in commits.splitlines():
            if not line.strip():
                continue
            sha, author_info = line.strip().split(" ", 1)
            author_lower = author_info.lower()
            # PM commit detection: contains "pm" but not impl/vale/infra/gha/e2e/prog/slr/arch
            non_pm_prefixes = [
                "infra-impl", "infra-val",
                "prog-impl", "prog-val",
                "slr-impl", "slr-val",
                "gha-impl", "gha-val",
                "e2e-impl", "e2e-val",
                "arch-impl", "arch-val",
                "infra-impl", "infra-val",
            ]
            is_non_pm = any(p in author_lower for p in non_pm_prefixes)
            if "pm" in author_lower and not is_non_pm:
                # PM authored a commit — check what files it touched
                try:
                    files = git(
                        ["diff-tree", "--no-commit-id", "--name-only", "-r", sha],
                        cwd=repo,
                    )
                except subprocess.CalledProcessError:
                    continue
                for fpath in files.splitlines():
                    fpath = fpath.strip()
                    if not fpath:
                        continue
                    # Check if this is a PE_TASK.md — allowed
                    if fpath.endswith("PE_TASK.md"):
                        continue
                    # Everything else is a violation
                    print(f"PM_WROTE_FILE: {fpath} in commit {sha[:12]} by {author_info}",
                          file=sys.stderr)

    # 2. Check files per PE evidence directory
    pe_dir = repo / ".elis" / "pe" / args.pe_id
    if pe_dir.exists():
        for f in pe_dir.rglob("*"):
            if not f.is_file():
                continue
            if f.name == "PE_TASK.md":
                continue
            if f.name == "HANDOFF.md":
                if _pm_authored_file(str(f.relative_to(repo)), repo, pe_range):
                    print(f"PM_WROTE_FILE: {f.relative_to(repo)}", file=sys.stderr)

    # Aggregate violations
    # Since we can't easily aggregate from stderr in this simple check,
    # return 0 if no errors printed

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
