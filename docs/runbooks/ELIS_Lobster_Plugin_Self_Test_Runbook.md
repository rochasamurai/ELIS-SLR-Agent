# ELIS Lobster Plugin Self-Test Runbook

**Runbook ID**: RB-LOBSTER-TEST-02  
**PE context**: PE-ARCH-06 (`feature/pe-arch-06-controlled-lobster-plugin-activation-self-test`)  
**Author**: infra-impl-a  
**Date**: 2026-05-02

---

## Purpose

This runbook documents the reversible self-test path for enabling the bundled Lobster plugin in an isolated OpenClaw test profile (`lobster-test`). It is intentionally limited to a non-production profile and must never be used to modify production OpenClaw configuration or to run production PE workflows.

> **⚠️ IMPORTANT**: The production OpenClaw config (`~/.openclaw/openclaw.json`) must remain untouched. If a step would modify production config, stop and escalate.

---

## Prerequisites

| Prerequisite | Check | Remediation |
|---|---|---|
| OpenClaw installed | `openclaw --version` | Install OpenClaw |
| Production config exists | `test -f ~/.openclaw/openclaw.json` | Start OpenClaw once, if needed |
| Lobster extension bundled | `test -d /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/` | Reinstall / repair OpenClaw |
| PE-ARCH-06 worktree present | `test -d /opt/elis/agent-worktrees/PE-ARCH-06-infra-impl-a` | Restore the worktree |
| Carlos approval obtained | — | Get written approval before first execution |

---

## 1. Preflight checks

Run these checks before creating or using the test profile.

```bash
# Confirm you are in the correct worktree
pwd
git status --short --branch
git rev-parse --show-toplevel

# Confirm the production config is present and unchanged
ls -la ~/.openclaw/openclaw.json

# Confirm the Lobster extension tree exists
ls -ld /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/
```

Pass criteria:
- `pwd` is the PE-ARCH-06 worktree
- `git rev-parse --show-toplevel` matches the same worktree
- `git status` is clean
- production config exists and is not edited by this runbook
- Lobster extension path exists

---

## 2. Create the isolated test profile

Create only the isolated profile directory.

```bash
mkdir -p ~/.openclaw/profiles/lobster-test
cat > ~/.openclaw/profiles/lobster-test/openclaw.json <<'JSON'
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
JSON
```

Notes:
- This profile is separate from the production config.
- It must not share data or logs with the production gateway.
- If your environment uses a different profile bootstrap mechanism, keep the same isolation guarantees.

---

## 3. Self-test procedure

Use only harmless checks.

```bash
# Confirm profile config exists
ls ~/.openclaw/profiles/lobster-test/openclaw.json && echo PROFILE_CONFIG_OK

# Confirm Lobster registration in the test profile
grep -q '"extensions".*"lobster"' ~/.openclaw/profiles/lobster-test/openclaw.json && echo LOBSTER_REGISTERED

# Confirm production config is untouched
ls ~/.openclaw/openclaw.json && echo PROD_CONFIG_PRESENT

# Confirm the extension entry point exists
test -f /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js && echo EXTENSION_BINARY_OK
```

Optional dry-run check:

```bash
node /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js run \
  --dry-run \
  --file /opt/elis/agent-worktrees/PE-ARCH-06-infra-impl-a/workflows/pe-implement-validate-loop.lobster \
  --args-json '{"pe_id":"PE-ARCH-06","branch":"feature/pe-arch-06-controlled-lobster-plugin-activation-self-test","implementer":"infra-impl-a","validator":"infra-val-b"}'
```

The dry-run must stay harmless and must not execute a production PE workflow.

---

## 4. Rollback procedure

```bash
# Stop the test profile gateway if it was started
openclaw gateway stop --profile lobster-test

# Remove the profile directory
rm -rf ~/.openclaw/profiles/lobster-test/

# Re-check production config remains untouched
ls -la ~/.openclaw/openclaw.json
```

Rollback is complete when the profile directory is gone and production config is unchanged.

---

## 5. Failure modes

| Failure class | Meaning | Recovery |
|---|---|---|
| `WRONG_WORKTREE` | Command ran outside the PE-ARCH-06 worktree | Stop, re-run from the correct worktree |
| `PARTIAL_EXECUTION_UNKNOWN` | Some steps may have landed, but outcome is unclear | Inspect state before retrying |
| `REPO_STATE_UNKNOWN` | Git state is not trustworthy | Re-check status and HEAD |
| `TOOL_CONTEXT_FAILURE` | The tool session lost the intended context | Start a fresh session |
| `UI_DELIVERY_FAILURE` | The test profile or gateway did not respond as expected | Verify profile config and retry harmlessly |

---

## 6. No-production-readiness statement

This test profile is **not production-ready**.

It is designed only to prove that Lobster can be isolated behind a dedicated OpenClaw profile and safely self-tested without touching production config.

---

## 7. Relationship to `.lobster` files

The `.lobster` workflows in `workflows/` remain architecture and test artefacts. This runbook does not claim production workflow execution capability.

---

*ELIS Lobster Plugin Self-Test Runbook · PE-ARCH-06 · 2026-05-02*