"""Check that a PR does not modify only CURRENT_PE.md while a feature-branch
PR for the same PE is already open.

Implements PE-INFRA-SLR-03 AC-7.

Exit codes:
  0  — check passed (no parallel governance PR conflict)
  1  — check failed (parallel governance PR detected)
  2  — check errored (API failure; treated as hard failure to prevent silent pass)

Environment variables expected (set by the calling GitHub Actions step):
  GH_TOKEN   — GitHub token for API calls
  PR_NUMBER  — the PR being checked
  BASE_REF   — target branch of the PR being checked
  HEAD_REF   — source branch of the PR being checked
  REPO       — owner/repo string

PM-CHORE commits to main are exempt: if the source branch is main or starts
with "chore/pm-chore-", the check always passes.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CURRENT_PE_FILE = "CURRENT_PE.md"

# Branches that are always exempt from this check.
EXEMPT_BRANCH_PREFIXES = ("chore/pm-chore-",)


class ApiError(RuntimeError):
    """Raised when the GitHub API returns an unexpected response."""


def _gh_api(path: str) -> dict | list:
    """Call the GitHub API and return parsed JSON.

    Raises ApiError on HTTP error, curl failure, or non-JSON response.
    Uses -f so curl exits non-zero on HTTP 4xx/5xx responses.
    """
    token = os.environ["GH_TOKEN"]
    repo = os.environ["REPO"]
    url = f"https://api.github.com/repos/{repo}/{path}"
    result = subprocess.run(
        [
            "curl",
            "-s",
            "-f",
            "-H",
            f"Authorization: Bearer {token}",
            "-H",
            "Accept: application/vnd.github+json",
            url,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ApiError(
            f"GitHub API call failed (curl exit {result.returncode}) for {url}: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ApiError(
            f"GitHub API returned non-JSON for {url}: {result.stdout[:200]}"
        ) from exc


def get_changed_files(pr_number: str) -> list[str]:
    """Return list of files changed in the given PR.

    Raises ApiError if the API call fails or returns a non-list.
    """
    data = _gh_api(f"pulls/{pr_number}/files?per_page=100")
    if not isinstance(data, list):
        raise ApiError(
            f"Expected list from pulls/{pr_number}/files, got {type(data).__name__}: "
            f"{str(data)[:200]}"
        )
    return [f["filename"] for f in data]


def get_open_prs(base_ref: str) -> list[dict]:
    """Return all open PRs targeting base_ref.

    Raises ApiError if the API call fails or returns a non-list.
    """
    data = _gh_api(f"pulls?state=open&base={base_ref}&per_page=100")
    if not isinstance(data, list):
        raise ApiError(
            f"Expected list from pulls?base={base_ref}, got {type(data).__name__}: "
            f"{str(data)[:200]}"
        )
    return data


def extract_pe_id_from_branch(branch: str) -> str | None:
    """Extract PE-ID from a feature branch name.

    The PE-ID is: 'PE-' followed by one or more letter-only segments, ending
    with a digit-only segment.  Everything after the digit segment is the
    human description and is ignored.

    Examples:
      feature/pe-infra-slr-03-pm-control-...  → PE-INFRA-SLR-03
      feature/pe-infra-01-branch-policy        → PE-INFRA-01
      feature/pe-oc-07-gate-automation         → PE-OC-07
    """
    import re

    # pe + one-or-more letter-segments + one digit-segment + (- or end)
    m = re.match(r"feature/(pe(?:-[a-z]+)+-\d+)(?:-|$)", branch, re.IGNORECASE)
    if not m:
        return None
    return m.group(1).upper()


def extract_pe_id_from_current_pe(content: str) -> str | None:
    """Extract the current active PE-ID from CURRENT_PE.md content."""
    import re

    m = re.search(r"^\|\s*PE\s*\|\s*(PE(?:-[A-Z0-9]+)+)\s*\|", content, re.MULTILINE)
    return m.group(1) if m else None


def main() -> int:
    pr_number = os.environ.get("PR_NUMBER", "")
    base_ref = os.environ.get("BASE_REF", "")
    head_ref = os.environ.get("HEAD_REF", "")

    # Exempt: PM-CHORE branches
    if any(head_ref.startswith(p) for p in EXEMPT_BRANCH_PREFIXES):
        print(f"PASS: branch '{head_ref}' is a PM-CHORE branch — exempt.")
        return 0

    # Get files changed in this PR — hard failure on API error
    try:
        changed = get_changed_files(pr_number)
    except ApiError as exc:
        print(f"ERROR: could not retrieve changed files — {exc}")
        return 2

    # An empty file list when PR_NUMBER is set is unexpected; treat as API error
    if not changed and pr_number:
        print(
            f"ERROR: API returned zero changed files for PR #{pr_number}. "
            "This is unexpected — treating as an API error to prevent silent pass."
        )
        return 2

    # Only trigger if the PR touches CURRENT_PE.md
    if CURRENT_PE_FILE not in changed:
        print(f"PASS: {CURRENT_PE_FILE} not in changed files.")
        return 0

    # If the PR changes files beyond CURRENT_PE.md, it is a feature PR — exempt
    non_governance_files = [f for f in changed if f != CURRENT_PE_FILE]
    if non_governance_files:
        print(
            f"PASS: PR modifies {len(non_governance_files)} non-governance file(s) "
            f"in addition to {CURRENT_PE_FILE} — feature PR, exempt."
        )
        return 0

    # PR modifies ONLY CURRENT_PE.md. Check for an open feature-branch PR for
    # the same PE.
    current_pe_path = REPO_ROOT / CURRENT_PE_FILE
    try:
        current_pe_content = current_pe_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"PASS: {CURRENT_PE_FILE} not found locally — cannot determine PE-ID.")
        return 0

    active_pe_id = extract_pe_id_from_current_pe(current_pe_content)
    if not active_pe_id:
        print(f"PASS: could not extract PE-ID from {CURRENT_PE_FILE}.")
        return 0

    try:
        open_prs = get_open_prs(base_ref)
    except ApiError as exc:
        print(f"ERROR: could not retrieve open PRs — {exc}")
        return 2

    conflicting_prs = []
    for pr in open_prs:
        branch = pr.get("head", {}).get("ref", "")
        pe_id = extract_pe_id_from_branch(branch)
        if pe_id and pe_id == active_pe_id and str(pr.get("number")) != pr_number:
            conflicting_prs.append(pr)

    if conflicting_prs:
        numbers = ", ".join(f"#{p['number']}" for p in conflicting_prs)
        print(
            f"FAIL: This PR modifies only {CURRENT_PE_FILE} but an open feature-branch "
            f"PR for {active_pe_id} already exists ({numbers}). "
            f"PM-CHORE governance updates must be direct commits to main, not PRs. "
            f"Close this PR and commit directly to main instead."
        )
        return 1

    print(f"PASS: no conflicting open feature-branch PR found for {active_pe_id}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
