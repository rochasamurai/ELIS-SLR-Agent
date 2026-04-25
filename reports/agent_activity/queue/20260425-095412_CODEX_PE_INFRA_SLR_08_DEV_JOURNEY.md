# Development Journey Report - CODEX - PE-INFRA-SLR-08

## Metadata

- **Agent:** CODEX
- **Role for this unit:** Implementer
- **PE / Unit:** PE-INFRA-SLR-08 - Control-Plane GitHub Workflow Wiring
- **Implementation branch:** `feature/pe-infra-slr-08-control-plane-workflow-wiring`
- **Methodology-report branch:** `chore/pe-infra-slr-08-dev-journey-report`
- **Target base:** `main`
- **PR:** #374 - https://github.com/rochasamurai/ELIS-Multi-AI-Agent-Platform/pull/374
- **Merged at:** 2026-04-25T07:29:30Z
- **Merge commit:** `0336ffb931f523273fb5a8f17ea9996aec323231`
- **Post-merge PM transition:** `bfd5263 chore(pm): PM-CHORE-65 - close PE-INFRA-SLR-08, open PE-SLR-11`
- **Report generated:** 2026-04-25 09:54:12 +01:00

## Purpose

This document records the PE-INFRA-SLR-08 implementation journey for
methodology improvement. It captures the implementation sequence, the issue
found by live GitHub automation, the sandbox and GitHub authorisation prompts,
the tests and checks run locally and in CI, and the GitHub commands used to
inspect or operate the PR.

The report is intentionally more procedural than `HANDOFF.md`. `HANDOFF.md`
summarises implementation and validator-facing evidence; this document records
the operational path, including friction points.

## PE Scope

PE-INFRA-SLR-08 acceptance criteria from
`ELIS_MultiAgent_Implementation_Plan_v1_9.md`:

| AC | Criterion |
|----|-----------|
| AC-1 | Implementer and validator dispatch paths are aligned with the state machine and local-first execution surface. |
| AC-2 | Workflow files do not attempt to perform GitHub-hosted agent coding where `elis-server` is the intended execution surface. |
| AC-3 | Portable gates remain bounded to CI/test duties: formatting, linting, validation, and tests. |
| AC-4 | Validator dispatch is blocked until implementer-complete evidence exists. |
| AC-5 | The workflow/documentation pair describes GitHub Actions as control plane, not the coding substrate. |

## Final Outcome

- PR #374 merged successfully.
- Validator verdict: PASS.
- `docs/reviews/archive/REVIEW_PE_INFRA_SLR_08.md` was committed by the
  Validator at `2c80c49`.
- Automated Gate 1 passed after the implementation fix.
- The first live `validator-dispatch` run failed, exposed a real workflow gap,
  and was fixed within the PE.
- The branch was merged by automation after Validator PASS and green checks.

## Timeline

### 1. Step 0 and canonical context

CODEX read the required governance files before implementation:

- `CURRENT_PE.md`
- `AGENTS.md`
- `LESSONS_LEARNED.md`
- `AUDITS.md`
- `ELIS_MultiAgent_Implementation_Plan_v1_9.md`
- `HANDOFF.md` from the previous PE where relevant
- `docs/workflow/PE_STATE_MACHINE.md`
- `elis/workflow_state_machine.py`
- related ADR material for state-machine and CI authority decisions

The active assignment confirmed:

- PE: `PE-INFRA-SLR-08`
- Branch: `feature/pe-infra-slr-08-control-plane-workflow-wiring`
- Base: `main`
- CODEX: Implementer
- Claude Code: Validator

### 2. Worktree and branch

A dedicated worktree was used:

```text
c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-08
```

The implementation branch was:

```text
feature/pe-infra-slr-08-control-plane-workflow-wiring
```

The first implementation commit was:

```text
15498d8 feat(pe-infra-slr-08): wire control-plane workflow guards
```

### 3. Initial implementation

The initial implementation aligned the workflow control plane with the v1.9
state machine:

- `elis/workflow_state_machine.py`
  - Added dispatch state constants.
  - Added helper functions for implementer and validator dispatch eligibility.
- `scripts/implementer_runner_common.py`
  - Rejected non-canonical `CURRENT_PE.md` statuses during parse.
- `scripts/dispatch_implementer_runner.py`
  - Used the canonical implementer dispatch helper.
