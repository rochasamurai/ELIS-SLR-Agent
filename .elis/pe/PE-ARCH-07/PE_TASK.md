# PE-ARCH-07 — Execute Isolated Lobster Plugin Self-Test

## Objective
Run the first controlled Lobster plugin self-test in the isolated `lobster-test` OpenClaw profile, without enabling Lobster in production and without running any production PE workflows.

## Scope
Documentation, planning, and harmless self-test evidence only. No production config edits. No production PE dispatch. No automatic push/PR/merge.

## Required deliverables
1. `.elis/pe/PE-ARCH-07/PE_TASK.md` — this file
2. `HANDOFF.md` — planning or implementation handoff with complete status packet
3. `docs/reports/PE_ARCH_07_Lobster_Self_Test_Report.md` — optional if test evidence is recorded
4. `docs/runbooks/ELIS_Lobster_Plugin_Self_Test_Runbook.md` — only if results need to be appended
5. `docs/architecture/ELIS_Lobster_Plugin_Test_Enablement.md` — only if findings change the enablement model

## Current state analysis

### What exists
- `PE-ARCH-06` documented the isolated Lobster profile procedure and the test-profile enablement model
- The Lobster plugin must remain isolated to the `lobster-test` profile
- Production OpenClaw configuration must remain untouched
- `CURRENT_PE.md` remains the authoritative active-PE registry and must be updated for this PE
- PE-AGT-01 remains held and Increment 3 remains paused

### What must happen next
- Confirm the isolated `lobster-test` profile exists and is isolated from production
- Verify Lobster registration in the test profile only
- Run only the documented harmless self-test
- Capture the command, output, rollback note, and evidence
- Preserve production config and production PE workflows unchanged

### What must remain unchanged
- ❌ Production OpenClaw config
- ❌ Production Lobster enablement
- ❌ Production PE workflows
- ❌ PE-AGT-01 continuation / resumption
- ❌ PE-OPS-01 Increment 3 resumption
- ❌ Push / PR / merge before validation and Carlos authorisation
- ❌ Any non-reversible test state

## Proposed staffing (provider-guarded)
- **Implementer**: infra-impl-b
- **Validator**: infra-val-a

> Do not dispatch implementation until provider status is rechecked and confirmed PASS, or Carlos explicitly waives the provider guard.

## Self-test command plan
```bash
ls ~/.openclaw/profiles/lobster-test/openclaw.json && echo "PROFILE_CONFIG_OK"
grep -q '"extensions".*"lobster"' ~/.openclaw/profiles/lobster-test/openclaw.json && echo "LOBSTER_REGISTERED"
ls ~/.openclaw/openclaw.json && echo "PROD_CONFIG_EXISTS"
grep -c '"extensions"' ~/.openclaw/openclaw.json || echo "PROD_NO_EXTENSIONS"
test -f /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js && echo "EXTENSION_BINARY_OK"
```

## Acceptance criteria
- [ ] The isolated test profile is defined clearly and does not alter production config
- [ ] Lobster is documented as enabled only in `lobster-test`
- [ ] The self-test stays harmless and does not run a production PE workflow
- [ ] Activation / verification / rollback / failure modes are documented or referenced
- [ ] `HANDOFF.md` carries a clear status packet for the next validation step
- [ ] `python scripts/check_current_pe.py` passes once the planning update is applied
- [ ] No production config or runtime config is modified
- [ ] No workflow execution is claimed outside the isolated test profile

## Mandatory principles
- **Do not modify production config** — this PE is to plan and validate an isolated test-profile self-test, not to execute production changes
- **Do not claim production readiness** — the test profile is isolated and non-production by design
- **Do not run production workflows** — any Lobster use must remain within the isolated test profile
- **All work within this repository only**: `/opt/elis/repo`
