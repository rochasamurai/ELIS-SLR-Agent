# HANDOFF.md — PE-OC-08

## Summary

Implements PE-OC-08 PO Status Reporting & Escalation automation for PM Agent:

- Added `scripts/pm_status_reporter.py` — status query formatter (`status` command)
  and immediate escalation handler (`escalate PE-X` command) per AGENTS.md §4.1–§4.2.
- Added `scripts/pm_stall_detector.py` — cron-triggered stall (> 48 h) and
  validator iteration-threshold (> 2 rounds) detector with structured escalation output.
- Added `tests/test_pm_status_reporter.py` (22 tests) and
  `tests/test_pm_stall_detector.py` (22 tests) covering all 5 ACs.
- Added `docs/pm_agent/ESCALATION_PROTOCOL.md` — full escalation reference including
  trigger conditions, message format, CLI reference, and examples.
- Updated `openclaw/workspaces/workspace-pm/AGENTS.md` with §4.4 Automation Tools
  table and Detection column in §5 Escalation Triggers.

## Files Changed

- `scripts/pm_status_reporter.py` (new)
- `scripts/pm_stall_detector.py` (new)
- `tests/test_pm_status_reporter.py` (new)
- `tests/test_pm_stall_detector.py` (new)
- `docs/pm_agent/ESCALATION_PROTOCOL.md` (new)
- `openclaw/workspaces/workspace-pm/AGENTS.md` (updated)
- `HANDOFF.md` (this file)

## Design Decisions

- **Self-contained scripts:** Both scripts copy `parse_active_registry()` verbatim from
  `scripts/pm_assign_pe.py` rather than importing it. `scripts/` has no package marker at
  root level; self-contained is safer and consistent with existing pattern.
- **Stall detection by last-updated date only:** The Active PE Registry stores
  `last-updated` as a calendar date (no time). The detector anchors the `last-updated`
  date at **end-of-day (23:59:59 UTC)** to avoid premature stall escalation — a PE
  updated at any time during a day will not be flagged as stalled until more than 48 h
  after that day ends. This was fixed in commit `c144b77` in response to NB-2.
- **Validator iteration count via REVIEW file Round History:** The simplest reliable
  signal for iteration count is the `## Round History` table in the PE's REVIEW file
  (`REVIEW_{PE_ID_WITH_UNDERSCORES}.md`). Each `| rN |` row counts as one round. If no
  REVIEW file exists, count is 0 (PE has not entered validation yet).
- **Emoji in escalation messages:** `🔴` is used per AGENTS.md §4.2. Scripts call
  `sys.stdout.reconfigure(encoding="utf-8")` in `main()` to handle Windows terminals.
  Tests use pytest `capsys` which is encoding-agnostic.
- **Threshold strictness:** Stall fires when age_hours **> 48** (not ≥ 48). Iteration
  breach fires when count **> 2** (not ≥ 2). This matches AC-2 ("49 hours") and AC-3
  ("3 validator iterations").

## Acceptance Criteria

- [x] AC-1: `python scripts/pm_status_reporter.py --command status` returns formatted
  Active PE table with Implementer engine and last-updated (`test_main_status_command`).
- [x] AC-2: PE with `last-updated` 49 h ago triggers stall escalation
  (`test_detect_stall_over_threshold`, `test_run_detection_stall_found`).
- [x] AC-3: PE with 3 validator rounds triggers iteration breach escalation with ≥ 2
  resolution options (`test_build_iteration_escalation_message`,
  `test_run_detection_iteration_breach`).
- [x] AC-4: All escalation messages include PM Agent recommendation field
  (`test_build_escalation_contains_required_fields`).
- [x] AC-5: `python scripts/pm_status_reporter.py --command escalate --pe-id PE-OC-08`
  responds immediately (`test_main_escalate_command`).

## Validation Commands

```text
python -m black --check scripts/pm_status_reporter.py scripts/pm_stall_detector.py tests/test_pm_status_reporter.py tests/test_pm_stall_detector.py
All done! ✨ 🍰 ✨
4 files would be left unchanged.
```

```text
python -m ruff check scripts/pm_status_reporter.py scripts/pm_stall_detector.py tests/test_pm_status_reporter.py tests/test_pm_stall_detector.py
All checks passed!
```

```text
python -m pytest tests/test_pm_status_reporter.py tests/test_pm_stall_detector.py -q
............................................                             [100%]
44 passed in 0.40s
```

```text
python scripts/pm_status_reporter.py --command status --registry CURRENT_PE.md
Active PEs — 2026-02-22 UTC:

PE-OC-08 | openclaw-infra | planning | Implementer: Claude Code | last updated 2026-02-22

1 PEs active. 13 merged this week.
```

```text
python scripts/pm_stall_detector.py --registry CURRENT_PE.md
No stalls or iteration breaches detected.
```

## Non-blocking findings (from PR #270 Validator review)

| ID | Description | Resolution |
|---|---|---|
| NB-1 | HANDOFF.md §6.1 showed dirty tree (`M HANDOFF.md`) and truncated SHA. | ✓ Fixed — Status Packet updated with clean working-tree state and full SHA (this commit). |
| NB-2 | `pm_stall_detector.py` used midnight UTC for `last-updated`, risking premature escalation by up to ~24h. | ✓ Fixed in `c144b77` — `_age_hours` now anchors at 23:59:59 UTC (end-of-day). |

## Status Packet

### 6.1 Working-tree state

Captured after all code commits pushed and branch in sync with origin — before this
HANDOFF edit.

```text
git status -sb
## feature/pe-oc-08-po-status-reporting...origin/feature/pe-oc-08-po-status-reporting

git diff --name-status
(no output — working tree clean)
```

### 6.2 Repository state

```text
git fetch --all --prune
(already up to date)

git branch --show-current
feature/pe-oc-08-po-status-reporting

git rev-parse HEAD
870e4436fa358441522e70fe05aa8af7810919de

git log -6 --oneline --decorate
870e443 (HEAD -> feature/pe-oc-08-po-status-reporting, origin/feature/pe-oc-08-po-status-reporting) docs(pe-oc-08): address NB-1 and NB-2 in HANDOFF update
c144b77 fix(pe-oc-08): treat last-updated as end-of-day to avoid premature stall
89a69ee docs(pe-oc-08): add HANDOFF.md with Status Packet
4cf8ac7 feat(pe-oc-08): add PO status reporting and escalation automation
38e8f50 (origin/main, origin/HEAD, main) chore(pm): advance registry to PE-OC-08
bb72e7f Merge pull request #269 from rochasamurai/feature/pe-oc-07-gate-automation
```

### 6.3 Scope evidence (against `origin/main`)

```text
git diff --name-status origin/main..HEAD
A	docs/pm_agent/ESCALATION_PROTOCOL.md
M	HANDOFF.md
M	openclaw/workspaces/workspace-pm/AGENTS.md
A	scripts/pm_stall_detector.py
A	scripts/pm_status_reporter.py
A	tests/test_pm_stall_detector.py
A	tests/test_pm_status_reporter.py
```

No out-of-scope files. The NB-2 fix is within `scripts/pm_stall_detector.py` and
`tests/test_pm_stall_detector.py` — both in-plan deliverables.

### 6.4 Quality gates

```text
python -m black --check .
All done! ✨ 🍰 ✨
111 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
RC: 0 — 534 tests, 17 warnings
```

### 6.4 Ready to merge

```text
YES — NB-1 and NB-2 addressed in this HANDOFF update.
```
