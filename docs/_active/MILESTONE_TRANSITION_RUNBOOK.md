# Milestone Transition Runbook

## Purpose

Defines the mandatory PM procedure to start a new development milestone without
hardcoding release-specific values in agent workflow files.

---

## Preconditions

1. Current milestone has merge-complete status or explicit PM closure decision.
2. New plan file exists and includes PE definitions with acceptance criteria.
3. Base branch for the new milestone is created and protected.

---

## PM Steps

1. Create/confirm milestone plan file.
   - Example: `docs/_active/RELEASE_PLAN_v2.1.md` or `ELIS_MultiAgent_Implementation_Plan.md`
2. Update `docs/_active/MILESTONES.md`.
   - Add new row with `Status=active`.
   - Mark previous milestone `completed` or `frozen`.
3. Update `CURRENT_PE.md` release context.
   - `Release`
   - `Base branch`
   - `Plan file`
   - `Plan location`
4. Open a milestone-transition PR.
   - Include Status Packet evidence.
   - Require validator PASS before merge.
5. After merge, open PE-0 / first PE assignment PR for the new milestone.

---

## Required Evidence in Transition PR

- `git status -sb`
- `git branch --show-current`
- `git diff --name-status origin/<base>..HEAD`
- Quality gates:
  - `python -m black --check .`
  - `python -m ruff check .`
  - `python -m pytest -q`

---

## Anti-patterns (Do Not)

- Do not hardcode branch names (for example `release/2.0`) in agent instructions.
- Do not hardcode plan filenames (for example `RELEASE_PLAN_v2.0.md`) in agent instructions.
- Do not start implementation before `CURRENT_PE.md` and milestone index are merged.
