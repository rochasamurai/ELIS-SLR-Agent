# OpenRouter + OpenCode Cutover Runbook

> Operational guide for the ELIS/OpenClaw stack on `elis-server`.
> Keep host-local runtime files out of GitHub; commit only repo-owned docs and runbooks.

---

## Purpose

This runbook captures the final operating pattern used today:

- OpenClaw remains the control plane
- OpenRouter is the primary model broker
- OpenCode is the local coding worker
- Hermes runs read-only monitoring and audit jobs
- local runtime state and secrets stay on the host, not in GitHub

---

## Target State

The preferred setup is:

- OpenClaw gateway healthy on `elis-server`
- OpenRouter auth configured for the PM path
- OpenCode authenticated to OpenRouter as the local worker
- daily read-only health audit scheduled at `07:00` and `19:00`
- minimal provider-specific CLI dependencies on the host

### What belongs in GitHub

Commit these:

- architecture/runbook documentation
- repo-owned workflow guidance
- smoke-test commands and expected outcomes
- caveats that matter to future maintainers

### What stays local

Do **not** commit:

- `~/.openclaw/*` runtime state
- secret-bearing env files
- auth tokens or token values
- transient session data
- host-only service state

---

## Verified Smoke Tests

### OpenClaw PM path

Use this to confirm the live control plane is healthy and the PM path can complete a simple turn:

```bash
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw agent --agent pm --message 'Reply with OK only.' --json --thinking low
```

Expected result:

- `status: ok`
- assistant payload text: `OK`
- provider: `openrouter`
- model path: `openrouter/auto`

### OpenClaw health checks

```bash
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw status --json
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw doctor
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw channels status
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw models status --plain
```

### OpenCode smoke test

```bash
opencode debug config
opencode run -m openrouter/xiaomi/mimo-v2.5-pro --format json 'Reply with OK only.'
```

Expected result:

- config loads successfully
- run returns `OK`
- OpenRouter credential is present in OpenCode provider state

---

## OpenRouter-first Operating Notes

### Good baseline commands

```bash
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw models set openrouter/auto
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw models auth order set openrouter:default --provider openrouter
opencode providers login --provider openrouter
opencode providers list
```

### Model routing caveat

Where catalog support is available, the exact model slug can be pinned in OpenClaw and OpenCode. In today’s setup the validated path was:

- `openrouter/xiaomi/mimo-v2.5-pro`

Fallback handling was kept simple:

- `openrouter/xiaomi/mimo-v2-pro`
- `openrouter/auto`

---

## Provider-Specific CLI Hygiene

The minimal stack does not require vendor-specific local CLIs unless a feature is explicitly vendor-only.

Recommended host policy:

- keep OpenClaw as the control plane
- keep OpenCode as the local worker
- prefer OpenRouter auth over direct vendor CLIs
- remove unused Codex/Gemini/Claude CLI installs and leftovers after confirming the OpenRouter path works

Do not remove any auth material until the replacement path has been smoke-tested.

---

## Hermes Audit Schedule

Hermes was set up as a read-only audit layer with a recurring health check at:

- `07:00`
- `19:00`

Audit scope:

- gateway health
- channel status
- model status
- auth drift
- config/runtime drift
- stale or orphaned state

The audit must remain read-only.

---

## Telegram Caveat

Telegram was removed from the config file, but the live OpenClaw status summary can still report Telegram as enabled from stale runtime state.

Treat that as a **runtime reporting bug**, not a desired configuration state.

When that happens:

1. verify the active config file
2. verify the gateway env/service state
3. restart the gateway
4. prefer file/env inspection over the live summary line

Do **not** re-add Telegram to config just to satisfy a stale status line.

---

## Recommended GitHub Update Workflow

When updating GitHub with local changes from this work:

1. keep the host runtime changes local
2. create a small docs-only branch from `main`
3. add or update runbook docs only
4. avoid secrets, tokens, and runtime state files
5. run a scope check before commit
6. open a focused PR with the docs diff only

This keeps the repo clean and makes the operational state reproducible without importing host-local credentials.

---

## Quick Reference

```bash
# OpenClaw PM smoke test
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw agent --agent pm --message 'Reply with OK only.' --json --thinking low

# OpenCode smoke test
opencode debug config && opencode run -m openrouter/xiaomi/mimo-v2.5-pro --format json 'Reply with OK only.'

# Daily read-only audit targets
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw doctor
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw channels status
OPENCLAW_STATE_DIR=/home/samurai/.openclaw /opt/openclaw/bin/openclaw models status --plain
```
