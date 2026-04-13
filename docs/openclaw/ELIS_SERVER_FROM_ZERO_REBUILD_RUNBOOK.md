# ELIS Server From-Zero Rebuild Runbook

> Purpose: rebuild `elis-server` to a clean ELIS baseline with GitHub as the source of truth, one canonical OpenClaw install, host-local secrets, and native `systemd --user` runtime management.
>
> Scope: `elis-server` host rebuild, OpenClaw runtime rebuild, ELIS repo redeploy, and baseline validation before executing `ELIS_MultiAgent_Implementation_Plan_v1_8.md`.

---

## 1. Rebuild Principles

This runbook standardises the long-term ELIS end state on `elis-server`.

GitHub is the source of truth for:

- architecture and implementation plans
- `CURRENT_PE.md`
- OpenClaw workspace definitions under `openclaw/workspaces/`
- sanitised runtime config under `openclaw/openclaw.json`
- deployment and operations runbooks

`elis-server` holds host-local data only:

- `~/.openclaw/.env`
- runtime session state
- approvals
- device identity
- logs and local memory stores

Operational rules:

- use one canonical OpenClaw install only
- do not mix installer methods
- do not keep parallel runtime roots
- do not store secret values in repository files or systemd unit `Environment=` lines
- do not treat notebook/chat text as operational truth until committed to GitHub

---

## 2. Target End State

Canonical layout on `elis-server`:

```text
/opt/openclaw
/opt/elis/repo
/opt/elis/projects
/home/samurai/.openclaw
/home/samurai/openclaw
/home/samurai/.config/systemd/user/openclaw-gateway.service
/usr/local/bin/openclaw -> /opt/openclaw/openclaw.mjs
```

Directory roles:

- `/opt/openclaw`
  - OpenClaw application code only
- `/opt/elis/repo`
  - canonical ELIS platform repo cloned from GitHub
- `/opt/elis/projects`
  - SLR review/project artefacts
- `~/.openclaw`
  - runtime state, secrets, approvals, logs, memory, live config
- `~/openclaw`
  - deployed OpenClaw workspaces

This layout deliberately separates:

- app code
- repo-controlled configuration
- runtime state
- project data

---

## 3. Preconditions

Before starting:

- maintenance window agreed
- GitHub `main` reflects the desired ELIS baseline
- operator has `sudo` on `elis-server`
- PM Agent, Telegram bot, Discord bot, and API keys are available for host-local restore
- current server state has been backed up if rebuilding an existing host

Recommended base OS:

- Ubuntu LTS
- `samurai` as the runtime user

Required base packages:

```bash
sudo apt-get update
sudo apt-get install -y git curl rsync jq python3 python3-venv ca-certificates
```

---

## 4. Backup Existing Host State

If rebuilding an existing `elis-server`, take a full backup before changing anything.

### 4.1 Capture host evidence

```bash
openclaw --version || true
systemctl --user status openclaw-gateway --no-pager || true
openclaw doctor || true
openclaw channels status --probe || true
git -C /opt/elis/repo status -sb || true
git -C /opt/elis/repo rev-parse HEAD || true
```

### 4.2 Back up mutable state

```bash
mkdir -p ~/backups/elis-rebuild
cp -a ~/.openclaw ~/backups/elis-rebuild/.openclaw.$(date +%F-%H%M%S) || true
cp -a ~/.config/systemd/user/openclaw-gateway.service* ~/backups/elis-rebuild/ 2>/dev/null || true
cp -a ~/openclaw ~/backups/elis-rebuild/openclaw-workspaces.$(date +%F-%H%M%S) || true
cp -a /opt/elis/repo ~/backups/elis-rebuild/repo.$(date +%F-%H%M%S) || true
```

### 4.3 Record installed OpenClaw roots

```bash
which openclaw || true
readlink -f "$(which openclaw)" || true
npm list -g openclaw --depth=0 || true
ls -ld /opt/openclaw || true
ls -ld ~/.openclaw ~/.openclaw.staging || true
```

Pass condition for this stage:

- backups exist
- current runtime version and service evidence are recorded
- existing OpenClaw install roots are identified

---

## 5. Reprovision the Host

For a true from-zero rebuild, start from a fresh Ubuntu host. If reusing the same machine, stop the runtime and clean old app installs first.

### 5.1 Stop the old runtime

```bash
systemctl --user stop openclaw-gateway || true
systemctl --user disable openclaw-gateway || true
```

### 5.2 Remove old non-canonical installs

Only remove paths once backups are confirmed.

```bash
sudo rm -rf /opt/openclaw
sudo npm uninstall -g openclaw || true
rm -rf ~/.openclaw.staging || true
```

Do not delete `~/.openclaw` unless you are intentionally discarding prior runtime state.

