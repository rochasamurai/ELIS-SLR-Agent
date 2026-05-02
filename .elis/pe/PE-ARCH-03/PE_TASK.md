# PE-ARCH-03 — Harmless Lobster Dry Run (Recovery)

## Objective
Recover and complete the PE-ARCH-03 harmless Lobster workflow dry-run that was interrupted by a connect-session timeout / UI delivery failure on the first attempt. Create the minimal artefact set for a dry-run that proves the implement → validate path can be exercised without modifying production code, architecture docs, governance docs, scripts, CI, or any workflow behaviour.

## Scope
A single dry-run artefact set. No production changes. No workflow execution.

## Allowed files (create only)
1. `.elis/pe/PE-ARCH-03/PE_TASK.md` — this file
2. `docs/sandbox/PE_ARCH_03_Lobster_Dry_Run_Stub.md` — harmless dry-run stub
3. `HANDOFF.md` — handoff document

## Strictly forbidden
- Modifying `CURRENT_PE.md`
- Modifying `docs/architecture/*` files
- Modifying `docs/governance/*` files
- Modifying any script in `scripts/`
- Modifying any CI configuration
- Modifying any Lobster workflow files in `workflows/`
- Creating PRs, pushing, or merging
- Creating reviews or REVIEW.md
- Dispatching other agents
- Modifying files outside this worktree

## Acceptance criteria
- `.elis/pe/PE-ARCH-03/` directory exists with `PE_TASK.md`
- `docs/sandbox/PE_ARCH_03_Lobster_Dry_Run_Stub.md` exists and states it is a harmless dry-run artefact
- `HANDOFF.md` exists and summarises what was done
- Mandatory checks pass (pwd, toplevel, git status, branch, HEAD hash, CURRENT_PE.md existence, task packet existence, stub existence, HANDOFF.md existence, `python scripts/check_current_pe.py`)
- No files outside the three allowed files were modified
- No commits exist beyond the base commit (47cf252)
- No pushes, PRs, or merges were performed

## HANDOFF.md requirement
HANDOFF.md is mandatory. The validator agent (infra-val-a) depends on it to know the implementer has completed its work and is ready for the validate stage.

## Recovery note
This is a recovery attempt after a connect-session timeout on the first try. The `implement → validate → PASS` path was not exercised on the first attempt. Before this second attempt, verify:
- Correct worktree: `/opt/elis/agent-worktrees/PE-ARCH-03-infra-impl-b`
- Base commit: `47cf252ea5fdb29da6b85c01a895a9bac21009f2`
- No prior artefacts exist
- Agent: infra-impl-b
- No wrong-workspace duplicates
- No partial commits or PRs
