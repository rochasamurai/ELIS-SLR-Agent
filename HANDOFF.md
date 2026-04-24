# HANDOFF — PE-INFRA-SLR-06

**PE:** PE-INFRA-SLR-06  
**Branch:** feature/pe-infra-slr-06-workflow-state-machine-formalisation  
**Implementer:** CODEX (`infra-impl-a`)  
**Date:** 2026-04-24  
**Base branch:** main  
**Implementation commit:** `244787cd2d74a8e907de9c3ffb6f74faadba2725`

---

## Summary

PE-INFRA-SLR-06 formalises the v1.9 PE workflow state machine as a first-class governance contract.

The implementation adds:

- a human-readable PE state-machine contract at `docs/workflow/PE_STATE_MACHINE.md`;
- a machine-readable mirror at `elis/workflow_state_machine.py`;
- ADR-013 to record the structural workflow decision;
- AGENTS.md, architecture, and implementation-plan references that use the same canonical state labels and transition guard names;
- targeted tests proving the state labels and guard language are discoverable and consistent across code and governing docs;
- validator/current-PE checks reusing the shared state contract instead of duplicating status strings.

---

## Files Changed

| File | Change |
|------|--------|
| `AGENTS.md` | Adds the canonical workflow state machine, allowed transitions, transition guards, and GitHub Actions boundary. |
| `ELIS_MultiAgent_Implementation_Plan_v1_9.md` | Adds the v1.9 workflow state-machine reference for future PE workflow language. |
| `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_9.md` | Links architecture state-machine authority to the human-readable and machine-readable contracts. |
| `docs/decisions/ADR-013-workflow-state-machine-contract.md` | Records the state-machine contract decision. |
| `docs/decisions/README.md` | Adds ADR-013 to the ADR index. |
| `docs/workflow/PE_STATE_MACHINE.md` | New human-readable canonical PE lifecycle state and guard contract. |
| `elis/workflow_state_machine.py` | New machine-readable state labels, transitions, guards, and helper functions. |
| `scripts/check_current_pe.py` | Reuses the shared state-machine constants for active and registry status validation. |
| `scripts/check_role_registration.py` | Reuses the shared state-machine constants and resolves imports from the active checkout. |
| `scripts/dispatch_validator_runner.py` | Format-only Black fix required by the full pinned Black gate. |
| `tests/test_workflow_state_machine.py` | New targeted tests for canonical states, transitions, guard lookup, validator reuse, and governing-doc consistency. |

---

## Design Decisions

- **First-class contract:** `docs/workflow/PE_STATE_MACHINE.md` is the human-readable source for agents and PM workflow use; `elis/workflow_state_machine.py` is the machine-readable mirror for tests and scripts.
- **Shared status constants:** `scripts/check_current_pe.py` and `scripts/check_role_registration.py` now consume the shared state-machine constants so future state changes are not duplicated in validator scripts.
- **ADR required:** This PE changes cross-cutting PE, agent, and CI governance semantics, so ADR-013 records the decision per `AGENTS.md` ADR rules.
- **GitHub Actions boundary:** The docs state that GitHub Actions may observe guards and dispatch bounded workflow steps, but must not perform agent coding unless the current state and execution-surface policy permit it.
- **Format-only gate fix:** `scripts/dispatch_validator_runner.py` was formatted because the full pinned Black gate failed on that existing import layout. No logic changed in that file.

---

## Acceptance Criteria

| AC | Criterion | Result |
|----|-----------|--------|
| AC-1 | The canonical workflow states (`planning`, `implementing`, `gate-1-pending`, `validating`, `gate-2-pending`, `merged`, `blocked`, `superseded`) are documented consistently across architecture and workflow guidance. | PASS — architecture, AGENTS.md, plan v1.9, `docs/workflow/PE_STATE_MACHINE.md`, and tests use the same labels. |
| AC-2 | Transition guards for implementer completion, validator authorisation, review completion, and merge approval are stated explicitly in the governing docs. | PASS — guard names and required evidence are documented in AGENTS.md and `docs/workflow/PE_STATE_MACHINE.md`, and mirrored in `elis/workflow_state_machine.py`. |
| AC-3 | GitHub Actions are restricted to observing guards and dispatching bounded workflow steps; they do not perform agent coding unless the state permits it. | PASS — AGENTS.md, the architecture, the plan, and the state-machine contract all state the boundary. |
| AC-4 | The state-machine language is reflected in the implementation-plan workflow references so future PEs follow the same terms. | PASS — plan v1.9 now has a dedicated workflow state-machine reference section. |
| AC-5 | A targeted validation check or test proves the state labels/guards are discoverable and consistent. | PASS — `tests/test_workflow_state_machine.py` validates code constants, transitions, guard lookup, script reuse, and governing-doc references. |

---

## Validation Commands

### Tool Versions

