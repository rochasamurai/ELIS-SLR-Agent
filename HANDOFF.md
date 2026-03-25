# HANDOFF.md — PE-MS-08

**PE:** `PE-MS-08`  
**Title:** PM Agent End-to-End Operational Validation and Native Runbooks  
**Implementer:** CODEX (`infra-impl-codex`)  
**Validator:** Claude Code (`infra-val-claude`)  
**Branch:** `feature/pe-ms-08-e2e-validation`  
**Base branch:** `main`  
**Plan:** `ELIS_MultiAgent_Implementation_Plan_v1_6.md`  
**Commit:** `pending final HANDOFF commit`

---

## Summary

This PE turns the current PM/native operating model into an auditable implementation
package. It adds a dedicated PM Agent E2E validation runbook, consolidates native
operations and restore procedures into a single host runbook, wires those references
into the existing deployment/runtime docs, and adds pytest coverage to prevent the
critical validation steps from silently drifting out of the documentation set.

The branch is intentionally documentation-first. It does not change runtime config or
prompt behavior directly; instead it defines the exact host and Discord evidence the
Validator must collect on `elis-server` to close the final E2E acceptance checks.

---

## Files Changed

| File | Change | Purpose |
|---|---|---|
| `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md` | Added | Canonical end-to-end PM validation flow for Discord and host cross-checks |
| `docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md` | Added | Native deploy, operations, PM recovery, and restore guidance |
| `docs/openclaw/DEPLOYMENT.md` | Modified | Points deploy flow to PM reset, E2E validation, and native restore runbooks |
| `docs/openclaw/NATIVE_INSTALL.md` | Modified | Declares the new authoritative operating runbooks |
| `docs/openclaw/PM_AGENT_RULES.md` | Modified | Links PM deploy/reset flow to the E2E validation runbook |
| `docs/openclaw/PM_SESSION_RESET.md` | Modified | Extends reset flow to require the full PM E2E validation set |
| `tests/test_pm_runbooks.py` | Added | Guards critical runbook coverage and cross-links with pytest |

---

## Design Decisions

1. **Validation runbook separate from reset runbook**: reset only proves a fresh session exists; it does not prove PM behavior. `PM_E2E_VALIDATION_RUNBOOK.md` carries the actual Discord scenarios.
2. **One native operations runbook**: the repo already had partial deploy/install guidance. `NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md` consolidates day-to-day ops, PM recovery, and restore into one host-facing flow.
3. **Docs are test-backed**: `tests/test_pm_runbooks.py` checks for required commands, questions, and references so the runbooks cannot quietly regress.
4. **Workspace entrypoints remain the runtime contract**: all PM validation is framed around `~/openclaw/workspace-pm/...`, not direct repo reads in Discord sessions.
5. **Validator captures live evidence**: because `elis-server` and Discord validation are external to this local worktree, the branch defines explicit evidence requirements for the Validator rather than inventing fake local runtime proof.

---

## Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| AC-1 | PM Agent identifies current PE state correctly from canonical files | READY FOR VALIDATION | `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md` Scenario 2 defines Discord + host proof |
| AC-2 | PM Agent reports worktrees only from explicit host evidence | READY FOR VALIDATION | `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md` Scenario 3 uses `git -C /opt/elis/repo worktree list` |
| AC-3 | PM Agent produces Discord-safe registry reporting | READY FOR VALIDATION | `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md` Scenario 4 defines chunked `(1/N)` behavior under Discord limit |
| AC-4 | Native operations and restore guidance are committed and validated | IMPLEMENTED | `docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md`; `tests/test_pm_runbooks.py` |

---

## Quality Gate Results

```bash
python scripts/check_agent_scope.py
Agent scope clean - no secret-pattern files detected in worktree.

python -m black --check .
All done! ✨ 🍰 ✨
125 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
598 passed, 17 warnings in 14.89s
```

---

## Scope

```bash
git diff --name-status origin/main
M	HANDOFF.md
M	docs/openclaw/DEPLOYMENT.md
M	docs/openclaw/NATIVE_INSTALL.md
A	docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md
M	docs/openclaw/PM_AGENT_RULES.md
A	docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md
M	docs/openclaw/PM_SESSION_RESET.md
A	tests/test_pm_runbooks.py

git diff --stat origin/main
 HANDOFF.md                                         | 131 +++++++------
 docs/openclaw/DEPLOYMENT.md                        |  26 ++-
 docs/openclaw/NATIVE_INSTALL.md                    |   6 +
 docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md | 188 ++++++++++++++++++
 docs/openclaw/PM_AGENT_RULES.md                    |   4 +
 docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md         | 214 +++++++++++++++++++++
 docs/openclaw/PM_SESSION_RESET.md                  |   1 +
 tests/test_pm_runbooks.py                          |  52 +++++
 8 files changed, 558 insertions(+), 64 deletions(-)
```

---

## Validator Checklist

- [ ] Run `python -m black --check .`
- [ ] Run `python -m ruff check .`
- [ ] Run `python -m pytest -q`
- [ ] Confirm `tests/test_pm_runbooks.py` passes
- [ ] Follow `docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md` on `elis-server`
- [ ] Follow `docs/openclaw/PM_SESSION_RESET.md` if prompt or exec-policy changes are in scope
- [ ] Execute all scenarios in `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md`
- [ ] Capture host evidence and Discord evidence in `REVIEW_PE_MS_08.md`
- [ ] Confirm no unrelated files appear in the scope diff

---

## Ready for Validator

Yes.

Local implementation is complete and the branch is scoped to PM/native runbooks plus
one supporting pytest file. Remaining evidence for AC-1 through AC-3 is intentionally
reserved for Validator capture on `elis-server`, because those acceptance criteria
require fresh Discord and host-side runtime validation.
