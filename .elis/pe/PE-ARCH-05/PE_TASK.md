# PE-ARCH-05 — Enable Bundled Lobster Plugin in a Controlled Test Profile

## Objective
Enable the bundled Lobster plugin within an **isolated OpenClaw test profile** so agents can safely invoke Lobster workflows without risking production gateway configuration. Deliver a documentation package covering enablement, invocation, preflight/self-test, rollback, and test-profile-only guardrails. The test profile must not affect the production gateway config, production workflows, or any running services.

## Scope
Documentation, analysis, and configuration specification only. No production config edits. No workflow execution. No PE dispatch.

### Required deliverables
1. `.elis/pe/PE-ARCH-05/PE_TASK.md` — this file
2. `docs/architecture/ELIS_Lobster_Plugin_Test_Enablement.md` — architecture and enablement analysis for the test-profile approach
3. `docs/runbooks/ELIS_Lobster_Plugin_Enablement_Runbook.md` — step-by-step runbook for enablement, preflight checks, self-test, and rollback
4. `HANDOFF.md` — implementation handoff with complete status packet

### Optional deliverables
- `workflows/README.md` — update only if existing content needs clarification about Lobster test-profile access

## Current state analysis

### What exists
- **Lobster plugin** is bundled inside OpenClaw distribution at `/opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/`
- **Lobster CLI** exists in rollback snapshot only (`@clawdbot/lobster` not in active install)
- **Production gateway config** (`~/.openclaw/openclaw.json`) has **no** `extensions` section and **no** Lobster plugin registration — this must remain untouched
- **OpenClaw supports profiles** via the `OPENCLAW_PROFILE` environment variable and/or `--profile` CLI flag — OpenClaw profiles load profile-specific config from `~/.openclaw/profiles/<name>/openclaw.json`
- **`.lobster` definition files** exist in `workflows/` but are not executable
- **No production Lobster tool surface** exists for any agent

### What must be enabled (test profile only)
- A dedicated OpenClaw profile named `lobster-test` (or similar) that registers the bundled Lobster extension
- A safe invocation path for agents to call `lobster run` within the test profile
- Preflight checks that verify the test profile is isolated from production
- Self-test steps that confirm the Lobster CLI compiles/runs under the test profile
- Rollback steps to cleanly remove the test profile without affecting production

### What must remain unchanged
- ❌ Production `~/.openclaw/openclaw.json` — no edits
- ❌ Production gateway config — no extension registration, no plugin entries
- ❌ Production `openclaw gateway` commands — no restart of the production gateway
- ❌ Production workflows — no execution via any profile
- ❌ Existing `.lobster` files — no modification, still architecture definitions only
- ❌ No pushes, PRs, or merges from this branch

## Acceptance criteria
- [ ] `.elis/pe/PE-ARCH-05/PE_TASK.md` exists and defines scope, current state, and test-profile enablement requirements
- [ ] `docs/architecture/ELIS_Lobster_Plugin_Test_Enablement.md` exists and documents the test-profile architecture, isolation model, and invocation contract
- [ ] `docs/runbooks/ELIS_Lobster_Plugin_Enablement_Runbook.md` exists with step-by-step enablement, preflight, self-test, and rollback
- [ ] `HANDOFF.md` exists with complete status packet
- [ ] No production config files modified
- [ ] No `.lobster` files modified or claimed as executable
- [ ] No workflow execution claimed or simulated
- [ ] No Lobster plugin registered in production
- [ ] `git status` confirms only expected files changed
- [ ] `python scripts/check_current_pe.py` passes (if script exists)

## Mandatory principles
- **Do not modify production config** — the PE task is to document a test-profile enablement path, not to execute it
- **Do not claim any Lobster execution** — the test profile is documented as a future action, not currently active
- **Do not modify `.lobster` files** — they remain architecture definitions only
- **All work within this worktree only**: `/opt/elis/agent-worktrees/PE-ARCH-05-infra-impl-b`

## No-production-readiness statement
This PE delivers **documentation and analysis only** for enabling the bundled Lobster plugin in a test profile. The described enablement must **not** be applied to production environments until a separate production-readiness review has been completed. The test profile itself is explicitly **not production-ready** — it is intended for isolated testing and validation only.
