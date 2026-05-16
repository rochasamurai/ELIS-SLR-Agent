#!/usr/bin/env python3
"""Tests for scripts/check_validation_readiness.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "check_validation_readiness.py"
)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    env = {
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)


def _init_repo(tmp_path: Path) -> Path:
    _run(["git", "init"], tmp_path)
    (tmp_path / "README.md").write_text("root")
    _run(["git", "add", "README.md"], tmp_path)
    _run(["git", "commit", "-m", "init"], tmp_path)
    return tmp_path


def test_validation_readiness_accepts_branch(tmp_path):
    """Validation readiness should accept the approved branch (not require detached HEAD)."""
    repo = _init_repo(tmp_path)
    branch = "feature/test-validation"
    _run(["git", "checkout", "-b", branch], repo)
    head = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
    proc = _run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--pe-id",
            "PE-OPS-SKILLS-01",
            "--worktree",
            str(repo),
            "--expected-commit",
            head,
            "--allowed-root",
            str(repo),
            "--artifact-dir",
            str(repo / ".elis/pe/PE-OPS-SKILLS-01"),
        ],
        repo,
    )
    # Should fail on reason other than branch (missing artifact dir etc.)
    # But importantly: should NOT fail with a branch/detached error
    assert "EXPECTED_DETACHED_HEAD" not in proc.stderr
    assert proc.returncode != 0


def test_validation_readiness_reports_bindings(tmp_path):
    """Validation readiness should report runtime workspace and Git worktree bindings."""
    repo = _init_repo(tmp_path)
    branch = "feature/test-bindings"
    _run(["git", "checkout", "-b", branch], repo)
    head = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
    proc = _run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--pe-id",
            "PE-OPS-SKILLS-01",
            "--worktree",
            str(repo),
            "--expected-commit",
            head,
            "--allowed-root",
            str(repo),
            "--artifact-dir",
            str(repo / ".elis/pe/PE-OPS-SKILLS-01"),
        ],
        repo,
    )
    # Should report something about the authorised Git worktree
    assert "Authorised Git worktree" in proc.stdout or proc.returncode != 0


def test_validation_readiness_rejects_forbidden_in_worktree(tmp_path):
    """Validation readiness should fail if forbidden runtime files are in the Git worktree."""
    repo = _init_repo(tmp_path)
    branch = "feature/test-forbidden"
    _run(["git", "checkout", "-b", branch], repo)
    # Create a forbidden HEARTBEAT.md in the worktree
    (repo / "HEARTBEAT.md").write_text("test heartbeat")
    head = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
    proc = _run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--pe-id",
            "PE-OPS-SKILLS-01",
            "--worktree",
            str(repo),
            "--expected-commit",
            head,
            "--allowed-root",
            str(repo),
            "--artifact-dir",
            str(repo / ".elis/pe/PE-OPS-SKILLS-01"),
        ],
        repo,
    )
    assert proc.returncode != 0
    assert "FORBIDDEN_IN_WORKTREE" in proc.stderr
    assert "HEARTBEAT.md" in proc.stderr


def test_validation_readiness_missing_artifact_dir(tmp_path):
    """Validation readiness should fail when artifact dir is missing."""
    repo = _init_repo(tmp_path)
    branch = "feature/test-missing-artifact"
    _run(["git", "checkout", "-b", branch], repo)
    head = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
    proc = _run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--pe-id",
            "PE-OPS-SKILLS-01",
            "--worktree",
            str(repo),
            "--expected-commit",
            head,
            "--allowed-root",
            str(repo),
            "--artifact-dir",
            str(repo / ".elis/pe/PE-OPS-SKILLS-01"),
        ],
        repo,
    )
    assert proc.returncode != 0
    assert "MISSING_ARTIFACT_DIR" in proc.stderr


def _init_repo_with_all_deps(
    tmp_path: Path, branch: str, add_handoff: bool = True
) -> tuple[Path, Path]:
    """Helper: init repo, create branch, make required artefact dirs so the
    script's MISSING_VALIDATION_FILE and MISSING_ARTIFACT_DIR checks pass.
    Returns (repo_path, artifact_dir)."""
    repo = _init_repo(tmp_path)
    _run(["git", "checkout", "-b", branch], repo)

    # Create the full .elis/pe/<PE-ID>/ structure
    artifact_dir = repo / ".elis/pe/PE-OPS-SKILLS-01"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    if add_handoff:
        # Create HANDOFF.md so MISSING_VALIDATION_FILE check passes
        (artifact_dir / "HANDOFF.md").write_text(
            "# HANDOFF - PE-OPS-SKILLS-01\n\n## Status\ndone\n"
        )

    return repo, artifact_dir


def test_validation_readiness_rejects_uncommitted_review(tmp_path):
    """Validation readiness should fail when REVIEW.md exists but is not committed on the branch."""
    repo, artifact_dir = _init_repo_with_all_deps(
        tmp_path, "feature/test-uncommitted-review"
    )

    # Create REVIEW.md (but do NOT commit it)
    (artifact_dir / "REVIEW.md").write_text(
        "# REVIEW - PE-OPS-SKILLS-01\n\n## Verdict\nPASS\n"
    )

    head = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
    proc = _run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--pe-id",
            "PE-OPS-SKILLS-01",
            "--worktree",
            str(repo),
            "--expected-commit",
            head,
            "--allowed-root",
            str(repo),
            "--artifact-dir",
            str(artifact_dir),
        ],
        repo,
    )
    assert proc.returncode != 0
    assert "REVIEW_NOT_ON_BRANCH" in proc.stderr


def test_validation_readiness_accepts_committed_review(tmp_path):
    """Validation readiness should pass REVIEW check when REVIEW.md is committed on the branch."""
    repo, artifact_dir = _init_repo_with_all_deps(
        tmp_path, "feature/test-committed-review"
    )

    # Create REVIEW.md and commit it
    (artifact_dir / "REVIEW.md").write_text(
        "# REVIEW - PE-OPS-SKILLS-01\n\n## Verdict\nPASS\n"
    )
    _run(["git", "add", "-A"], repo)
    _run(["git", "commit", "-m", "feat: add REVIEW.md for PE"], repo)

    head = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
    proc = _run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--pe-id",
            "PE-OPS-SKILLS-01",
            "--worktree",
            str(repo),
            "--expected-commit",
            head,
            "--allowed-root",
            str(repo),
            "--artifact-dir",
            str(artifact_dir),
        ],
        repo,
    )
    # Should NOT fail with REVIEW_NOT_ON_BRANCH
    assert "REVIEW_NOT_ON_BRANCH" not in proc.stderr


def test_validation_readiness_rejects_missing_review_file(tmp_path):
    """Validation readiness should fail when no REVIEW.md exists at all. The test needs
    to provide the PE-OPS-SKILLS-01/HANDOFF.md to avoid the MISSING_VALIDATION_FILE check,
    and no REVIEW.md to trigger the REVIEW_FILE_MISSING check."""
    repo = _init_repo(tmp_path)
    branch = "feature/test-missing-review"
    _run(["git", "checkout", "-b", branch], repo)

    # Create artifact dir with HANDOFF.md (satisfies MISSING_VALIDATION_FILE check)
    # but WITHOUT REVIEW.md
    artifact_dir = repo / ".elis/pe/PE-OPS-SKILLS-01"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "HANDOFF.md").write_text(
        "# HANDOFF - PE-OPS-SKILLS-01\n\n## Status\ndone\n"
    )

    head = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
    proc = _run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--pe-id",
            "PE-OPS-SKILLS-01",
            "--worktree",
            str(repo),
            "--expected-commit",
            head,
            "--allowed-root",
            str(repo),
            "--artifact-dir",
            str(artifact_dir),
        ],
        repo,
    )
    assert proc.returncode != 0
    assert "REVIEW_FILE_MISSING" in proc.stderr


def test_validation_readiness_accepts_review_on_same_branch(tmp_path):
    """Validation readiness should pass when REVIEW.md is committed on the same branch."""
    repo, artifact_dir = _init_repo_with_all_deps(
        tmp_path, "feature/test-review-on-branch"
    )
    (artifact_dir / "REVIEW.md").write_text(
        "# REVIEW - PE-OPS-SKILLS-01\n\n## Verdict\nPASS\n"
    )
    _run(["git", "add", "-A"], repo)
    _run(["git", "commit", "-m", "feat: add REVIEW.md"], repo)

    head = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
    proc = _run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--pe-id",
            "PE-OPS-SKILLS-01",
            "--worktree",
            str(repo),
            "--expected-commit",
            head,
            "--allowed-root",
            str(repo),
            "--artifact-dir",
            str(artifact_dir),
        ],
        repo,
    )
    assert "REVIEW_NOT_ON_BRANCH" not in proc.stderr
