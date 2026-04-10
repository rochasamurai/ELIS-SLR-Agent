# AUTOMATION_PLAN_DEPLOYMENT_RUNBOOK.md
# Deploying the 2-Agent Automation Plan to elis-server

> Use this runbook to install the completed ELIS 2-Agent Automation Plan onto
> `elis-server` after the plan reaches the `plan complete` state in `CURRENT_PE.md`.
>
> This runbook covers everything that runs on the server: the PM Agent workspace,
> Python scripts, loop-control config, and GitHub CLI wiring. The GitHub Actions
> workflows are already live — they do not require server deployment.
>
> **Audience:** operator (PO or delegated engineer) with SSH access to `elis-server`.
> **Runtime:** native `systemd --user` on `elis-server`. Not Docker.

---

## 1. What Was Delivered and Where It Runs

### 1.1 Runs on GitHub Actions (already active — no server work needed)

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci.yml` | push / PR | lint, type-check, pytest |
| `ci-current-pe.yml` | push to main | validate `CURRENT_PE.md` |
| `auto-assign-validator.yml` | PR synchronize | Gate 1 — post validator assignment |
| `auto-merge-on-pass.yml` | PR review / status | Gate 2 — merge on PASS + green CI |
| `implementer-runner.yml` | workflow_dispatch | launch Implementer agent |
| `validator-runner.yml` | workflow_dispatch | launch Validator agent |
| `validator-dispatch.yml` | workflow_dispatch | dispatch Validator via bot token |
| `pe-sequencer.yml` | workflow_dispatch | advance sequencer after merge |
| `pm-arbiter.yml` | workflow_dispatch | PM arbitration on FAIL iteration |
| `pm-discord-command.yml` | workflow_dispatch | respond to `!pe *` Discord commands |
| `pm-observability-dashboard.yml` | cron (hourly) | post dashboard to `#pe-status` |
| `pm-plan-load.yml` | workflow_dispatch | `!plan load` — validate plan before sequencer |
| `bot-auth-verify.yml` | workflow_dispatch | verify bot token health |

### 1.2 Runs on elis-server (requires deployment)

| Component | Location on server | Source in repo |
|---|---|---|
| PM Agent workspace config | `~/openclaw/workspace-pm/` | `openclaw/workspaces/workspace-pm/` |
| PM Agent docs entrypoints | `~/openclaw/workspace-pm/docs/` | symlinks → `/opt/elis/repo/...` |
| OpenClaw runtime config | `~/.openclaw/openclaw.json` | `openclaw/openclaw.json` |
| Python scripts | `/opt/elis/repo/scripts/` | `scripts/` (pulled via git) |
| Plan schema | `/opt/elis/repo/schemas/` | `schemas/plan_schema.json` |
| Loop-control file | `/opt/elis/repo/config/` | `config/pm_loop_control.json` |
| Plan file | `/opt/elis/repo/ELIS_2Agent_Automation_Plan_v2_0.md` | repo root |
| CURRENT_PE.md | `/opt/elis/repo/CURRENT_PE.md` | repo root |

### 1.3 New capabilities requiring PM Agent awareness (added by PRs #315–#318)

| Capability | AGENTS.md section | Backing component |
|---|---|---|
| Discord loop commands (`!pe status`, `!pe veto`, etc.) | §5.4 | `pm-discord-command.yml` + `scripts/pm_discord_command.py` |
| Plan load command (`!plan load`) | §5.5 | `pm-plan-load.yml` + `scripts/plan_loader.py` |
| Observability dashboard | §5.6 | `pm-observability-dashboard.yml` + `scripts/generate_pe_status_report.py` |
| Parallel track scheduling | n/a (sequencer-internal) | `scripts/check_parallel_eligibility.py` + `scripts/pe_sequencer.py` |

The PM Agent workspace (`openclaw/workspaces/workspace-pm/AGENTS.md`) already includes
§5.4–§5.6. Deploying pulls these rules into the live PM session.

---

## 2. Prerequisites

Verify these before starting:

