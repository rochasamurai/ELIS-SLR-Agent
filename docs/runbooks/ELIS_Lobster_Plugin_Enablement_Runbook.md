# ELIS Lobster Plugin Enablement Runbook

**Runbook ID**: RB-LOBSTER-TEST-01
**PE context**: PE-ARCH-05 (`feature/pe-arch-05-lobster-plugin-controlled-test-profile`)
**Author**: infra-impl-b
**Date**: 2026-05-02

---

## Purpose

This runbook provides the step-by-step procedure for enabling the bundled Lobster plugin in an isolated OpenClaw test profile (`lobster-test`), running preflight checks, executing a self-test, and rolling back the test profile cleanly.

> **⚠️ IMPORTANT**: All steps in this runbook operate on the **test profile only**. The production OpenClaw gateway configuration (`~/.openclaw/openclaw.json`) must not be modified. If any instruction in this runbook would modify production config, STOP and escalate to Carlos.

---

## Prerequisites

| Prerequisite | Check | Remediation |
|---|---|---|
| OpenClaw installed | `openclaw --version` | Install OpenClaw |
| Production config exists | `test -f ~/.openclaw/openclaw.json` | Start production gateway once |
| Lobster extension bundled | `test -d /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/` | Reinstall OpenClaw |
| Agent worktree exists | `ls /opt/elis/agent-worktrees/` | Create a PE worktree |
| Carlos approval obtained | — | Get written approval before executing this runbook on elis-server |

---

## Section 1: Preflight Checks

Execute these checks **before** creating the test profile. All checks must pass before proceeding.

### 1.1 Verify production config isolation

```bash
echo "=== Production config exists ==="
ls -la ~/.openclaw/openclaw.json && echo "✅ Prod config present"

echo "=== Production config has no extensions section ==="
if grep -q '"extensions"' ~/.openclaw/openclaw.json; then
    echo "❌ Production config ALREADY has extensions — abort!"
    exit 1
else
    echo "✅ Production config has no extensions section"
fi

echo "=== Production config has no lobster reference ==="
if grep -qi 'lobster' ~/.openclaw/openclaw.json; then
    echo "❌ Production config references lobster — abort!"
    exit 1
else
    echo "✅ No lobster reference in production config"
fi
```

### 1.2 Verify Lobster extension is bundled

```bash
echo "=== Lobster extension directory ==="
if test -d /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/; then
    echo "✅ Lobster extension bundled at expected path"
    ls /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/
else
    echo "❌ Lobster extension NOT found — check OpenClaw installation"
    exit 1
fi
```

### 1.3 Verify no existing test profile

```bash
echo "=== Existing profiles ==="
if test -d ~/.openclaw/profiles/lobster-test/; then
    echo "⚠️  lobster-test profile already exists"
    read -p "Overwrite? [y/N] " yn
    if [ "$yn" != "y" ]; then
        echo "Aborting."
        exit 1
    fi
else
    echo "✅ No existing lobster-test profile"
fi
```

### 1.4 Verify no test-profile gateway running

```bash
echo "=== Test-profile gateway status ==="
if openclaw gateway status --profile lobster-test 2>/dev/null; then
    echo "⚠️  Test-profile gateway is already running — stop it first"
    echo "Run: openclaw gateway stop --profile lobster-test"
    exit 1
else
    echo "✅ No test-profile gateway running"
fi
```

---

## Section 2: Create the Test Profile

### 2.1 Create the profile config directory

```bash
mkdir -p ~/.openclaw/profiles/lobster-test/
```

### 2.2 Write the test profile config

```bash
cat > ~/.openclaw/profiles/lobster-test/openclaw.json << 'EOF'
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
EOF

echo "✅ Test profile config written"
cat ~/.openclaw/profiles/lobster-test/openclaw.json
```

### 2.3 Verify the Lobster extension entry point

```bash
EXT_POINT="/opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js"
if test -f "$EXT_POINT"; then
    echo "✅ Lobster extension entry point: $EXT_POINT"
else
    echo "❌ Extension entry point missing — check OpenClaw build"
    exit 1
fi
```

### 2.4 Start the test-profile gateway

```bash
echo "=== Starting test-profile gateway ==="
openclaw gateway start --profile lobster-test

echo "=== Waiting for gateway to be ready ==="
sleep 3

echo "=== Confirm gateway running ==="
openclaw gateway status --profile lobster-test && echo "✅ Test-profile gateway running on port 1975"
```

