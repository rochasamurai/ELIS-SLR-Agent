# PE-OPS-GITHUB-AGENT-ENFORCEMENT-01 — Enforce GitHub Agent Path for GitHub Operations

## PE_ID
PE-OPS-GITHUB-AGENT-ENFORCEMENT-01

## Objective
Make GitHub Agent deterministic and safe for GitHub write operations.

## Background
PR #429 exposed a wrong-path PR source defect. PR #430 was a one-time fallback exception. This PE hardens the GitHub Agent path-selection rules so it always resolves exactly one authorised PR source path and fails closed otherwise.

## Staffing
- Implementer: `infra-impl-a`
- Validator: `infra-val-b`

## Branch
`feature/pe-ops-github-agent-enforcement-01-deterministic-github-agent-source-path`

## Fixed worktrees
- PM: `/opt/elis/agent-worktrees/pm`
- Implementer: `/opt/elis/agent-worktrees/infra-impl-a`
- Validator: `/opt/elis/agent-worktrees/infra-val-b`
- GitHub Agent runtime: `/opt/elis/agent-worktrees/github-agent`

`/opt/elis/agent-worktrees/github-agent` is the GitHub Agent runtime workspace only; it is not the default PR source path.

## Required rules
- `RULE_DEFINED_PR_SOURCE_PATH`
- `GITHUB_AGENT_READS_SOURCE_WRITES_REMOTE`
- `NO_RUNTIME_WORKSPACE_AS_PR_SOURCE`
- `NO_SINGLE_AUTHORISED_PR_SOURCE_PATH_NO_GITHUB_WRITE`
- `NO_PREPARED_GITHUB_AGENT_RUNTIME_NO_GITHUB_WRITE`

## Opening scope
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-GITHUB-AGENT-ENFORCEMENT-01/PE_TASK.md`

## Approved implementation scope
- define `RULE_DEFINED_PR_SOURCE_PATH`
- define `GITHUB_AGENT_READS_SOURCE_WRITES_REMOTE`
- prohibit GitHub Agent from defaulting to its runtime workspace as PR source
- define action type `open_pr_for_validated_pe_branch`
- define how GitHub Agent resolves exactly one authorised PR source path
- block if no single authorised source path exists
- add GitHub Agent request/report templates
- add runtime workspace readiness check, including `.openclaw` creation
- document wrong-path PR #429 as evidence
- document one-time fallback PR #430 as exception
- add end-to-end acceptance test for correct PR source-path resolution
- record the GitHub identity issue: `rochasamurai` was used; replace it in a later credentials/security PE or include it here only if safe

## Hard boundaries
- no secret/token rotation unless explicitly approved
- no GitHub permission changes unless explicitly approved
- no OpenClaw/Hermes service/config changes unless explicitly approved
- no PM direct GitHub writes
- no PE-specific runtime worktrees

## Acceptance criteria
- GitHub Agent rules are documented before future GitHub Agent PR operations
- exactly one authorised PR source path is resolved, or the operation blocks
- runtime workspace readiness checks include `.openclaw` creation
- GitHub Agent never defaults to its runtime workspace as PR source
- request/report templates make the source-path decision explicit
- PR #429 wrong-path evidence is preserved in the PE record
- PR #430 fallback exception is documented as one-time only
- end-to-end acceptance test covers correct source-path resolution
- identity issue is recorded without changing secrets or permissions

## Reset / binding acknowledgement plan
1. Confirm PM, Implementer, Validator, and GitHub Agent runtime bindings.
2. Confirm the single authorised PR source path before any PR operation.
3. Confirm `.openclaw` exists in the GitHub Agent runtime workspace.
4. Fail closed if zero or multiple authorised source paths exist.
5. Require explicit in-thread reset/binding acknowledgement before dispatch.

## Confirmation required before dispatch
- no OpenClaw/Hermes config changes
- no service changes/restarts
- no secret/token changes
- no GitHub permission changes
- no PM direct GitHub writes
- no PE-specific runtime worktrees
