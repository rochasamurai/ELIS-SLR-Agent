# OpenClaw Exec Approval Policy — ELIS PM Agent

**Date:** 2026-03-22
**PE:** PE-MS-01
**Host:** elis-server (NUC8i7BEH · Ubuntu 24.04.4 LTS)

---

## Overview

The PM Agent (`pm`) can execute shell commands on elis-server via OpenClaw's exec tool. This policy defines which commands are auto-approved, which require operator confirmation, and which are permanently blocked.

The exec policy is configured in `~/.openclaw/openclaw.json` under `agents.exec` and enforced by OpenClaw at runtime.

---

## Policy Tiers

### Tier 1 — Auto-Approved (`exec.autoApprove`)

These commands are read-only and safe to run without confirmation:

| Pattern | Purpose |
|---|---|
| `ls *` | List directory contents |
| `cat ~/openclaw/workspace-pm/*` | Read PM Agent workspace files |
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

### Tier 2 — Requires Operator Approval (`exec.ask`)

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

### Tier 3 — Permanently Blocked (`exec.block`)

These commands are never allowed regardless of operator approval:

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

The exec policy is applied via the OpenClaw CLI during PE-MS-01 implementation:

```bash
# Set autoApprove patterns
openclaw config set agents.exec.autoApprove '[
  "ls *",
  "cat ~/openclaw/workspace-pm/*",
  "git * log *",
  "git * status *",
  "git * diff *",
  "git * show *",
  "openclaw doctor*",
  "openclaw config get*",
  "openclaw channels status*",
  "openclaw sessions*",
  "gh pr list*",
  "gh pr view*",
  "gh issue list*"
]'

# Set ask patterns
openclaw config set agents.exec.ask '[
  "openclaw config set*",
  "git * commit*",
  "git * push*",
  "git * checkout*",
  "docker restart*",
  "gh pr create*",
  "gh pr merge*",
  "gh pr review*",
  "mkdir *",
  "cp *",
  "mv *"
]'

# Set block patterns
openclaw config set agents.exec.block '[
  "rm *",
  "chmod *",
  "chown *",
  "docker rm*",
  "docker rmi*",
  "cat .env*",
  "cat *credentials*",
  "printenv*",
  "env",
  "export *KEY*",
  "export *TOKEN*",
  "curl * | bash",
  "wget * -O- | bash"
]'
```

---

*ELIS PM Agent · Exec Policy · PE-MS-01 · 2026-03-22*
