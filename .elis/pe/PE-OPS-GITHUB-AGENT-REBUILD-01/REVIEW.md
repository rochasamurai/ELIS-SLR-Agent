# PE-OPS-GITHUB-AGENT-REBUILD-01 Validation Review

## Verdict: PASS_WITH_NOTES

## Validated Commits
1. `1102e951c962ddd18c4ac9b9ffa3c8e469139f3b` — docs: add GitHub Agent rebuild first-pass governance
2. `a68102bf527f9b00c226af870528945fd4f1fab3` — chore: ignore OpenClaw native workspace files

## Files Reviewed
| File | Status | Notes |
|------|--------|-------|
| `.elis/pe/PE-OPS-GITHUB-AGENT-REBUILD-01/HANDOFF.md` | NEW | PE handoff artefact, appropriate |
| `.elis/pe/PE-OPS-GITHUB-AGENT-REBUILD-01/PE_TASK.md` | NEW | PE task definition, appropriate |
| `docs/governance/ELIS_Agent_Dispatch_Binding_and_Validation_Rules.md` | MODIFIED | Substantial rewrite; v1.3→v1.0 (version reset concern, see notes) |
| `docs/governance/ELIS_GITHUB_AGENT_EXECUTION_ADAPTATION_GOVERNANCE.md` | NEW | New governance doc for runtime/worktree separation |
| `docs/ops/github-agent/GITHUB_AGENT_REBUILD_RUNBOOK.md` | NEW | Rebuild runbook with separation model |
| `docs/ops/github-agent/GITHUB_AGENT_RULES.md` | MODIFIED | Added runtime/worktree separation rules |
| `.gitignore` | MODIFIED | Added root-level OpenClaw native file protections |

## Checks Performed

### 1. Worktree Binding ✓
- Branch: `feature/pe-ops-github-agent-rebuild-01-explicit-runtime-worktree-separation`
- HEAD: `a68102bf527f9b00c226af870528945fd4f1fab3`
- Status: clean (no uncommitted changes)

### 2. All Changed Files Within Scope ✓
All 7 changed files are governance/runbook/PE-artefact/docs files. No code, no scripts, no runtime config.

### 3. No Live Runtime/Config/Auth Changes ✓
- No `openclaw.json` edits
- No restart/reload instructions executed
- No GitHub auth/credential mutation
- No SOUL.md recreation in the Git worktree
- No current GitHub Agent deletion
- No push/open PR/merge

### 4. No CURRENT_PE.md Update ✓
Not touched in either commit.

### 5. No SOUL.md or Native Runtime Files Committed ✓
SOUL.md, IDENTITY.md, USER.md, etc. are not in the committed tree. The `.gitignore` now explicitly excludes them at root level.

### 6. .gitignore Protection Appropriate and Root-Level Only ✓
All 14 new entries use leading `/` to anchor at repo root only. This correctly protects native OpenClaw files without interfering with subdirectory files of the same name.

### 7. OpenClaw Workspace Semantics Correctly Reflected ✓
Documents consistently describe runtime workspace vs authorised Git worktree separation. Fixed workspace paths match the established pattern (`/opt/elis/agent-worktrees/<role>-<slot>`).

### 8. Git-Working Agents Use Authorised Fixed Git Worktrees ✓
Rules require `git rev-parse --show-toplevel` to match assigned worktree path. Source path authorization and validation are specified.

## Notes (non-blocking)

### N1: Version History Regression in Dispatch Rules
The `ELIS_Agent_Dispatch_Binding_and_Validation_Rules.md` was rewritten from v1.3 to v1.0 with substantial content removed (§4 dispatch packet fields, §5 binding rules detail, §6a/6b rules, §7 persistent context, §8 deterministic checks, §9 dispatch packet format, §10/11). The new version is a first-pass overview and does not contain the detailed binding certificate format, §6a LATEST_VALIDATOR_REVIEW_MUST_BE_ON_FINAL_PR_BRANCH_RULE, or §6b AUTHORISED_EXECUTION_OWNER_FOR_BRANCH_INTEGRATION_RULE. This is acceptable for a first-pass but these rules should be restored or explicitly referenced before operational use.

### N2: SELF_CONTAINED_STATE_CHANGING_DISPATCH_RULE Not Explicitly Named
The exact named rule `SELF_CONTAINED_STATE_CHANGING_DISPATCH_RULE` (or equivalent) does not appear in the committed artefacts. The concept of self-contained dispatch is present in existing governance docs (ELIS_Multi_Agent_Governance_Implementation_Plan_v2.md) and the new artefacts reference authorization chains for state-changing operations, but the specific named rule is not codified here. Recommend explicit inclusion in a subsequent pass.

### N3: Runtime ≠ Source Worktree Assertion
The new artefacts assert that runtime and source worktree paths must always differ. However, for many current ELIS agents the OpenClaw runtime workspace and the Git worktree are already separate by design. The documents should clarify whether this rule applies specifically to the GitHub Agent (which may execute in a temporary directory) or universally to all agents.

## Risks
- **Low**: The Dispatch Rules rewrite lost detailed operational rules (§6a, §6b, §8 checks). These rules still exist in git history but are not in the current HEAD of the file. Follow-up pass needed before operational deployment.
- **Low**: No executable validation scripts were created; all enforcement is documented as design intent only.

## Conclusion
Both commits are within scope, contain no runtime/config/auth changes, protect native OpenClaw files correctly, and correctly reflect the runtime/worktree separation model. The notes above are non-blocking improvement recommendations for subsequent passes.

**Verdict: PASS_WITH_NOTES**
