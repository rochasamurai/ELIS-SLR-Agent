# HANDOFF - PE-INFRA-SLR-08

**PE:** PE-INFRA-SLR-08  
**Branch:** feature/pe-infra-slr-08-control-plane-workflow-wiring  
**Implementer:** CODEX (`infra-impl-a`)  
**Date:** 2026-04-24  
**Base branch:** main  
**Implementation commit:** `15498d8df25351e5d14478fc629c74505fce4dbc`

---

## Summary

PE-INFRA-SLR-08 wires the GitHub Actions control plane to the v1.9 workflow
state machine and local-first execution boundary.

The implementation:

- adds dispatch helper constants/functions to `elis/workflow_state_machine.py`;
- validates parsed `CURRENT_PE.md` statuses against canonical workflow states;
- updates implementer and validator dispatch scripts to use the state-machine
  helpers instead of duplicating raw string checks;
- keeps validator dispatch blocked until the `gate-1-pending -> validating`
  transition is allowed and required HANDOFF/Status Packet evidence is present;
- replaces brittle provider-substring validator mention logic in
  `auto-assign-validator.yml` with `scripts/resolve_validator_handle.py`;
- adds `scripts/check_control_plane_wiring.py` to prove development-agent coding
  entrypoints stay on the self-hosted `elis-server` runner and CI workflows stay
  bounded to gates;
- documents the control-plane boundary in `AGENTS.md`,
  `docs/workflow/PE_STATE_MACHINE.md`, and ADR-014; and
- adds focused tests for the wiring, dispatch helpers, and Gate 1 state guard.

---

## Files Changed

| File | Change |
|------|--------|
| `.github/workflows/auto-assign-validator.yml` | Use the model-agnostic validator handle resolver instead of inline provider substring parsing. |
| `AGENTS.md` | Document GitHub Actions as control plane, not the development-agent coding substrate. |
| `docs/decisions/ADR-014-control-plane-workflow-wiring.md` | New ADR for the control-plane workflow boundary. |
| `docs/decisions/README.md` | Add ADR-014 to the ADR index. |
| `docs/workflow/PE_STATE_MACHINE.md` | Add the control-plane wiring section and validation command. |
| `elis/workflow_state_machine.py` | Add dispatch state constants and helper functions. |
| `scripts/check_control_plane_wiring.py` | New repository check for local-first agent runners and bounded CI workflows. |
| `scripts/dispatch_implementer_runner.py` | Use the canonical implementer dispatch helper. |
| `scripts/dispatch_validator_runner.py` | Use canonical validator transition helpers and report guard evidence on blocked dispatch. |
| `scripts/implementer_runner_common.py` | Reject non-canonical `CURRENT_PE.md` registry statuses during parse. |
| `scripts/pm_gate_evaluator.py` | Add Gate 1 source-state guard aligned to `gate-1-pending -> validating`. |
| `tests/test_control_plane_workflow_wiring.py` | New focused control-plane wiring tests. |
| `tests/test_pm_gate_evaluator.py` | Add a Gate 1 state-machine source guard test. |
| `tests/test_workflow_state_machine.py` | Cover dispatch helpers and control-plane documentation language. |

---

## Design Decisions

- **State-machine helpers live in `elis/workflow_state_machine.py`:** dispatch
  eligibility is part of the lifecycle contract, so the implementer and
  validator dispatch scripts now consume the canonical mirror rather than
  hardcoding state strings locally.
- **Workflow boundary check is conservative:** only the implementer and validator
  runner workflows may invoke development-agent coding entrypoints, and they
  must run on the self-hosted `elis-server` surface.
- **CI remains credential-free:** the new check rejects bot/App credentials in
  CI workflows so portable gates stay reproducible and merge-authoritative.
- **Validator mention resolution is model-agnostic:** `auto-assign-validator.yml`
  now delegates to the existing resolver, which handles role-slot IDs such as
  `infra-val-a` / `infra-val-b` correctly.

---

## Acceptance Criteria

| AC | Criterion | Result |
|----|-----------|--------|
| AC-1 | Implementer and validator dispatch paths are aligned with the state machine and local-first execution surface. | PASS - dispatch scripts use canonical state-machine helpers; runner workflows stay on `[self-hosted, elis-server]`; focused tests cover both paths. |
| AC-2 | Workflow files do not attempt to perform GitHub-hosted agent coding where `elis-server` is the intended execution surface. | PASS - `scripts/check_control_plane_wiring.py` and tests fail if Codex/Claude development-agent entrypoints appear outside local runner workflows or on `ubuntu-latest`. |
| AC-3 | Portable gates remain bounded to CI/test duties: formatting, linting, validation, and tests. | PASS - the control-plane check verifies CI workflows avoid bot/App credentials and agent coding entrypoints while retaining portable gate commands. |
| AC-4 | Validator dispatch is blocked until implementer-complete evidence exists. | PASS - `dispatch_validator_runner.py` still requires HANDOFF and Status Packet sections and now also requires the canonical `gate-1-pending -> validating` source state. |
| AC-5 | The workflow/documentation pair describes GitHub Actions as control plane, not the coding substrate. | PASS - `AGENTS.md`, `docs/workflow/PE_STATE_MACHINE.md`, and ADR-014 all state the control-plane boundary; tests assert the governing language is present. |

