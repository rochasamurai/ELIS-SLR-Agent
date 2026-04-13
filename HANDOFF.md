# HANDOFF — PE-SLR-02 · Harvest Workflow Reliability and Audit

**PE:** PE-SLR-02  
**Branch:** feature/pe-slr-02-harvest-workflow-reliability-audit  
**PR:** #324  
**Base:** main  
**Implementer:** Claude Code (`prog-impl-claude`)  
**Validator:** CODEX (`prog-val-codex` @ `elis-server`)  
**Date:** 2026-04-13

---

## Summary

PE-SLR-02 strengthens the Harvest workflow established in PE-SLR-01 with
reliability and audit capabilities.  A new module `elis/harvest_workflow.py`
provides:

- **`HarvestRetryPolicy`** — configurable retry behaviour (max attempts,
  backoff seconds)
- **`HarvestAuditEntry`** — structured JSONL log entry for each step attempt
- **`HarvestStepError`** — operator-visible failure diagnostic raised after
  exhausting retries
- **`run_with_retry()`** — execute any callable with retry semantics, audit
  trail, and sleep injection for testability
- **`write_audit_log()`** — persist audit entries as sorted JSONL under the
  evidence contract path
- **`package_harvest_output()`** — build a deterministic, review-scoped
  output manifest

`HarvestWorkflowContract` gains an `audit_log()` path method.
`HARVEST_WORKFLOW_CONTRACT.md` gains a Reliability contract section
documenting all four AC invariants.

---

## Files Changed

| File | Change |
|------|--------|
| `elis/harvest_contract.py` | Added `audit_log()` path method to `HarvestWorkflowContract` |
| `elis/harvest_workflow.py` | New module — retry policy, audit log, failure diagnostics, output packaging |
| `tests/test_harvest_workflow.py` | New test file — 27 tests covering AC-1 through AC-4 |
| `docs/slr/HARVEST_WORKFLOW_CONTRACT.md` | Extended with Reliability contract section (AC-1 to AC-4) |
| `CURRENT_PE.md` | Implementer reassigned from Gemini CLI to Claude Code (PM chore) |

---

## Design Decisions

**`_sleep` injection in `run_with_retry`**: `time.sleep` is injected via
`_sleep` keyword argument.  This avoids any real waiting in tests without
requiring mock patches on the module namespace.

**`HarvestRetryPolicy` is frozen**: Prevents accidental mutation.  The
default policy (3 attempts, 2 s backoff) mirrors a reasonable production
default; callers override by passing a new instance.

**Audit entries accumulate in a caller-owned list**: The caller passes
`audit_entries` in and `run_with_retry` appends to it.  This allows a single
audit log to cover multiple sources in one run before writing to disk.

**`package_harvest_output` is pure**: No I/O — it builds a dict from path
methods.  Reproducibility is guaranteed by sorted source lists and stable
`HarvestWorkflowContract` path methods.

---

## Acceptance Criteria Checklist

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | Harvest workflow logs are sufficient for audit replay | **PASS** |
| AC-2 | Failure paths produce explicit operator-visible diagnostics | **PASS** |
| AC-3 | Retry policy is documented and tested | **PASS** |
| AC-4 | Output packaging is reproducible and review-specific | **PASS** |
| AC-5 | `python -m pytest tests/test_harvest_workflow.py -v` passes | **PASS** |

---

## Validation Commands and Output

### AC-5 — PE-specific test run

```
$ python -m pytest tests/test_harvest_workflow.py -v
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.1, pluggy-1.6.0
rootdir: C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-slr-02
configfile: pyproject.toml
plugins: cov-7.0.0
collected 27 items

tests\test_harvest_workflow.py ...........................               [100%]

============================= 27 passed in 0.45s ==============================
```

### Quality gates

```
$ python -m black --check .
All done! 169 files would be left unchanged.
BLACK: PASS

$ python -m ruff check .
All checks passed!
RUFF: PASS
```

### Scope gate

```
$ git diff --name-status origin/main..HEAD
M	CURRENT_PE.md
M	docs/slr/HARVEST_WORKFLOW_CONTRACT.md
M	elis/harvest_contract.py
A	elis/harvest_workflow.py
A	tests/test_harvest_workflow.py

$ git diff --stat origin/main..HEAD
 CURRENT_PE.md                         |   7 +-
 docs/slr/HARVEST_WORKFLOW_CONTRACT.md |  76 ++++-
 elis/harvest_contract.py              |   3 +
 elis/harvest_workflow.py              | 267 +++++++++++++++++
 tests/test_harvest_workflow.py        | 521 ++++++++++++++++++++++++++++++++++
 5 files changed, 867 insertions(+), 7 deletions(-)
```

### HEAD commit

```
186a1d9 feat(pe-slr-02): harvest workflow reliability and audit
```

---

## Pre-existing Defects (not introduced by this PE)

| Defect | File | Blocking? |
|--------|------|-----------|
| `test_fails_when_credentials_file_missing` — subprocess call to `claude` CLI fails (FileNotFoundError) in local test runner | `tests/test_verify_claude_auth.py` | No |
| `test_fails_when_credentials_file_lacks_oauth_key` — same cause | `tests/test_verify_claude_auth.py` | No |
