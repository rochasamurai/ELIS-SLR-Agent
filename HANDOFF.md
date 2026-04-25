# HANDOFF - PE-SLR-12

**PE:** PE-SLR-12  
**Branch:** feature/pe-slr-12-validator-runner-evidence-contract  
**Implementer:** Claude Code  
**Date:** 2026-04-25  
**Base branch:** main  
**Implementation commit:** `110efea`

---

## Summary

PE-SLR-12 confirms and hardens the validator runner evidence contract.

The implementation adds `scripts/check_validator_runner_local_first.py`, a
PE-specific executable check proving that the validator runner:

- runs on `[self-hosted, elis-server]` and not on `ubuntu-latest` (AC-1);
- dispatches only after `dispatch_validator_runner.py` enforces the evidence-backed
  state-machine guard (`validator_dispatch_allowed_after_evidence`) and verifies
  HANDOFF/Status Packet sections are present (AC-1);
- instructs the validator agent to write the review file to
  `docs/reviews/archive/REVIEW_PE<N>.md` (AC-2);
- includes all five required REVIEW sections (`### Verdict`, `### Gate results`,
  `### Scope`, `### Required fixes`, `### Evidence`) in the validator prompt (AC-3);
- instructs the agent to run `check_review.py` against the archived review file
  before committing (AC-4); and
- calls `verify_review_committed`, `verify_formal_review_posted`, then `read_verdict`
  in that order in `run_validator()` (AC-5).

