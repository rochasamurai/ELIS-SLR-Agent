# OpenClaw Exec Approval Policy — ELIS PM Agent

**Date:** 2026-03-23 (updated — Round 4)
**PE:** PE-MS-01
**Host:** elis-server (NUC8i7BEH · Ubuntu 24.04.4 LTS)
**Runtime:** Native (systemd user service — not Docker)

---

## Overview

The PM Agent (`pm`) can execute shell commands on elis-server via OpenClaw's exec tool. This policy defines which commands are auto-approved, which require operator confirmation, and which are permanently blocked.

OpenClaw exec approvals use an **allowlist model**: patterns on the allowlist auto-approve; everything else routes to the operator approval queue (Web UI at `localhost:18789` or Discord/Telegram if those approval channels are enabled). There is no separate config-level block tier — any command not on the allowlist is implicitly held for operator decision.

The allowlist is stored in `~/.openclaw/exec-approvals.json` and managed via `openclaw approvals allowlist`.

**Runtime note:** OpenClaw runs natively on elis-server as the `samurai` user under `systemd --user`. Exec commands therefore operate on host paths directly; use host paths consistently in all PM Agent instructions and allowlist patterns.

**Workspace-entrypoint rule:** PM reads governance state through workspace entrypoints (`~/openclaw/workspace-pm/CURRENT_PE.md`, `~/openclaw/workspace-pm/MEMORY.md`, `~/openclaw/workspace-pm/docs/PLAN_CURRENT.md`). These entrypoints resolve the current release state without hardcoding an obsolete plan version and avoid Discord elevated-exec approval timeouts.

**Elevated exec — disabled for `pm`:** The `pm` agent has `agents.list[id=pm].tools.elevated.enabled: false` in `openclaw.json`. This prevents read-only PM commands from being routed as elevated Discord execs (which would enter the approval queue and time out after 120 s). All PM read operations must be expressible as non-elevated allowlist patterns.

---

## Allowlist — Auto-Approved (`openclaw approvals allowlist add --agent pm`)

These commands are read-only and safe to run without confirmation:

| Pattern | Purpose |
|---|---|
| `ls *` | List directory contents |
| `cat ~/openclaw/workspace-pm/*` | Read PM workspace root files |
| `cat ~/openclaw/workspace-pm/CURRENT_PE.md` | Read Active PE Registry via workspace symlink |
| `cat ~/openclaw/workspace-pm/MEMORY.md` | Read PM durable operating memory |
| `cat ~/openclaw/workspace-pm/docs/*` | Read PM workspace docs (including `PLAN_CURRENT.md`) |
| `cat /opt/elis/repo/CURRENT_PE.md` | Read Active PE Registry (fallback — direct repo path) |
| `git * log *` | Read git log |
| `git * status *` | Read git status |
| `git * diff *` | Read git diff |
| `git * worktree list*` | List active worktrees (required for worktree queries) |
| `openclaw doctor*` | Run health check |
| `openclaw config get*` | Read OpenClaw config |
| `openclaw channels status*` | Check channel connectivity |
| `openclaw sessions*` | List/inspect sessions |
| `openclaw approvals get*` | Read current allowlist |
| `gh pr list*` | List GitHub PRs |
| `gh pr view*` | View GitHub PR details |
| `gh issue list*` | List GitHub issues |

---

## Never-Run List (hard blocked by policy, never add to allowlist)

| Pattern | Reason |
|---|---|
| `rm *`, `rm -rf *` | Destructive — data loss |
| `chmod *`, `chown *` | Permission escalation |
| `cat ~/.openclaw/.env*` | Secret exposure |
| `printenv*`, `env` | Secret exposure |
| `sudo *` | Privilege escalation |
| `curl * \| bash*` | Remote code execution |
| `git push *`, `git commit *` | Repo mutation (PO/agent responsibility) |

---

## Applying This Policy

### Step 1 — Disable elevated exec for pm (run once)

```bash
openclaw config set agents.list[id=pm].tools.elevated.enabled false
systemctl --user restart openclaw-gateway
```

This prevents PM read-only commands from entering the Discord elevated approval queue.

### Step 2 — Set workspace path (run once)

```bash
openclaw config set agents.list[id=pm].workspace ~/openclaw/workspace-pm
systemctl --user restart openclaw-gateway
```

### Step 3 — Rebuild the allowlist

```bash
openclaw approvals allowlist add --agent pm 'ls *'
openclaw approvals allowlist add --agent pm 'cat ~/openclaw/workspace-pm/*'
openclaw approvals allowlist add --agent pm 'cat ~/openclaw/workspace-pm/CURRENT_PE.md'
openclaw approvals allowlist add --agent pm 'cat ~/openclaw/workspace-pm/MEMORY.md'
openclaw approvals allowlist add --agent pm 'cat ~/openclaw/workspace-pm/docs/*'
openclaw approvals allowlist add --agent pm 'cat /opt/elis/repo/CURRENT_PE.md'
openclaw approvals allowlist add --agent pm 'git * log *'
openclaw approvals allowlist add --agent pm 'git * status *'
openclaw approvals allowlist add --agent pm 'git * diff *'
openclaw approvals allowlist add --agent pm 'git * worktree list*'
openclaw approvals allowlist add --agent pm 'openclaw doctor*'
openclaw approvals allowlist add --agent pm 'openclaw config get*'
openclaw approvals allowlist add --agent pm 'openclaw channels status*'
openclaw approvals allowlist add --agent pm 'openclaw sessions*'
openclaw approvals allowlist add --agent pm 'openclaw approvals get*'
openclaw approvals allowlist add --agent pm 'gh pr list*'
openclaw approvals allowlist add --agent pm 'gh pr view*'
openclaw approvals allowlist add --agent pm 'gh issue list*'
```

### Step 4 — Verify

```bash
openclaw approvals get --gateway
# Expected: Agents=1, Allowlist≥17, all patterns listed for agent pm
# Including: cat ~/openclaw/workspace-pm/MEMORY.md, cat ~/openclaw/workspace-pm/docs/*, and git * worktree list*
openclaw config get agents.list
# Expected: pm workspace = ~/openclaw/workspace-pm, elevated.enabled = false
```

---

## Non-allowlisted commands

Any exec command not matching an allowlist pattern is held in the operator approval queue. The operator can approve or deny via:
- **Web UI:** `http://localhost:18789` (requires token from `openclaw dashboard --no-open`)
- **Terminal UI:** `openclaw tui`
- **Discord/Telegram:** if `channels.<channel>.execApprovals.enabled: true` is set

Approval requests time out after 120 seconds if not acted on.

---

*ELIS PM Agent · Exec Policy · PE-MS-01 · 2026-03-23 · Native runtime*
