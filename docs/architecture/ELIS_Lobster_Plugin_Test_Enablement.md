# ELIS Lobster Plugin Test Enablement — Architecture & Analysis

**Document status**: Analysis and test-profile enablement specification
**PE context**: PE-ARCH-06 (`feature/pe-arch-06-controlled-lobster-plugin-activation-self-test`)
**Author**: infra-impl-a
**Date**: 2026-05-02
**Review level**: Implementer analysis — ready for validator (infra-val-b)

---

## 1. Overview

The Lobster plugin is bundled inside the OpenClaw distribution but is **not enabled** in the production configuration. PE-ARCH-06 documents the self-test path for enabling Lobster in an **isolated OpenClaw test profile** so it can be verified without affecting the production gateway.

This document describes the test-profile model, isolation boundaries, invocation contract, rollback posture, and the relationship to the runbook in this PE.

---

## 2. Architecture: OpenClaw Profiles Model

### 2.1 How OpenClaw profiles work

OpenClaw supports configuration profiles that keep separate, isolated gateway state on the same host. The test profile is selected via:

```bash
export OPENCLAW_PROFILE=lobster-test
# or
openclaw gateway start --profile lobster-test
```

Each profile uses its own configuration directory under `~/.openclaw/profiles/<name>/`.

### 2.2 Isolation boundaries

| Aspect | Production (`default`) | Test (`lobster-test`) |
|---|---|---|
| Config file | `~/.openclaw/openclaw.json` | `~/.openclaw/profiles/lobster-test/openclaw.json` |
| Extensions | None | `["lobster"]` |
| Gateway process | Default gateway | `openclaw gateway --profile lobster-test` |
| Data directory | Production data | Profile-scoped data |
| Logs | Production logs | Profile-scoped logs |
| Port binding | Production port | Local test port (e.g. `1975`) |
| Lobster available | ❌ | ✅ |
| Production impact | None | None |

---

## 3. Enablement model

### 3.1 What must happen in the test profile only

1. Create the profile config under `~/.openclaw/profiles/lobster-test/openclaw.json`
2. Register Lobster as an extension only in that profile
3. Invoke Lobster through the documented extension entry point
4. Preflight, dry-run, verify, and rollback without touching production config

### 3.2 What is not required

- ❌ No modification to production `~/.openclaw/openclaw.json`
- ❌ No restart of the production gateway
- ❌ No system-wide Lobster installation
- ❌ No changes to CI, `.github/`, or agent definitions
- ❌ No modification of `.lobster` workflow files

### 3.3 Profile config structure

```json
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

### 3.4 Invocation contract

The documented Lobster entry point remains:

```bash
node /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js run --dry-run --file <workflow-file> --args-json '{...}'
```

This contract is profile-scoped and must stay inside the isolated test profile.

---

## 4. Self-test posture

PE-ARCH-06 adds a harmless self-test to verify:

- profile isolation
- Lobster registration in the test profile
- extension binary reachability
- safe dry-run behavior
- rollback safety

The self-test must not execute a production PE workflow.

---

## 5. Security boundaries and guardrails

- Lobster is only registered in the test profile.
- Production config remains untouched.
- The test profile is localhost-bound and isolated.
- No test-state artifact may be treated as production readiness.
- Human approval is required before any first-time live execution.

---

## 6. No-production-readiness statement

This test profile is explicitly not production-ready.

It is a controlled verification path, not a production enablement of Lobster.

---

## 7. Relationship to `.lobster` files

The `.lobster` files under `workflows/` remain specification artefacts. This PE does not modify their semantics; it only documents how they would be invoked inside the isolated test profile.

---

*ELIS Lobster Plugin Test Enablement · PE-ARCH-06 · 2026-05-02*