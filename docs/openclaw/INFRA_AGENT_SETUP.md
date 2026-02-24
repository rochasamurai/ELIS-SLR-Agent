# Infra Agent Setup — PE-OC-19 Runbook

> **Prerequisite:** PE-OC-18 merged (OpenClaw running, CODEX/Claude tier policy live, keys stored in `~/.openclaw/.env`).

## Overview

PE-OC-19 registers the missing `infra-*` agents and ensures the container mounts the `workspace-infra-val`, `workspace-slr-impl`, and `workspace-slr-val` volumes that those agents need at runtime. This runbook captures the steps to add the agent entries, verify the workspace layout, and rerun the relevant checks.

---

## Step 1 — Confirm API Key storage

Make sure both secret keys live in your host `~/.openclaw/.env`. From PowerShell:

```powershell
Add-Content -Path "$env:USERPROFILE\.openclaw\.env" -Value 'OPENAI_API_KEY=<your-openai-key>'
Add-Content -Path "$env:USERPROFILE\.openclaw\.env" -Value 'ANTHROPIC_API_KEY=<your-anthropic-key>'
```

Inside the container, verify both entries exist (the CLI will not commit this file):

```bash
docker exec openclaw sh -c 'echo "OPENAI: ${OPENAI_API_KEY:0:8}... ANTHROPIC: ${ANTHROPIC_API_KEY:0:8}..."'
```

---

## Step 2 — Add the missing workspaces

PE-OC-04 already mounted `workspace-infra-impl`. Now add the remaining volumes to `docker-compose.yml` so OpenClaw can load the infra and SLR workspaces:

```
- ${HOME}/openclaw/workspace-infra-val:/app/workspaces/workspace-infra-val:ro
- ${HOME}/openclaw/workspace-slr-impl:/app/workspaces/workspace-slr-impl:ro
- ${HOME}/openclaw/workspace-slr-val:/app/workspaces/workspace-slr-val:ro
```

Restart the stack so Docker picks up the new mounts:

```bash
docker compose down
docker compose up -d
docker compose ps
```

Do not mount the ELIS repo itself into the container—PE governance forbids that.

---

## Step 3 — Register the infra agents

Run the CLI to append the four `infra-*` entries:

```bash
docker exec openclaw node /app/openclaw.mjs agents add infra-impl-codex
docker exec openclaw node /app/openclaw.mjs agents add infra-impl-claude
docker exec openclaw node /app/openclaw.mjs agents add infra-val-codex
docker exec openclaw node /app/openclaw.mjs agents add infra-val-claude
```

Each command will prompt to confirm the workspace and configure the provider (OpenAI for `*-codex`, Anthropic for `*-claude`). Answer **Yes** to update the existing agent and skip channel reconfiguration.

Confirm OpenClaw lists them:

```bash
docker exec openclaw node /app/openclaw.mjs agents list
```

Expect each agent to report the correct workspace and model (OpenAI agents on `workspace-infra-*`, Claude agents on the same workspace with `modelFallback` pointing at Opus).

---

## Step 4 — Restart the PM agent if needed

Since `pm` now orchestrates all PE-OC agents, restart it to ensure routes pick up the new infra entries:

```bash
docker exec openclaw node /app/openclaw.mjs agents add pm
```

Leave the workspace default, configure auth for whichever provider the PM runs at the moment, and decline channel reconfiguration.

---

## Step 5 — Validation checklist

1. `python scripts/check_openclaw_doctor.py` → must exit 0.  
2. `python -m black --check .`, `python -m ruff check .`, `python -m pytest -q` → all pass, 547 tests referenced in the PE status packet.  
3. `docker exec openclaw node /app/openclaw.mjs agents list` → shows new `infra-*` entries plus the existing SLR/Prog agents.  
4. Send `status` via Telegram to confirm the PM Agent (now `openai/gpt-5.1-codex`) still replies after the infrastructure update.  
5. Document the new infrastructure agents and workspace mounts in `HANDOFF.md` and `docs/openclaw/INFRA_AGENT_SETUP.md`.

---

## Troubleshooting

| Symptom | Action |
|---|---|
| infra agent doesn’t appear | rerun `docker exec openclaw node /app/openclaw.mjs agents add <infra-id>` with the same workspace; confirm `openclaw/openclaw.json` has the entry |
| Workspace mounts missing | check `docker compose config` and ensure the volumes block lists `workspace-infra-val`, `workspace-slr-impl`, and `workspace-slr-val`; restart the stack |
| `check_openclaw_doctor.py` fails | ensure `exec.ask: true` on all agents and `skills.hub.autoInstall` remains `false` |
| Keys missing | cat `/home/node/.openclaw/.env` inside the container (never commit) |