- `scripts/dispatch_validator_runner.py`
  - Used canonical validator transition helpers.
  - Checked required HANDOFF and Status Packet sections.
- `scripts/pm_gate_evaluator.py`
  - Added Gate 1 state-machine source-state guard.
- `.github/workflows/auto-assign-validator.yml`
  - Replaced inline provider-substring parsing with
    `scripts/resolve_validator_handle.py`.
- `scripts/check_control_plane_wiring.py`
  - Added a repository check proving development-agent coding entrypoints remain
    local-first on `elis-server`.
- `tests/test_control_plane_workflow_wiring.py`
  - Added focused control-plane boundary tests.
- `tests/test_workflow_state_machine.py`
  - Added dispatch helper and documentation assertions.
- `tests/test_pm_gate_evaluator.py`
  - Added Gate 1 state guard coverage.
- `docs/workflow/PE_STATE_MACHINE.md`, `AGENTS.md`, and ADR-014
  - Documented GitHub Actions as control plane rather than coding substrate.

### 4. First HANDOFF and PR

After the first implementation pass, `HANDOFF.md` was committed as the final
implementation deliverable:

```text
255d87e docs(pe-infra-slr-08): add implementation handoff
```

The branch was pushed and PR #374 was opened:

```text
PR: #374
Title: feat(pe-infra-slr-08): control-plane workflow wiring
Base: main
Head: feature/pe-infra-slr-08-control-plane-workflow-wiring
```

### 5. Live Gate 1 failure found by GitHub automation

After PR checks passed, automated Gate 1 posted the validator assignment comment:

```text
2026-04-25T04:04:23Z
@claude-code - assigned as Validator. Begin review.
<!-- validator-assignment -->
```

That comment triggered `validator-dispatch.yml`. The run failed:

```text
Run: 24922153851
Workflow: ELIS - Validator Dispatcher
Triggered: issue_comment
Failure step: Resolve validator inputs from CURRENT_PE.md
```

The failed log showed:

```text
FAIL: Current PE status is 'implementing' - validator dispatch requires
'gate-1-pending' before 'validating'. Required guard evidence:
Explicit PM authorisation is recorded; Validator assignment evidence is present;
The PE remains active in CURRENT_PE.md.
```

This was not an incidental CI error. It revealed a real design gap:

- The PR branch already contained complete implementer evidence.
- `HANDOFF.md` and Status Packet were present.
- Gate 1 had posted validator assignment evidence.
- The active registry in `CURRENT_PE.md` still recorded `implementing`.
- The dispatcher required the registry to have been manually advanced to
  `gate-1-pending` before it could dispatch the Validator.

That contradicted the intended control-plane behaviour: after complete
implementer evidence exists, automation should be able to observe
`implementing -> gate-1-pending` and then dispatch through
`gate-1-pending -> validating` in one bounded Gate 1 step.

### 6. Evidence-backed dispatch fix

The fix commit was:

```text
2a01fa2 fix(pe-infra-slr-08): allow evidence-backed validator dispatch
```

Key changes:

- Added `IMPLEMENTER_COMPLETION_TARGET_STATE = "gate-1-pending"`.
- Added `implementer_completion_observable(state)`.
- Added `validator_dispatch_allowed_after_evidence(state)`.
- Kept strict `validator_dispatch_allowed("implementing") == False`.
- Allowed evidence-backed validator dispatch from `implementing` only after
  HANDOFF and Status Packet sections had already been verified.
- Updated `dispatch_validator_runner.py` to verify evidence first, then call
  the evidence-backed helper.
- Updated `pm_gate_evaluator.py` to use the same evidence-backed decision.
- Added tests for:
  - dispatch from `implementing` when evidence is complete;
  - rejection from `planning`;
  - strict state-machine behaviour still requiring `gate-1-pending`;
  - Gate 1 pass from `implementing` when evidence is complete.
- Updated `AGENTS.md`, `docs/workflow/PE_STATE_MACHINE.md`, and ADR-014 to
  describe the evidence-backed bounded Gate 1 step.

### 7. Refreshed HANDOFF

After the fix, `HANDOFF.md` was refreshed and committed last:

```text
b3e94e5 docs(pe-infra-slr-08): refresh handoff after dispatch fix
```

