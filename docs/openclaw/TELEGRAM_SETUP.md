# Telegram Channel Setup — Authoritative Runbook

> **Replaces** the PE-OC-17 version of this document, which contained incorrect
> procedures (wrong binding accountId concept, wrong pairing flow order, old schema
> references).  Updated 2026-02-26 after live resolution of the `token:none` issue.

---

## Prerequisites

- OpenClaw container running (`docker compose ps` → `Up`)
- `TELEGRAM_BOT_TOKEN` in `~/.openclaw/.env` (format: `<BOT_ID>:<HASH>`)
- `BOT_ID` = the numeric prefix before the first colon in the token
- `openclaw/openclaw.json` binding has `"accountId": "<BOT_ID>"` (not PO's user ID)

---

## One-time channel registration (run once per bot token)

Run in order. Step 1 only needs re-running when the token is rotated.

### Step 1 — Register bot token with explicit account ID

```bash
MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c \
  'node /app/openclaw.mjs channels add --channel telegram \
   --token "$(printenv TELEGRAM_BOT_TOKEN)" \
   --account <BOT_ID>'
```

Expected output: `Added Telegram account "<BOT_ID>".`

> **Why `--account <BOT_ID>` is required:** OpenClaw stores the token under the
> account ID you specify. The binding's `match.accountId` must equal this ID for the
> gateway to find the token. Omitting `--account` stores the token as `"default"`,
> which never matches a numeric accountId in the binding → `token:none`.

### Step 2 — Set gateway mode (one-time)

```bash
MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c \
  'node /app/openclaw.mjs config set gateway.mode local'
```

> Without `gateway.mode` set, the Telegram plugin never initializes even if the token
> is present. The `--allow-unconfigured` flag only allows the gateway process to start;
> it does not activate channel plugins.

### Step 3 — Complete doctor wizard metadata

```bash
MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c \
  'node /app/openclaw.mjs doctor --fix'
```

### Step 4 — Restart container

```bash
docker compose down && docker compose up -d
```

### Step 5 — Verify Telegram is running

```bash
MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c \
  'node /app/openclaw.mjs channels status'
```

Expected: `Telegram <BOT_ID>: enabled, configured, running, mode:polling, token:config`

If you see `token:none` or `not configured`, re-read `docs/openclaw/TELEGRAM_DEBUG.md §7`.

---

## PO pairing (run once per PO account; survives restarts)

The bot's `dmPolicy: "pairing"` means every unknown sender is denied until explicitly
paired. Pairing is stored in the state directory and persists across container restarts.

1. **PO sends any plain message** (e.g. "Hello") to the bot on Telegram.
   - Do NOT send `/pair` — that is an admin CLI command, not a bot message.
2. **Bot replies** with: `OpenClaw: access not configured. Pairing code: XXXXXXXX`
3. **Admin approves** the code:

```bash
MSYS_NO_PATHCONV=1 docker exec openclaw /bin/sh -c \
  'node /app/openclaw.mjs pairing approve telegram <CODE>'
```

Expected: `Approved telegram sender <PO_TELEGRAM_USER_ID>.`

4. **PO sends `/status`** — PM Agent replies with the Active PE Registry summary.

---

## Rotating the bot token

When the bot token is revoked and replaced:

1. Update `TELEGRAM_BOT_TOKEN` in `~/.openclaw/.env`
2. Re-run Step 1 above with the new token and same `--account <BOT_ID>`
3. Re-run Steps 3–5
4. PO pairing is preserved (no re-pairing needed unless the PO's user ID changed)

---

## `openclaw/openclaw.json` binding — correct accountId

The `bindings[].match.accountId` must equal the **bot's Telegram user ID** (the
numeric prefix of the token), not the PO's personal Telegram user ID.

```json
"bindings": [
  {
    "agentId": "pm",
    "match": {
      "channel": "telegram",
      "accountId": "<BOT_ID>"
    }
  }
]
```

The PO's Telegram user ID appears in pairing output (`Approved telegram sender <ID>`)
and in `Your Telegram user id: <ID>` from the bot's pairing message. It is stored in
the state dir's pairing record, not in `openclaw/openclaw.json`.

---

## Troubleshooting quick reference

| Symptom | Cause | Fix |
|---|---|---|
| `token:none` | `channels add` used without `--account <BOT_ID>` | Re-run Step 1 with correct `--account` |
| `not configured` | `gateway.mode` unset or token not loaded | Run Steps 2–4 |
| `stopped` after restart | Config not reloaded | Restart container (Step 4) |
| "You are not authorized" on any message | PO not paired | Run pairing flow above |
| "/pair" → "You are not authorized" | `/pair` is a CLI admin command, not a bot message | PO should send a plain message, not `/pair` |
| Token rotated → `token:none` | Old token registered; needs re-registration | Re-run Step 1 with new token |

---

## deploy_openclaw_workspaces.sh and channel credentials

The deploy script merges repo config into the state dir, **preserving** the `channels`
and `meta` keys. Running the deploy script will NOT destroy the registered bot token.
However, if the state dir config is wiped (e.g. fresh container with new state dir
mount), re-run Steps 1–5.
