# ELIS TODO — Improvements Backlog

Items that are known limitations or future improvements, not blocking current workflow.

---

## OpenClaw / elis-server

### DISCORD-01 — Discord server channel messages not received by PM Agent

**Status:** Open
**Priority:** Low (DMs work; server channels are not part of current workflow)
**Logged:** 2026-03-22

**Description:**
Messages posted in Discord server channels (e.g. `#general`) are not received by ELIS PM Agent. Only DMs work.

**Root cause:**
OpenClaw is not requesting the `MESSAGE_CONTENT` privileged intent in its Discord Gateway connection, despite the intent being enabled in the Discord Developer Portal. OpenClaw logs report `intents:content=limited` on every startup cycle.

**Impact:**
- Bot ignores messages in `#general` and other server channels.
- DM communication with PM Agent (the primary workflow) is unaffected.

**Possible fixes:**
1. Check if OpenClaw has a config key (e.g. `channels.discord.intents`) to explicitly request `MESSAGE_CONTENT`, `GUILD_MEMBERS`, and `PRESENCE` at the Gateway level.
2. File a bug report with the OpenClaw project if no config key exists.

---

### DISCORD-02 — Discord Gateway cycling every 10 minutes

**Status:** Open
**Priority:** Low (bot reconnects automatically; DMs are not lost)
**Logged:** 2026-03-22

**Description:**
The Discord Gateway WebSocket disconnects approximately every 10 minutes. The health-monitor restarts the channel, and `gatewayConnected=true` is restored within ~2 seconds. No messages are lost during this window for DM workflows.

**Root cause:**
Unknown. Suspected keepalive / heartbeat issue in this version of OpenClaw running in a Docker container. May be related to the limited intents above.

**Possible fixes:**
1. Investigate OpenClaw heartbeat config.
2. Check if enabling full privileged intents (DISCORD-01) resolves the cycling.
3. Upgrade OpenClaw image if a newer version addresses gateway stability.

---
