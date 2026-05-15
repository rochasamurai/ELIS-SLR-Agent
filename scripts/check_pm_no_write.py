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


class PMWriteViolation(Exception):
    """Raised when a PM-authored write to a disallowed path is detected."""
    def __init__(self, file_path: str, commit_sha: str = "", author: str = ""):
        self.file_path = file_path
        self.commit_sha = commit_sha
        self.author = author
        msg_parts = [f"PM_WROTE_FILE: {file_path}"]
        if commit_sha:
            msg_parts.append(f"in commit {commit_sha[:12]}")
        if author:
            msg_parts.append(f"by {author}")
        super().__init__(" ".join(msg_parts))


class PMWriteCheckError(Exception):
    """Raised when the check itself encounters an error (e.g. git failure)."""


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


def check_violations(repo: Path, pe_range: str, pe_id: str) -> list[PMWriteViolation]:
    """Check for PM write violations and return a list of violations found."""
    violations: list[PMWriteViolation] = []

    # 1. If pe_range given, check commit authors in that range
    if pe_range:
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
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            sha, author_info = parts
            author_lower = author_info.lower()
            # PM commit detection: contains "pm" but not impl/val/infra/gha/e2e/prog/slr/arch
            non_pm_prefixes = [
                "infra-impl", "infra-val",
                "prog-impl", "prog-val",
                "slr-impl", "slr-val",
                "gha-impl", "gha-val",
                "e2e-impl", "e2e-val",
                "arch-impl", "arch-val",
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
                    violations.append(
                        PMWriteViolation(fpath, sha, author_info)
                    )

    # 2. Check files per PE evidence directory
    pe_dir = repo / ".elis" / "pe" / pe_id
    if pe_dir.exists():
        for f in pe_dir.rglob("*"):
            if not f.is_file():
                continue
            if f.name == "PE_TASK.md":
                continue
            if f.name == "HANDOFF.md":
                if _pm_authored_file(str(f.relative_to(repo)), repo, pe_range):
                    violations.append(
                        PMWriteViolation(str(f.relative_to(repo)))
                    )

    return violations


def main() -> int:
    p = argparse.ArgumentParser(description="Check PM has not written disallowed files")
    p.add_argument("--repo", default=".")
    p.add_argument("--pe-range", help="Git range (e.g. base..HEAD) to check")
    p.add_argument("--pe-id", required=True)
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    pe_range = args.pe_range or "HEAD~1..HEAD"

    violations = check_violations(repo, pe_range, args.pe_id)

    for v in violations:
        print(str(v), file=sys.stderr)

    if violations:
        print(f"PM_WRITE_VIOLATIONS_FOUND: {len(violations)} violation(s) detected",
              file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())