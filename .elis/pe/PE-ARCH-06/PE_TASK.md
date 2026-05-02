# PE-ARCH-06 — Controlled Lobster Plugin Activation Self-Test

## Objective
Safely test activation of the bundled Lobster plugin in an **isolated OpenClaw test profile** without modifying production OpenClaw config and without running production PE workflows.

## Scope
Documentation, analysis, and test-profile enablement specification only. No production config edits. No production PE dispatch. No automatic push/PR/merge.

## Required deliverables
1. `.elis/pe/PE-ARCH-06/PE_TASK.md` — this file
2. `docs/runbooks/ELIS_Lobster_Plugin_Self_Test_Runbook.md` — self-test runbook for isolated profile activation, verification, rollback, and failure modes
3. `docs/architecture/ELIS_Lobster_Plugin_Test_Enablement.md` — update only if the invocation contract or guardrails need revision
4. `HANDOFF.md` — implementation or planning handoff with complete status packet
5. `workflows/README.md` — update only if the Lobster invocation contract changes

## Current state analysis

### What exists
- Lobster is bundled with OpenClaw but remains disabled by default in production
- PE-ARCH-05 documented the isolated test-profile enablement path
- `CURRENT_PE.md` remains authoritative for the active PE state and currently still reflects the held PE context
- Increment 3 remains paused and must not be resumed without explicit Carlos authorization

### What must happen next
- Create a reversible self-test path for enabling Lobster only in an isolated OpenClaw profile or test configuration
- Identify the actual tool / command / API surface exposed after activation
- Run only a harmless self-test, not an ELIS production PE workflow
- Document activation, verification, rollback, and failure modes

### What must remain unchanged
- ❌ Production OpenClaw config
- ❌ Production Lobster enablement
- ❌ Production PE workflows
- ❌ PE-AGT-01 continuation / resumption
- ❌ PE-OPS-01 Increment 3 resumption
- ❌ Push / PR / merge before validation and Carlos authorisation
- ❌ Any non-reversible test state

## Proposed staffing (provider-guarded)
- **Implementer**: infra-impl-a
- **Validator**: infra-val-b

> Staffing remains provisional until provider status is rechecked at dispatch time.

## Acceptance criteria
- [ ] The isolated test profile is defined clearly and does not alter production config
- [ ] The Lobster activation path is documented as reversible and profile-scoped
- [ ] The self-test stays harmless and does not run a production PE workflow
- [ ] Activation / verification / rollback / failure modes are documented
- [ ] `HANDOFF.md` carries a clear status packet for the next validation step
- [ ] `python scripts/check_current_pe.py` passes once the planning update is applied
- [ ] No production config or runtime config is modified
- [ ] No workflow execution is claimed outside the isolated test profile

## Mandatory principles
- **Do not modify production config** — the PE is to document a test-profile activation path, not to execute production changes
- **Do not claim production readiness** — the test profile is isolated and non-production by design
- **Do not run production workflows** — any Lobster use must remain within the isolated test profile
- **All work within this repository only**: `/opt/elis/repo`
