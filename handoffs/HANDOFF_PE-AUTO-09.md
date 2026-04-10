# HANDOFF_PE-AUTO-09.md

**PE:** PE-AUTO-09 — Plan Loader — New Plan Ingestion
**Branch:** `feature/pe-auto-09-plan-loader-new-plan-ingestion`
**Implementer:** Claude Code
**Date:** 2026-04-08

---

## Summary

Delivered the Plan Loader — a validation and ingestion engine that reads a
JSON PE execution plan, checks it against a formal schema, verifies DAG
acyclicity, enforces the Codex/Claude alternation rule, and writes a ready-to-use
`CURRENT_PE.md` for the first executable PE.

This branch adds:

- `schemas/plan_schema.json` — JSON Schema (draft 2020-12) for PE execution plans
- `scripts/plan_loader.py` — validation engine (5 checks: schema, DAG, alternation,
  first-PE readiness, CURRENT_PE.md generation) plus a full CLI with `--json`,
  `--write-current-pe`, and `--already-merged` flags
- `tests/test_plan_loader.py` — 36 tests covering all acceptance criteria, error
  paths, CLI exit codes, and edge cases
- `.github/workflows/pm-plan-load.yml` — `workflow_dispatch` workflow that runs the
  loader on command and posts a Discord webhook confirmation before the sequencer starts
- `docs/openclaw/workspace-pm/AGENTS.md` §5.5 — documents the `!plan load` Discord
  command and the confirmation flow

---

## Files Changed

```text
A  .github/workflows/pm-plan-load.yml
M  docs/openclaw/workspace-pm/AGENTS.md
A  schemas/plan_schema.json
A  scripts/plan_loader.py
A  tests/test_plan_loader.py
M  HANDOFF.md
A  handoffs/HANDOFF_PE-AUTO-09.md
```

---

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| AC-1 | `validate_schema` rejects plans missing required fields or with wrong types | done — `validate_schema()` checks all top-level and per-PE required fields; raises `LoaderError` with descriptive path |
| AC-2 | `validate_dag` detects cycles and returns topological order | done — Kahn's algorithm; raises with cycle diagram listing all cyclic nodes |
| AC-3 | `validate_alternation` enforces Codex/Claude alternation per domain | done — checks consecutive PEs in same domain; also rejects same engine for implementer+validator within one PE |
| AC-4 | `generate_current_pe` writes a valid CURRENT_PE.md for the first ready PE | done — `--write-current-pe OUTPUT` flag writes full CURRENT_PE.md; roles table, registry row, and PM chore entry all populated |
| AC-5 | Discord `!plan load` confirms validation before starting sequencer | done — `pm-plan-load.yml` workflow dispatches `plan_loader.py`, posts Discord webhook confirmation on VALID, blocks on INVALID; AGENTS.md §5.5 documents the command; CLI exits 0/1 with `--json` structured output |

---

## Design Decisions

**Why a lightweight schema validator (no `jsonschema` library):**
The `jsonschema` package is not in the project dependencies. Writing a small
recursive type-checker keeps the dependency footprint zero and avoids pip install
changes that would touch unrelated files.

**Why Kahn's algorithm for cycle detection:**
Kahn's algorithm naturally surfaces all cyclic nodes (not just one), making the
error diagram actionable. A DFS approach would require additional bookkeeping to
collect all participants in the cycle.

**Why alternation is checked per domain, not globally:**
PEs in different domains are independent work streams. Requiring Codex/Claude
alternation globally would artificially constrain scheduling when two domains run in
parallel. Per-domain tracking matches the real operational constraint.

**Why `validate_first_pe_ready` skips already-merged PEs:**
A re-invocation of the loader after mid-release progress must not re-propose a PE
that is already merged. The `--already-merged` flag lets PM drive the loader
incrementally through a release.

**Why the CURRENT_PE.md template uses `->` (ASCII) instead of `->` (Unicode arrow):**
The repo may be opened on Windows systems with cp1252 locale. The Unicode arrow
`->` (U+2192) cannot be encoded in cp1252 and would cause a `UnicodeEncodeError`
when the file is written or piped. ASCII `->` is unambiguous and portable.

---

## Validation Commands

```text
(.venv) $ python -m pytest tests/test_plan_loader.py -q
36 passed in 0.XXs

(.venv) $ python -m black --check .
All done! 158 files would be left unchanged.

(.venv) $ python -m ruff check .
All checks passed!

(.venv) $ python -m pytest -q
749 passed, 17 warnings

(.venv) $ python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

---

*ELIS SLR Agent · HANDOFF.md · Claude Code · 2026-04-08*
