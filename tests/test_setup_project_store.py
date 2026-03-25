"""Tests for scripts/setup_project_store.py and scripts/check_project_store_layout.py"""

from __future__ import annotations


from scripts import check_project_store_layout as cpl
from scripts import setup_project_store as sps


# ---------------------------------------------------------------------------
# setup_project_store — create_project_store
# ---------------------------------------------------------------------------


def test_create_builds_canonical_layout(tmp_path):
    rc = sps.create_project_store("test-review", "Test Review", "TBD", tmp_path)
    assert rc == 0
    store = tmp_path / "test-review"
    assert store.is_dir()
    assert (store / "MANIFEST.md").is_file()
    for subdir in sps.PHASE_SUBDIRS:
        assert (store / subdir).is_dir()


def test_create_manifest_contains_review_id(tmp_path):
    sps.create_project_store("my-slr-2026", "My SLR", "TBD", tmp_path)
    manifest = (tmp_path / "my-slr-2026" / "MANIFEST.md").read_text(encoding="utf-8")
    assert "my-slr-2026" in manifest
    assert "My SLR" in manifest


def test_create_is_idempotent(tmp_path):
    rc1 = sps.create_project_store("idempotent-review", "Title", "TBD", tmp_path)
    rc2 = sps.create_project_store("idempotent-review", "Title", "TBD", tmp_path)
    assert rc1 == 0
    assert rc2 == 0
    # MANIFEST.md should only be written once
    manifest = (tmp_path / "idempotent-review" / "MANIFEST.md").read_text(
        encoding="utf-8"
    )
    assert manifest.count("review_id:") == 1


def test_create_manifest_not_overwritten_on_rerun(tmp_path):
    sps.create_project_store("stable-review", "Original Title", "TBD", tmp_path)
    # Manually edit the manifest
    manifest_path = tmp_path / "stable-review" / "MANIFEST.md"
    manifest_path.write_text("# Custom content", encoding="utf-8")
    # Re-run should not overwrite
    sps.create_project_store("stable-review", "New Title", "TBD", tmp_path)
    assert manifest_path.read_text(encoding="utf-8") == "# Custom content"


def test_create_rejects_invalid_review_id(tmp_path):
    rc = sps.create_project_store("invalid id!", "Title", "TBD", tmp_path)
    assert rc == 1


def test_create_rejects_uppercase_review_id(tmp_path):
    rc = sps.create_project_store("My-Review", "Title", "TBD", tmp_path)
    assert rc == 1


def test_create_rejects_mixed_case_review_id(tmp_path):
    rc = sps.create_project_store("SLR2026", "Title", "TBD", tmp_path)
    assert rc == 1


def test_create_all_five_phase_subdirs(tmp_path):
    sps.create_project_store("phase-check", "Title", "TBD", tmp_path)
    store = tmp_path / "phase-check"
    for phase in ["harvest", "screen", "extract", "synth", "prisma"]:
        assert (store / phase).is_dir(), f"Missing phase dir: {phase}"


# ---------------------------------------------------------------------------
# check_project_store_layout — check_project_store
# ---------------------------------------------------------------------------


def test_check_passes_valid_store(tmp_path):
    sps.create_project_store("valid-store", "Title", "TBD", tmp_path)
    errors = cpl.check_project_store(tmp_path / "valid-store")
    assert errors == []


def test_check_fails_missing_manifest(tmp_path):
    store = tmp_path / "no-manifest"
    store.mkdir()
    for phase in cpl.REQUIRED_SUBDIRS:
        (store / phase).mkdir()
    errors = cpl.check_project_store(store)
    assert any("MANIFEST.md" in e for e in errors)


def test_check_fails_missing_subdir(tmp_path):
    store = tmp_path / "missing-phase"
    store.mkdir()
    (store / "MANIFEST.md").write_text("# manifest", encoding="utf-8")
    for phase in cpl.REQUIRED_SUBDIRS[:-1]:  # omit last (prisma)
        (store / phase).mkdir()
    errors = cpl.check_project_store(store)
    assert any("prisma" in e for e in errors)


def test_check_fails_nonexistent_path(tmp_path):
    errors = cpl.check_project_store(tmp_path / "does-not-exist")
    assert any("does not exist" in e for e in errors)


def test_check_fails_path_is_file(tmp_path):
    f = tmp_path / "not-a-dir.txt"
    f.write_text("x", encoding="utf-8")
    errors = cpl.check_project_store(f)
    assert any("not a directory" in e for e in errors)


def test_check_reports_all_missing_subdirs(tmp_path):
    store = tmp_path / "empty-store"
    store.mkdir()
    (store / "MANIFEST.md").write_text("# manifest", encoding="utf-8")
    # No phase subdirs created
    errors = cpl.check_project_store(store)
    assert len(errors) == len(cpl.REQUIRED_SUBDIRS)