The refreshed handoff recorded:

- the live dispatcher failure;
- the evidence-backed fix;
- updated PE-specific test count (`30/30`);
- current PR evidence;
- full local suite failure details for the unrelated Claude-auth tests.

### 8. Push and successful Gate 1 rerun

The branch was pushed:

```powershell
git push
```

The second Gate 1 assignment comment was posted:

```text
2026-04-25T04:18:43Z
@claude-code - assigned as Validator. Begin review.
<!-- validator-assignment -->
```

The fixed validator-dispatch run passed:

```text
Run: 24922399698
Workflow: ELIS - Validator Dispatcher
Status: success
Triggered: issue_comment
```

The validator runner was dispatched:

```text
Run: 24922402927
Workflow: Validator Agent Runner
Status at CODEX close-out: queued
```

### 9. Implementer Status Packet comment

CODEX posted the final implementer Status Packet to PR #374:

```powershell
gh pr comment 374 --body <status-packet-body>
```

Comment:

```text
https://github.com/rochasamurai/ELIS-Multi-AI-Agent-Platform/pull/374#issuecomment-4318058693
```

The comment stated:

- implementation PASS;
- Gate 1 passed after the fix;
- PE-specific tests `30/30` passed;
- local full-suite preflight had 2 unrelated Windows/Claude-auth failures;
- the PR was not ready to merge until Validator review/verdict.

### 10. Validator result and merge

The Validator committed review evidence:

```text
2c80c49 test(pe-infra-slr-08): add validator review evidence
```

Validator review artefact:

```text
docs/reviews/archive/REVIEW_PE_INFRA_SLR_08.md
```

Validator PR comment:

```text
2026-04-25T07:27:38Z
Verdict: PASS
```

Important Validator note:

```text
Single-account fallback: formal gh pr review --approve blocked
(same GitHub account as PR author). Verdict posted as PR comment per AGENTS.md
section 5.2.
```

The PR merged:

```text
Merged at: 2026-04-25T07:29:30Z
Merge commit: 0336ffb931f523273fb5a8f17ea9996aec323231
```

PM then closed PE-INFRA-SLR-08 and opened PE-SLR-11:

```text
bfd5263 chore(pm): PM-CHORE-65 - close PE-INFRA-SLR-08, open PE-SLR-11
```

## Issues Found

### Issue 1 - Gate 1 dispatcher required manual registry advancement

**Symptom:** `validator-dispatch.yml` failed after the first automated Gate 1
assignment comment.

**Failing run:** `24922153851`

**Error:**

```text
FAIL: Current PE status is 'implementing' - validator dispatch requires
'gate-1-pending' before 'validating'.
```

**Cause:** `dispatch_validator_runner.py` only allowed strict dispatch from
`gate-1-pending`. It did not model the case where the PR branch already carried
complete implementer evidence but `CURRENT_PE.md` still said `implementing`.

**Fix:** Added evidence-backed state-machine helper
`validator_dispatch_allowed_after_evidence(state)` and used it only after
HANDOFF and Status Packet verification.

**Regression coverage:**

- `tests/test_dispatch_validator_runner.py`
  - complete-evidence dispatch from `implementing`;
  - rejection from `planning`;
  - incomplete HANDOFF rejection still enforced.
- `tests/test_pm_gate_evaluator.py`
  - Gate 1 pass from `implementing` when evidence is complete;
  - Gate 1 block from `planning`.
- `tests/test_workflow_state_machine.py`
  - strict dispatch still rejects `implementing`;
  - evidence-backed helper permits `implementing`.

### Issue 2 - Local full-suite Windows/Claude-auth failures

**Symptom:** local full-suite preflight failed in two tests:

```text
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_missing
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_lacks_oauth_key
```

**Error:** `FileNotFoundError: [WinError 2] The system cannot find the file specified`
when `scripts/verify_claude_auth.py` invoked the `claude` CLI.

**Scope decision:** Not PE-INFRA-SLR-08 scope.

**Evidence:**

```powershell
git diff --name-status -- tests/test_verify_claude_auth.py scripts/verify_claude_auth.py
```

Output was empty, proving the PE did not modify those files.

### Issue 3 - `pe-sequencer.yml` failed immediately on push

**Symptom:** each push showed a failed `.github/workflows/pe-sequencer.yml` run.