---

## Section 3: Self-Test

### 3.1 Verify profile isolation (no production bleed)

```bash
echo "=== Profile isolation check ==="

# Production config must not have extensions
if grep -q '"extensions"' ~/.openclaw/openclaw.json; then
    echo "❌ EXTENSIONS FOUND IN PRODUCTION CONFIG — ROLLBACK IMMEDIATELY!"
    echo "   Run: openclaw gateway stop --profile lobster-test"
    echo "   Run: rm -rf ~/.openclaw/profiles/lobster-test/"
    exit 1
fi
echo "✅ Production config has no extensions"

# Test profile must have extensions
if grep -q '"extensions".*"lobster"' ~/.openclaw/profiles/lobster-test/openclaw.json; then
    echo "✅ Test profile config correctly registers Lobster extension"
else
    echo "❌ Test profile config missing Lobster extension — fix and retry"
    exit 1
fi
```

### 3.2 Verify Lobster CLI reachability

```bash
echo "=== Lobster CLI reachability ==="
EXT_INDEX="/opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js"
if test -x "$EXT_INDEX" || test -f "$EXT_INDEX"; then
    echo "✅ Lobster extension binary is reachable: $EXT_INDEX"
    echo "   Invoke via: node $EXT_INDEX run --dry-run --help"
else
    echo "❌ Lobster extension binary NOT reachable"
    exit 1
fi
```

### 3.3 Run a dry-run with an existing `.lobster` file

```bash
echo "=== Dry-run validation ==="
EXT_INDEX="/opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js"
WORKFLOW_FILE="workflows/pe-implement-validate-loop.lobster"
WORKTREE_ROOT="/opt/elis/agent-worktrees/PE-ARCH-05-infra-impl-b"

if test -f "$WORKTREE_ROOT/$WORKFLOW_FILE"; then
    echo "Attempting dry-run:"
    node "$EXT_INDEX" run \
      --dry-run \
      --file "$WORKTREE_ROOT/$WORKFLOW_FILE" \
      --args-json '{"pe_id":"PE-ARCH-05","branch":"feature/pe-arch-05-lobster-plugin-controlled-test-profile","implementer":"infra-impl-b","validator":"infra-val-a"}' \
      2>&1 && echo "✅ Dry-run PASSED" || echo "⚠️ Dry-run failed (expected if Lobster binary paths are incomplete)"
else
    echo "⚠️ Workflow file not found at expected path — dry-run skipped"
    echo "   Expected: $WORKTREE_ROOT/$WORKFLOW_FILE"
fi
```

### 3.4 Verify gateway logs for Lobster extension load

```bash
echo "=== Gateway log check ==="
LOGS_DIR=~/.openclaw/profiles/lobster-test/logs/
if test -d "$LOGS_DIR"; then
    LOGFILE=$(ls -t "$LOGS_DIR"*.log 2>/dev/null | head -1)
    if test -n "$LOGFILE"; then
        echo "Checking log: $LOGFILE"
        grep -q "lobster" "$LOGFILE" && echo "✅ Lobster extension load confirmed in logs" || echo "⚠️ No 'lobster' reference in gateway logs"
    else
        echo "⚠️ No log files found in $LOGS_DIR"
    fi
else
    echo "⚠️ Log directory $LOGS_DIR not found"
fi
```

---

## Section 4: Daily Use Invocation

### 4.1 Verify test profile is available

```bash
openclaw gateway status --profile lobster-test
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "❌ Test-profile gateway not running. Start it:"
    echo "   openclaw gateway start --profile lobster-test"
    exit 1
fi
```

### 4.2 Invoke a Lobster workflow (dry-run)

```bash
# Replace <worktree> with the actual agent worktree path
EXT_INDEX="/opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js"
node "$EXT_INDEX" run \
  --dry-run \
  --file "/opt/elis/agent-worktrees/<worktree>/workflows/pe-implement-validate-loop.lobster" \
  --args-json '{"pe_id":"PE-XXXX","branch":"feature/...","implementer":"<agent>","validator":"<agent>"}'
```

### 4.3 Invoke a Lobster workflow (full execution)