```bash
# On elis-server
ssh elis-server

# Repo clone exists and is on the correct remote
git -C /opt/elis/repo remote get-url origin
# Expected: https://github.com/rochasamurai/ELIS-SLR-Agent.git

# Service exists
systemctl --user status openclaw-gateway --no-pager
# Expected: any state — active, inactive, or failed — but the unit must exist

# Python 3 and pip available
python3 --version
pip3 --version

# GitHub CLI authenticated and repo accessible
gh auth status
gh repo view rochasamurai/ELIS-SLR-Agent --json name
```

**Stop and resolve before continuing if any of these fail.**

---

## 3. Pre-Deployment Baseline Snapshot

Capture the current server state for rollback reference.

```bash
cd /opt/elis/repo

# Record deployed commit before pull
git rev-parse HEAD > /tmp/elis_pre_deploy_sha.txt
cat /tmp/elis_pre_deploy_sha.txt

# Record current service state
systemctl --user status openclaw-gateway --no-pager

# Record runtime health
openclaw doctor
openclaw channels status --probe

# Record entrypoint state
ls -la ~/openclaw/workspace-pm/
ls -la ~/openclaw/workspace-pm/docs/

# Record Python package state (compare after deploy if regressions occur)
pip3 list --format=freeze > /tmp/elis_pre_deploy_pip.txt
```

Save the output — you need the pre-deploy SHA for rollback (Step 9).

---

## 4. Pull Latest main

```bash
cd /opt/elis/repo
git fetch --all --prune
git status -sb
```

If the working tree is clean:

```bash
git pull
git rev-parse HEAD
```

If there are local modifications on the server (unexpected):

```bash
# Inspect before discarding anything
git diff
git status -sb
```

> **Do not force-reset the server repo without inspecting uncommitted state.**
> If unexpected modifications exist, escalate to PO before proceeding.

Verify the pull landed at the correct commit:

```bash
git log -3 --oneline --decorate
```

Expected tip: `chore(pm): PM-CHORE-30 — close PE-AUTO-11, plan complete`

---

## 5. Install / Update Python Dependencies

The automation scripts added in PRs #309–#318 require no new third-party packages beyond
what was already present. Verify by running the test suite before touching the live service:

```bash
cd /opt/elis/repo
python3 -m pytest scripts/ tests/ -q --tb=short 2>&1 | tail -5
```

Expected: all tests pass, 0 failures.

If new packages are required and missing, install via:

```bash
pip3 install -r requirements.txt
```

> **Never install packages as root.** Use the user-level pip (`pip3 install --user ...`)
> if a system-level venv is not in use.

---

## 6. Deploy Workspaces and Config

This step updates the PM Agent workspace files and OpenClaw runtime config.

```bash
cd /opt/elis/repo
bash scripts/deploy_openclaw_workspaces.sh
```

The script:

1. Rsyncs `openclaw/workspaces/` → `~/openclaw/`
2. Recreates PM workspace entrypoints:
   - `~/openclaw/workspace-pm/CURRENT_PE.md` → symlink to `/opt/elis/repo/CURRENT_PE.md`
   - `~/openclaw/workspace-pm/docs/AGENTS.md` → symlink to `/opt/elis/repo/AGENTS.md`
   - `~/openclaw/workspace-pm/docs/PLAN_CURRENT.md` → symlink to active plan file
3. Merges `openclaw/openclaw.json` into `~/.openclaw/openclaw.json` — preserving
   `channels`, `meta`, and `gateway` runtime keys (secrets are never overwritten)

Verify entrypoints after deploy:

```bash
ls -la ~/openclaw/workspace-pm/
ls -la ~/openclaw/workspace-pm/docs/
```

Expected: `CURRENT_PE.md`, `AGENTS.md`, and `PLAN_CURRENT.md` present as symlinks pointing
into `/opt/elis/repo/`.

Verify the plan entrypoint resolves to the correct file:

```bash
readlink ~/openclaw/workspace-pm/docs/PLAN_CURRENT.md
# Expected: /opt/elis/repo/ELIS_2Agent_Automation_Plan_v2_0.md

cat ~/openclaw/workspace-pm/CURRENT_PE.md | grep "Plan file"
# Expected: ELIS_2Agent_Automation_Plan_v2_0.md
```

---

## 7. Restart the Native Service

```bash
systemctl --user restart openclaw-gateway
systemctl --user status openclaw-gateway --no-pager
```

