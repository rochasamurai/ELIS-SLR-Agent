# Telegram Bot Troubleshooting Log

This document records the live diagnostic steps taken when the ELIS PM Agent Telegram bot would not respond despite the gateway running.

## 1. Ensure secrets sync
- Verified `~/.openclaw/.env` contains `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENCLAW_GATEWAY_TOKEN`, and the current `TELEGRAM_BOT_TOKEN`.  
- Confirmed Compose’s `env_file` references `${HOME}/.openclaw/.env`, and restarted the stack after each change so the container re-read the tokens.  
- Re-ran `docker exec openclaw printenv | grep TELEGRAM_BOT_TOKEN` to confirm the container saw the updated value.
### Commands used
- `Get-Content "$env:USERPROFILE\.openclaw\.env" | Where-Object { $_ -like 'TELEGRAM_BOT_TOKEN=*' }` → confirmed the host file held the new token.
- `docker exec openclaw /bin/sh -c "printenv | grep TELEGRAM_BOT_TOKEN"` → ensured the container environment reflected the new value after each restart.
### Mistakes to avoid
- Restarting Compose before the host token matched the intended value meant the old token persisted; always edit `.env` then restart.

## 2. Confirm environment readiness
- `docker exec openclaw /bin/sh -c "curl -I https://api.telegram.org"` returned `HTTP/2 302`, proving the container can reach Telegram’s API.  
- Gateway logs (`docker logs openclaw`) consistently show the bridge starting (`canvas`, `heartbeat`, `gateway listening on ws://0.0.0.0:18789`).

## 3. Observe pairing attempts
- PO account sent `/pair` and `/status` repeatedly, but `docker logs openclaw --tail 40 --follow` never recorded any Telegram updates, and `node /app/openclaw.mjs pairing list --channel telegram` reported “No pending requests.”
- `curl https://api.telegram.org/bot<TOKEN>/getUpdates` returned valid JSON showing the `/pair` messages, so Telegram accepted the token.
 - The `/pair` sequence has now been run **ten consecutive times** (see chat timestamps) without a single reply or pairing code, yet Telegram still marks the messages as delivered.
### Commands used
| Command | Response |
|---|---|
| `docker exec openclaw node /app/openclaw.mjs pairing list --channel telegram` | `No pending telegram pairing requests.` |
| `curl "https://api.telegram.org/bot<TOKEN>/getUpdates"` | `{"ok":true,"result":[...,"text":"/pair",...]}` |
| `docker logs openclaw --tail 40 --follow` + `/pair` | Only startup logs—no Telegram updates. |
### Mistakes / wrong answers
- Running `node /app/openclaw.mjs pairing approve telegram <code>` before any code existed produced “missing required argument `codeOrChannel`” or “no pending pairing request,” because the bot never issued a code without a webhook event.
- Forgetting to restart Compose after editing `.env` meant the container kept the old token and ignored the new `pair` attempt.

## 4. Diagnose webhook delivery
- Since Telegram shows the updates yet OpenClaw logs nothing, the webhook never reaches the gateway.  
- Next actions under consideration: examine `getWebhookInfo`, expose the gateway via an nginx/ngrok tunnel, or temporarily run the gateway in polling mode so OpenClaw actively fetches updates instead of relying on webhook callbacks.
### Commands in this phase
- `curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"` (planned) to check webhook registration status.
- `docker exec openclaw node /app/openclaw.mjs channels status --probe` (future) to inspect the Telegram channel’s state inside OpenClaw.
- `node /app/openclaw.mjs gateway --poll-telegram --bind lan` (optional) to run the gateway in polling mode while the webhook issues are resolved.
### Mistakes to avoid
- Assuming the webhook works because the bot token is valid; the empty logs prove webhook delivery can still fail even with a good token.

## 5. Alternative troubleshooting approach
1. Keep the gateway in polling mode but temporarily raise logging level (`OPENCLAW_GATEWAY_LOG_LEVEL=debug`) so we can watch the `getUpdates` requests and confirm the container is actually polling Telegram.  
2. If that still shows no `/pair` call, disable webhook/polling filters altogether by setting `OPENCLAW_TELEGRAM_MODE=polling` and running `node /app/openclaw.mjs gateway --allow-unconfigured --bind lan --poll` (or the equivalent CLI flag) directly in the container, capturing the log output.  
3. If Telegram updates still never reach OpenClaw, switch to a public webhook tunnel (e.g. `ngrok http 18789`) and register that URL with BotFather so webhook delivery can be observed; once a pairing code arrives, approving it should resume normal operation.

## 6. Status Packet references
- Capture the successful commands/outputs so future reviews trace the exact steps:
  - `docker exec openclaw /bin/sh -c "printenv | grep TELEGRAM_BOT_TOKEN"`  
  - `curl https://api.telegram.org/bot<TOKEN>/getUpdates` showing the PO `/pair` messages  
  - `node /app/openclaw.mjs pairing approve telegram <code>` output once it succeeds  
  - Telegram chat showing the `status` reply  

Documenting these steps ensures a durable log of the live-agent investigation for PE-OC-17.