---

## Validation Commands

### Current PE and Scope Checks

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' scripts/check_current_pe.py
CURRENT_PE.md OK — release context, roles, registry, and alternation valid.
```

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

```powershell
git diff --name-status -- tests/test_verify_claude_auth.py scripts/verify_claude_auth.py
```

(no output)

### Formatting

```powershell
$env:BLACK_CACHE_DIR = (Join-Path (Get-Location) '.black-cache-pe'); & 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' -m black --check --include "\.py$" elis/ scripts/ tests/; if (Test-Path .black-cache-pe) { Remove-Item -LiteralPath (Resolve-Path .black-cache-pe).Path -Recurse -Force }
All done! \u2728 \U0001f370 \u2728
184 files would be left unchanged.
```

### Ruff

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' -m ruff check elis scripts tests
All checks passed!
```

### Control-Plane Wiring Check

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' scripts/check_control_plane_wiring.py
Control-plane wiring OK — agent coding is local-first and CI is bounded.
```

### PE-Specific Tests

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' -m pytest tests/test_control_plane_workflow_wiring.py tests/test_workflow_state_machine.py tests/test_dispatch_implementer_runner.py tests/test_dispatch_validator_runner.py tests/test_pm_gate_evaluator.py -q -p no:cacheprovider
............................                                             [100%]
```

### Full Test Suite

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' -m pytest tests/ -q --tb=short -p no:cacheprovider
........................................................................ [  6%]
........................................................................ [ 13%]
........................................................................ [ 20%]
........................................................................ [ 27%]
........................................................................ [ 34%]
........................................................................ [ 41%]
........................................................................ [ 48%]
........................................................................ [ 55%]
........................................................................ [ 62%]
........................................................................ [ 69%]
........................................................................ [ 76%]
........................................................................ [ 82%]
........................................................................ [ 89%]
........................................................................ [ 96%]
..............FF..................                                       [100%]
================================== FAILURES ===================================
__________________ test_fails_when_credentials_file_missing ___________________
tests\test_verify_claude_auth.py:32: in test_fails_when_credentials_file_missing
    assert verify_claude_auth.main() == 1
           ^^^^^^^^^^^^^^^^^^^^^^^^^
