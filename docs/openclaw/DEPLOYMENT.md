# OpenClaw Deployment Runbook

> Use this runbook after any merge that changes OpenClaw workspace files or runtime config.
> Production runtime on `elis-server` is native `systemd --user`, not Docker.

---

## Step 1 — Deploy workspaces and config

Run from the repo root on `elis-server`:

```bash
bash scripts/deploy_openclaw_workspaces.sh
```

This deploys:

1. `openclaw/workspaces/` → `~/openclaw/`
2. `openclaw/openclaw.json` → `~/.openclaw/openclaw.json`
3. PM workspace entrypoints:
   - `~/openclaw/workspace-pm/CURRENT_PE.md`
   - `~/openclaw/workspace-pm/docs/AGENTS.md`
   - `~/openclaw/workspace-pm/docs/PLAN_CURRENT.md`

---

## Step 2 — Restart native service

```bash
systemctl --user restart openclaw-gateway
systemctl --user status openclaw-gateway
```

---

## Step 3 — Verify runtime health

```bash
openclaw doctor
openclaw channels status --probe
openclaw approvals get --gateway
ls -l ~/openclaw/workspace-pm
ls -l ~/openclaw/workspace-pm/docs
```

Expected:

- gateway service active
- `doctor` healthy
- channels probe healthy
- PM workspace entrypoints present

---

## Step 4 — Reset PM session if prompt files changed

If `SOUL.md`, `AGENTS.md`, `MEMORY.md`, or PM exec-policy rules changed, use:

- `docs/openclaw/PM_SESSION_RESET.md`

Do not treat validation evidence as current until a fresh PM session has started.

---

## Step 5 — Run PM E2E validation

After deploy/restart and any required PM session reset, validate the Discord behavior with:

- `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md`

This is the authoritative flow for:

- identity
- current PE state
- worktree reporting
- full-registry chunking
- assignment dry-run behavior

---

## Step 6 — Native operations and restore

For routine native operations, PM recovery, or host restore after drift, use:

- `docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md`

---

## Troubleshooting

| Symptom | Action |
|---|---|
| PM still answers with old behavior | deploy again, restart service, then reset PM session |
| `PLAN_CURRENT.md` missing | check `CURRENT_PE.md` and rerun deploy script |
| PM cannot read `CURRENT_PE.md` | verify workspace entrypoint symlink and allowlist |
| runtime health differs from repo docs | update repo docs and rerun validation before merge |

---

*OpenClaw Deployment Runbook · Native runtime · 2026-03-23*
