# Native Operations and Restore Runbook

> Production runtime on `elis-server` is native `systemd --user`.
> Use this runbook for deploy, restart, health checks, approvals inspection,
> PM recovery, and restore after host/runtime drift.

---

## Runtime Contract

Canonical paths on `elis-server`:

- repo: `/opt/elis/repo`
- OpenClaw state: `~/.openclaw`
- workspace root: `~/openclaw`
- PM workspace: `~/openclaw/workspace-pm`
- SLR project root: `/opt/elis/projects`
- service: `~/.config/systemd/user/openclaw-gateway.service`

The PM Agent must read governance through workspace entrypoints:

- `~/openclaw/workspace-pm/CURRENT_PE.md`
- `~/openclaw/workspace-pm/docs/AGENTS.md`
- `~/openclaw/workspace-pm/docs/PLAN_CURRENT.md`

---

## Standard Deploy

Run from `/opt/elis/repo` on `elis-server`:

```bash
git pull
bash scripts/deploy_openclaw_workspaces.sh
systemctl --user restart openclaw-gateway
systemctl --user status openclaw-gateway
```

Then verify:

```bash
openclaw doctor
openclaw channels status --probe
openclaw approvals get --gateway
ls -l ~/openclaw/workspace-pm
ls -l ~/openclaw/workspace-pm/docs
```

---

## Day-to-Day Operations

Health and logs:

```bash
systemctl --user status openclaw-gateway
journalctl --user -u openclaw-gateway -n 100
openclaw doctor
openclaw channels status --probe
```

Approvals and config:

```bash
openclaw approvals get --gateway
openclaw config get agents.list
```

PM-specific validation:

```bash
cat ~/openclaw/workspace-pm/CURRENT_PE.md
git -C /opt/elis/repo worktree list
```

---

## PM Recovery

Use this section when the PM Agent behaves incorrectly in Discord.

1. Re-deploy the repo-defined workspace and config:

```bash
bash scripts/deploy_openclaw_workspaces.sh
systemctl --user restart openclaw-gateway
```

2. Verify runtime health:

```bash
openclaw doctor
openclaw channels status --probe
openclaw approvals get --gateway
```

3. Reset the PM session if prompts or exec rules changed:

- follow `docs/openclaw/PM_SESSION_RESET.md`

4. Re-run the E2E checks:

- follow `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md`

---

## Restore Procedure

Use this when host state has drifted, workspace entrypoints are broken, or the
PM Agent is no longer reading canonical governance correctly.

### Step 1 - Confirm repo truth

```bash
cd /opt/elis/repo
git status -sb
git rev-parse HEAD
cat CURRENT_PE.md
```

### Step 2 - Restore repo-defined workspaces and config

```bash
bash scripts/deploy_openclaw_workspaces.sh
```

This restores:

- workspaces under `~/openclaw/`
- PM entrypoints to canonical repo files
- `~/.openclaw/openclaw.json` while preserving runtime `channels` and `meta`

### Step 3 - Restart native service

```bash
systemctl --user restart openclaw-gateway
systemctl --user status openclaw-gateway
journalctl --user -u openclaw-gateway -n 100
```

### Step 4 - Re-check host evidence

```bash
openclaw doctor
openclaw channels status --probe
openclaw approvals get --gateway
ls -l ~/openclaw/workspace-pm
ls -l ~/openclaw/workspace-pm/docs
git -C /opt/elis/repo worktree list
```

### Step 5 - Reset PM session

If prompt files or exec policy were part of the restore:

- follow `docs/openclaw/PM_SESSION_RESET.md`

### Step 6 - Re-validate PM behavior

- follow `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md`

Pass condition:

- PM answers identity, PE-state, worktree, and registry questions correctly from a fresh session

---

## Restore Notes

- do not instruct the PM Agent to read `/opt/elis/repo/...` directly during Discord validation
- do not enable elevated exec for read-only PM operations
- use `channels status --probe` as the connectivity check, not plain `channels status`
- any command not on the PM allowlist is expected to route to operator approval

---

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| PM asks for approval to read `CURRENT_PE.md` | PM exec policy drift or broken entrypoint | verify allowlist, confirm `elevated.enabled=false`, redeploy, reset session |
| PM reports branches as worktrees | prompt drift or stale session | reset PM session and re-run E2E validation |
| PM dumps malformed full registry table | old prompt stack or stale session | redeploy, reset, revalidate chunked reporting |
| Discord appears disconnected but probe works | stale non-probe status path | trust `channels status --probe` and `doctor`; capture note in evidence |

---

*Native Operations and Restore Runbook · 2026-03-25*
