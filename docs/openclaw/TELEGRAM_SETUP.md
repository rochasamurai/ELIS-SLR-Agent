# Telegram Setup — PO Onboarding Guide

> **Prerequisite:** PE-OC-01 complete (OpenClaw Docker container running).

## Overview

The PM Agent is the only agent accessible via Telegram. The PO sends natural-language
directives to the PM Agent and receives status updates, escalations, and gate notifications.
All 10 worker agents are internal — they are never reachable from Telegram.

---

## Step 1 — Create a Telegram Bot

1. Open Telegram and start a conversation with `@BotFather`.
2. Send `/newbot` and follow the prompts to choose a name and username.
3. Copy the bot token (format: `123456789:AAFxxxx...`).

## Step 2 — Store the Bot Token

On the host machine (not in the ELIS repo):

```bash
mkdir -p ~/.openclaw
chmod 700 ~/.openclaw
# Add the token to the OpenClaw gateway config — do NOT commit this file
echo 'TELEGRAM_BOT_TOKEN=<your-token-here>' >> ~/.openclaw/.env
```

## Step 3 — Deploy Workspace Files to Host

```bash
bash scripts/deploy_openclaw_workspaces.sh
```

This syncs `openclaw/workspaces/` (repo) → `~/openclaw/` (host).

## Step 4 — Start the OpenClaw Container

```bash
docker compose up -d
```

Verify the container is running:

```bash
docker compose ps
python scripts/check_openclaw_health.py
```

## Step 5 — Pair the PO Telegram Account

Inside the container:

```bash
docker exec -it openclaw openclaw pairing approve
```

The bot will send a pairing code to the Telegram bot. Send the code to the bot from
your Telegram account to complete pairing.

After pairing, `accountId` in `openclaw.json` should be updated from `"po-channel"` to
the actual Telegram user ID returned by the pairing step. Commit that change via a PE.

## Step 6 — Verify PM Agent Responds

Send a test message to the bot:

```
status
```

Expected response:

```
Active PEs — [date UTC]:

No active PEs. Registry is empty.
```

If the PM Agent does not respond within 30 seconds, check container logs:

```bash
docker compose logs openclaw --tail=50
```

---

## Security Notes

- The Telegram bot token must never be committed to the ELIS repo.
- Store it only in `~/.openclaw/.env` (host, `chmod 700` directory).
- The bot must only accept messages from the paired PO account (`pm-review-required` policy).
- Run `openclaw doctor --check dm-policy` to verify DM policy enforcement.

---

## Troubleshooting

| Symptom | Check |
|---|---|
| Bot does not respond | Container running? `docker compose ps` |
| "Unauthorized" error | Bot token correct in `~/.openclaw/.env`? |
| Wrong account can message bot | DM policy enforced? `openclaw doctor --check dm-policy` |
| PM Agent gives wrong status | `CURRENT_PE.md` accessible to PM Agent? Check workspace mount |
