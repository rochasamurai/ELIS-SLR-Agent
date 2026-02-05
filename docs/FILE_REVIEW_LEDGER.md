# File Review Ledger

**Created:** 2026-02-05
**Source:** `docs/_inventory_tracked_files.txt` (176 tracked files at time of creation)
**Plan:** `docs/REPO_HYGIENE_PLAN_2026-02-05.md` (Section 5)

Populate this ledger for every tracked file. Each file must have an explicit decision — no "maybe".

| Path | Purpose (1 line) | Status | Action | Notes | Tests/Docs impacted |
|---|---|---|---|---|---|
| | | | | | |

**Status values:** KEEP, MOVE, DELETE, DEPRECATE

**Review order (highest value first):**
1. `scripts/` — harvesters, preflights, agent entrypoints, validators
2. `schemas/` — Appendix A/B/C schemas + alignment with validator
3. `tests/` — unit vs integration boundaries; fixture strategy
4. `config/` + `configs/` — consolidate; remove duplication
5. `docs/` — keep only active; archive old
6. `json_jsonl/` — canonical vs generated; remove `README-old.md`
7. `imports/`, `validation_reports/`, `presentations/`, `data/` — policies
