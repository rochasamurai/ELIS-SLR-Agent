"""Validator adversarial tests for PE-INFRA-SLR-07 review archive handling."""

from __future__ import annotations

from subprocess import CompletedProcess

import pytest

from scripts import validator_runner_common as common


REVIEW_PASS = """## Agent update -- CODEX / PE-INFRA-SLR-07 / 2026-04-24

### Verdict
PASS

### Gate results
black: PASS

### Scope
M file

### Required fixes
None

### Evidence
```text
evidence
```
"""


def test_read_verdict_does_not_fallback_to_root_review_file(tmp_path):
    """A stale root REVIEW file must not satisfy the archived REVIEW contract."""
    pe_id = "PE-INFRA-SLR-07"
    root_review = tmp_path / common.review_file_name(pe_id)
    root_review.write_text(REVIEW_PASS, encoding="utf-8")

    assert common.read_verdict(tmp_path, pe_id) == "NOT_FOUND"


def test_read_verdict_prefers_archive_even_when_root_review_exists(tmp_path):
    pe_id = "PE-INFRA-SLR-07"
    root_review = tmp_path / common.review_file_name(pe_id)
    root_review.write_text(REVIEW_PASS.replace("PASS", "FAIL", 1), encoding="utf-8")

    archive = tmp_path / common.REVIEW_ARCHIVE_DIR
    archive.mkdir(parents=True)
    archived_review = archive / common.review_file_name(pe_id)
    archived_review.write_text(REVIEW_PASS, encoding="utf-8")

    assert common.read_verdict(tmp_path, pe_id) == "PASS"


def test_verify_review_committed_rejects_root_only_review(monkeypatch):
    pe_id = "PE-INFRA-SLR-07"

    def fake_run(*args, **kwargs):
        return CompletedProcess(
            args=args,
            returncode=0,
            stdout=f"{common.review_file_name(pe_id)}\n",
            stderr="",
        )

    monkeypatch.setattr(common.subprocess, "run", fake_run)

    with pytest.raises(common.RunnerError, match=common.review_file_path(pe_id)):
        common.verify_review_committed(pe_id, "main")
