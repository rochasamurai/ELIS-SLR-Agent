# PE-ARCH-04 — Lobster Runner Enablement

## Objective
Document the current Lobster enablement state and produce the minimum safe implementation path for activating the Lobster workflow runner within the ELIS agent runtime. This is a **documentation-and-analysis PE only** — no production code, no CI changes, no workflow execution simulation.

## Scope
Research and documentation. No Lobster workflow execution. No claims that `.lobster` files are executable.

### Required deliverables
1. `.elis/pe/PE-ARCH-04/PE_TASK.md` — this file
2. `docs/architecture/ELIS_Lobster_Runner_Enablement.md` — comprehensive enablement analysis
3. `HANDOFF.md` — implementation handoff with status packet

### Optional deliverables
- `workflows/README.md` — only if edits are needed to remove false execution claims

## Current state analysis

### What exists
- **Lobster workflow definitions** exist in `workflows/pe-implement-validate-loop.lobster` and `workflows/pe-recovery-check.lobster` — created during PE-ARCH-01/02 as architecture definition files. These are plain-text YAML-like definitions, **not** executable scripts.
- **Lobster extension binary** (`@clawdbot/lobster`) is bundled inside the OpenClaw distribution at:
  - Extension plugin: `/opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/`
  - CLI binary (rollback only): `/opt/openclaw/lib/node_modules/openclaw.rollback-20260417T200113Z/node_modules/.bin/lobster`
- **Lobster is NOT enabled** in the running gateway config (`~/.openclaw/openclaw.json`) — no `extensions` section registers it, and it is not listed as an active plugin entry.
- **No CLI wrapper** is installed in PATH (`which lobster` returns nothing).
- **No OpenClaw tool** exposes Lobster to agents — no `lobster` subcommand or tool binding exists.
- **Lobster Skills/TaskFlow** supports `lobster` files natively but this is a higher-level abstraction, not a direct runner.

### What must be documented as NOT possible (currently)
- ❌ No CLI runner surface (`lobster run` not available on PATH)
- ❌ No gateway extension activated (Lobster plugin not registered)
- ❌ No workflow execution possible (no tool, no extension, no binary in active install)
- ❌ `.lobster` files are NOT executable — they are architecture definition files only

### Minimum safe implementation path
1. **Register Lobster as an OpenClaw extension** — add `"extensions": ["lobster"]` to `~/.openclaw/openclaw.json` and restart the gateway
2. **Install CLI binary** — the `@clawdbot/lobster` npm package must be linked or installed into the active OpenClaw installation (it exists in rollback only)
3. **Create a PATH wrapper** — add a shell script in `/usr/local/bin/lobster` or `~/.openclaw/bin/lobster` that invokes the bundled binary
4. **Define invocation contract** — document how agents invoke Lobster workflows via the wrapper
5. **Test with dry-run** — `lobster run --dry-run --file workflows/pe-implement-validate-loop.lobster`

### Invocation contract (designed, not yet active)
```bash
# Once enabled, invocation will follow this contract:
lobster run --file workflows/<workflow>.lobster \
  --args-json '{"pe_id":"PE-XXXX","branch":"feature/...","implementer":"<agent-id>","validator":"<agent-id>"}'
```

## Acceptance criteria
- [ ] `.elis/pe/PE-ARCH-04/PE_TASK.md` exists and defines scope, analysis, and invocation contract
- [ ] `docs/architecture/ELIS_Lobster_Runner_Enablement.md` exists and documents current state truthfully
- [ ] `HANDOFF.md` exists with complete status packet
- [ ] No production code modified
- [ ] No CI configuration modified
- [ ] No workflow execution claimed or simulated
- [ ] No `.lobster` files claimed as executable
- [ ] `git status` confirms only expected files changed
- [ ] `python scripts/check_current_pe.py` passes (if script exists)

## Mandatory principles
- **Do not fake execution** — this PE produces documentation only
- **Do not modify production code** — no `scripts/`, no `.github/`, no CI
- **Do not register extensions** — this PE documents the path, it does not execute it
- **Do not claim `.lobster` files are executable**
- **All work within this worktree only**: `/opt/elis/agent-worktrees/PE-ARCH-04-infra-impl-b`