```powershell
C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe -m black --version
python -m black, 24.8.0 (compiled: no)
Python (CPython) 3.14.0

C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe -m ruff --version
ruff 0.6.9
```

### Current PE Validation

```powershell
C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe scripts/check_current_pe.py
CURRENT_PE.md OK — release context, roles, registry, and alternation valid.
```

```powershell
C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe scripts/check_role_registration.py
CURRENT_PE.md OK — role registration valid.
```

```powershell
C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

### Scope Evidence

```powershell
git diff --name-status origin/main..HEAD
M	AGENTS.md
M	ELIS_MultiAgent_Implementation_Plan_v1_9.md
M	ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_9.md
A	docs/decisions/ADR-013-workflow-state-machine-contract.md
M	docs/decisions/README.md
A	docs/workflow/PE_STATE_MACHINE.md
A	elis/workflow_state_machine.py
M	scripts/check_current_pe.py
M	scripts/check_role_registration.py
M	scripts/dispatch_validator_runner.py
A	tests/test_workflow_state_machine.py
```

```powershell
git diff --stat origin/main..HEAD
 AGENTS.md                                          |  44 +++++++++
 ELIS_MultiAgent_Implementation_Plan_v1_9.md        |  21 +++++
 ...SLR_AI_Platform_Conceptual_Architecture_v1_9.md |   9 ++
 .../ADR-013-workflow-state-machine-contract.md     |  58 ++++++++++++
 docs/decisions/README.md                           |   1 +
 docs/workflow/PE_STATE_MACHINE.md                  |  76 +++++++++++++++
 elis/workflow_state_machine.py                     | 104 +++++++++++++++++++++
 scripts/check_current_pe.py                        |  20 +---
 scripts/check_role_registration.py                 |  23 +++--
 scripts/dispatch_validator_runner.py               |   4 +-
 tests/test_workflow_state_machine.py               | 102 ++++++++++++++++++++
 11 files changed, 432 insertions(+), 30 deletions(-)
```

### Formatting

```powershell
$env:Path='C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts;' + $env:Path; $env:BLACK_CACHE_DIR='C:\Users\carlo\ELIS-SLR-Agent\.tmp\black-cache-pe-infra-slr-06'; python -m black --check --include "\.py$" elis/ tests/ scripts/
All done! \u2728 \U0001f370 \u2728
180 files would be left unchanged.
```

### Ruff

```powershell
$env:Path='C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts;' + $env:Path; python -m ruff check .
All checks passed!
```

### Targeted PE Tests

```powershell
C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe -m pytest tests/test_workflow_state_machine.py tests/test_check_current_pe.py tests/test_check_role_registration.py --basetemp=C:\Users\carlo\ELIS-SLR-Agent\.tmp\pe-infra-slr-06-targeted -q --tb=short
.....................                                                    [100%]
```

### Full Test Suite

```powershell
C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe -m pytest tests/ --basetemp=C:\Users\carlo\ELIS-SLR-Agent\.tmp\pe-infra-slr-06-full --tb=no -q
........................................................................ [  7%]
........................................................................ [ 14%]
........................................................................ [ 21%]
........................................................................ [ 28%]
........................................................................ [ 35%]
........................................................................ [ 42%]
........................................................................ [ 49%]
........................................................................ [ 56%]
........................................................................ [ 63%]
........................................................................ [ 70%]
........................................................................ [ 77%]
........................................................................ [ 84%]
........................................................................ [ 91%]
...................................................................FF... [ 98%]
..............                                                           [100%]
============================== warnings summary ===============================
tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-06\elis\pipeline\screen.py:276: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    else g.get("year_to", dt.datetime.utcnow().year)

tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-06\elis\pipeline\screen.py:30: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

tests/test_pipeline_search.py::TestBuildRunInputs::test_defaults
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-06\elis\pipeline\search.py:154: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    year_to = int(g.get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-06\elis\pipeline\search.py:405: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    y1 = int(config.get("global", {}).get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-06\elis\pipeline\search.py:43: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_missing
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_lacks_oauth_key
```

The full-suite failures are not in PE-INFRA-SLR-06 scope. This branch does not modify `tests/test_verify_claude_auth.py` or Claude-auth verification logic:

```powershell
git diff --name-status -- tests/test_verify_claude_auth.py scripts/verify_claude_auth.py elis/verify_claude_auth.py
```

(no output)

---

## Notes for Validator

- Validate AC-1 through AC-5 against `ELIS_MultiAgent_Implementation_Plan_v1_9.md` verbatim.
- Start with `tests/test_workflow_state_machine.py`; it is the PE-specific validation surface.
- `scripts/dispatch_validator_runner.py` is intentionally format-only to satisfy the full pinned Black gate.
- The two full-suite failures are unrelated to this PE and should be treated separately from the state-machine work unless CI shows a different result.
