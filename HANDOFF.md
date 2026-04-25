# HANDOFF - PE-SLR-11

**PE:** PE-SLR-11  
**Branch:** feature/pe-slr-11-implementer-runner-local-first-confirmation  
**Implementer:** CODEX  
**Date:** 2026-04-25  
**Base branch:** main  
**Implementation commit:** `3b5f51db6d763c607d4df0035769e1f4d0e6cb97`

---

## Summary

PE-SLR-11 confirms and hardens the implementer-runner local-first contract.

The implementation:

- adds `scripts/check_implementer_runner_local_first.py`, a PE-specific contract
  check proving that the implementer runner:
  - runs on `[self-hosted, elis-server]`;
  - exposes the governed `workflow_dispatch` inputs;
  - invokes both implementer entrypoints with `--pe-id`, `--plan`, `--branch`,
    and `--base-branch`;
  - emits the PM started webhook; and
  - reads `CURRENT_PE.md` and the active plan before building the agent prompt;
- tightens `scripts/implementer_runner_common.py` so PR creation/readying is
  reserved for the runner, not the agent prompt;
- adds `ensure_handoff_ready_for_pr()` so the runner refuses PR operations unless
  the working tree is clean and `HANDOFF.md` is part of the last commit;
- moves the PR-create guard before `create_draft_pr()` in `run_implementer()`,
  ensuring `HANDOFF.md` is committed before any PR is opened;
- updates the implementer prompt to include the active plan acceptance criteria
  explicitly and to tell the agent not to open or ready the PR itself; and
- adds focused tests covering the local-first check, prompt contract, handoff
  guard, and PR-operation ordering.

No PR was opened before this HANDOFF commit. That ordering is intentional for
PE-SLR-11 AC-3.

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/check_implementer_runner_local_first.py` | New local verification check for the implementer-runner contract. |
| `scripts/implementer_runner_common.py` | Tighten implementer prompt, add handoff-before-PR guard, and enforce guard before PR creation. |
| `tests/test_implementer_runner_common.py` | Add prompt, handoff guard, and PR operation ordering tests. |
| `tests/test_implementer_runner_local_first.py` | Add focused tests for the new local-first contract check. |
| `HANDOFF.md` | Replace previous PE handoff with PE-SLR-11 handoff and Status Packet. |

---

## Design Decisions

- **Runner owns PR operations:** the agent prompt now explicitly tells the
  implementer agent not to open, refresh, or ready the PR. The runner performs
  PR operations only after checking the handoff contract.
- **AC-3 takes precedence over draft-PR habit:** this PE specifically confirms
  that `HANDOFF.md` is committed before the PR is opened. The PR is therefore
  intentionally opened only after this handoff commit.
- **Local verification is executable:** `check_implementer_runner_local_first.py`
  checks the live repository workflow and runner code instead of relying only on
  prose.
- **The check reads real Step 0 context:** the local-first check parses
  `CURRENT_PE.md`, loads the active plan, extracts the active PE criteria, and
  builds the prompt before reporting PASS.

---

## Acceptance Criteria

| AC | Criterion | Result |
|----|-----------|--------|
| AC-1 | Implementer runner launches from the governed workflow and starts a local session on `elis-server`. | PASS - the new check verifies `.github/workflows/implementer-runner.yml` runs on `[self-hosted, elis-server]`, has governed dispatch inputs, invokes the implementer entrypoints, and emits the PM started webhook. |
| AC-2 | The implementer session reads `CURRENT_PE.md` and the active plan before changing files. | PASS - `run_implementer()` parses `CURRENT_PE.md` and `build_prompt()` extracts active-plan criteria before `run_cli()` invokes the agent; tests and the local-first check cover this path. |
| AC-3 | `HANDOFF.md` is committed before the PR is opened. | PASS - `ensure_handoff_ready_for_pr()` now runs before `create_draft_pr()`, and no PE-SLR-11 PR existed before this HANDOFF commit. |
| AC-4 | The feature branch stays scope-safe and contains only PE-intended changes. | PASS - committed scope contains only runner contract code, focused tests, and `HANDOFF.md`. |
| AC-5 | Local verification proves the runner invocation path is stable. | PASS - `check_implementer_runner_local_first.py`, control-plane wiring check, Black, Ruff, and 25 focused pytest tests pass locally. |

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

### PE-Specific Local-First Checks

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' scripts/check_control_plane_wiring.py
Control-plane wiring OK — agent coding is local-first and CI is bounded.
```

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' scripts/check_implementer_runner_local_first.py
Implementer runner local-first contract OK - PE-SLR-11 reads CURRENT_PE.md and ELIS_MultiAgent_Implementation_Plan_v1_9.md before agent run.
```

### Formatting

```powershell
$env:BLACK_CACHE_DIR = (Join-Path (Get-Location) '.black-cache-pe'); & 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' -m black --check --include '\.py$' elis scripts tests; $code = $LASTEXITCODE; if (Test-Path .black-cache-pe) { Remove-Item -LiteralPath (Resolve-Path .black-cache-pe).Path -Recurse -Force }; exit $code
All done! \u2728 \U0001f370 \u2728
186 files would be left unchanged.
```

### Ruff

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' -m ruff check elis scripts tests
All checks passed!
```

