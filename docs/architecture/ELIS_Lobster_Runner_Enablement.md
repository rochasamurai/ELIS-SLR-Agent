# ELIS Lobster Runner Enablement

**Document status**: Analysis and minimum safe implementation path  
**PE context**: PE-ARCH-04 (feature/pe-arch-04-lobster-runner-enablement)  
**Author**: infra-impl-b  
**Date**: 2026-05-02  
**Review level**: Implementer analysis — ready for validator (infra-val-a)

---

## 1. Overview

Lobster is a typed workflow engine bundled within the OpenClaw runtime. It provides resumable, approval-gated workflow execution suitable for the ELIS implement-validate PE loop. This document analyses the current enablement state, documents the gap between the existing `.lobster` definition files and a working runner surface, and provides the minimum safe implementation path.

---

## 2. Current Enablement State

### 2.1 What Lobster provides
- **Typed workflow shell**: YAML-like pipeline definitions with step-level controls
- **Resumable approvals**: Workflows can pause for human approval and resume with a token
- **Plugin extension**: Distributed as `dist/extensions/lobster/` inside the OpenClaw npm package
- **CLI interface**: `lobster run --file <path> --args-json '{...}'` for programmatic execution

### 2.2 What files exist

#### `workflows/pe-implement-validate-loop.lobster`
The bounded implement-validate loop definition. Accepts 4 inputs (`pe_id`, `branch`, `implementer`, `validator`). Defines preflight, implement, validate, and decide steps. Created during PE-ARCH-01/02 as an architecture specification file.

#### `workflows/pe-recovery-check.lobster`
The read-only recovery workflow. Classifies failures into 9 categories. Defines verification fields. Created during PE-ARCH-01/02.

**Important**: Both files are **architecture definition files**, not executable scripts. They are plain-text YAML-like documents that describe workflow behaviour. They do not have execute permissions and cannot be run by Lobster or any other engine until the runner infrastructure is enabled.

### 2.3 What is bundled vs what is active

| Component | Bundled | Active | Notes |
|-----------|---------|--------|-------|
| Lobster CLI binary | ❌ (rollback only) | ❌ | `@clawdbot/lobster` exists in `/opt/openclaw/lib/node_modules/openclaw.rollback-20260417T200113Z/node_modules/.bin/lobster` but NOT in the active install |
| Lobster extension plugin | ✅ `/opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/` | ❌ | Extension code is bundled at build time but NOT registered in `~/.openclaw/openclaw.json` |
| Lobster in PATH | ❌ | ❌ | `which lobster` returns nothing |
| Lobster in plugin config | ❌ | ❌ | No `plugins.entries.lobster` or `extensions` section in gateway config |
| Lobster as agent tool | ❌ | ❌ | No `process` or tool binding exposes Lobster to agent runtime |
| `.lobster` files | ✅ | ✅ (as docs) | Exist in `workflows/` but only as architectural definitions |
| TaskFlow lobster skill | ✅ | ✅ | OpenClaw Skill supports lobster files as orchestration scripts, not CLI runnable |

### 2.4 Gap analysis

**Critical gaps preventing Lobster execution today:**

1. **No active Lobster CLI**: The `@clawdbot/lobster` npm package is not installed in the active OpenClaw runtime (`/opt/openclaw/lib/node_modules/openclaw/`). It exists only in the rollback snapshot. The extension directory exists but the core `@clawdbot/lobster` package (referenced by `import`) is missing.

2. **No extension registration**: Even if the CLI were present, OpenClaw's gateway does not have Lobster registered as an extension or plugin. The `~/.openclaw/openclaw.json` config has no `extensions` key and no Lobster plugin entry.

3. **No PATH exposure**: There is no `lobster` binary or wrapper script in any PATH directory (`/usr/local/bin`, `~/.local/bin`, etc.).

4. **No agent tool surface**: Agents cannot invoke Lobster because no OpenClaw tool, process binding, or subcommand maps to `lobster run`.

5. **No invocation contract documented**: Prior to this PE, there was no documented specification of how an agent would call Lobster, what arguments to pass, or what output to expect.

---

## 3. Minimum Safe Implementation Path

This section describes the **minimum changes** to enable Lobster workflow execution. **Do not execute these steps as part of this PE** — they are documented for future implementation.

### Step 1: Restore the Lobster CLI package

```bash
# From the rollback snapshot, link or copy the @clawdbot/lobster package
cp -r /opt/openclaw/lib/node_modules/openclaw.rollback-20260417T200113Z/node_modules/@clawdbot/lobster \
      /opt/openclaw/lib/node_modules/openclaw/node_modules/@clawdbot/lobster
```

Alternatively, install from npm:
```bash
cd /opt/openclaw/lib/node_modules/openclaw
npm install @clawdbot/lobster
```

### Step 2: Register the Lobster extension

Edit `~/.openclaw/openclaw.json` to add:
```json
{
  "extensions": ["lobster"]
}
```

Then restart the gateway:
```bash
openclaw gateway restart
```

### Step 3: Create a PATH wrapper

