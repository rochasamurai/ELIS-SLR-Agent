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
- bypass validator or Gatekeeper controls
- implement code or docs as the PE owner
- approve merges on behalf of Carlos

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

## Boundary rules
- Implementer and validator must remain separate.
- Validators are read-only by default.
- Recovery checks are read-only until a remediation task is explicitly assigned.
- No external agent output is authoritative until reflected in GitHub.
- Every PASS/FAIL/BLOCKED decision must include evidence.
