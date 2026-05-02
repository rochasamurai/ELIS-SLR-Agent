# PE-ARCH-01 — ELIS Deterministic Multi-Agent Architecture

## Objective
Formalise the ELIS multi-agent operating model before any further OpenClaw dispatch changes.

## Scope
Document-first architecture PE.

### Required outputs
1. `docs/architecture/ELIS_Deterministic_Multi_Agent_Architecture.md`
2. `docs/governance/ELIS_Agent_Roles_and_Boundaries.md`
3. `workflows/pe-implement-validate-loop.lobster`
4. `workflows/pe-recovery-check.lobster`
5. `HANDOFF.md`

## Mandatory principles
- GitHub remains the canonical ELIS repository and governance record.
- OpenClaw/Lobster is the execution and orchestration layer.
- Persistent OpenClaw peer agents replace free-form PM chat and ordinary sub-agent spawning.
- Lobster-controlled PE workflows are the preferred mechanism for longer-running agent sessions.
- Hermes runs ELIS Platform Monitor and ELIS PO Advisor as external supervisory/advisory agents.
- ELIS Platform Monitor and ELIS PO Advisor make OpenClaw more resilient, observable, recoverable, and governable.
- OpenClaw/Lobster executes.
- GitHub records.
- Hermes supervises and advises.
- Carlos approves.
- No external agent workflow output is authoritative until reflected in GitHub through commits, artefacts, validation evidence, CI status, and required ELIS governance files.

## Role boundaries
- ELIS PM may orchestrate but must not bypass validator/Gatekeeper controls.
- Implementers may modify assigned files only.
- Validators must validate and report; they must not modify implementation files.
- Gatekeeper must enforce governance checks; it must not implement.
- ELIS Platform Monitor must monitor, diagnose, and report; it must not dispatch implementers or validators.
- ELIS PO Advisor must advise Carlos and draft safe messages; it must not execute, dispatch, approve, push, merge, or modify files.
- Carlos remains final approval authority for push, PR, merge, release, and major governance decisions.

## Lobster workflow requirements
- One implementer.
- One validator.
- Maximum 3 implement-validation iterations.
- Mandatory `HANDOFF.md` after implementation.
- Mandatory `REVIEW.md` after validation.
- Automatic loop on FAIL.
- Stop on PASS.
- No automatic push/PR.
- Human approval before push/PR/merge.

## Recovery requirements
The workflow must address the recurring OpenClaw UI failure:

> Agent couldn't generate a response. Note: some tool actions may have already been executed — please verify before retrying.

The recovery check must verify:
- whether the agent started
- whether files changed
- whether commits were created
- whether PRs were created
- whether HANDOFF.md exists
- whether REVIEW.md exists
- whether the correct worktree was used
- whether the canonical repo is clean
- which failure class applies before any retry

## Failure-class taxonomy
At minimum:
- UI_DELIVERY_FAILURE
- WRONG_WORKTREE
- RATE_LIMIT
- TOOL_CONTEXT_FAILURE
- PARTIAL_EXECUTION_UNKNOWN
- REPO_STATE_UNKNOWN
- MISSING_HANDOFF
- MISSING_REVIEW
- ROLE_BOUNDARY_VIOLATION

## Validation criteria
Validator must confirm that PE-ARCH-01 preserves:
- GitHub authority
- OpenClaw/Lobster execution role
- Hermes supervisory/advisory role
- Carlos final approval authority
- implementer/validator separation
- Gatekeeper independence
- no-silent-failure recovery
- no-modify validator boundary
- explicit evidence fields
- bounded loop behaviour
- no automatic push/PR/merge

## Increment 3 status
Increment 3 remains paused unless Carlos explicitly authorises otherwise.