Examples:

```text
24922123616 - failed after docs(pe-infra-slr-08): add implementation handoff
24922379136 - failed after docs(pe-infra-slr-08): refresh handoff after dispatch fix
24925691330 - failed after test(pe-infra-slr-08): add validator review evidence
```

`gh run view 24922379136` reported:

```text
This run likely failed because of a workflow file issue.
```

**Scope decision:** Not PE-INFRA-SLR-08 scope. The branch diff against main did
not modify `.github/workflows/pe-sequencer.yml`; the only workflow file changed
by the PE was `.github/workflows/auto-assign-validator.yml`.

### Issue 4 - Single-account formal review limitation

**Symptom:** Validator could not post a formal GitHub approval review because
the repository was operating through the same GitHub identity as the PR author.

**Resolution:** The Validator used the AGENTS.md single-account fallback:

- committed `docs/reviews/archive/REVIEW_PE_INFRA_SLR_08.md`;
- posted PASS as a PR comment;
- noted that formal `gh pr review --approve` was blocked by same-account
  identity constraints.

## Tests and Checks Run

### Local implementer checks

| Command | Result | Purpose |
|---------|--------|---------|
| `python scripts/check_current_pe.py` | PASS | Confirmed release context, roles, registry, and alternation. |
| `python scripts/check_agent_scope.py` | PASS | Confirmed no secret-pattern files in worktree. |
| `python -m black --check --include '\.py$' elis scripts tests` | PASS | Formatting preflight. |
| `python -m ruff check elis scripts tests` | PASS | Lint preflight. |
| `python scripts/check_control_plane_wiring.py` | PASS | PE-specific control-plane boundary check. |
| `python -m pytest tests/test_control_plane_workflow_wiring.py tests/test_workflow_state_machine.py tests/test_dispatch_implementer_runner.py tests/test_dispatch_validator_runner.py tests/test_pm_gate_evaluator.py -q -p no:cacheprovider` | PASS, 30/30 | PE-specific regression suite. |
| `python -m pytest tests -q --tb=short -p no:cacheprovider` | FAIL local preflight | Full suite reached completion with 2 unrelated Windows/Claude-auth failures. |
| `python scripts/check_handoff.py` | PASS | Confirmed HANDOFF required sections. |
| `python scripts/check_status_packet.py` | PASS | Confirmed HANDOFF Status Packet sections. |

### PE-specific pytest result

```text
..............................                                           [100%]
```

### Full-suite local preflight result

```text
1042 tests passed and 2 failed in the local preflight context.
```

The two local failures were the known unrelated `test_verify_claude_auth.py`
cases described above.

### GitHub Actions checks observed

Final PR checks included:

```text
current-pe-check: pass
gate-1: pass
openclaw-config-sync-check: pass
openclaw-doctor-check: pass
openclaw-health-check: pass
openclaw-security-check: pass
quality: pass
review-evidence-check: pass
secrets-scope-check: pass
slr-quality-check: pass
tests: pass
validate: pass
```

The final `deep-review` job was skipped, which matched the existing workflow
behaviour and did not block merge.

## GitHub Commands Used During the PE

### PR creation and state changes

The PR was created for the implementation branch:

```powershell
gh pr create --base main --head feature/pe-infra-slr-08-control-plane-workflow-wiring --title "feat(pe-infra-slr-08): control-plane workflow wiring" ...
```

The exact long body text is preserved in PR #374.

The PR was converted to ready after `HANDOFF.md` was committed:

```powershell
gh pr ready 374
```

### PR metadata and checks

Commands used repeatedly to inspect the PR:

```powershell
gh pr list --state open --base main
gh pr view 374 --json number,state,url,headRefName,baseRefName,title,isDraft,mergeStateStatus,reviewDecision
gh pr checks 374
```

Commands used to poll checks after pushing the fix:

```powershell
Start-Sleep -Seconds 30; gh pr checks 374
Start-Sleep -Seconds 30; gh pr checks 374
```

Commands used after merge for this methodology report:

```powershell
gh pr view 374 --json number,state,url,headRefName,baseRefName,title,isDraft,mergeStateStatus,reviewDecision,mergedAt,mergeCommit
gh pr view 374 --json comments,reviews --jq '{comments: [.comments[] | {author:.author.login,createdAt,body}], reviews: [.reviews[] | {author:.author.login,state,submittedAt,body}]}'
```