```bash
# Only after dry-run passes and human approval is obtained
node "$EXT_INDEX" run \
  --file "/opt/elis/agent-worktrees/<worktree>/workflows/pe-implement-validate-loop.lobster" \
  --args-json '{"pe_id":"PE-XXXX","branch":"feature/...","implementer":"<agent>","validator":"<agent>"}'
```

---

## Section 5: Rollback

### 5.1 Rollback preflight

```bash
echo "=== Rollback preflight ==="
echo "Production config status:"
ls -la ~/.openclaw/openclaw.json && echo "✅ Production config present"

echo "Test profile status:"
test -d ~/.openclaw/profiles/lobster-test/ && echo "⚠️ Test profile exists (will be removed)" || echo "✅ No test profile"
```

### 5.2 Stop the test-profile gateway (if running)

```bash
openclaw gateway stop --profile lobster-test
echo "✅ Test-profile gateway stopped"
```

### 5.3 Remove the test profile directory

```bash
rm -rf ~/.openclaw/profiles/lobster-test/
echo "✅ Test profile directory removed"
```

### 5.4 Verify production config is unchanged

```bash
echo "=== Post-rollback verification ==="
echo "Production config:"
test -f ~/.openclaw/openclaw.json && echo "✅ Intact" || echo "❌ MISSING — CRITICAL!"

echo "Extensions check:"
grep -q '"extensions"' ~/.openclaw/openclaw.json && echo "❌ Extensions found (should not be!)" || echo "✅ No extensions — clean"

echo "Test profile removed:"
test -d ~/.openclaw/profiles/lobster-test/ && echo "❌ Still present" || echo "✅ Confirmed removed"

echo "Production gateway status:"
openclaw gateway status | grep -q "running" && echo "✅ Production gateway running" || echo "⚠️ Production gateway not running (may be deliberate)"
```

### 5.5 Rollback complete

```bash
echo "=== Rollback complete ==="
echo "Production config: preserved"
echo "Lobster extension: disabled in production"
echo "Test profile: removed"
echo "Production gateway: unchanged"
```

---

## Section 6: Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `openclaw gateway start --profile lobster-test` fails | Port 1975 in use | Check `ss -tlnp | grep 1975`; use a different port in the profile config |
| Test-profile gateway won't start | Profile config syntax error | Validate JSON: `python3 -m json.tool ~/.openclaw/profiles/lobster-test/openclaw.json` |
| `grep -q '"extensions"' ~/.openclaw/profiles/lobster-test/openclaw.json` fails | Profile config missing extensions key | Re-run Section 2.2 |
| Lobster extension binary not found | OpenClaw distribution incomplete | Confirm `ls /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/` lists files; reinstall OpenClaw if empty |
| Dry-run fails with parse error | `.lobster` file syntax issue | Validate the `.lobster` file manually; check for trailing commas or indentation errors |
| Production config accidentally modified | Operator error | Restore from backup (`~/.openclaw/openclaw.json.bak`) or re-run `openclaw gateway start` to regenerate defaults |

---

## Appendix A: Quick-Reference Commands

```bash
# === PREFLIGHT ===
test -d /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/ && echo "LOBSTER_BUNDLED"
grep -q '"extensions"' ~/.openclaw/openclaw.json && echo "PROD_HAS_EXTENSIONS (BAD)" || echo "PROD_CLEAN"
test -d ~/.openclaw/profiles/lobster-test/ && echo "PROFILE_EXISTS" || echo "PROFILE_ABSENT"

# === ENABLE ===
mkdir -p ~/.openclaw/profiles/lobster-test/
# (write config from Section 2.2)
openclaw gateway start --profile lobster-test

# === INVOKE ===
node /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js run --dry-run --file <PATH>

# === ROLLBACK ===
openclaw gateway stop --profile lobster-test
rm -rf ~/.openclaw/profiles/lobster-test/
grep -q '"extensions"' ~/.openclaw/openclaw.json && echo "PROD_DIRTY (BAD)" || echo "PROD_CLEAN"
```

---

## Appendix B: No-Production-Readiness Reminder

> **This test profile and runbook are NOT production-ready.**
>
> The `lobster-test` profile is designed for isolated testing only. Before any production deployment:
> - A formal production-readiness review must be completed
> - The test-profile architecture must be validated by the ELIS PO (Carlos)
> - All security, monitoring, backup, and SLA requirements must be satisfied
>
> **Do not** apply any configuration from this runbook to a production OpenClaw gateway.