### 5.3 Recreate the canonical directory layout

```bash
sudo mkdir -p /opt/openclaw
sudo mkdir -p /opt/elis/repo
sudo mkdir -p /opt/elis/projects
mkdir -p ~/.openclaw
mkdir -p ~/openclaw
mkdir -p ~/.config/systemd/user
sudo chown -R samurai:samurai /opt/openclaw /opt/elis
```

---

## 6. Install One Canonical OpenClaw Runtime

ELIS standardises on:

- app install root: `/opt/openclaw`
- state root: `~/.openclaw`
- CLI symlink: `/usr/local/bin/openclaw`

Install OpenClaw into the canonical app root:

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install-cli.sh | sudo bash -s -- --prefix /opt/openclaw --version latest --no-onboard
sudo ln -sf /opt/openclaw/openclaw.mjs /usr/local/bin/openclaw
openclaw --version
which openclaw
readlink -f "$(which openclaw)"
```

Required result:

- `openclaw --version` succeeds
- `which openclaw` returns `/usr/local/bin/openclaw`
- resolved path points to `/opt/openclaw/openclaw.mjs`

Do not:

- install a second global npm copy
- keep a staging install as the active runtime
- point the CLI at a different root than the service

---

## 7. Restore Host-Local Secrets and State

Secrets remain host-local and must not be committed to GitHub.

### 7.1 Create the env file

```bash
install -m 700 -d ~/.openclaw
install -m 600 /dev/null ~/.openclaw/.env
```

Populate `~/.openclaw/.env` with the required host-local secrets:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENCLAW_GATEWAY_TOKEN`
- `DISCORD_BOT_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `CODEX_BOT_TOKEN`
- `CLAUDE_BOT_TOKEN`
- `PM_BOT_TOKEN`
- `CLAUDE_SETUP_TOKEN`

### 7.2 Restore selected runtime state if needed

Restore only if intentionally carrying forward state:

- approvals
- pairing/device identity
- PM memory DB
- session history required for continuity

Avoid blindly restoring drifted generated files from an older runtime unless reviewed first.

---

## 8. Create the Canonical User Service

Use a hand-maintained systemd user service that reads secrets from `~/.openclaw/.env`.

Do not rely on generated units that inline secret values into `Environment=` lines.

Create `~/.config/systemd/user/openclaw-gateway.service`:

```bash
cat > ~/.config/systemd/user/openclaw-gateway.service <<'EOF'
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target
StartLimitBurst=5
StartLimitIntervalSec=60

[Service]
ExecStart=/usr/bin/node /opt/openclaw/dist/index.js gateway --port 18789
Restart=always
RestartSec=5
RestartPreventExitStatus=78
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group
EnvironmentFile=/home/samurai/.openclaw/.env
Environment=HOME=/home/samurai
Environment=TMPDIR=/tmp
Environment=OPENCLAW_STATE_DIR=/home/samurai/.openclaw
Environment=PATH=/home/samurai/.local/bin:/usr/local/bin:/usr/bin:/bin
Environment=OPENCLAW_GATEWAY_PORT=18789
Environment=OPENCLAW_SYSTEMD_UNIT=openclaw-gateway.service
Environment="OPENCLAW_WINDOWS_TASK_NAME=OpenClaw Gateway"
Environment=OPENCLAW_SERVICE_MARKER=openclaw
Environment=OPENCLAW_SERVICE_KIND=gateway