### Workflow run inspection

Commands used to inspect workflow history:

```powershell
gh run list --branch feature/pe-infra-slr-08-control-plane-workflow-wiring --limit 20
gh run list --workflow validator-dispatch.yml --limit 8
gh run list --workflow validator-runner.yml --limit 5
```

Commands used to inspect the failed and fixed validator-dispatch runs:

```powershell
gh run view 24922153851
gh run view 24922153851 --log-failed
gh run view 24922399698
```

Commands used to inspect the local validator runner dispatch:

```powershell
gh run view 24922402927
gh run view --job=72986186903
```

Commands used to inspect the unrelated `pe-sequencer.yml` failure:

```powershell
gh run view 24922379136
gh run view 24922379136 --log-failed
```

The log was not available for `24922379136`, but the summary stated it likely
failed because of a workflow file issue.

### PR comments

CODEX posted the final implementer Status Packet:

```powershell
gh pr comment 374 --body <status-packet-body>
```

The Validator posted PASS as a PR comment because formal review was blocked by
the single-account constraint.

## Authorisation Prompts and Why They Were Needed

The local environment ran with `workspace-write` filesystem sandboxing and
restricted network access. Some operations required explicit PM authorisation
through escalated tool calls. The main categories were:

- network operations to GitHub;
- commands needing host GitHub credentials;
- Git commands against worktrees whose metadata was created by elevated Git;
- pytest runs needing Windows temp/cache writes outside the sandbox;
- Git staging and commit operations that needed write access to Git metadata.

### Implementation-phase authorisations

| Command | Reason for PM authorisation | Outcome |
|---------|-----------------------------|---------|
| `python -m pytest tests/test_control_plane_workflow_wiring.py tests/test_workflow_state_machine.py tests/test_dispatch_implementer_runner.py tests/test_dispatch_validator_runner.py tests/test_pm_gate_evaluator.py -q -p no:cacheprovider` | PE-specific pytest needed Windows temp/cache writes that the sandbox commonly blocks. | PASS, 30/30 after the fix. |
| `python -m pytest tests -q --tb=short -p no:cacheprovider` | Full local suite needed the same Windows temp/cache access. | Ran to completion; 2 unrelated Claude-auth failures. |
| `git add AGENTS.md docs/decisions/ADR-014-control-plane-workflow-wiring.md docs/workflow/PE_STATE_MACHINE.md elis/workflow_state_machine.py scripts/dispatch_validator_runner.py scripts/pm_gate_evaluator.py tests/test_dispatch_validator_runner.py tests/test_pm_gate_evaluator.py tests/test_workflow_state_machine.py` | Staging required writing Git index metadata in an elevated-created worktree. | Staged dispatch-fix files. |
| `git commit -m "fix(pe-infra-slr-08): allow evidence-backed validator dispatch"` | Commit required writing Git object/index metadata. | Created commit `2a01fa2`. |
| `git fetch --all --prune` | Needed network access to refresh origin before final handoff evidence. | Completed. |
| `gh pr list --state open --base main` | Needed GitHub API access and host credentials. | Confirmed PR #374 was open. |
| `gh pr view 374 --json number,state,url,headRefName,baseRefName,title,isDraft,mergeStateStatus,reviewDecision` | Needed GitHub API access and host credentials. | Confirmed PR metadata. |
| `git add HANDOFF.md` | Staging required writing Git index metadata. | Staged final HANDOFF refresh. |
| `git commit -m "docs(pe-infra-slr-08): refresh handoff after dispatch fix"` | Commit required writing Git object/index metadata. | Created commit `b3e94e5`. |
| `git push` | Needed network access and host GitHub credentials. | Pushed `255d87e..b3e94e5`. |
| `gh pr checks 374` | Needed GitHub API access to inspect checks. | Showed pending, then passing checks. |
| `Start-Sleep -Seconds 30; gh pr checks 374` | Needed GitHub API access to poll CI. | First poll: one pending OpenClaw security check. Second poll: all visible checks passed, Gate 1 passed. |
| `gh run list --branch feature/pe-infra-slr-08-control-plane-workflow-wiring --limit 12` | Needed GitHub API access to inspect workflow history. | Confirmed CI, auto-merge, and `pe-sequencer.yml` runs. |
| `gh pr view 374 --json comments --jq ...` | Needed GitHub API access to confirm validator assignment comments. | Confirmed two Gate 1 assignment comments. |
| `gh run view 24922379136 --log-failed` | Needed GitHub API access to inspect `pe-sequencer.yml` failure. | Log unavailable. |
| `gh run view 24922379136` | Needed GitHub API access to inspect run summary. | Summary said likely workflow file issue. |
| `gh run list --workflow validator-dispatch.yml --limit 5` | Needed GitHub API access to confirm fixed dispatcher behaviour. | Confirmed failed first dispatcher and successful fixed dispatcher. |
| `gh run list --workflow validator-runner.yml --limit 5` | Needed GitHub API access to confirm validator runner dispatch. | Confirmed validator runner queued. |
| `gh run view 24922402927` | Needed GitHub API access to inspect dispatched validator runner. | Confirmed job existed. |
| `gh run view --job=72986186903` | Needed GitHub API access to inspect validator runner job. | Confirmed job identity/status. |
| `gh pr comment 374 --body <status-packet-body>` | Needed GitHub API access and credentials to post final implementer Status Packet. | Posted comment `4318058693`. |
| `gh pr checks 374` | Needed GitHub API access for final close-out evidence. | Confirmed all visible PR checks passing. |
| `gh run list --workflow validator-runner.yml --limit 1` | Needed GitHub API access for final close-out evidence. | Confirmed validator runner queued at that time. |

