# HANDOFF_PE-INFRA-SLR-01.md

**PE:** PE-INFRA-SLR-01 — Role-Based Agent Surface Normalisation
**Branch:** `feature/pe-infra-slr-01-role-based-agent-surface-normalisation`
**Implementer:** Claude Code (`infra-impl-claude`)
**Date:** 2026-04-14

---

## Summary

Adds a Role-Based Agent Surface Normalisation section to `AGENTS.md` (§14)
and a supporting Python module + test suite. The section documents the
canonical mapping from workflow surface names (agentIds such as
`infra-impl-claude`) to provider-neutral role names (such as `infra-impl`),
defines governance rules, and specifies the derivation algorithm.

`elis/role_surface.py` exposes `SURFACE_ROLE_MAP`, `role_from_surface()`,
and `is_structured_surface()`. `tests/test_pe_infra_slr_01.py` covers all
37 test cases (mapping completeness, round-trip derivation, adversarial
inputs, engine suffix invariants, and AGENTS.md section presence).

---

## Files Changed

```text
M  AGENTS.md
M  HANDOFF.md
M  scripts/check_handoff.py
M  scripts/copy_handoff.py
A  elis/role_surface.py
A  handoffs/HANDOFF_PE-INFRA-SLR-01.md
A  tests/test_pe_infra_slr_01.py
```

---

## Design Decisions

1. **Module location** — `elis/role_surface.py` keeps the mapping inside the
   `elis` package alongside other workflow helpers (`harvest_contract.py`,
   `manifest.py`). No new top-level module needed.

2. **Explicit map + fallback** — `SURFACE_ROLE_MAP` lists all 12 canonical
   surfaces explicitly so tooling gets a single authoritative lookup.
   `role_from_surface()` falls back to the derivation rule (strip engine
   suffix) only for structured surfaces not yet in the table, making the
   function forward-compatible with new engine assignments.

3. **One-off surfaces** — `gemini-cli` does not follow the
   `<role>-<engine>` convention and raises `ValueError` from
   `role_from_surface()`. Guest/one-off surfaces are excluded from the
   alternation rule and do not belong in `SURFACE_ROLE_MAP`.

4. **AGENTS.md section** — added as §14 after §13 (Secrets isolation policy)
   so the governance rules land in the same document that defines all other
   workflow invariants. No existing section was modified.

5. **copy_handoff.py / check_handoff.py regex** — both scripts contained the
   legacy `PE-[A-Z]+-[0-9]+` pattern which silently rejected compound PE-IDs
   such as `PE-INFRA-SLR-01`.  Applied the same fix as PE-AUTO-04 commit
   `b5be1a6` (updated to `PE-[A-Z0-9-]+-[0-9]+`) so the HANDOFF workflow
   functions correctly for this and all subsequent compound-ID PEs.  Pre-existing
   defect; fix is in scope because `copy_handoff.py` failing would block AC-2.

---

## Acceptance Criteria

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | Add a Role-Based Agent Surface Normalisation section and explicit mapping for workflow surface names to role names. | **PASS** |
| AC-2 | Commit the updated handoff template in handoffs/HANDOFF_PE-INFRA-SLR-01.md. | **PASS** |
| AC-3 | Update tests to validate role-based naming and run `pytest tests/test_pe_infra_slr_01.py` (placeholder). | **PASS** |

---

## Validation Commands

### AC-1 — Section presence in AGENTS.md

```
$ grep -n "## 14) Role-Based Agent Surface Normalisation" AGENTS.md
693:## 14) Role-Based Agent Surface Normalisation
```

### AC-2 — Handoff file present

```
$ ls handoffs/HANDOFF_PE-INFRA-SLR-01.md
handoffs/HANDOFF_PE-INFRA-SLR-01.md
```

### AC-3 — PE-specific tests

```
$ python -m pytest tests/test_pe_infra_slr_01.py -v
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/runner/work/ELIS-SLR-Agent/ELIS-SLR-Agent
configfile: pyproject.toml
collected 37 items

tests/test_pe_infra_slr_01.py .....................................      [100%]

============================== 37 passed in 0.07s
```

### Quality gates

```
$ python -m black --check .
All done! ✨ 🍰 ✨
171 files would be left unchanged.

$ python -m ruff check .
scripts/dispatch_implementer_runner.py:15:1: E402 Module level import not at top of file
Found 1 error.
(pre-existing — not introduced by this PE; present since PE-AUTO-04 commit 20bea8c)

$ python -m pytest --tb=no -q
871 passed in 3.87s
(PE-specific: 37/37 passed)
```

### Scope gate

```
$ git diff --name-status origin/main..HEAD
M       AGENTS.md
M       HANDOFF.md
M       scripts/check_handoff.py
M       scripts/copy_handoff.py
A       elis/role_surface.py
A       handoffs/HANDOFF_PE-INFRA-SLR-01.md
A       tests/test_pe_infra_slr_01.py
```