scripts\verify_claude_auth.py:76: in main
    result = subprocess.run(
..\..\.python-runtime\pythoncore-3.14-64\Lib\subprocess.py:554: in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\.python-runtime\pythoncore-3.14-64\Lib\subprocess.py:1038: in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
..\..\.python-runtime\pythoncore-3.14-64\Lib\subprocess.py:1552: in _execute_child
    hp, ht, pid, tid = _winapi.CreateProcess(executable, args,
E   FileNotFoundError: [WinError 2] The system cannot find the file specified
---------------------------- Captured stdout call -----------------------------
OK: CLAUDE_CREDENTIALS_JSON is set (length=17)
OK: credentials file exists at C:\Users\carlo\.claude\.credentials.json
OK: credentials file contains claudeAiOauth entry
OK: claude CLI found at C:\Users\carlo\AppData\Roaming\npm\claude.CMD
______________ test_fails_when_credentials_file_lacks_oauth_key _______________
tests\test_verify_claude_auth.py:40: in test_fails_when_credentials_file_lacks_oauth_key
    assert verify_claude_auth.main() == 1
           ^^^^^^^^^^^^^^^^^^^^^^^^^
scripts\verify_claude_auth.py:76: in main
    result = subprocess.run(
..\..\.python-runtime\pythoncore-3.14-64\Lib\subprocess.py:554: in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\.python-runtime\pythoncore-3.14-64\Lib\subprocess.py:1038: in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
..\..\.python-runtime\pythoncore-3.14-64\Lib\subprocess.py:1552: in _execute_child
    hp, ht, pid, tid = _winapi.CreateProcess(executable, args,
E   FileNotFoundError: [WinError 2] The system cannot find the file specified
---------------------------- Captured stdout call -----------------------------
OK: CLAUDE_CREDENTIALS_JSON is set (length=17)
OK: credentials file exists at C:\Users\carlo\.claude\.credentials.json
OK: credentials file contains claudeAiOauth entry
OK: claude CLI found at C:\Users\carlo\AppData\Roaming\npm\claude.CMD
============================== warnings summary ===============================
tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-08\elis\pipeline\screen.py:276: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    else g.get("year_to", dt.datetime.utcnow().year)

tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-08\elis\pipeline\screen.py:30: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

tests/test_pipeline_search.py::TestBuildRunInputs::test_defaults
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-08\elis\pipeline\search.py:154: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    year_to = int(g.get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-08\elis\pipeline\search.py:405: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    y1 = int(config.get("global", {}).get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-08\elis\pipeline\search.py:43: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_missing
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_lacks_oauth_key
```

The full-suite failures are outside PE-INFRA-SLR-08 scope. This branch does not
modify `tests/test_verify_claude_auth.py` or `scripts/verify_claude_auth.py`, as
shown by the empty diff command above.

---

## Status Packet

### 6.1 Working-tree state

```powershell
git status -sb
## feature/pe-infra-slr-08-control-plane-workflow-wiring...origin/main [ahead 1]
warning: unable to access 'C:\Users\carlo/.config/git/ignore': Permission denied
warning: unable to access 'C:\Users\carlo/.config/git/ignore': Permission denied

git diff --name-status

git diff --stat
```

### 6.2 Repository state

```powershell
git fetch --all --prune

git branch --show-current
feature/pe-infra-slr-08-control-plane-workflow-wiring

git rev-parse HEAD
15498d8df25351e5d14478fc629c74505fce4dbc

git log -5 --oneline --decorate
15498d8 (HEAD -> feature/pe-infra-slr-08-control-plane-workflow-wiring) feat(pe-infra-slr-08): wire control-plane workflow guards
2bbdcea (origin/main, origin/HEAD, main) chore(pm): PM-CHORE-64 — close PE-INFRA-SLR-07, open PE-INFRA-SLR-08
ce06c48 Merge pull request #373 from rochasamurai/feature/pe-infra-slr-07-review-archive-migration
b064040 test(pe-infra-slr-07): add validator review evidence
98b578d (feature/pe-infra-slr-07-review-archive-migration) docs(pe-infra-slr-07): update handoff — DOCUMENT_CLASSIFICATION fix and test count
```

### 6.3 Scope evidence

```powershell
git diff --name-status origin/main..HEAD
M	.github/workflows/auto-assign-validator.yml
M	AGENTS.md
A	docs/decisions/ADR-014-control-plane-workflow-wiring.md
M	docs/decisions/README.md
M	docs/workflow/PE_STATE_MACHINE.md
M	elis/workflow_state_machine.py
A	scripts/check_control_plane_wiring.py
M	scripts/dispatch_implementer_runner.py
M	scripts/dispatch_validator_runner.py
M	scripts/implementer_runner_common.py
M	scripts/pm_gate_evaluator.py
A	tests/test_control_plane_workflow_wiring.py
M	tests/test_pm_gate_evaluator.py
M	tests/test_workflow_state_machine.py

git diff --stat origin/main..HEAD
 .github/workflows/auto-assign-validator.yml        |  30 +----
 AGENTS.md                                          |   5 +
 .../ADR-014-control-plane-workflow-wiring.md       |  76 +++++++++++
 docs/decisions/README.md                           |   1 +
 docs/workflow/PE_STATE_MACHINE.md                  |  24 ++++
 elis/workflow_state_machine.py                     |  26 ++++
 scripts/check_control_plane_wiring.py              | 140 +++++++++++++++++++++
 scripts/dispatch_implementer_runner.py             |   3 +-
 scripts/dispatch_validator_runner.py               |  19 ++-
 scripts/implementer_runner_common.py               |   5 +
 scripts/pm_gate_evaluator.py                       |  18 ++-
 tests/test_control_plane_workflow_wiring.py        |  73 +++++++++++
 tests/test_pm_gate_evaluator.py                    |  17 +++
 tests/test_workflow_state_machine.py               |  16 +++
 14 files changed, 418 insertions(+), 35 deletions(-)
```

### 6.4 Quality gates

```powershell
black: PASS - 184 files would be left unchanged.
ruff: PASS - All checks passed!
PE-specific tests: PASS - 28 passed.
Control-plane wiring check: PASS.
pytest full suite: FAIL local preflight - 2 unrelated Windows/Claude-auth failures; all other tests pass.
```

### 6.5 PR evidence

```powershell
gh pr list --state open --base main
HTTP 401: Requires authentication (https://api.github.com/graphql)
Try authenticating with:  gh auth login
```

No PR has been opened from this session because the local `gh` session is not
authenticated.

---

## Notes for Validator

- Validate PE-INFRA-SLR-08 AC-1 through AC-5 verbatim against
  `ELIS_MultiAgent_Implementation_Plan_v1_9.md`.
- Start with `scripts/check_control_plane_wiring.py` and
  `tests/test_control_plane_workflow_wiring.py`; they are the PE-specific
  enforcement surface for AC-1 through AC-5.
- The local full-suite failure is pre-existing/host-specific and isolated from
  this PE by the empty diff for `tests/test_verify_claude_auth.py` and
  `scripts/verify_claude_auth.py`.
