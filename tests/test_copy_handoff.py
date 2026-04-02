"""Tests for copy_handoff.py — root HANDOFF copy generation."""

from __future__ import annotations

from pathlib import Path

from scripts import copy_handoff

CURRENT_PE_BODY = """\
## Current PE

| Field   | Value       |
|---------|-------------|
| PE      | PE-TEST-01  |
| Branch  | feature/pe-test-01 |
"""

HANDOFF_BODY = """\
## Summary
Test handoff.

## Files Changed
- scripts/copy_handoff.py

## Acceptance Criteria
| # | Criterion | Status |
|---|---|---|
| AC-1 | test | ✓ |

## Validation Commands
```text
python scripts/copy_handoff.py
```
"""


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_copies_namespaced_handoff_to_root(tmp_path, monkeypatch):
    monkeypatch.setenv("CURRENT_PE_PATH", str(tmp_path / "CURRENT_PE.md"))
    monkeypatch.setenv("HANDOFFS_DIR", str(tmp_path / "handoffs"))
    monkeypatch.setenv("ROOT_HANDOFF", str(tmp_path / "HANDOFF.md"))

    _write(tmp_path / "CURRENT_PE.md", CURRENT_PE_BODY)
    _write(tmp_path / "handoffs" / "HANDOFF_PE-TEST-01.md", HANDOFF_BODY)

    assert copy_handoff.main() == 0
    assert (tmp_path / "HANDOFF.md").read_text(encoding="utf-8") == HANDOFF_BODY


def test_missing_current_pe_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("CURRENT_PE_PATH", str(tmp_path / "CURRENT_PE.md"))
    assert copy_handoff.main() == 1


def test_missing_pe_field_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("CURRENT_PE_PATH", str(tmp_path / "CURRENT_PE.md"))
    _write(tmp_path / "CURRENT_PE.md", "No PE field here.\n")
    assert copy_handoff.main() == 1


def test_missing_namespaced_file_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("CURRENT_PE_PATH", str(tmp_path / "CURRENT_PE.md"))
    monkeypatch.setenv("HANDOFFS_DIR", str(tmp_path / "handoffs"))
    monkeypatch.setenv("ROOT_HANDOFF", str(tmp_path / "HANDOFF.md"))

    _write(tmp_path / "CURRENT_PE.md", CURRENT_PE_BODY)
    # handoffs directory exists but the namespaced file does not
    (tmp_path / "handoffs").mkdir()

    assert copy_handoff.main() == 1
