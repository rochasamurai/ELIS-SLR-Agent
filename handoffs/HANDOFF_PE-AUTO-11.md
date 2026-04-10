# HANDOFF_PE-AUTO-11.md

**PE:** PE-AUTO-11 — Parallel Track Scheduler
**Branch:** `feature/pe-auto-11-parallel-track-scheduler`
**Implementer:** Claude Code
**Date:** 2026-04-10

---

## Summary

Delivered the parallel track scheduler for the PM loop. The branch adds
eligibility checking for parallel PE dispatch, extends the sequencer to
issue dual-track decisions, extends `check_current_pe.py` to validate
dual-track `CURRENT_PE.md` format, and provides a human-readable guide
covering all eligibility criteria and operational procedures.

This branch adds / modifies:

- `scripts/check_parallel_eligibility.py` — new script with
  `check_eligibility(pe_a_id, pe_b_id, plan_pes)` returning
  `(eligible: bool, failures: list[str])`; checks both PEs exist, no
  direct dependency, no transitive dependency, and opposite implementer
  engines; CLI exits 0=ELIGIBLE / 1=INELIGIBLE
- `scripts/pe_sequencer.py` — extended `SequencerDecision` with
  `track_b_*` fields; added `_is_dual_track`, `_make_dual_track_body`,
  `_make_single_track_body`, `_replace_current_pe_section`,
  `_find_all_ready_pes`; `advance_current_pe()` now handles dual-track
  `track_a_closed` action and `dual_advance` action
- `scripts/check_current_pe.py` — extended with `_is_dual_track`,
  `_dual_track_value`, `_validate_dual_track`; `main()` dispatches to
  dual-track validation path when `Track A PE` field is present
- `docs/openclaw/PARALLEL_TRACK_GUIDE.md` — new guide covering
  eligibility criteria, `CURRENT_PE.md` dual-track format, manual Track B
  population steps, sequencer decision pseudocode, and AC-5 Track A close
  behaviour
- `tests/test_parallel_track_scheduler.py` — 25 tests covering all 6 ACs

---

## Files Changed

```text
A  scripts/check_parallel_eligibility.py
M  scripts/pe_sequencer.py
M  scripts/check_current_pe.py
A  docs/openclaw/PARALLEL_TRACK_GUIDE.md
A  tests/test_parallel_track_scheduler.py
M  HANDOFF.md
A  handoffs/HANDOFF_PE-AUTO-11.md
```

---

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| AC-1 | `check_parallel_eligibility.py` returns ELIGIBLE for two independent PEs with opposite engines | done — `check_eligibility()` returns `(True, [])` when both IDs exist, no direct or transitive dependency in either direction, and engines differ |
| AC-2 | `check_parallel_eligibility.py` returns INELIGIBLE with reasons for direct dep, transitive dep, or same engine | done — each failing criterion appends a human-readable reason string; all three classes of ineligibility are covered and tested |
| AC-3 | Sequencer issues `dual_advance` when ≥2 eligible PEs are ready simultaneously | done — `advance_current_pe()` calls `_find_all_ready_pes()` then iterates candidates checking eligibility; first eligible pair triggers `dual_advance` action with Track A/B fields populated in `SequencerDecision` |
| AC-4 | Dual-track `CURRENT_PE.md` format validated by `check_current_pe.py` | done — `_validate_dual_track()` checks all four Track A/B fields present and valid, both PEs in registry with matching branches, opposite implementer engines, and no mutual dependency via `check_parallel_eligibility` |
| AC-5 | When Track A closes, sequencer transitions `CURRENT_PE.md` back to single-track with Track B | done — `advance_current_pe()` detects dual-track mode first, marks Track A merged, rewrites `## Current PE` to single-track format with Track B, updates roles table, appends PM chore, returns `action="track_a_closed"` |
| AC-6 | `PARALLEL_TRACK_GUIDE.md` documents all eligibility criteria and dual-track format | done — guide covers the 5-criterion eligibility table, ELIGIBLE/INELIGIBLE examples, dual-track `CURRENT_PE.md` format, manual population steps, sequencer pseudocode, and AC-5 Track A close behaviour |

---

## Design Decisions

**Why dual-track detection must precede `_current_pe_id()` in `advance_current_pe()`:**
In dual-track mode `## Current PE` contains `Track A PE` / `Track B PE` fields, not
the `PE` field expected by the single-track path. Attempting `_current_pe_id()` before
the dual-track check raises `SequencerError: Missing 'PE'`. The fix moves the full
dual-track handling block to the top of the function before any single-track field
extraction.

**Why `check_eligibility` is imported lazily inside `advance_current_pe()`:**
`pe_sequencer.py` and `check_parallel_eligibility.py` both import from `pe_sequencer`
(`PlanPE`, `parse_plan`). A top-level import in `pe_sequencer.py` would create a
circular import. The lazy `from scripts.check_parallel_eligibility import
check_eligibility` inside the function body avoids this without requiring package
restructuring.

**Why the transitive-dependency check uses iterative DFS rather than recursion:**
Python's default recursion limit is 1 000 frames. A plan with many chained PEs could
hit this limit during recursive DFS. The iterative stack-based approach handles
arbitrarily deep dependency chains without requiring `sys.setrecursionlimit`.

**Why `_find_all_ready_pes` returns all ready PEs rather than the first eligible pair:**
The sequencer needs to check every ready candidate against the first ready PE to
find a valid parallel pair. Returning all ready PEs keeps the search logic in
`advance_current_pe()` and makes the eligibility filtering transparent to callers.

---

## Validation Commands

```text
(.venv) $ python -m black --check scripts/check_parallel_eligibility.py \
    scripts/pe_sequencer.py scripts/check_current_pe.py \
    tests/test_parallel_track_scheduler.py
All done! ✨ 🍰 ✨
4 files would be left unchanged.

(.venv) $ python -m ruff check scripts/check_parallel_eligibility.py \
    scripts/pe_sequencer.py scripts/check_current_pe.py \
    tests/test_parallel_track_scheduler.py
All checks passed!

(.venv) $ python -m pytest tests/test_parallel_track_scheduler.py -q
.........................
25 passed in 0.45s

(.venv) $ python -m pytest -q
779 passed, 17 warnings in 13.73s

(.venv) $ python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

Targeted PE tests: 25 passed
Full repository test suite: 779 passed

---

*ELIS SLR Agent · HANDOFF.md · Claude Code · 2026-04-10*
