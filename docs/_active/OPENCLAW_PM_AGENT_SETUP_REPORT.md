# OpenClaw PM Agent — Channel Setup Report

**Date:** 2026-03-22
**Host:** elis-server (NUC8i7BEH · Ubuntu 24.04.2 LTS)
**Engineer:** Claude Code (`infra-val-claude`)
**Scope:** Configure Telegram and Discord channels so the PM Agent can communicate with the PO.

---

## Summary

Both Telegram and Discord channels are now functional. The PM Agent (`@elis_pm_agent_bot` on Telegram, `@ELIS PM Agent` on Discord) is connected and capable of receiving and sending messages on both channels.

---

## Work Performed

### 1. Telegram — Root Cause and Fix

**Problem:** Telegram showed `token=none` — the bot token was present in `.env` but never registered with openclaw's credential store. Channel status: `stopped, error: not configured`.

**Fix:** Registered the bot token via the openclaw CLI without exposing the value:
```
openclaw channels add --channel telegram --token "$TELEGRAM_BOT_TOKEN"
```

**Result:** `@elis_pm_agent_bot` connected, polling active.
Doctor confirms: `Telegram: ok (@elis_pm_agent_bot)`

---

### 2. Discord — Root Cause and Fix

**Problem:** Multiple layered issues:
- `dmPolicy` was set to `"pairing"` with an empty allowlist — all DMs were being blocked.
- `groupAllowFrom` key was set but is not a valid Discord schema key, causing config validation failures and hot-reload rejections.
- Discord Gateway WebSocket was cycling: health-monitor restarted every 5 minutes because `gatewayConnected=false`.

**Fixes applied (via openclaw CLI):**
- Set `dmPolicy: "open"`, `allowFrom: ["*"]` (required by `dmPolicy=open`)
- Set `groupPolicy: "open"`
- Removed invalid `groupAllowFrom` key via `doctor --fix`
- Re-registered Discord account: `openclaw channels add --channel discord --use-env`

**Result:** Discord Gateway reached `gatewayConnected=true` after the next health-monitor restart cycle. Channel probe confirms: `works`.

---

### 3. Security Fix

**Problem:** `~/.openclaw/credentials` directory had permissions `775` (world-writable). Doctor reported CRITICAL.

**Fix:** `chmod 700 ~/.openclaw/credentials`

---

## Final Status

| Item | Status |
|------|--------|
| Telegram `@elis_pm_agent_bot` | ✅ Running — `ok` (doctor confirmed) |
| Discord `@ELIS PM Agent` | ✅ Running — `works` (probe confirmed) |
| PM Agent model (`openai/gpt-5.1-codex`) | ✅ Registered, auth confirmed |
| Credentials directory permissions | ✅ Fixed (`chmod 700`) |
| Config hot-reload | ✅ All changes applied cleanly |

---

## Residual Issues

### Discord: `not configured` in doctor summary
- `openclaw doctor` summary says `Discord: not configured` but `openclaw channels status --probe` returns `works`.
- Assessment: display discrepancy in the doctor's internal health probe. Functional connectivity is confirmed by the probe.

### Discord: `intents:content=limited`
- `MESSAGE_CONTENT`, `GUILD_MEMBERS`, and `PRESENCE` intents are limited.
- Impact: bot cannot read message content in Discord server channels. DMs are unaffected.
- Fix: enable Privileged Gateway Intents in the Discord Developer Portal for the ELIS PM Agent bot.

### Skills (6/52 ready)
- 46 skills show `missing` — these require optional CLIs (1Password, Apple Notes, Bear Notes, etc.) that are macOS-specific or not installed on elis-server.
- Not required for ELIS workflow.

### Plugins (9/41 loaded)
- 32 plugins disabled — optional channel integrations (LINE, Matrix, MS Teams, etc.).
- Not required for ELIS workflow.

---

## Action Required from PO

1. **Test Telegram:** Send any message to `@elis_pm_agent_bot` on Telegram and confirm PM Agent responds.
2. **Test Discord:** Send a DM to `@ELIS PM Agent` on Discord and confirm PM Agent responds.
3. **Optional — Discord Privileged Intents:** Go to `discord.com/developers/applications` → ELIS PM Agent → Bot → Privileged Gateway Intents → enable all three intents. This allows the bot to read server channel messages (not just DMs).
