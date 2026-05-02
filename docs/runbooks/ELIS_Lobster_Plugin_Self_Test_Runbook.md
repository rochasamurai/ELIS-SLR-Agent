# ELIS Lobster Plugin Self-Test Runbook

**Runbook ID**: RB-LOBSTER-TEST-02
**PE context**: PE-ARCH-07 (`feature/pe-arch-07-execute-isolated-lobster-plugin-self-test`)
**Author**: infra-impl-b
**Date**: 2026-05-02

## Purpose

Document the isolated `lobster-test` profile self-test used for PE-ARCH-07. This is a harmless profile check only: no production config changes, no production PE workflow runs, and no Lobster enablement outside the test profile.

## Self-test procedure used

```bash
ls ~/.openclaw/profiles/lobster-test/openclaw.json && echo "PROFILE_CONFIG_OK"
grep -q '"extensions".*"lobster"' ~/.openclaw/profiles/lobster-test/openclaw.json && echo "LOBSTER_REGISTERED"
ls ~/.openclaw/openclaw.json && echo "PROD_CONFIG_EXISTS"
grep -c '"extensions"' ~/.openclaw/openclaw.json || echo "PROD_NO_EXTENSIONS"
test -f /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js && echo "EXTENSION_BINARY_OK"
```

## Observed results

- `PROFILE_CONFIG_OK`
- `LOBSTER_REGISTERED`
- `PROD_CONFIG_EXISTS`
- `PROD_NO_EXTENSIONS`
- `EXTENSION_BINARY_OK`

## Rollback note

If the test profile ever needs removal, delete only `~/.openclaw/profiles/lobster-test/` after stopping the test-profile gateway. Production `~/.openclaw/openclaw.json` remains untouched.

## Non-goals

- No production OpenClaw edits
- No production Lobster enablement
- No production PE workflow execution
