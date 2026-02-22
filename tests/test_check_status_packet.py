"""Tests for scripts/check_status_packet.py (PE-OC-12 fix)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_status_packet.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_status_packet", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MODULE = _load()


def _handoff(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "HANDOFF.md"
    p.write_text(content, encoding="utf-8")
    return p


FULL_HANDOFF = """\
# HANDOFF.md — PE-TEST

## Summary
Test PE.

## Files Changed
- HANDOFF.md

## Acceptance Criteria
- [ ] AC-1 passes

## Validation Commands
```
python -m pytest
```

## Status Packet

### 6.1 Working-tree state
```
git status -sb
## feature/test...origin/feature/test
```

### 6.2 Repository state
```
git rev-parse HEAD
abc1234
```

### 6.3 Scope evidence (against `origin/main`)
```
git diff --name-status origin/main..HEAD
M   HANDOFF.md
```

### 6.4 Quality gates
```
python -m black --check .  → 100 files unchanged
python -m ruff check .     → All checks passed
python -m pytest -q        → 534 passed
```

### 6.5 Ready to merge
```
YES
```
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_ok(tmp_path, monkeypatch):
    p = _handoff(tmp_path, FULL_HANDOFF)
    monkeypatch.setenv("HANDOFF_PATH", str(p))
    assert MODULE.main() == 0


def test_missing_status_packet_header(tmp_path, monkeypatch):
    content = FULL_HANDOFF.replace("## Status Packet", "## StatusPkt")
    p = _handoff(tmp_path, content)
    monkeypatch.setenv("HANDOFF_PATH", str(p))
    assert MODULE.main() == 1


def test_missing_subsection_6_3(tmp_path, monkeypatch):
    content = FULL_HANDOFF.replace("### 6.3", "### 6.X")
    p = _handoff(tmp_path, content)
    monkeypatch.setenv("HANDOFF_PATH", str(p))
    assert MODULE.main() == 1


def test_missing_subsection_6_5(tmp_path, monkeypatch):
    content = FULL_HANDOFF.replace("### 6.5", "### 6.Y")
    p = _handoff(tmp_path, content)
    monkeypatch.setenv("HANDOFF_PATH", str(p))
    assert MODULE.main() == 1


def test_empty_file(tmp_path, monkeypatch):
    p = _handoff(tmp_path, "   \n\n  ")
    monkeypatch.setenv("HANDOFF_PATH", str(p))
    assert MODULE.main() == 1


def test_missing_file(tmp_path, monkeypatch):
    monkeypatch.setenv("HANDOFF_PATH", str(tmp_path / "HANDOFF.md"))
    assert MODULE.main() == 1


def test_custom_path_env_var(tmp_path, monkeypatch):
    custom = tmp_path / "custom_handoff.md"
    custom.write_text(FULL_HANDOFF, encoding="utf-8")
    monkeypatch.setenv("HANDOFF_PATH", str(custom))
    assert MODULE.main() == 0


def test_all_six_subsections_required(tmp_path, monkeypatch):
    """Each of 6.1–6.5 individually causes failure when absent."""
    for n in range(1, 6):
        content = FULL_HANDOFF.replace(f"### 6.{n}", f"### X.{n}")
        p = _handoff(tmp_path, content)
        monkeypatch.setenv("HANDOFF_PATH", str(p))
        result = MODULE.main()
        assert result == 1, f"Expected failure when ### 6.{n} is missing"
