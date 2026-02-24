# OpenClaw Deployment Runbook

> **When to use this runbook:** after any merge that touches `openclaw/openclaw.json`
> or `docker-compose.yml`, run the deploy script to sync the live container.

---

## Why manual deployment is required

The OpenClaw container reads its config from `~/.openclaw/openclaw.json` (the state
directory on the host, mounted as `/app/.openclaw`).  The repository copy at
`openclaw/openclaw.json` is the source of truth, but it is **not** automatically
synced on merge.  CI checks (`check_openclaw_doctor.py`, `check_openclaw_security.py`)
validate the *repo* copy only.

Without running the deploy step, agent registrations committed to the repo remain
invisible to the live PM Agent.

---

## Step 1 — Deploy config and workspaces

Run from the repo root:

```bash
bash scripts/deploy_openclaw_workspaces.sh
```

This script:
1. Syncs `openclaw/workspaces/` → `~/openclaw/` (workspace AGENTS.md files)
2. Copies `openclaw/openclaw.json` → `~/.openclaw/openclaw.json`
3. Prints a restart reminder

---

## Step 2 — Restart the container

```bash
docker compose down
docker compose up -d
docker compose ps
```

The container must be restarted for the new config to take effect.

---

## Step 3 — Verify sync

Run the sync verifier on the host (Docker must be running):

```bash
python scripts/check_openclaw_config_sync.py
```

Expected output when in sync:

```
Declared agents (13): pm, slr-impl-codex, slr-impl-claude, ...
Live agents (13): pm, slr-impl-codex, slr-impl-claude, ...
OK: all declared agents are present in the live container.
```

If agents are missing, re-run Step 1 and Step 2.

---

## Step 4 — Confirm PM Agent responds

Send `status` from the PO Telegram account.  The PM Agent should reply with the
Active PE Registry summary.

If no response within 30 seconds:

```bash
docker compose logs openclaw --tail=50
```

---

## Troubleshooting

| Symptom | Action |
|---|---|
| `check_openclaw_config_sync.py` reports missing agents after deploy | Re-run `bash scripts/deploy_openclaw_workspaces.sh` and restart container |
| PM Agent reports only `main` after merge | Config not deployed — run the deploy script |
| `~/.openclaw/openclaw.json` not updated | Confirm deploy script ran from repo root; check file mtime |
| Container fails to start after config update | Check `openclaw.json` is valid JSON: `python -c "import json; json.load(open('openclaw/openclaw.json'))"` |

---

## CI behaviour

`check_openclaw_config_sync.py` runs in CI as the `openclaw-config-sync-check` job.
It always exits 0 in CI because the Docker daemon is not available in GitHub Actions
runners — this is intentional and non-blocking.  The script only gates on the host
where Docker is reachable.