### Methodology-report authorisations

| Command | Reason for PM authorisation | Outcome |
|---------|-----------------------------|---------|
| `gh pr view 374 --json number,state,url,headRefName,baseRefName,title,isDraft,mergeStateStatus,reviewDecision,body --jq ...` | Needed GitHub API access to determine PR state before writing this report. | Revealed PR #374 had already merged. |
| `gh pr checks 374` | Needed GitHub API access to capture final check status. | Confirmed checks passed. |
| `gh run list --workflow validator-runner.yml --limit 3` | Needed GitHub API access to capture validator-runner state. | Showed queued runner records. |
| `git fetch --all --prune` | Needed network access and origin refresh before creating a report branch from current `origin/main`. | Fetched and pruned the merged PE branch from origin. |
| `git worktree add .worktrees/pe-infra-slr-08-dev-journey-report -b chore/pe-infra-slr-08-dev-journey-report origin/main` | Needed filesystem/Git metadata writes outside normal sandbox ownership expectations. | Created the report worktree at current `origin/main`. |
| `git status -sb` in the report worktree | The new worktree `.git` metadata was owned by the elevated Git process, causing "dubious ownership" without escalation. | Confirmed clean report branch state. |
| `git log --oneline --decorate --max-count=12` in the report worktree | Same elevated metadata ownership issue. | Confirmed the merged PE and PM-CHORE-65 history. |
| `gh pr view 374 --json number,state,url,headRefName,baseRefName,title,isDraft,mergeStateStatus,reviewDecision,mergedAt,mergeCommit` | Needed GitHub API access to record merge details. | Captured merge timestamp and merge commit. |
| `gh run list --branch feature/pe-infra-slr-08-control-plane-workflow-wiring --limit 20` | Needed GitHub API access to record workflow run history. | Captured CI, validator, auto-merge, and `pe-sequencer.yml` run sequence. |
| `gh pr view 374 --json comments,reviews --jq ...` | Needed GitHub API access to record Gate 1, Status Packet, and Validator PASS comments. | Captured comments and single-account fallback note. |
| `gh run list --workflow validator-dispatch.yml --limit 8` | Needed GitHub API access to record failed/fixed dispatcher run sequence. | Confirmed failure then success. |
| `gh run view 24922153851` | Needed GitHub API access to inspect the failed dispatcher summary. | Confirmed failure step. |
| `gh run view 24922399698` | Needed GitHub API access to inspect the fixed dispatcher summary. | Confirmed success. |
| `gh run view 24922153851 --log-failed` | Needed GitHub API access to capture the exact failure message. | Retrieved the precise `implementing` vs `gate-1-pending` error. |

## Sandbox and GitHub Friction Points

### Host GitHub credentials are outside the sandbox

`gh` commands and `git push` needed escalation because the sandboxed process did
not have access to host GitHub credentials. This is expected for:

