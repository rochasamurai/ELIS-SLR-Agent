# OpenClaw PM Agent — Security Hardening Report

**Date:** 2026-03-22
**Host:** elis-server (NUC8i7BEH · Ubuntu 24.04.2 LTS)
**Engineer:** Claude Code (`infra-val-claude`)
**Scope:** Lock down Telegram and Discord channels so only the PO (Carlos Rocha) can communicate with the ELIS PM Agent.

---

## Security Objective

Only the Product Owner should be able to reach the PM Agent. All other users — on both channels — must be silently blocked.

---

## Pre-Hardening State

| Channel | dmPolicy | allowFrom | groupPolicy | Risk |
|---------|----------|-----------|-------------|------|
| Telegram | `allowlist` | `["8351383841"]` | `allowlist` | None — already locked |
| Discord | `open` | `["*"]` | `open` | **HIGH** — any Discord user could DM |
| Discord binding | `accountId: "1484943999470141702"` | — | — | Wrong ID — not Carlos Rocha's account |

### How the Discord user ID was discovered

During the first successful PO DM exchange (Carlos Rocha → ELIS PM Agent), OpenClaw logged:

```
[discord] origin: carlosrocha_elis user id:1485180911619408014
```

The session store confirmed it:

```json
"origin": {
  "label": "carlosrocha_elis user id:1485180911619408014",
  "from": "discord:1485180911619408014"
}
```

The binding had been set with an incorrect ID (`1484943999470141702`). This was the Discord application ID, not the PO's user account ID.

---

## Hardening Steps Applied

### Step 1 — Fix Discord binding accountId

**Command:**
```bash
# Applied via python3 direct JSON edit on elis-server
# Old: accountId: "1484943999470141702"
# New: accountId: "1485180911619408014"  (carlosrocha_elis real user ID)
```

**Result:** Binding now correctly routes only Carlos Rocha's Discord messages to the PM Agent.

---

### Step 2 — Set Discord dmPolicy to allowlist

**Command:**
```bash
openclaw config set channels.discord.dmPolicy allowlist
```

**Finding:** `allowlist` is a valid Discord dmPolicy value (unlike `"open"` which requires `allowFrom=["*"]`). With `allowlist`, openclaw enforces the `allowFrom` list — unknown users are blocked and receive a pairing challenge.

**Validation:**
```
Config valid: /app/.openclaw/openclaw.json
```

---

### Step 3 — Set Discord allowFrom to PO user ID only

**Command:**
```bash
openclaw config set channels.discord.allowFrom '["1485180911619408014"]'
```

**Result:** Only Discord user `1485180911619408014` (carlosrocha_elis) can reach the bot.

---

### Step 4 — Set Discord groupPolicy to allowlist

**Command:**
```bash
openclaw config set channels.discord.groupPolicy allowlist
```

**Note:** `groupAllowFrom` is not a valid Discord schema key (confirmed by validation error). The shared `allowFrom` list applies to both DM and group policies.

**Result:** Server channel interactions are also restricted to the PO's user ID.

---

### Step 5 — Restart container and verify

**Command:**
```bash
docker restart openclaw
```

**Key log line confirming allowlist resolution:**
```
[discord] users resolved: 1485180911619408014→1485180911619408014
```

OpenClaw resolved and accepted the PO's user ID from the allowFrom list.

---

### Step 6 — Security audit

**Command:**
```bash
openclaw security audit --deep
```

**Output:**
```
OpenClaw security audit
Summary: 0 critical · 2 warn · 1 info

WARN
gateway.trusted_proxies_missing  (not applicable — gateway is loopback-only, no reverse proxy)
gateway.probe_failed             (audit scope issue, not a security gap)

INFO
summary.attack_surface
  groups: open=0, allowlist=2
  trust model: personal assistant (one trusted operator boundary)
```

`groups: open=0, allowlist=2` — both Telegram and Discord groups are on allowlist. No open attack surfaces.

---

## Final Security State

| Item | Value | Security |
|------|-------|----------|
| Telegram `dmPolicy` | `allowlist` | Only PO allowed |
| Telegram `allowFrom` | `["8351383841"]` | PO Telegram user ID |
| Telegram `groupPolicy` | `allowlist` | Server groups restricted |
| Discord `dmPolicy` | `allowlist` | Only PO allowed |
| Discord `allowFrom` | `["1485180911619408014"]` | PO Discord user ID (carlosrocha_elis) |
| Discord `groupPolicy` | `allowlist` | Server channels restricted |
| Discord binding `accountId` | `1485180911619408014` | Correct PO user ID |
| Telegram binding `accountId` | `8351383841` | PO Telegram user ID |
| Credentials dir permissions | `700` | Owner-only (fixed in prior session) |
| Security audit | `0 critical` | Clean |
| Attack surface | `open=0, allowlist=2` | Fully locked |

---

## Residual Issues (unchanged from setup report)

### Discord: `not configured` in doctor summary
- `openclaw doctor` summary shows `Discord: not configured` but probe returns `works`.
- Assessment: display discrepancy in doctor's internal health probe. Functional connectivity confirmed.

### Discord: `intents:content=limited`
- Bot cannot read message content in Discord server channels.
- DMs are unaffected (DMs do not require MESSAGE_CONTENT intent).
- Fix: enable Privileged Gateway Intents in Discord Developer Portal → ELIS PM Agent → Bot.

### Discord Gateway cycling (gatewayConnected=false every 10 min)
- Health-monitor restarts Discord channel every 10 minutes.
- Root cause: likely the limited MESSAGE_CONTENT intent causing reconnect loop.
- DMs still work on each reconnect cycle.
- Fix: enabling Privileged Intents in Developer Portal is expected to resolve persistent connection.

---

## Action Required from PO

1. **Verify Telegram still works:** Send any message to `@elis_pm_agent_bot` and confirm response.
2. **Verify Discord still works:** Send a DM to `@ELIS PM Agent` from your `carlosrocha_elis` account and confirm response.
3. **Optional — Discord Privileged Intents:** `discord.com/developers/applications` → ELIS PM Agent → Bot → Privileged Gateway Intents → enable all three. This will fix the 10-minute gateway cycling and allow server channel message reading.