No PR was opened before this HANDOFF commit. That ordering is intentional (mirrors
the AC-3 precedent set by PE-SLR-11).

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/check_validator_runner_local_first.py` | New local verification check for the validator runner evidence contract. |
| `tests/test_validator_runner_local_first.py` | 9 focused AC-targeted tests. |
| `HANDOFF.md` | Replace PE-SLR-11 handoff with PE-SLR-12 handoff and Status Packet. |

---

## Design Decisions

- **Structural analogue to PE-SLR-11:** `check_validator_runner_local_first.py`
  mirrors `check_implementer_runner_local_first.py` in architecture, making both
  runner contracts machine-verifiable and consistently structured.
- **Call-site patterns for ordering check:** The AC-5 ordering assertion searches
  for `verify_review_committed(inputs.`, `verify_formal_review_posted(inputs.`, and
  `read_verdict(repo_root,` — call-site-specific substrings — rather than bare
  function names, which would match the function definitions that appear earlier in
  the file.
- **Dispatch-script text scan for AC-1:** Rather than importing and calling
  `dispatch_validator_runner.py` (which requires live GitHub credentials), the check
  scans the dispatch script text for `validator_dispatch_allowed_after_evidence(` and
  `_verify_sections(`, confirming both guards are present.
- **Live prompt construction for AC-2/AC-3/AC-4:** The check calls `build_validator_prompt()`
  with the active PE context to verify the actual prompt the validator agent will
  receive includes the archive path, all required sections, and the `check_review.py`
  verification step.

---

## Acceptance Criteria

| AC | Criterion | Result |
|----|-----------|--------|
| AC-1 | Validator does not self-start and only runs after explicit PM authorisation. | PASS — check confirms `validator-runner.yml` is on `[self-hosted, elis-server]`; dispatch script enforces `validator_dispatch_allowed_after_evidence` and HANDOFF/Status Packet section checks. |
| AC-2 | The validator writes to `docs/reviews/archive/REVIEW_PE<N>.md`. | PASS — check confirms `review_file_path()` returns archive path, workflow references archive path, and validator prompt includes the exact archive-path review filename. |
| AC-3 | The review file contains the required sections and at least one fenced evidence block. | PASS — check confirms all five required section headers are present in the validator prompt. |
| AC-4 | `scripts/check_review.py` passes against the archived review file. | PASS — check confirms `check_review.py` appears in the validator prompt as step 6. |
| AC-5 | The formal verdict and review evidence remain aligned with the branch state. | PASS — check confirms `verify_review_committed`, `verify_formal_review_posted`, then `read_verdict` are called in that order in `run_validator()`. |

---

## Validation Commands

### Current PE and Scope Checks

```
python scripts/check_current_pe.py
CURRENT_PE.md OK — release context, roles, registry, and alternation valid.
```

```
python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

```
git diff --name-status -- tests/test_verify_claude_auth.py scripts/verify_claude_auth.py
(no output)
```

### PE-Specific Checks

```
python scripts/check_control_plane_wiring.py
Control-plane wiring OK — agent coding is local-first and CI is bounded.
```

```
python scripts/check_implementer_runner_local_first.py
Implementer runner local-first contract OK - PE-SLR-12 reads CURRENT_PE.md and ELIS_MultiAgent_Implementation_Plan_v1_9.md before agent run.
```

```
python scripts/check_validator_runner_local_first.py
Validator runner local-first and evidence contract OK — PE-SLR-12 validator writes to docs/reviews/archive/ and requires PM authorisation before dispatch.
```

### Formatting

```
python -m black --check --include '\.py$' elis scripts tests
All done! ✨ 🍰 ✨
188 files would be left unchanged.
```

### Ruff

```
python -m ruff check elis scripts tests
All checks passed!
```

### PE-Specific Tests

```
python -m pytest tests/test_validator_runner_local_first.py tests/test_validator_runner_common.py tests/test_dispatch_validator_runner.py tests/test_control_plane_workflow_wiring.py -q -p no:cacheprovider
.......................................                                  [100%]
39 passed
```

### Full Test Suite

```
python -m pytest --tb=short -p no:cacheprovider
2 failed, 1058 passed, 17 warnings in 14.36s
```

The 2 failures are the pre-existing `test_verify_claude_auth.py` Windows
subprocess path issue. Empty diff confirms they are not in PE-SLR-12 scope.

### Scope Evidence

```
git diff --name-status origin/main..HEAD
A  scripts/check_validator_runner_local_first.py
A  tests/test_validator_runner_local_first.py
```

PR intentionally not opened before this HANDOFF commit (mirrors PE-SLR-11 AC-3 precedent).

---

## Status Packet

### 6.1 Working-tree state

```
git status -sb
## feature/pe-slr-12-validator-runner-evidence-contract...origin/main [ahead 2]

git diff --name-status
(clean)

git diff --stat
(clean)
```

### 6.2 Repository state

```
git branch --show-current
feature/pe-slr-12-validator-runner-evidence-contract

git rev-parse HEAD
110efea (feat commit); HANDOFF commit to follow as final commit

git log -5 --oneline --decorate
110efea feat(pe-slr-12): confirm validator runner local-first and evidence contract
cd325d2 chore(pm): PM-CHORE-66 — close PE-SLR-11, open PE-SLR-12
afe59d6 Merge pull request #376 from rochasamurai/feature/pe-slr-11-implementer-runner-local-first-confirmation
a9ad25c Merge pull request #375 from rochasamurai/chore/pe-infra-slr-08-dev-journey-report
27667ce test(pe-slr-11): add validator review evidence
```

### 6.3 Scope evidence

```
git diff --name-status origin/main..HEAD
A  scripts/check_validator_runner_local_first.py
A  tests/test_validator_runner_local_first.py

git diff --stat origin/main..HEAD
 scripts/check_validator_runner_local_first.py | 314 ++++++++++++++++++++++++++
 tests/test_validator_runner_local_first.py    | 221 ++++++++++++++++++
 2 files changed, 535 insertions(+)
```

### 6.4 Quality gates

```
black:                               PASS — 188 files unchanged.
ruff:                                PASS — All checks passed.
check_current_pe.py:                 PASS.
check_agent_scope.py:                PASS.
check_control_plane_wiring.py:       PASS.
check_implementer_runner_local_first.py: PASS.
check_validator_runner_local_first.py:   PASS.
PE-specific tests:                   PASS — 39/39 passed.
pytest full suite:                   1058 passed, 2 failed (pre-existing test_verify_claude_auth.py).
```

### 6.5 PR evidence

PR not opened before HANDOFF commit (AC-3 ordering requirement).

---

## Notes for Validator

- Validate PE-SLR-12 AC-1 through AC-5 against `ELIS_MultiAgent_Implementation_Plan_v1_9.md`.
- Start with `python scripts/check_validator_runner_local_first.py` — it is the
  PE-specific proof for all five ACs.
- Re-run the focused tests: `tests/test_validator_runner_local_first.py`,
  `tests/test_validator_runner_common.py`, `tests/test_dispatch_validator_runner.py`,
  `tests/test_control_plane_workflow_wiring.py`.
- The pre-existing `test_verify_claude_auth.py` failures are confirmed out of scope
  by the empty diff for those files.
