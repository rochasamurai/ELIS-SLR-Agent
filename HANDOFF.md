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
reliability and audit capabilities. A new module `elis/harvest_workflow.py`
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

**Note on implementer assignment:** Gemini CLI was the initial assignee.
Gemini stopped mid-PE on 2026-04-13; PM reassigned to Claude Code.
`CURRENT_PE.md` on `main` (commit `b260df8`) and
`ELIS_MultiAgent_Implementation_Plan_v1_8_2.md` on `main` (commit `b51cd8b`)
both record `prog-impl-claude` (Claude Code) as Implementer.

---

## Files Changed

| File | Change |
|------|--------|
| `elis/harvest_contract.py` | Added `audit_log()` path method to `HarvestWorkflowContract` |
| `elis/harvest_workflow.py` | New module — retry policy, audit log, failure diagnostics, output packaging |
| `tests/test_harvest_workflow.py` | New test file — 27 tests covering AC-1 through AC-4 |
| `docs/slr/HARVEST_WORKFLOW_CONTRACT.md` | Extended with Reliability contract section (AC-1 to AC-4) |

---

## Design Decisions

**`_sleep` injection in `run_with_retry`:** `time.sleep` is injected via
`_sleep` keyword argument. This avoids real waiting in tests without
requiring mock patches on the module namespace.

**`HarvestRetryPolicy` is frozen:** Prevents accidental mutation. The
default policy (3 attempts, 2 s backoff) mirrors a reasonable production
default; callers override by passing a new instance.

**Audit entries accumulate in a caller-owned list:** The caller passes
`audit_entries` in and `run_with_retry` appends to it. This allows a single
audit log to cover multiple sources in one run before writing to disk.

**`package_harvest_output` is pure:** No I/O — it builds a dict from path
methods. Reproducibility is guaranteed by sorted source lists and stable
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

## Status Packet

### §6.1 Working-tree state

```
$ git status -sb
## feature/pe-slr-02-harvest-workflow-reliability-audit...origin/feature/pe-slr-02-harvest-workflow-reliability-audit [ahead 5, behind 3]

$ git diff --name-status
(clean — no unstaged changes)

$ git diff --stat
(clean — no unstaged changes)
```

### §6.2 Repository state

```
$ git fetch --all --prune
(fetched)

$ git branch --show-current
feature/pe-slr-02-harvest-workflow-reliability-audit

$ git rev-parse HEAD   # implementer submission state before validator-owned review-file updates
e20c2a09d2d256ea0cb1b7f15de2fbf2961a91ff

$ git log -5 --oneline --decorate   # latest implementer / PM-visible branch history before validator follow-up commits
e20c2a0 fix(pe-slr-02): update HANDOFF Status Packet to current HEAD
e6d07f2 review(pe-slr-02): record validator round 2 fail
a485839 fix(pe-slr-02): address Validator r1 blocking findings
c23dc22 review(pe-slr-02): record validator round 1 fail
13ac360 docs(pe-slr-02): add HANDOFF.md
```

Validator-owned commits may advance the branch after the implementer handoff is submitted.
At the time of this handoff update, the latest validator-only review-file commit is:

```
6c39f56 review(pe-slr-02): reformat review file for CI
```

### §6.3 Scope evidence (vs origin/main)

```
$ git diff --name-status origin/main..HEAD
M	HANDOFF.md
A	REVIEW_PE_SLR_02.md
M	docs/slr/HARVEST_WORKFLOW_CONTRACT.md
M	elis/harvest_contract.py
A	elis/harvest_workflow.py
A	tests/test_harvest_workflow.py

$ git diff --stat origin/main..HEAD
 HANDOFF.md                            | 507 +++++++++------------------------
 REVIEW_PE_SLR_02.md                   |  63 ++++
 docs/slr/HARVEST_WORKFLOW_CONTRACT.md |  76 ++++-
 elis/harvest_contract.py              |   3 +
 elis/harvest_workflow.py              | 267 +++++++++++++++++
 tests/test_harvest_workflow.py        | 521 ++++++++++++++++++++++++++++++++++
 6 files changed, 1068 insertions(+), 369 deletions(-)
```

Note: `REVIEW_PE_SLR_02.md` was committed by CODEX (Validator) to this branch.
`HANDOFF.md` shows large deletions because it is replacing the PE-SLR-01 handoff
content that was present in the base branch.

### §6.4 Quality gates

```
$ python -m black --check .
All done! 169 files would be left unchanged.
BLACK: PASS

$ python -m ruff check .
All checks passed!
RUFF: PASS

$ python -m pytest -q
2 failed, 831 passed, 17 warnings in 19.28s
```

PE-specific tests:

```
$ python -m pytest tests/test_harvest_workflow.py -q
27 passed in 0.45s
PE-specific: 27/27 PASS
```

Pre-existing failures (not introduced by this PE):
- `tests/test_verify_claude_auth.py::test_fails_when_credentials_file_missing`
- `tests/test_verify_claude_auth.py::test_fails_when_credentials_file_lacks_oauth_key`

Both fail because `verify_claude_auth.py` invokes `claude --version` as a
subprocess and `claude.CMD` is not resolvable via `subprocess.run` without
shell=True on Windows. These failures pre-date PE-SLR-02 and are unrelated
to the changed files.
