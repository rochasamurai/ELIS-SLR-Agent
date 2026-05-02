# ELIS Lobster Plugin Test Enablement — Architecture & Analysis

**Document status**: Analysis and test-profile enablement specification
**PE context**: PE-ARCH-05 (`feature/pe-arch-05-lobster-plugin-controlled-test-profile`)
**Author**: infra-impl-b
**Date**: 2026-05-02
**Review level**: Implementer analysis — ready for validator (infra-val-a)

---

## 1. Overview

The Lobster plugin is bundled inside the OpenClaw distribution but is **not enabled** in the production configuration. PE-ARCH-05 specifies the architecture for enabling Lobster in an **isolated OpenClaw test profile** so agents can safely invoke Lobster workflows for testing and validation without risking the production gateway.

This document describes the test-profile approach, isolation model, invocation contract, security boundaries, and the relationship between the test profile and the existing `.lobster` workflow definition files.

---

## 2. Architecture: OpenClaw Profiles Model

### 2.1 How OpenClaw profiles work

OpenClaw supports **configuration profiles** that allow separate, isolated gateways on the same host. Profiles are selected via:

```bash
# Environment variable
export OPENCLAW_PROFILE=lobster-test

# CLI flag
openclaw gateway start --profile lobster-test
```

Each profile uses its own configuration directory under `~/.openclaw/profiles/<name>/`:

```
~/.openclaw/
├── openclaw.json                    # Production config (UNTOUCHED)
└── profiles/
    └── lobster-test/
        ├── openclaw.json            # Test profile config (EXTENSIONS + PLUGINS)
        ├── data/                    # Profile-scoped data
        └── logs/                    # Profile-scoped logs
```

### 2.2 Test profile isolation boundaries

| Aspect | Production (`default`) | Test (`lobster-test`) |
|--------|----------------------|-----------------------|
| Config file | `~/.openclaw/openclaw.json` | `~/.openclaw/profiles/lobster-test/openclaw.json` |
| Extensions | None | `["lobster"]` |
| Gateway process | `openclaw gateway` (default) | `openclaw gateway --profile lobster-test` |
| Data directory | `~/.openclaw/data/` | `~/.openclaw/profiles/lobster-test/data/` |
| Logs | `~/.openclaw/logs/` | `~/.openclaw/profiles/lobster-test/logs/` |
| Port binding | 1974 (default) | 1975 (or other available port) |
| Lobster available | ❌ | ✅ |
| Production impact | None | None (fully isolated) |

---

## 3. Enablement Model

### 3.1 What needs to happen

To make Lobster available inside the test profile, the following must be done **in the test profile only**:

1. **Create the profile config** — `~/.openclaw/profiles/lobster-test/openclaw.json` with Lobster registered as an extension
2. **Expose the Lobster CLI** — ensure `@clawdbot/lobster` is available as a Node.js dependency in the Lobster extension path, or install a PATH-level wrapper that invokes the bundled CLI
3. **Define the invocation contract** — agents invoke `lobster run` via OpenClaw's `exec` tool, targeting the test-profile gateway
4. **Add guardrails** — preflight checks, rollback procedures, and a self-test workflow

### 3.2 What is NOT required

- ❌ No modification to production `~/.openclaw/openclaw.json`
- ❌ No restart of the production gateway
- ❌ No change to any `AGENTS.md`, CI config, or `.github/` directory
- ❌ No installation of system-wide Lobster binary outside the test profile
- ❌ No modification of existing `.lobster` workflow definition files

### 3.3 Test profile config structure

```json
// ~/.openclaw/profiles/lobster-test/openclaw.json
{
  "gateway": {
    "port": 1975,
    "bind": "127.0.0.1"
  },
  "extensions": ["lobster"],
  "plugins": {
    "entries": {}
  }
}
```

### 3.4 Lobster CLI wrapper

Since the bundled Lobster CLI (`@clawdbot/lobster`) is part of the OpenClaw extension tree, it can be invoked directly via the extension path without a system-level install:

```bash
# Invoke Lobster CLI via the extension binary
node /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js run --file <path> --args-json '{...}'
```

Alternatively, if the `@clawdbot/lobster` package is restored from rollback:

```bash
/opt/openclaw/lib/node_modules/openclaw/node_modules/.bin/lobster run --file <path> --args-json '{...}'
```

---

## 4. Safe Invocation Path

### 4.1 Agent invocation contract

Once the test profile is configured, agents can invoke Lobster workflows via OpenClaw's `exec` tool within the test-profile context:

```bash
# Step 1: Ensure the test-profile gateway is running
openclaw gateway status --profile lobster-test

# Step 2: Invoke Lobster run (dry-run first)
node /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js run \
  --dry-run \
  --file /opt/elis/agent-worktrees/<worktree>/workflows/pe-implement-validate-loop.lobster \
  --args-json '{"pe_id":"PE-XXXX","branch":"feature/...","implementer":"infra-impl-a","validator":"infra-val-b"}'

# Step 3: Full execution (after dry-run passes)
node /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js run \
  --file /opt/elis/agent-worktrees/<worktree>/workflows/pe-implement-validate-loop.lobster \
  --args-json '{"pe_id":"PE-XXXX","branch":"feature/...","implementer":"infra-impl-a","validator":"infra-val-b"}'
```

### 4.2 Preflight checks (before any invocation)

Every Lobster invocation in the test profile must be preceded by these preflight checks:

1. **Profile isolation** — verify that `OPENCLAW_PROFILE` (if set) resolves to `lobster-test`, not `default`
2. **Gateway running** — confirm the test-profile gateway is responsive on port 1975
3. **Lobster binary present** — confirm the extension entry point exists at the expected path
4. **Dry-run passes** — run `lobster run --dry-run` on the target `.lobster` file
5. **Worktree path valid** — confirm the `.lobster` file path resolves within an approved agent worktree

### 4.3 Self-test procedure

After initial test-profile creation, a self-test validates that Lobster is reachable:

```bash
# 1. Confirm profile isolation
ls ~/.openclaw/profiles/lobster-test/openclaw.json && echo "PROFILE_CONFIG_OK"
grep -q '"extensions".*"lobster"' ~/.openclaw/profiles/lobster-test/openclaw.json && echo "LOBSTER_REGISTERED"

# 2. Confirm production config unmodified
ls ~/.openclaw/openclaw.json && echo "PROD_CONFIG_EXISTS"
grep -c '"extensions"' ~/.openclaw/openclaw.json || echo "PROD_NO_EXTENSIONS"

# 3. Confirm Lobster extension binary reachable
test -f /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js && echo "EXTENSION_BINARY_OK"
```

---

## 5. Rollback Procedure

To remove the test profile and all Lobster test artefacts cleanly:

```bash
# 1. Stop the test-profile gateway (if running)
openclaw gateway stop --profile lobster-test

# 2. Remove the profile directory
rm -rf ~/.openclaw/profiles/lobster-test/

# 3. Verify production config is untouched
diff <(echo "production") <(cat ~/.openclaw/openclaw.json | head -c 10)
```

---

## 6. Security Boundaries and Guardrails

### 6.1 Test-profile-only guardrails

- The Lobster extension is only registered in `~/.openclaw/profiles/lobster-test/openclaw.json`. It is **never** added to the production `~/.openclaw/openclaw.json`.
- The test-profile gateway binds to `127.0.0.1:1975` — localhost-only, not exposed on any network interface.
- The test profile shares no data directory with production.
- No Lobster workflow can access production data or configuration through the test profile.

### 6.2 Agent invocation guardrails

- Agents must verify profile isolation before invoking Lobster.
- Agents must always run `--dry-run` before full execution.
- Agents must not invoke Lobster workflows from outside the agent worktree directory.
- Agents must not invoke Lobster workflows that modify files outside the worktree.

### 6.3 Human oversight requirements

- Carlos (PO) must approve before the test profile is created on the production `elis-server`.
- Carlos (PO) must approve before any Lobster workflow is executed for the first time.
- Carlos (PO) must approve before the test profile is used outside its intended testing scope.

---

## 7. No-Production-Readiness Statement

**This test profile is explicitly not production-ready.**

The `lobster-test` profile is designed for isolated testing and validation only. It does not meet production requirements in the following areas:

- **No high-availability** — single gateway process, no failover
- **No monitoring** — no health checks, no alerting, no metrics
- **No backup** — no backup policy for test-profile data
- **No RBAC** — no access controls beyond filesystem permissions
- **No change management** — no formal change review process for test-profile modifications
- **No SLA** — no uptime guarantee or support commitment

A separate production-readiness review must be completed before any configuration described in this document may be applied to a production OpenClaw gateway.

---

## 8. Relationship to Existing `.lobster` Files

The `.lobster` files in `workflows/` (created during PE-ARCH-01/02) remain **architecture definition files** and are **not** executable by any currently active runtime. With the test profile, they become **runnable** within that isolated context, but:

- Their content is not modified by this PE
- They are not claimed as executable outside the test profile
- They are not registered as OpenClaw tools or skills
- They do not confer any production workflow execution capability