- `gh pr view`
- `gh pr checks`
- `gh run list`
- `gh run view`
- `gh pr comment`
- `git push`

Methodology improvement:

- Keep all GitHub-inspection commands grouped and purposeful.
- Request one command prefix approval where practical, such as `gh pr view`,
  `gh pr checks`, `gh run list`, and `gh run view`.

### Pytest needed elevated execution on Windows

PE-specific and full pytest runs required escalation because the local Windows
environment and pytest temp/cache writes can cross sandbox boundaries.

Methodology improvement:

- For Windows worktrees, prefer `-p no:cacheprovider` and an explicit temp/cache
  strategy.
- State in the Status Packet whether local pytest was preflight and CI was the
  authoritative portable gate.

### Elevated worktree creation causes later Git ownership prompts

The report worktree was created through elevated Git. Subsequent non-elevated
Git commands in that worktree hit:

```text
fatal: detected dubious ownership in repository
```

Methodology improvement:

- If a worktree is created with elevated Git, expect future Git commands in that
  worktree to require escalation too.
- Prefer a consistent privilege mode for worktree creation and later Git
  operations.

### Merged PE branch should not receive methodology commits

While gathering metadata for this report, PR #374 was found to be already
merged. The report therefore moved to a dedicated chore branch rather than
adding commits to the completed PE branch.

Methodology improvement:

- Before writing post-PE artefacts, check PR state first.
- If the PR is merged, create a methodology/report branch from current
  `origin/main`.

## Methodology Lessons

1. Gate automation should model evidence, not only registry labels.

   The first validator-dispatch failure showed that strict state labels alone
   can create a manual precondition even when evidence is complete. The fix kept
   the state machine authoritative while allowing the control plane to observe
   an evidence-backed transition.

2. Live automation is a valuable acceptance test.

   Local tests passed before the first push, but the real Gate 1 workflow found
   an integration gap that local unit tests did not yet cover. The new tests now
   encode that live failure mode.

3. HANDOFF must be refreshed after any implementation correction.

   The fix changed behaviour and test counts, so the handoff needed a final
   refresh. That made the Validator's review path clear and preserved evidence
   continuity.

4. GitHub run inspection should be part of implementation close-out.

   `gh pr checks`, `gh run list`, and `gh run view` were necessary to distinguish
   true PE failures from unrelated workflow failures such as `pe-sequencer.yml`.

5. Single-account review fallback remains operationally important.

   Validator PASS had to be posted as a PR comment because formal approval was
   blocked by same-account GitHub constraints. The durable REVIEW file and PR
   comment together preserved the handshake.

## Files Touched by PE-INFRA-SLR-08

Final PE scope:

```text
M  .github/workflows/auto-assign-validator.yml
M  AGENTS.md
M  HANDOFF.md
A  docs/decisions/ADR-014-control-plane-workflow-wiring.md
M  docs/decisions/README.md
M  docs/workflow/PE_STATE_MACHINE.md
M  elis/workflow_state_machine.py
A  scripts/check_control_plane_wiring.py
M  scripts/dispatch_implementer_runner.py
M  scripts/dispatch_validator_runner.py
M  scripts/implementer_runner_common.py
M  scripts/pm_gate_evaluator.py
A  tests/test_control_plane_workflow_wiring.py
M  tests/test_dispatch_validator_runner.py
M  tests/test_pm_gate_evaluator.py
M  tests/test_workflow_state_machine.py
A  docs/reviews/archive/REVIEW_PE_INFRA_SLR_08.md
```

The methodology report itself is outside the PE implementation branch and is
recorded separately on `chore/pe-infra-slr-08-dev-journey-report`.

## References

- PR #374: https://github.com/rochasamurai/ELIS-Multi-AI-Agent-Platform/pull/374
- Failed validator dispatcher: https://github.com/rochasamurai/ELIS-Multi-AI-Agent-Platform/actions/runs/24922153851
- Fixed validator dispatcher: https://github.com/rochasamurai/ELIS-Multi-AI-Agent-Platform/actions/runs/24922399698
- Merge commit: `0336ffb931f523273fb5a8f17ea9996aec323231`
- Validator review file: `docs/reviews/archive/REVIEW_PE_INFRA_SLR_08.md`
