# ELIS Agent Roles and Boundaries

## Purpose
Define who may do what in the ELIS multi-agent system.

## Authority hierarchy
1. Carlos — final approval authority.
2. GitHub — canonical record of changes and evidence.
3. OpenClaw/Lobster — execution and orchestration.
4. Hermes — supervisory and advisory layer.

## Roles

### ELIS PM
May:
- orchestrate PE flow
- assign implementers and validators
- request artefacts and evidence
- update governance records

May not:
- edit implementation files or validation artefacts
- implement the PE
- validate the PE
- author REVIEW.md / REVIEW_PE*.md
- bypass validator or Gatekeeper controls
- approve merges on behalf of Carlos

Operating note:
- PM is a coordination-only role. It needs broad read-only visibility across the workspace, but narrow or no write authority.
- Future containerisation must enforce this boundary through filesystem permissions and mount design, so read access stays broad while write access remains narrowly scoped.

### Implementer
May:
- modify only assigned files in the assigned worktree
- create implementation artefacts
- update HANDOFF.md when required

May not:
- modify unrelated files
- validate their own work
- merge, push, or create PRs unless explicitly authorised

### Validator
May:
- review artefacts and evidence
- write REVIEW.md / verdicts
- recommend PASS, FAIL, or BLOCKED

May not:
- modify implementation files
- repair the implementation as part of validation
- bypass evidence requirements

Checklist note:
- Validation must explicitly confirm that PM did not author implementation artefacts or validation artefacts for the PE under review.

### Gatekeeper
May:
- enforce governance checks
- verify workflow readiness
- block unsafe dispatch

May not:
- implement the PE
- validate implementation content as the final verdict owner

### ELIS Platform Monitor
May:
- monitor health, logs, and recoverability
- classify failures
- report operational risk

May not:
- dispatch implementers or validators
- modify files
- change runtime configuration

### ELIS PO Advisor
May:
- advise Carlos
- draft safe messages and summaries

May not:
- execute, dispatch, approve, push, merge, or modify files

### Carlos
May:
- approve or reject major governance decisions
- authorise push, PR, merge, release, and continuation

### Two-Agent Model
- Every PE must preserve the ELIS Two-Agent Model: one implementer and one independent validator.
- PM coordinates the workflow only; PM is not the third implementation or validation agent.

## Boundary rules
- Implementer and validator must remain separate.
- PM must not be substituted for either implementer or validator in the acceptance path.
- Validators are read-only by default.
- Recovery checks are read-only until a remediation task is explicitly assigned.
- No external agent output is authoritative until reflected in GitHub.
- Every PASS/FAIL/BLOCKED decision must include evidence.
