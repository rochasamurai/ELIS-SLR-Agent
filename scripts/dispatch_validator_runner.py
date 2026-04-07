"""Resolve CURRENT_PE.md into workflow_dispatch inputs for PE-AUTO-05.

Called by validator-dispatch.yml when the Gate 1 assignment comment is detected.
Reads CURRENT_PE.md from the base branch (main) and verifies that the PR's head
branch matches the active PE branch before dispatching.

Environment variables:
  PR_NUMBER      — pull request number (required, from github.event.issue.number)
  CURRENT_PE_PATH — override path to CURRENT_PE.md (default: ``CURRENT_PE.md``)
  GITHUB_OUTPUT  — GitHub Actions output file path (written if set)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from scripts.implementer_runner_common import RunnerError, parse_current_pe


def _pr_head_branch(pr_number: str) -> str:
    """Return the head branch name for the given PR number via gh CLI."""
    result = subprocess.run(
        ["gh", "pr", "view", pr_number, "--json", "headRefName"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise RunnerError(result.stderr.strip() or "gh pr view failed.")
    match = re.search(r'"headRefName"\s*:\s*"([^"]+)"', result.stdout)
    if match is None:
        raise RunnerError("Could not parse headRefName from gh pr view output.")
    return match.group(1)


def main() -> int:
    try:
        pr_number = os.environ.get("PR_NUMBER", "").strip()
        if not pr_number:
            print("FAIL: PR_NUMBER env var is not set.", file=sys.stderr)
            return 1

        current_pe_path = Path(os.environ.get("CURRENT_PE_PATH", "CURRENT_PE.md"))
        context = parse_current_pe(current_pe_path)

        pr_branch = _pr_head_branch(pr_number)
        should_dispatch = pr_branch == context.branch

        lines = [
            f"should_dispatch={'true' if should_dispatch else 'false'}",
            f"pe_id={context.pe_id}",
            f"branch={context.branch}",
            f"engine={context.validator_engine}",
            f"plan_file={context.plan_file}",
            f"base_branch={context.base_branch}",
            f"pr_number={pr_number}",
        ]

        output_path = os.environ.get("GITHUB_OUTPUT")
        if output_path:
            with open(output_path, "a", encoding="utf-8") as handle:
                handle.write("\n".join(lines) + "\n")
        else:
            print("\n".join(lines))

        if not should_dispatch:
            print(
                f"PR #{pr_number} branch '{pr_branch}' does not match active PE "
                f"branch '{context.branch}' — skipping dispatch.",
                file=sys.stderr,
            )
        return 0
    except RunnerError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
