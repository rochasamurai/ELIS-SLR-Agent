# CODEX Agent Setup — PE-OC-18 Runbook

> **Prerequisite:** PE-OC-17 complete (OpenClaw running, Telegram paired).

## Model Tier Policy

| Role | Model | Fallback |
|---|---|---|
| PM Agent (orchestration) | `openai/gpt-5.1-codex` | — |
| CODEX agents (`*-impl-codex`, `*-val-codex`) | `openai/gpt-5.1-codex` | — |
| Claude coding agents (`*-impl-claude`, `*-val-claude`) | `anthropic/claude-sonnet-4-6` | `anthropic/claude-opus-4-6` |

**Rationale:** `openai/gpt-5.1-codex` drives all CODEX roles and PM orchestration.
`anthropic/claude-sonnet-4-6` is the primary for Claude coding/validation; Opus is its fallback only.

---

## Step 1 — Store API Keys on Host

Both keys must be present in `~/.openclaw/.env` before starting the container:

```bash
# On Windows (PowerShell) — append to existing file
Add-Content -Path "$env:USERPROFILE\.openclaw\.env" -Value 'OPENAI_API_KEY=<your-openai-key>'
Add-Content -Path "$env:USERPROFILE\.openclaw\.env" -Value 'ANTHROPIC_API_KEY=<your-anthropic-key>'
```

Verify both keys are present:

```bash
docker exec openclaw sh -c 'grep -E "OPENAI_API_KEY|ANTHROPIC_API_KEY" /home/node/.openclaw/.env | cut -d= -f1'
# Expected output:
# OPENAI_API_KEY
# ANTHROPIC_API_KEY
```

> /!\ Never commit `.env`. Keys live on the host only.

---

## Step 2 — Restart Container to Apply Env Changes

```bash
docker compose down
docker compose up -d
docker compose ps
```

Verify both keys are visible inside the container:

```bash
docker exec openclaw sh -c 'echo "OPENAI: ${OPENAI_API_KEY:0:8}... ANTHROPIC: ${ANTHROPIC_API_KEY:0:8}..."'
```

---

## Step 3 — Verify Agent Registration

```bash
docker exec openclaw node /app/openclaw.mjs agents list
```

Expected output includes all registered agents:

```
* main (default)
  Model: openai/gpt-5.1-codex
* pm
  Workspace: workspace-pm
  Model: openai/gpt-5.1-codex
* prog-impl-codex
  Workspace: workspace-prog-impl
  Model: openai/gpt-5.1-codex
* prog-impl-claude
  Workspace: workspace-prog-impl
  Model: anthropic/claude-sonnet-4-6
* prog-val-codex
  Workspace: workspace-prog-val
  Model: openai/gpt-5.1-codex
* prog-val-claude
  Workspace: workspace-prog-val
  Model: anthropic/claude-sonnet-4-6
```

---

## Step 4 — Run Doctor Check

```bash
python scripts/check_openclaw_doctor.py
```

Expected: `OK: openclaw doctor configuration meets expected policies` (exit 0).

---

## Step 5 — Verify PM Agent Still Responds via Telegram

Send `status` from the PO Telegram account. The PM Agent (now running on `openai/gpt-5.1-codex`) should respond with the Active PE Registry summary.

If no response within 30 seconds:

```bash
docker compose logs openclaw --tail=50
```

---

## Troubleshooting

| Symptom | Action |
|---|---|
| Agent list missing `prog-*` entries | Confirm `openclaw/openclaw.json` was synced: `bash scripts/deploy_openclaw_workspaces.sh` |
| PM Agent no longer responds after model change | Check `OPENAI_API_KEY` is valid: `docker exec openclaw sh -c 'echo $OPENAI_API_KEY \| cut -c1-8'` |
| Claude agent auth failure | Confirm `ANTHROPIC_API_KEY` in container env: `docker exec openclaw sh -c 'echo $ANTHROPIC_API_KEY \| cut -c1-8'` |
| `openclaw doctor` fails | Verify all agents have `exec.ask: true` and `skills.hub.autoInstall: false` in `openclaw.json` |
