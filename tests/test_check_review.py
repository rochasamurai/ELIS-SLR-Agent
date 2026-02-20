import os
from pathlib import Path

from scripts import check_review


REVIEW_BASE = """## Agent update — Claude Code / PE-X / 2026-02-20

### Verdict
PASS

### Gate results
black: PASS
ruff: PASS
pytest: PASS

### Scope
M scripts/check_review.py

### Required fixes
None

### Evidence
```text
python -m pytest tests/test_check_review.py -q
8 passed
```
"""


def _write_review(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_missing_review_file_env_returns_1(monkeypatch, tmp_path):
    missing = tmp_path / "REVIEW_PE999.md"
    monkeypatch.setenv("REVIEW_FILE", str(missing))
    monkeypatch.delenv("REVIEW_PATH", raising=False)

    assert check_review.main() == 1


def test_missing_evidence_section_returns_1(monkeypatch, tmp_path):
    review = tmp_path / "REVIEW_PE1.md"
    _write_review(
        review,
        REVIEW_BASE.replace(
            "### Evidence\n```text\npython -m pytest tests/test_check_review.py -q\n8 passed\n```\n",
            "",
        ),
    )
    monkeypatch.setenv("REVIEW_FILE", str(review))

    assert check_review.main() == 1


def test_evidence_without_code_block_returns_1(monkeypatch, tmp_path):
    review = tmp_path / "REVIEW_PE2.md"
    _write_review(
        review,
        REVIEW_BASE.replace(
            "```text\npython -m pytest tests/test_check_review.py -q\n8 passed\n```",
            "(none)",
        ),
    )
    monkeypatch.setenv("REVIEW_FILE", str(review))

    assert check_review.main() == 1


def test_fail_verdict_with_empty_required_fixes_returns_1(monkeypatch, tmp_path):
    review = tmp_path / "REVIEW_PE3.md"
    content = REVIEW_BASE.replace("### Verdict\nPASS", "### Verdict\nFAIL").replace(
        "### Required fixes\nNone", "### Required fixes\n\n"
    )
    _write_review(review, content)
    monkeypatch.setenv("REVIEW_FILE", str(review))

    assert check_review.main() == 1


def test_fail_verdict_with_none_required_fixes_returns_1(monkeypatch, tmp_path):
    review = tmp_path / "REVIEW_PE4.md"
    content = REVIEW_BASE.replace("### Verdict\nPASS", "### Verdict\nFAIL")
    _write_review(review, content)
    monkeypatch.setenv("REVIEW_FILE", str(review))

    assert check_review.main() == 1


def test_pass_verdict_with_valid_evidence_returns_0(monkeypatch, tmp_path):
    review = tmp_path / "REVIEW_PE5.md"
    _write_review(review, REVIEW_BASE)
    monkeypatch.setenv("REVIEW_FILE", str(review))

    assert check_review.main() == 0


def test_fail_verdict_with_fix_listed_returns_0(monkeypatch, tmp_path):
    review = tmp_path / "REVIEW_PE6.md"
    content = REVIEW_BASE.replace("### Verdict\nPASS", "### Verdict\nFAIL").replace(
        "### Required fixes\nNone", "### Required fixes\n- Add missing evidence block"
    )
    _write_review(review, content)
    monkeypatch.setenv("REVIEW_FILE", str(review))

    assert check_review.main() == 0


def test_multi_section_review_checks_last_evidence_section(monkeypatch, tmp_path):
    review = tmp_path / "REVIEW_PE7.md"
    older = """## Agent update — Claude Code / PE-X / 2026-02-19

### Verdict
PASS

### Gate results
black: PASS
ruff: PASS
pytest: PASS

### Scope
M file

### Required fixes
None

### Evidence
(none)
"""
    newer = REVIEW_BASE
    _write_review(review, older + "\n" + newer)
    monkeypatch.setenv("REVIEW_FILE", str(review))

    assert check_review.main() == 0


def test_review_path_fallback_uses_most_recent_review(monkeypatch, tmp_path):
    older = tmp_path / "REVIEW_PE_A.md"
    newer = tmp_path / "REVIEW_PE_B.md"

    _write_review(older, REVIEW_BASE)
    _write_review(
        newer, REVIEW_BASE.replace("PASS", "FAIL", 1).replace("None", "- fix", 1)
    )

    os.utime(older, (1, 1))
    os.utime(newer, (2, 2))

    monkeypatch.delenv("REVIEW_FILE", raising=False)
    monkeypatch.setenv("REVIEW_PATH", str(tmp_path))

    assert check_review.main() == 0