[Install]
WantedBy=default.target
EOF
```

Activate the service:

```bash
sudo loginctl enable-linger samurai
systemctl --user daemon-reload
systemctl --user enable openclaw-gateway
systemctl --user start openclaw-gateway
systemctl --user status openclaw-gateway --no-pager
```

If the packaged runtime uses a different Node entrypoint in a future release, update `ExecStart` to the installed canonical path under `/opt/openclaw` before starting the service.

---

## 9. Clone and Deploy ELIS from GitHub

Clone the canonical platform repo:

```bash
git clone https://github.com/rochasamurai/ELIS-SLR-Agent.git /opt/elis/repo
cd /opt/elis/repo
git checkout main
git pull
```

Deploy repo-defined OpenClaw workspaces and sanitised config:

```bash
bash scripts/deploy_openclaw_workspaces.sh
systemctl --user restart openclaw-gateway
systemctl --user status openclaw-gateway --no-pager
```

This step should:

- populate `~/openclaw/...`
- deploy `~/.openclaw/openclaw.json`
- preserve runtime `channels` and `meta` where the deploy script is designed to do so

---

## 10. Baseline Validation

Run the baseline health checks:

```bash
openclaw --version
systemctl --user status openclaw-gateway --no-pager
journalctl --user -u openclaw-gateway -n 100 --no-pager
openclaw doctor
openclaw channels status --probe
openclaw approvals get --gateway
ls -l ~/openclaw/workspace-pm
ls -l ~/openclaw/workspace-pm/docs
cat ~/openclaw/workspace-pm/CURRENT_PE.md
git -C /opt/elis/repo status -sb
git -C /opt/elis/repo rev-parse HEAD
```

If using Ollama as the local support tier, validate it separately:

```bash
systemctl status ollama --no-pager
ollama list
```

Do not treat Ollama health as a blocker for PM/OpenClaw runtime readiness unless the active PE depends on it.

---

## 11. PM and Channel Validation

After baseline health is green, validate PM behaviour:

```bash
openclaw channels status --probe
openclaw doctor
```

Then follow:

- `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md`
- `docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md`

Required PM outcomes:

- PM identifies itself correctly
- PM reads the active PE from workspace entrypoints
- PM reports the current plan correctly
- Discord and Telegram bindings both probe as healthy

---

## 12. Migration Notes From Older ELIS Hosts

Use these notes when rebuilding from a previously drifted host.

### 12.1 Mixed-install drift

If the host ever had more than one OpenClaw install root, remove all but the canonical `/opt/openclaw` root before go-live.

Common drift patterns:

- `/opt/openclaw` plus `/usr/lib/node_modules/openclaw`
- `/opt/openclaw` plus `~/.openclaw.staging`
- CLI pointing to one root while the service points to another

### 12.2 Generated service files with inline secrets

If a generated unit writes actual tokens into:

- `~/.config/systemd/user/openclaw-gateway.service`

that unit is non-compliant for ELIS and must be replaced with a service that uses:

- `EnvironmentFile=/home/samurai/.openclaw/.env`

### 12.3 Config-shape drift across OpenClaw versions

If `openclaw doctor` reports legacy config keys or invalid channel settings:

```bash
openclaw doctor --fix
systemctl --user restart openclaw-gateway
openclaw channels status --probe
```

Record any config repair in the operational notes before proceeding with PE work.

---

## 13. Acceptance Criteria

The rebuild passes only if all of the following are true:

- one active OpenClaw install exists at `/opt/openclaw`
- `/usr/local/bin/openclaw` resolves to `/opt/openclaw/openclaw.mjs`
- the user service points to the canonical install under `/opt/openclaw`
- the service reads secrets from `~/.openclaw/.env`
- no secret values appear in the committed repo or the service unit
- `openclaw --version` succeeds
- `openclaw doctor` completes without blocking errors
- `openclaw channels status --probe` reports healthy Telegram and Discord bindings
- `bash scripts/deploy_openclaw_workspaces.sh` succeeds
- `~/openclaw/workspace-pm` and its `docs/` entrypoints exist
- `git -C /opt/elis/repo status -sb` shows the expected branch state
- PM E2E validation succeeds

Only after these criteria pass should ELIS start executing `ELIS_MultiAgent_Implementation_Plan_v1_8.md`.

---

## 14. Rollback

If the rebuild fails after the old host was backed up, roll back in this order.

### 14.1 Stop the new runtime

```bash
systemctl --user stop openclaw-gateway || true
systemctl --user disable openclaw-gateway || true
```

### 14.2 Restore the previous service and state

```bash
cp -a ~/backups/elis-rebuild/.openclaw.<backup-timestamp> ~/.openclaw.restore
cp -a ~/backups/elis-rebuild/openclaw-workspaces.<backup-timestamp> ~/openclaw.restore
cp ~/backups/elis-rebuild/openclaw-gateway.service.bak-<backup-timestamp> ~/.config/systemd/user/openclaw-gateway.service
```

If restoring a full previous host image is available, prefer that over partial manual rollback.

### 14.3 Restore the prior application root if intentionally preserved

```bash
sudo rm -rf /opt/openclaw
sudo cp -a /path/to/backup/openclaw /opt/openclaw
sudo ln -sf /opt/openclaw/openclaw.mjs /usr/local/bin/openclaw
```

### 14.4 Restart and verify

```bash
systemctl --user daemon-reload
systemctl --user enable openclaw-gateway
systemctl --user start openclaw-gateway
systemctl --user status openclaw-gateway --no-pager
openclaw doctor
openclaw channels status --probe
```

Rollback success means the prior runtime behaviour is restored well enough to resume operations.

---

## 15. Post-Rebuild Next Step

Once this runbook has been completed and the acceptance criteria pass:

1. confirm the active release and PE in `CURRENT_PE.md`
2. redeploy repo-controlled workspaces if any last-minute config drift was corrected
3. start execution of `ELIS_MultiAgent_Implementation_Plan_v1_8.md`

Until then, treat the host as being in rebuild or stabilisation mode, not active PE execution mode.

---

*ELIS Server From-Zero Rebuild Runbook · 2026-04-13*