Install a wrapper script at `/usr/local/bin/lobster`:
```bash
#!/bin/bash
# ELIS Lobster wrapper — invokes the bundled Lobster CLI
exec /opt/openclaw/lib/node_modules/openclaw/node_modules/.bin/lobster "$@"
```

Make it executable: `chmod +x /usr/local/bin/lobster`

### Step 4: Verify with dry-run

```bash
lobster run --dry-run --file /path/to/workflows/pe-implement-validate-loop.lobster \
  --args-json '{"pe_id":"PE-XXXX","branch":"feature/...","implementer":"infra-impl-b","validator":"infra-val-a"}'
```

The `--dry-run` flag validates the workflow without executing any steps.

---

## 4. Invocation Contract

### 4.1 Workflow arguments

The `pe-implement-validate-loop.lobster` workflow accepts these inputs:

| Input | Type | Description |
|-------|------|-------------|
| `pe_id` | string | PE identifier, e.g. `PE-ARCH-05` |
| `branch` | string | Git branch name, e.g. `feature/pe-arch-05-something` |
| `implementer` | string | Agent ID for implementer role, e.g. `infra-impl-a` |
| `validator` | string | Agent ID for validator role, e.g. `infra-val-b` |

### 4.2 CLI invocation

```bash
# From the worktree root:
cd /opt/elis/agent-worktrees/<worktree>

# Dry-run (validate structure, no execution):
lobster run --dry-run --file workflows/pe-implement-validate-loop.lobster \
  --args-json '{"pe_id":"PE-XXXX","branch":"feature/...","implementer":"infra-impl-b","validator":"infra-val-a"}'

# Full execution:
lobster run --file workflows/pe-implement-validate-loop.lobster \
  --args-json '{"pe_id":"PE-XXXX","branch":"feature/...","implementer":"infra-impl-b","validator":"infra-val-a"}'

# Recovery check:
lobster run --file workflows/pe-recovery-check.lobster
```

### 4.3 Agent dispatch

The Lobster workflow is designed to be invoked from within an OpenClaw agent session. Once Lobster is available as a tool, agents will use it via:

```
exec command="lobster run --file ... --args-json '...'"
```

Or, if Lobster is registered as an OpenClaw extension, via an `openclaw lobster run` subcommand.

### 4.4 Approval flow

Lobster supports resumable approvals. When a workflow step requires human approval, Lobster pauses and emits a resume token. The human (Carlos) approves via:
```bash
lobster resume --token <token> --approve yes
```

This matches the PE state machine requirement: "Carlos approval required before push/PR/merge."

### 4.5 Output and status packets

Lobster workflow output includes a status packet with these fields (matching the existing `pe-recovery-check.lobster` output):
- `PE`, `Branch`, `Current state`, `Last activity`
- `Expected artefacts`, `Found artefacts`, `Missing artefacts`
- `Errors`, `Failure class`, `Next owner`, `Next action`
- `Evidence`

---

## 5. Safety Rules

### 5.1 No automatic push/PR/merge
The Lobster workflow definitions explicitly disable automatic push, PR, and merge. Carlos approval is required at the final gate.

### 5.2 Read-only recovery
The `pe-recovery-check.lobster` workflow is read-only — it classifies failures without modifying state.

### 5.3 Bounded loop
The implement-validate loop enforces `max_iterations: 3`, preventing unbounded execution.

### 5.4 Worktree isolation
All Lobster workflow execution must occur within the assigned agent worktree. The workflow file paths are relative to the worktree root.

---

## 6. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Lobster CLI fails to start | Execution blocked | Low | Step-by-step verification per Section 3 |
| Wrong npm package version | Compatibility issue | Low | Use rollback copy as source of truth |
| Gateway restart fails | Service interruption | Low | `openclaw gateway status` before/after; rollback config if needed |
| Agent cannot find `lobster` in PATH | Invocation fails | Medium | Create wrapper script explicitly |
| `.lobster` parse error | Workflow won't run | Low | Run `lobster run --dry-run` for validation before production use |

---

## 7. Verification Checklist

Once the enablement steps are executed (separate PE or PO action):

- [ ] `lobster --help` returns CLI usage
- [ ] `lobster run --dry-run --file workflows/pe-implement-validate-loop.lobster --args-json '{}'` passes validation
- [ ] `lobster run --dry-run --file workflows/pe-recovery-check.lobster` passes validation
- [ ] OpenClaw gateway logs show `lobster` extension loaded (no errors)
- [ ] A local PE workflow dry-run completes without modifying any files
- [ ] The approval/resume flow can be demonstrated in test mode

---

## 8. Current State Summary

| Aspect | Current | Target |
|--------|---------|--------|
| Lobster CLI | Not in active install | Active via wrapper |
| Extension registration | Not configured | Registered in openclaw.json |
| PATH availability | None | `/usr/local/bin/lobster` |
| `.lobster` files | Architecture definitions only | Runnable via `lobster run` |
| Agent tool surface | None | `lobster run` via exec |
| Invocation contract | Not documented | Documented in this file |
| Workflow execution | Not possible | Demonstrated via dry-run |
