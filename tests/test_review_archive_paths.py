"""Tests for PE-INFRA-SLR-07 — review archive path resolution.

Verifies AC-4: review-related docs and workflow guidance reference
docs/reviews/archive/, not the repo root.
"""

from __future__ import annotations

from pathlib import Path

from scripts import validator_runner_common as common

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# review_file_path
# ---------------------------------------------------------------------------


def test_review_file_path_includes_archive_dir():
    result = common.review_file_path("PE-AUTO-05")
    assert result == "docs/reviews/archive/REVIEW_PE_AUTO_05.md"


def test_review_file_path_infra_domain():
    result = common.review_file_path("PE-INFRA-SLR-07")
    assert result == "docs/reviews/archive/REVIEW_PE_INFRA_SLR_07.md"


def test_review_file_path_starts_with_archive_prefix():
    result = common.review_file_path("PE-OC-21")
    assert result.startswith("docs/reviews/archive/")


# ---------------------------------------------------------------------------
# No REVIEW_PE*.md at repo root
# ---------------------------------------------------------------------------


def test_no_review_pe_files_at_repo_root():
    root_review_files = list(REPO_ROOT.glob("REVIEW_PE*.md"))
    assert root_review_files == [], (
        f"Found REVIEW_PE*.md at repo root (should be in docs/reviews/archive/): "
        f"{[f.name for f in root_review_files]}"
    )


# ---------------------------------------------------------------------------
# Workflow files reference archive path, not bare REVIEW_*.md
# ---------------------------------------------------------------------------


def _workflow_content(name: str) -> str:
    return (REPO_ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")


def test_ci_yml_references_archive_path():
    content = _workflow_content("ci.yml")
    assert "docs/reviews/archive/REVIEW_*.md" in content
    # The old bare pathspec must not appear in a git diff context
    assert "-- 'REVIEW_*.md'" not in content


def test_auto_merge_references_archive_path():
    content = _workflow_content("auto-merge-on-pass.yml")
    assert "docs/reviews/archive/REVIEW_*.md" in content
    assert "-- 'REVIEW_*.md'" not in content


def test_validator_runner_references_archive_path():
    content = _workflow_content("validator-runner.yml")
    assert "docs/reviews/archive/REVIEW_" in content


# ---------------------------------------------------------------------------
# AGENTS.md references archive path in step commands
# ---------------------------------------------------------------------------


def test_agents_md_check_review_command_uses_archive_path():
    content = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "REVIEW_FILE=docs/reviews/archive/REVIEW_PE<N>.md" in content


# ---------------------------------------------------------------------------
# docs/reviews/README.md pointer is not stale
# ---------------------------------------------------------------------------


def test_review_index_pointer_exists_in_archive():
    readme = (REPO_ROOT / "docs" / "reviews" / "README.md").read_text(encoding="utf-8")
    # Extract the archive/<filename> from the README
    import re

    match = re.search(r"archive/(REVIEW_[^\s`]+\.md)", readme)
    assert match is not None, "README.md must reference a file in archive/"
    pointed_file = REPO_ROOT / "docs" / "reviews" / "archive" / match.group(1)
    assert (
        pointed_file.exists()
    ), f"README.md points to {match.group(1)} but that file does not exist in archive/"
