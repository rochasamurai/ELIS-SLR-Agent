# HANDOFF.md — PE-OC-06

## Summary

Implements automated PE assignment for the PM Agent: a Python CLI
(`scripts/pm_assign_pe.py`) that reads the Active PE Registry in `CURRENT_PE.md`,
enforces the alternation rule, writes the new registry row, and creates the
feature branch on the remote.

Delivered in this PE:
- Added `scripts/pm_assign_pe.py`: CLI with `--domain`, `--pe`, `--description`,
  `--dry-run`, and `--current-pe` flags; enforces codex↔claude alternation guard.
- Added `tests/test_pm_assign_pe.py`: 26 unit tests covering all acceptance criteria.
- Modified `openclaw/workspaces/workspace-pm/AGENTS.md`: appended §8 Assignment Rules
  (algorithm pseudocode, domain prefix table, first-PE default, violation handling).
- Added `docs/pm_agent/ASSIGNMENT_PROTOCOL.md`: full PM workflow reference
  (trigger syntax, 7-step flow, response format, branch naming, error handling, examples).

## Files Changed

- `scripts/pm_assign_pe.py` (new)
- `tests/test_pm_assign_pe.py` (new)
- `openclaw/workspaces/workspace-pm/AGENTS.md` (modified — §8 appended)
- `docs/pm_agent/ASSIGNMENT_PROTOCOL.md` (new)
- `HANDOFF.md` (this file)

## Design Decisions

- **Self-contained script:** `parse_active_registry()` and `extract_engine()` are copied
  verbatim from `scripts/check_role_registration.py` rather than imported. `scripts/` has
  no root `__init__.py` so cross-script imports are fragile in CI; self-contained is safer.
- **Alternation guard as assert:** Uses `assert new_engine != prev_engine` (§8.4) rather
  than a silent override. Any logic bug surfaces immediately with a clear error message and
  exit 1, matching AGENTS.md §8.4 policy.
- **Branch creation via push refspec:** `git push origin origin/<base>:refs/heads/<branch>`
  creates the remote branch atomically without requiring a local checkout. Failure warns but
  does not block the registry write — PM can create the branch manually if needed.
- **Two-commit pattern:** Code deliverables committed first (`8de423e`); HANDOFF.md written
  after capturing the clean post-commit snapshot to avoid the pre-commit dirty-tree anti-pattern
  (NB-1, PE-INFRA-07 r1).

## Acceptance Criteria

- [x] AC-1: `pm_assign_pe.py --domain programs --pe PE-PROG-08` writes correct row
  (`test_main_writes_row` + smoke `--dry-run` confirmed).
- [x] AC-2: Same engine raises `AssertionError: Alternation violation` (`test_alternation_guard_raises`).
- [x] AC-3: PO Telegram → PM Agent responds with implementer/validator/branch
  (§8 in `AGENTS.md` + §§2–4 in `ASSIGNMENT_PROTOCOL.md`).
- [x] AC-4: Branch `feature/pe-prog-08-pdf-export` created automatically
  (`test_main_dry_run` with mocked git; smoke `--dry-run` output confirmed).

## Validation Commands

```text
python -m black --check scripts/pm_assign_pe.py tests/test_pm_assign_pe.py
All done! ✨ 🍰 ✨
2 files would be left unchanged.
```

```text
python -m ruff check scripts/pm_assign_pe.py tests/test_pm_assign_pe.py
All checks passed!
```

```text
python -m pytest tests/test_pm_assign_pe.py -v
26 passed in 0.21s
```

```text
python -m pytest -q (full suite)
480 passed, 17 warnings (RC: 0)
```

```text
python scripts/pm_assign_pe.py --domain programs --pe PE-PROG-08 \
    --description "PDF export" --dry-run

PE-PROG-08 assigned.
Domain: programs
Implementer: CODEX (prog-impl-codex)
Validator: CLAUDE (prog-val-claude)
Branch: feature/pe-prog-08-pdf-export
Status: planning
[dry-run] CURRENT_PE.md would be updated (row appended).
[dry-run] Git branch 'feature/pe-prog-08-pdf-export' would be created from 'main'.
```

## Status Packet

### 6.1 Working-tree state

```text
git status -sb
## feature/pe-oc-06-pe-assignment-alternation...origin/main [ahead 1]
```

```text
git show --stat --oneline HEAD
8de423e feat(pe-oc-06): add PM agent PE assignment script with alternation enforcement
 docs/pm_agent/ASSIGNMENT_PROTOCOL.md       | 213 +++++++++++++++
 openclaw/workspaces/workspace-pm/AGENTS.md |  41 +++
 scripts/pm_assign_pe.py                    | 316 +++++++++++++++++++++++
 tests/test_pm_assign_pe.py                 | 402 +++++++++++++++++++++++++++++
 4 files changed, 972 insertions(+)
```

### 6.2 Repository state

```text
git branch --show-current
feature/pe-oc-06-pe-assignment-alternation
```

### 6.3 Quality gates

```text
black: PASS (2 files unchanged)
ruff: PASS
pytest: PASS (480 passed, 17 warnings — RC: 0)
smoke --dry-run: PASS
```

### 6.4 Ready to merge

```text
YES — awaiting validator review.
```
