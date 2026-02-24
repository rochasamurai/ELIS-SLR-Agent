# Telegram Setup — PO Onboarding Guide (PE-OC-17)

> **Prerequisite:** PE-OC-01 through PE-OC-16 complete. OpenClaw Docker container is running with the gateway bound to the LAN interface (`--bind lan`). The host has your Telegram bot token and PO account ready.

## Overview

The PM Agent is the only agent exposed to Telegram. PO messages go to the PM Agent through the bot, and all worker agents remain isolated inside the container with `:ro` workspace mounts. This runbook documents the live pairing sequence for PE-OC-17.

---

## Step 0 — Confirm gateway binding and port mapping

1. `docker compose ps` → OpenClaw container must be `Up`.
2. Inspect `docker-compose.yml`:
   - Port mapping should read `127.0.0.1:18789:18789`.
   - The service command should be `node openclaw.mjs gateway --allow-unconfigured --bind lan`.
3. The gateway must expose a WebSocket endpoint on `ws://127.0.0.1:18789`.
4. Run the WebSocket health check:

   ```bash
   python scripts/check_openclaw_health.py
   ```

   Success message: `OpenClaw WebSocket handshake succeeded (status 101).`

---

## Step 1 — Acquire the Telegram bot token

1. On Telegram, open `@BotFather` and send `/newbot`.
2. Follow the prompts to name and username the bot.
3. Copy the token (`123456789:AAFxxxxx` style).
4. Secure the token outside the repo:

   ```bash
   mkdir -p ~/.openclaw
   chmod 700 ~/.openclaw
   cat <<'EOF' >> ~/.openclaw/.env
   TELEGRAM_BOT_TOKEN=<your-token-here>
   EOF
   ```

   > /!\ Do **not** commit `.env`. The token must stay on the host.

---

## Step 2 — Deploy workspaces (if not already present)

```bash
bash scripts/deploy_openclaw_workspaces.sh
```

This syncs `openclaw/workspaces/` → `~/openclaw/workspaces/` so the PM Agent sees the latest AGENTS, LESSONS, and SOUL files.

---

## Step 3 — Pair the PO Telegram account

1. Run inside the container:

   ```bash
   docker exec openclaw node openclaw.mjs pairing approve
   ```

2. The bot sends a pairing code to the PO’s Telegram account.
3. From the PO account, reply to the bot with that code within five minutes.
4. The gateway prints the paired Telegram user ID. Update `openclaw/openclaw.json` immediately:

   ```json
   "bindings": [
     {
       "agentId": "pm",
       "match": {
         "channel": "telegram",
         "accountId": "<PAIRED_TELEGRAM_USER_ID>"
       }
     }
   ]
   ```

   Replace `<PAIRED_TELEGRAM_USER_ID>` with the actual numeric ID returned by the pairing command. Commit that change as part of this PE.

---

## Step 4 — Verify PM Agent responds to `status`

1. From the PO Telegram account, send:

   ```
   status
   ```

2. Expect a reply within 30 seconds:

   ```
   Active PEs — YYYY-MM-DD HH:MM UTC
   PE-OC-17 | planning | CODEX / Claude Code
   ```

3. If no reply arrives, inspect container logs and re-run the health check:

   ```bash
   docker compose logs openclaw --tail 50
   python scripts/check_openclaw_health.py
   ```

4. Confirm `python scripts/check_openclaw_doctor.py` still exits 0 after the pairing (enforces `exec.ask` and `skills.hub.autoInstall` rules).

---

## Security notes

- The bot token must stay on the host and **never** be committed. The paired Telegram account ID is safe to record inside `openclaw/openclaw.json` so the binding survives container restarts.
- Running the gateway with `--bind lan` exposes `ws://0.0.0.0:18789` inside the container; keep the host port bound to `127.0.0.1`.
- `scripts/check_openclaw_health.py` now uses a WebSocket handshake. If it fails, restart the container before retrying pairing.
- Re-run the pairing flow whenever the PO account or bot token changes.

---

## Troubleshooting

| Symptom | Action |
|---|---|
| No handshake success | Confirm `command` includes `--bind lan` and port mapping is `:18789`. |
| Pairing code expires | Re-run `docker exec openclaw node openclaw.mjs pairing approve` and reply faster. |
| PM Agent ignores `status` | Check `~/.openclaw/.env` for the bot token and confirm pairing succeeded. |
| `openclaw doctor` warns | Adjust `openclaw/openclaw.json` so every agent slot has `exec.ask: true` and `skills.hub.autoInstall` remains `false`. |