Wait 10–15 seconds for the gateway to fully bind.

```bash
journalctl --user -u openclaw-gateway -n 30 --no-pager
```

Look for the gateway ready line (no crash, no bind errors).

---

## 8. Runtime Health Checks

Run all checks before Discord validation.

```bash
openclaw doctor
openclaw channels status --probe
openclaw approvals get --gateway
```

| Check | Expected |
|---|---|
| `openclaw doctor` | Discord `ok`, Telegram `ok` (if bound) |
| `channels status --probe` | Discord `works` |
| `approvals get --gateway` | gateway listed, no error |

If any check fails, see [Section 11 — Troubleshooting](#11-troubleshooting) before proceeding.

---

## 9. PM Session Reset

The PM Agent workspace `AGENTS.md` changed in PRs #315–#317 (added §5.4–§5.6 for Discord
loop, plan load, and observability dashboard commands). A session reset is mandatory.

**Do not skip this step.** The PM Agent's loaded prompt is not the deployed prompt until a
fresh session starts.

1. Confirm deploy and restart completed (Steps 6–7 above).
2. PO sends `/reset` in the Discord PM Agent DM (preferred) or starts a new DM thread.
3. Wait for the PM Agent to acknowledge the fresh session start.
4. Do not use any evidence from the old session as proof the new rules are active.

For the full reset procedure, see: `docs/openclaw/PM_SESSION_RESET.md`

---

## 10. Post-Deployment Validation

Run all five E2E scenarios from `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md` first,
then run the three automation-specific scenarios below.

### 10.1 Baseline E2E Scenarios (from PM_E2E_VALIDATION_RUNBOOK.md)

| Scenario | PO message | Pass criteria |
|---|---|---|
| 1 — Identity | `/reset` then `Who are you?` | identifies as ELIS PM Agent; names PO authority |
| 2 — PE state | `What are the current PEs?` | reads `CURRENT_PE.md`; reports plan complete; no approval prompt |
| 3 — Worktrees | `What are the current worktrees?` | runs `git worktree list`; reports from host evidence only |
| 4 — Full registry | `Show the full Active PE Registry.` | compact bullet chunks; ≤25 entries/message; no raw table |
| 5 — Assignment | `Who should be Implementer for the next infra PE?` | applies alternation rule from `CURRENT_PE.md` |

Scenario 2 pass criterion for this deployment: PM reports **plan complete** (no active PE)
and does not attempt to open a new PE without PO instruction.

### 10.2 Automation-Specific Scenarios (new with this deployment)

#### Scenario 6 — `!pe status` routes through dashboard generator

PO sends:

```text
!pe status
```

Pass criteria:

- PM dispatches `pm-discord-command.yml` via `gh workflow run`
- Response content matches the format produced by `scripts/generate_pe_status_report.py`
  (series title, per-PE status lines, autonomy rate, auth summary)
- PM does not call `pm_status_reporter.py` directly (old path, removed in PE-AUTO-10)

Host cross-check — confirm the workflow ran:

```bash
gh run list --workflow=pm-discord-command.yml --limit 3
```

#### Scenario 7 — `!plan load` triggers validation workflow

PO sends `!plan load` with a valid plan attachment.

Pass criteria:

- PM dispatches `pm-plan-load.yml` via `gh workflow run`
- On validation success: PM posts Discord confirmation in the format `plan load VALID: N PEs validated`
- On validation failure: PM posts the `INVALID:` diagnosis without starting the sequencer

Host cross-check — confirm the workflow ran:

```bash
gh run list --workflow=pm-plan-load.yml --limit 3
```

#### Scenario 8 — Observability dashboard posts to `#pe-status`

Confirm the hourly cron last ran or trigger manually:

```bash
gh workflow run pm-observability-dashboard.yml
sleep 30
gh run list --workflow=pm-observability-dashboard.yml --limit 3
```

Pass criteria:

- workflow run status: `success`
- Discord channel `#pe-status` shows a post with series title and PE status table

### 10.3 Evidence Packet

Capture all of the following:

```bash
cd /opt/elis/repo

git rev-parse HEAD
systemctl --user status openclaw-gateway --no-pager
openclaw doctor
openclaw channels status --probe
openclaw approvals get --gateway
ls -la ~/openclaw/workspace-pm/
ls -la ~/openclaw/workspace-pm/docs/
readlink ~/openclaw/workspace-pm/docs/PLAN_CURRENT.md
git worktree list
python3 -m pytest tests/ -q --tb=short 2>&1 | tail -5
```

Plus:

- Discord transcript or screenshots for Scenarios 1–8
- explicit PASS / FAIL note for each scenario
- confirmation that PM session reset was completed before Scenario 1

---

## 11. Troubleshooting

| Symptom | Likely cause | Remedy |
|---|---|---|
| PM still answers with old commands or missing §5.4–§5.6 | session not reset after deploy | send `/reset` in Discord; do not trust evidence from old session |
| `PLAN_CURRENT.md` symlink missing or broken | `deploy_openclaw_workspaces.sh` failed; plan file not found at expected path | re-run deploy script; verify `Plan file` value in `CURRENT_PE.md` matches a file at repo root |
| `channels status --probe` fails | Discord token not set or gateway not bound | check `openclaw approvals get --gateway`; verify `PM_DISCORD_TOKEN` is set; restart service |
| PM asks for approval to `cat CURRENT_PE.md` | exec allowlist drift | verify `openclaw/workspaces/workspace-pm/AGENTS.md` §6 allowlist deployed; re-run deploy; reset session |
| `pm-discord-command.yml` not dispatched by PM | `gh` CLI unauthenticated or wrong repo | `gh auth status`; confirm PM bot token has `workflow` scope |
| `!pe status` returns old-format response | old script path cached | verify `pm-discord-command.yml` line 76 calls `generate_pe_status_report.py` (not `pm_status_reporter.py`) |
| pytest failures after pull | dependency change or import error in new scripts | run `pip3 install -r requirements.txt`; inspect failing test for missing module |
| Gateway fails to start after restart | port conflict or config parse error | `journalctl --user -u openclaw-gateway -n 50`; look for bind or JSON parse error |

---

## 12. Rollback Procedure

Use this only if post-deployment validation fails and a hotfix is not immediately available.

```bash
cd /opt/elis/repo

# Confirm pre-deploy SHA
cat /tmp/elis_pre_deploy_sha.txt

# Hard-reset to pre-deploy state
git fetch --all
git checkout <pre-deploy-sha>

# Redeploy workspaces at that commit
bash scripts/deploy_openclaw_workspaces.sh

# Restart service
systemctl --user restart openclaw-gateway
systemctl --user status openclaw-gateway --no-pager

# Re-run health checks
openclaw doctor
openclaw channels status --probe

# Reset PM session
# PO sends /reset in Discord

# Confirm old behavior is restored before logging the rollback
```

After rollback, open a GitHub issue or PM-CHORE noting:

- the pre-deploy SHA restored
- which scenario failed
- what was observed vs expected

Do not re-attempt deployment until the root cause is identified and a fix is merged to `main`.

---

## 13. Summary Checklist

| # | Step | Done |
|---|---|---|
| 1 | Verify prerequisites (git remote, systemd unit, Python, gh auth) | ☐ |
| 2 | Capture pre-deployment baseline snapshot (SHA, service state, health) | ☐ |
| 3 | `git pull` — verify tip commit is PM-CHORE-30 | ☐ |
| 4 | Run pytest — all tests pass | ☐ |
| 5 | `bash scripts/deploy_openclaw_workspaces.sh` — entrypoints verified | ☐ |
| 6 | `systemctl --user restart openclaw-gateway` — service active | ☐ |
| 7 | `openclaw doctor` + `channels status --probe` — both healthy | ☐ |
| 8 | PM session reset — PO sends `/reset` in Discord | ☐ |
| 9 | Baseline E2E scenarios 1–5 — all PASS | ☐ |
| 10 | Automation scenarios 6–8 — `!pe status`, `!plan load`, dashboard — all PASS | ☐ |
| 11 | Evidence packet captured | ☐ |

---

*ELIS SLR Agent · AUTOMATION_PLAN_DEPLOYMENT_RUNBOOK.md · Claude Code · 2026-04-10*
