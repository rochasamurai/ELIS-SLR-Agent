# OpenClaw Exec Approval Policy — ELIS PM Agent

**Date:** 2026-03-22
**PE:** PE-MS-01
**Host:** elis-server (NUC8i7BEH · Ubuntu 24.04.4 LTS)

---

## Overview

The PM Agent (`pm`) can execute shell commands on elis-server via OpenClaw's exec tool. This policy defines which commands are auto-approved, which require operator confirmation, and which are permanently blocked.

The exec policy has two layers:
1. **Channel exec enable** — `channels.<channel>.execApprovals.enabled: true` must be set for each channel (Discord, Telegram) where exec commands will originate. Without this, all exec is blocked at the channel gate before the allowlist is checked.
2. **Allowlist** — `~/.openclaw/exec-approvals.json` defines which command patterns are auto-approved without operator confirmation.

Both layers must be configured. Allowlist patterns have no effect if `execApprovals.enabled` is not set for the channel.

---

## Policy Model

OpenClaw exec approvals use an **allowlist model**: patterns on the allowlist auto-approve; everything else requires manual operator confirmation before execution. There is no separate config-level block tier — any command not on the allowlist is implicitly blocked from auto-approval.

The allowlist is stored in `~/.openclaw/exec-approvals.json` on elis-server and managed via `openclaw approvals allowlist`.

---

## Allowlist — Auto-Approved (`openclaw approvals allowlist add --agent pm`)

These commands are read-only and safe to run without confirmation:

| Pattern | Purpose |
|---|---|
| `ls *` | List directory contents |
| `cat /app/workspace-pm/*` | Read PM Agent workspace files (container path) |
| `gh api repos/rochasamurai/ELIS-SLR-Agent/contents/CURRENT_PE.md*` | Read Active PE Registry via GitHub API |
| `git * log *` | Read git log |
| `git * status *` | Read git status |
| `git * diff *` | Read git diff |
| `git * show *` | Read git objects |
| `openclaw doctor*` | Run health check |
| `openclaw config get*` | Read config values |
| `openclaw channels status*` | Check channel status |
| `openclaw sessions*` | List sessions |
| `gh pr list*` | List PRs |
| `gh pr view*` | View PR details |
| `gh issue list*` | List issues |

### Not Allowlisted — Requires Manual Approval

These commands make changes and require a confirmation prompt before execution:

| Pattern | Purpose |
|---|---|
| `openclaw config set*` | Change OpenClaw configuration |
| `git * commit*` | Create a git commit |
| `git * push*` | Push to remote |
| `git * checkout*` | Switch branches |
| `docker restart*` | Restart containers |
| `gh pr create*` | Create a PR |
| `gh pr merge*` | Merge a PR |
| `gh pr review*` | Post a PR review |
| `mkdir *` | Create directories |
| `cp *` | Copy files |
| `mv *` | Move files |

### Never Run — Operator Must Refuse These

These commands must never be approved even if requested:

| Pattern | Reason |
|---|---|
| `rm *` | Destructive — data loss risk |
| `chmod *` | Security — permission changes |
| `chown *` | Security — ownership changes |
| `docker rm*` | Destructive — container removal |
| `docker rmi*` | Destructive — image removal |
| `cat .env*` | Secrets — exposes credentials |
| `cat *credentials*` | Secrets — exposes credentials |
| `printenv*` | Secrets — exposes environment |
| `env` | Secrets — exposes environment |
| `export *KEY*` | Secrets — exposes API keys |
| `export *TOKEN*` | Secrets — exposes tokens |
| `curl * | bash` | Security — remote code execution |
| `wget * -O- | bash` | Security — remote code execution |

---

## Rationale

The PM Agent requires exec access to:
1. Read `CURRENT_PE.md` from the ELIS repo to track PE state
2. Run `openclaw doctor` to verify health
3. Read channel and session status

It does **not** require exec access to modify the ELIS codebase (that is the implementer agents' role) or to manage secrets (that is the host operator's role).

The block list follows the ELIS secrets isolation policy (`AGENTS.md` §13) and the principle of least privilege.

---

## Applying This Policy

### Step 1 — Enable exec on Discord channel (required before allowlist takes effect)

```bash
# Enable exec approvals gate for Discord
docker exec openclaw openclaw config set channels.discord.execApprovals '{"enabled": true}'
docker restart openclaw
```

Without this, all exec commands from Discord are blocked before the allowlist is consulted.

### Step 2 — Configure the allowlist

```bash
# Add auto-approved read-only patterns for the pm agent
openclaw approvals allowlist add --agent pm 'ls *'
openclaw approvals allowlist add --agent pm 'cat /app/workspace-pm/*'
openclaw approvals allowlist add --agent pm 'gh api repos/rochasamurai/ELIS-SLR-Agent/contents/CURRENT_PE.md*'
openclaw approvals allowlist add --agent pm 'git * log *'
openclaw approvals allowlist add --agent pm 'git * status *'
openclaw approvals allowlist add --agent pm 'git * diff *'
openclaw approvals allowlist add --agent pm 'openclaw doctor*'
openclaw approvals allowlist add --agent pm 'openclaw config get*'
openclaw approvals allowlist add --agent pm 'openclaw channels status*'
openclaw approvals allowlist add --agent pm 'openclaw sessions*'
openclaw approvals allowlist add --agent pm 'gh pr list*'
openclaw approvals allowlist add --agent pm 'gh pr view*'
openclaw approvals allowlist add --agent pm 'gh issue list*'

# Verify
openclaw approvals get --gateway
```

**Note — exec runs inside the container:** All paths in exec commands must use container-internal paths:
- Workspace files: `/app/workspace-pm/` (not `~/openclaw/workspace-pm/`)
- ELIS repo is NOT mounted inside the container — use `gh api` to read repo files
- ELIS repo on host: `/opt/elis/repo/` — inaccessible from inside the container

To verify the applied policy on elis-server:
```bash
docker exec openclaw openclaw config get channels.discord.execApprovals
# Expected: {"enabled": true}

docker exec openclaw openclaw approvals get --gateway
# Expected: Agents=1, Allowlist=13, all patterns listed under agent pm
```

---

*ELIS PM Agent · Exec Policy · PE-MS-01 · 2026-03-22*