### PE-Specific Tests

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' -m pytest tests/test_implementer_runner_common.py tests/test_implementer_runner_local_first.py tests/test_dispatch_implementer_runner.py tests/test_control_plane_workflow_wiring.py -q -p no:cacheprovider
.........................                                                [100%]
```

PE-specific tests: PASS - 25/25 passed.

### Full Test Suite

```powershell
& 'C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe' -m pytest tests -q --tb=short -p no:cacheprovider
........................................................................ [  6%]
........................................................................ [ 13%]
........................................................................ [ 20%]
........................................................................ [ 27%]
........................................................................ [ 34%]
........................................................................ [ 41%]
........................................................................ [ 47%]
........................................................................ [ 54%]
........................................................................ [ 61%]
........................................................................ [ 68%]
........................................................................ [ 75%]
........................................................................ [ 82%]
........................................................................ [ 89%]
........................................................................ [ 95%]
.......................FF..................                              [100%]
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
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-slr-11\elis\pipeline\screen.py:276: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    else g.get("year_to", dt.datetime.utcnow().year)

tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-slr-11\elis\pipeline\screen.py:30: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

tests/test_pipeline_search.py::TestBuildRunInputs::test_defaults
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-slr-11\elis\pipeline\search.py:154: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    year_to = int(g.get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-slr-11\elis\pipeline\search.py:405: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    y1 = int(config.get("global", {}).get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-slr-11\elis\pipeline\search.py:43: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_missing
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_lacks_oauth_key
```

The full-suite failures are outside PE-SLR-11 scope. This branch does not modify
`tests/test_verify_claude_auth.py` or `scripts/verify_claude_auth.py`, as shown
by the empty diff command above.

### PR Pre-Open Evidence

```powershell
gh pr list --state open --base main --head feature/pe-slr-11-implementer-runner-local-first-confirmation
```

(no output)

This confirms no PE-SLR-11 PR existed before `HANDOFF.md` was written and
committed for this PE.

---

## Status Packet

### 6.1 Working-tree state

```powershell
git status -sb
## feature/pe-slr-11-implementer-runner-local-first-confirmation...origin/main [ahead 1]

git diff --name-status

git diff --stat
```

### 6.2 Repository state

```powershell
git fetch --all --prune

git branch --show-current
feature/pe-slr-11-implementer-runner-local-first-confirmation

git rev-parse HEAD
3b5f51db6d763c607d4df0035769e1f4d0e6cb97

git log -5 --oneline --decorate
3b5f51d (HEAD -> feature/pe-slr-11-implementer-runner-local-first-confirmation) feat(pe-slr-11): confirm local-first implementer runner
bfd5263 (origin/main, origin/HEAD, main) chore(pm): PM-CHORE-65 — close PE-INFRA-SLR-08, open PE-SLR-11
0336ffb Merge pull request #374 from rochasamurai/feature/pe-infra-slr-08-control-plane-workflow-wiring
2c80c49 (feature/pe-infra-slr-08-control-plane-workflow-wiring) test(pe-infra-slr-08): add validator review evidence
b3e94e5 docs(pe-infra-slr-08): refresh handoff after dispatch fix
```

### 6.3 Scope evidence

```powershell
git diff --name-status origin/main..HEAD
A	scripts/check_implementer_runner_local_first.py
M	scripts/implementer_runner_common.py
M	tests/test_implementer_runner_common.py
A	tests/test_implementer_runner_local_first.py
```

```powershell
git diff --stat origin/main..HEAD
 scripts/check_implementer_runner_local_first.py | 234 ++++++++++++++++++++++++
 scripts/implementer_runner_common.py            |  31 +++-
 tests/test_implementer_runner_common.py         |  77 ++++++++
 tests/test_implementer_runner_local_first.py    | 107 +++++++++++
 4 files changed, 440 insertions(+), 9 deletions(-)
```

### 6.4 Quality gates

```text
black: PASS - 186 files would be left unchanged.
ruff: PASS - All checks passed.
check_current_pe.py: PASS.
check_agent_scope.py: PASS.
check_control_plane_wiring.py: PASS.
check_implementer_runner_local_first.py: PASS.
PE-specific tests: PASS - 25/25 passed.
pytest full suite: FAIL local preflight - 2 unrelated Windows/Claude-auth failures in tests/test_verify_claude_auth.py.
GitHub Actions CI: authoritative portable gate evidence will be collected on PR after this HANDOFF commit is pushed.
```

### 6.5 PR evidence

```powershell
gh pr list --state open --base main --head feature/pe-slr-11-implementer-runner-local-first-confirmation
```

(no output)

PR intentionally not opened before HANDOFF commit to satisfy PE-SLR-11 AC-3.

---

## Notes for Validator

- Validate PE-SLR-11 AC-1 through AC-5 verbatim against
  `ELIS_MultiAgent_Implementation_Plan_v1_9.md`.
- Start with `scripts/check_implementer_runner_local_first.py`; it is the
  PE-specific proof for AC-1, AC-2, AC-3, and AC-5.
- Re-run the focused tests:
  `tests/test_implementer_runner_common.py`,
  `tests/test_implementer_runner_local_first.py`,
  `tests/test_dispatch_implementer_runner.py`, and
  `tests/test_control_plane_workflow_wiring.py`.
- The local full-suite failure is host-specific and isolated from this PE by the
  empty diff for `tests/test_verify_claude_auth.py` and
  `scripts/verify_claude_auth.py`.
