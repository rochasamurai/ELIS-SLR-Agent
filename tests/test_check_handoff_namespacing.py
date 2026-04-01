"""Tests for check_handoff.py PE-AUTO-03 namespacing behaviour."""

from __future__ import annotations

from pathlib import Path

from scripts import check_handoff

VALID_BODY = """\
## Summary
Test handoff.

## Files Changed
- scripts/check_handoff.py

## Acceptance Criteria
| # | Criterion | Status |
|---|---|---|
| AC-1 | test | ✓ |

## Validation Commands
```text
python scripts/check_handoff.py
```
"""

CURRENT_PE_BODY = """\
## Current PE

| Field   | Value       |
|---------|-------------|
| PE      | PE-TEST-01  |
| Branch  | feature/pe-test-01 |
"""


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Resolution: explicit HANDOFF_PATH
# ---------------------------------------------------------------------------


def test_explicit_handoff_path_used(tmp_path, monkeypatch):
    p = _write(tmp_path / "explicit.md", VALID_BODY)
    monkeypatch.setenv("HANDOFF_PATH", str(p))
    assert check_handoff.main() == 0


def test_explicit_missing_path_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("HANDOFF_PATH", str(tmp_path / "missing.md"))
    assert check_handoff.main() == 1


# ---------------------------------------------------------------------------
# Resolution: namespaced handoffs/HANDOFF_{PE_ID}.md
# ---------------------------------------------------------------------------


def test_namespaced_path_preferred_over_root(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "CURRENT_PE.md", CURRENT_PE_BODY)
    _write(tmp_path / "handoffs" / "HANDOFF_PE-TEST-01.md", VALID_BODY)
    # root HANDOFF.md is absent — namespaced path must be used
    assert check_handoff.main() == 0
    assert "HANDOFF_PE-TEST-01.md" in capsys.readouterr().out


def test_namespaced_path_missing_falls_back_to_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "CURRENT_PE.md", CURRENT_PE_BODY)
    # no handoffs/ dir — falls back to root HANDOFF.md
    _write(tmp_path / "HANDOFF.md", VALID_BODY)
    assert check_handoff.main() == 0


# ---------------------------------------------------------------------------
# Resolution: root HANDOFF.md fallback
# ---------------------------------------------------------------------------


def test_root_handoff_used_when_no_current_pe(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "HANDOFF.md", VALID_BODY)
    assert check_handoff.main() == 0


def test_no_handoff_anywhere_fails(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert check_handoff.main() == 1


# ---------------------------------------------------------------------------
# Content validation
# ---------------------------------------------------------------------------


def test_missing_section_fails(tmp_path, monkeypatch):
    body = VALID_BODY.replace("## Summary\nTest handoff.\n", "")
    p = _write(tmp_path / "HANDOFF.md", body)
    monkeypatch.setenv("HANDOFF_PATH", str(p))
    assert check_handoff.main() == 1


def test_all_sections_present_passes(tmp_path, monkeypatch):
    p = _write(tmp_path / "HANDOFF.md", VALID_BODY)
    monkeypatch.setenv("HANDOFF_PATH", str(p))
    assert check_handoff.main() == 0
