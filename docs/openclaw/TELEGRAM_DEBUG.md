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
  - Verify token is SET (not its value): `MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c '[ -n "$(printenv TELEGRAM_BOT_TOKEN)" ] && echo set || echo unset'`
  - `curl https://api.telegram.org/bot<TOKEN>/getUpdates` showing the PO `/pair` messages
  - `node /app/openclaw.mjs pairing approve telegram <code>` output once it succeeds
  - Telegram chat showing the `status` reply

Documenting these steps ensures a durable log of the live-agent investigation for PE-OC-17.

---

## 7. Resolution (2026-02-26) — Five root causes identified and fixed

After extended live debugging across PE-OC-17 and post-merge ops, the bot reached
`enabled, configured, running, mode:polling, token:config`. The PO sent "Hello" and
received a pairing code; after `pairing approve`, `/status` replied successfully.

### Root cause 1 — `docker-compose.yml` environment block silenced `env_file`

`environment:` listed `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, and `ANTHROPIC_API_KEY`
using `${VAR}`. Docker Compose expands these from the **host shell**, not from
`env_file`. The host PowerShell session did not export those variables, so Compose
substituted empty strings — silently overriding the valid values from `env_file`.

**Fix:** Removed the three secret entries from `environment:`. `env_file` is now the
sole source for all secrets. `OPENCLAW_STATE_DIR` (a non-secret constant) remains.

### Root cause 2 — `deploy_openclaw_workspaces.sh` destroyed channel credentials

The script used a plain `cp` to overwrite `~/.openclaw/openclaw.json` with the repo
copy. The repo copy has no `channels` section, so every deployment erased the
`channels.telegram.accounts.<BOT_ID>.botToken` that `channels add` had written.

**Fix:** Replaced `cp` with a Python-based JSON merge that preserves the `channels`
and `meta` keys from the live state dir while updating all other keys from the repo.

### Root cause 3 — `gateway.mode` not set in config

OpenClaw requires `gateway.mode` in the config to initialize channel plugins. Without
it the gateway starts (`--allow-unconfigured`) but the Telegram plugin is never loaded.
`OPENCLAW_GATEWAY_MODE=polling` controls how Telegram fetches updates (polling vs
webhook) — it does **not** substitute for `gateway.mode`.

**Fix:** `openclaw config set gateway.mode local` + `doctor --fix`.

### Root cause 4 (primary) — `channels add` missing `--account <BOT_ID>`

`channels add --channel telegram --token <TOKEN>` without `--account` stores the token
under account name `"default"`. The gateway maps by the **accountId** from the binding.
Without `--account 8508429120` the gateway found no matching account → `token:none`.

**Fix:** `channels add --channel telegram --token <TOKEN> --account <BOT_ID>`
where `BOT_ID` = the numeric prefix of the bot token (digits before the first colon).

### Root cause 5 — binding `accountId` referenced PO's user ID instead of bot's ID

The binding had `"accountId": "8351383841"` (the PO's Telegram user ID). OpenClaw
bindings use `accountId` to identify the **channel account (the bot)**, not the sender.
The bot's Telegram ID is the token prefix (e.g. `8508429120`).

**Fix:** Updated `openclaw/openclaw.json` binding to `"accountId": "8508429120"`.

### Correct one-time channel setup sequence

```bash
# 1. Register the bot token with the correct account ID
#    BOT_ID = numeric prefix of the token (digits before the first colon)
MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c \
  'node /app/openclaw.mjs channels add --channel telegram \
   --token "$(printenv TELEGRAM_BOT_TOKEN)" \
   --account <BOT_ID>'

# 2. Set gateway mode (one-time if not already set)
MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c \
  'node /app/openclaw.mjs config set gateway.mode local'

# 3. Run doctor --fix to complete wizard metadata
MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c \
  'node /app/openclaw.mjs doctor --fix'

# 4. Restart container — Telegram starts polling automatically
docker compose down && docker compose up -d

# 5. Verify: expect "enabled, configured, running, mode:polling, token:config"
MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c \
  'node /app/openclaw.mjs channels status'

# 6. PO sends any plain message → bot replies with pairing code
# 7. Approve pairing
MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c \
  'node /app/openclaw.mjs pairing approve telegram <CODE>'
```

### `channels status` field reference

| Field | Healthy | Problem → fix |
|---|---|---|
| `token:` | `token:config` | `token:none` → missing `--account <BOT_ID>` in `channels add` |
| configured | `configured` | `not configured` → token not loaded or `gateway.mode` unset |
| running | `running` | `stopped` → restart container after fixing config |
| `mode:` | `mode:polling` | `mode:webhook` → webhook requires a public URL |

### Security note

Never run `printenv` or filter env output to check secrets — even grep on printenv
can expose values in logs. Use existence checks only:
`[ -n "$(printenv VAR)" ] && echo set || echo unset`

---

## 8. Secret rotation recovery (2026-02-26)

After OPENAI_API_KEY, ANTHROPIC_API_KEY, and TELEGRAM_BOT_TOKEN were rotated following
a security incident, the Telegram channel required re-registration with the new bot token.

### Symptom after rotation

```
Telegram 8508429120: enabled, configured, stopped, mode:polling, token:config,
error:Call to 'getMe' failed! (401: Unauthorized)
```

`token:config` confirmed the new token was loaded from `openclaw.json`. The `401` meant
Telegram was rejecting it — because the state dir's `channels` section still held the old
(now-revoked) token from the previous `channels add`.

### Root cause

Two issues combined:

1. **Stale channels section** — Rotating the token in `.env` and restarting the container
   reloads the environment but does NOT update the `channels.telegram.accounts.<BOT_ID>.botToken`
   field inside `~/.openclaw/openclaw.json`. `channels add` must be re-run explicitly.

2. **In-memory state not flushed** — After `channels add` rewrites the config file, the
   gateway process already running in memory still holds the old token. A second restart
   (`docker compose restart`) is required to flush it.

### Fix sequence (Windows PowerShell, secret-safe)

```powershell
# Step 1 — Re-register new token (reads from .env, never prints the value)
$t = (Select-String '^TELEGRAM_BOT_TOKEN=' "$env:USERPROFILE\.openclaw\.env").Line -replace '^TELEGRAM_BOT_TOKEN=',''
docker exec openclaw node openclaw.mjs channels add --channel telegram --token $t --account 8508429120

# Step 2 — Flush in-memory state
docker compose restart

# Step 3 — Verify (wait ~10 s)
docker exec openclaw node openclaw.mjs channels status
# Expected: enabled, configured, running, mode:polling, token:config
```

PO pairing survived the rotation — no re-pairing was needed.
