#!/usr/bin/env python3
"""check_review_artifact.py — validate REVIEW file path and authorship.

Ensures REVIEW.md is at the correct PE path and was not authored by
the implementer, PM, or GitHub/Gateway agent.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _git_blame(path: Path, repo: Path) -> tuple[str | None, str | None]:
    """Return (author_name, author_email) for the last commit touching path."""
    try:
        out = subprocess.check_output(
            ["git", "blame", "--porcelain", "-l", str(path)],
            cwd=repo,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None, None
    author = email = None
    for line in out.splitlines():
        if line.startswith("author "):
            author = line[len("author "):]
        elif line.startswith("author-mail "):
            email = line[len("author-mail "):].strip("<>")
        if author and email:
            break
    return author, email


def main() -> int:
    p = argparse.ArgumentParser(description="Check REVIEW file artifact")
    p.add_argument("--repo", default=".")
    p.add_argument("--pe-id", required=True)
    p.add_argument("--implementer-id", default="infra-impl")
    p.add_argument("--forbidden-authors", nargs="*", default=[])
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    review_path = repo / ".elis" / "pe" / args.pe_id / "REVIEW.md"

    if not review_path.exists():
        print("MISSING_REVIEW", file=sys.stderr)
        return 1

    # Check path convention
    expected = repo / ".elis" / "pe" / args.pe_id / "REVIEW.md"
    if review_path.resolve() != expected.resolve():
        print(f"WRONG_REVIEW_PATH: {review_path}", file=sys.stderr)
        return 2

    # Check authorship
    author, email = _git_blame(review_path, repo)
    if author is None:
        print("UNKNOWN_REVIEW_AUTHORSHIP", file=sys.stderr)
        return 3

    forbidden = list(args.forbidden_authors)
    forbidden.append("infra-impl")
    forbidden.append("infra-impl-codex")
    forbidden.append("infra-impl-claude")
    forbidden.append("infra-impl-a")
    forbidden.append("infra-impl-b")
    forbidden.append("pm")

    # Match against forbidden ID prefixes
    for f in forbidden:
        if f.lower() in author.lower():
            print(f"FORBIDDEN_REVIEW_AUTHOR: {author} (matches {f})", file=sys.stderr)
            return 4

    print(f"REVIEW_OK author={author} path={review_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
