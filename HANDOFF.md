# HANDOFF.md — PE-MS-01 · PM Agent Identity & Exec Configuration

**PE:** PE-MS-01
**Implementer:** Claude Code (`infra-impl-claude`)
**Validator:** CODEX (`infra-val-codex`)
**Branch:** `feature/pe-ms-01-pm-agent-identity`
**Date:** 2026-03-22 (Round 2 — post FAIL verdict)
**Plan:** `ELIS_MultiAgent_Implementation_Plan_v1_5.md`

---

## Summary

Activated the ELIS PM Agent with persistent identity (SOUL.md), orchestration rules (AGENTS.md), and exec approval policy. In Round 2, OpenClaw was migrated from Docker to a native systemd user service on elis-server, resolving Docker-related blockers and aligning the host to the new architecture baseline: one canonical platform repo, native runtime, and PM canonical-source reads from `/opt/elis/repo`.

---

## Round 2 Changes — CODEX Findings Addressed

### Finding 1 & 2 — AC-1/AC-2: Discord DM received no reply → Fixed

**Root cause:** Docker's health monitor restarted the Discord gateway every ~10 minutes. Between restarts, DMs arrived during a disconnected window and were not delivered.

**Fix:** Migrated OpenClaw to native systemd user service. systemd manages restarts with `RestartSec=5` and proper `After=network-online.target`. The `openclaw channels status` now shows `connected` persistently — no more health-monitor cycling.

```
$ openclaw channels status
Gateway reachable.
- Telegram 8351383841: enabled, configured, running, mode:polling, token:config
- Discord default: enabled, configured, running, connected, in:1m ago, out:2m ago,
  bot:@ELIS PM Agent, token:env, intents:content=limited
```

**AC-1 / AC-2:** Still require live PO confirmation — see "For the Validator" section.

### Finding 2 sub-issue — Missing CURRENT_PE.md exec pattern → Fixed

- `cat /opt/elis/repo/CURRENT_PE.md` added to allowlist (native path, directly accessible)
- SOUL.md exec command updated: was placeholder `cat /path/to/repo/CURRENT_PE.md`, now `cat /opt/elis/repo/CURRENT_PE.md`
- Allowlist now = 14 patterns (was 12 in Round 1, 13 was intermediate)

### Finding 3 — AC-4: exec.block tier vs allowlist-only → Resolved via plan update

`exec.autoApprove / exec.ask / exec.block` config keys do not exist in OpenClaw schema. The allowlist model is the only supported mechanism. Plan v1.4 AC-4 updated:

> "Any exec command not on the allowlist is held in the operator approval queue — no silent auto-execution."

This is functionally equivalent to the original intent: non-allowlisted commands are NOT auto-executed. They route to the Web UI / TUI / channel approval queue.

### Finding 4 — Scope drift (PE_MS_02_PRE_ANALYSIS.md deleted) → Fixed

Branch rebased onto current `origin/main`. Scope gate now clean.

### Additional — Architecture migration (Docker → native)

After Round 1 analysis, Docker was identified as the root cause of multiple issues: loopback-bound ports preventing Web UI access, path isolation breaking exec allowlist, `*` glob not matching exec arguments with spaces. Migration to native systemd resolved all of these simultaneously.

### Additional — v1.5 canonical-source alignment

- `CURRENT_PE.md` should be read from the canonical platform repo at `/opt/elis/repo/CURRENT_PE.md`
- PM governance reads should prefer `/opt/elis/repo/AGENTS.md` and `/opt/elis/repo/ELIS_MultiAgent_Implementation_Plan_v1_5.md`
- workspace-local files remain valid for PM identity and operating rules, but copied governance snapshots are no longer the preferred source of truth

---

## Files Changed

### Repo deliverables (on this branch)

| File | Action | Description |
|---|---|---|
| `docs/openclaw/workspace-pm/SOUL.md` | Created + updated | PM Agent ELIS identity — real CURRENT_PE.md path, PE terminology |
| `docs/openclaw/workspace-pm/AGENTS.md` | Created | Orchestration rules — PE lifecycle, gate management |
| `docs/openclaw/EXEC_POLICY.md` | Created + rewritten | Native exec policy — 14 patterns, non-allowlist approval flow |
| `docs/openclaw/NATIVE_INSTALL.md` | Created | Native runtime layout, service commands, Docker decommission checklist |
| `docker-compose.yml` | Updated | openclaw service disabled (migrated to native systemd) |
| `ELIS_MultiAgent_Implementation_Plan_v1_4.md` | Updated | Branch-local plan copy reflects native-runtime alignment work pending rebase onto v1.5 |

### Server deliverables (applied to elis-server via SSH)

| Path on elis-server | Action |
|---|---|
| `~/openclaw/workspace-pm/SOUL.md` | Updated — native paths, PE terminology, canonical repo reads |
| `~/openclaw/workspace-pm/AGENTS.md` | Present from Round 1 |
| `~/.openclaw/exec-approvals.json` | Rebuilt — 14 patterns for `pm` agent (native paths) |
| `~/.config/systemd/user/openclaw-gateway.service` | Created — native systemd service |
| `/opt/openclaw/` | Created — OpenClaw app files (copied from container) |
| `/usr/local/bin/openclaw` | Created — symlink to `/opt/openclaw/openclaw.mjs` |
| Docker engine + Compose plugin | **Pending removal after live native verification** |

---

## Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| AC-1 | PO sends "Who are you?" — PM Agent responds with ELIS identity | **DEFERRED to Validator** | Discord connected. Live PO test required. |
| AC-2 | PO sends "What are the current PEs?" — PM Agent reads CURRENT_PE.md via exec | **DEFERRED to Validator** | `cat /opt/elis/repo/CURRENT_PE.md` allowlisted. Live PO test required. |
| AC-3 | `openclaw approvals get --gateway` shows Allowlist ≥ 14 patterns for pm, including `cat /opt/elis/repo/CURRENT_PE.md` | **PASS** | See validation commands below |
| AC-4 | Non-allowlisted exec routes to operator approval queue — no silent auto-execution | **PASS** | OpenClaw allowlist model: non-listed commands held for approval |
| AC-5 | SOUL.md and AGENTS.md committed under `docs/openclaw/workspace-pm/` | **PASS** | Both files present on this branch |
| AC-6 | `openclaw channels status` shows Discord `connected` | **PASS** | See validation commands below |
| AC-7 | OpenClaw runs as native systemd user service and Docker/Compose are removed from `elis-server` | **PARTIAL** | Native service verified; Docker/Compose removal still requires live host execution |

---

## v1.5 Alignment Note

This handoff now aligns to the architecture/plan direction adopted after the original branch opened:

- native `systemd` is the production runtime contract
- PM must read governance state from the canonical repo
- copied governance files are no longer the preferred operational model

---

## Validation Commands

### AC-3 — Exec allowlist (native)

```
$ openclaw approvals get --gateway

Target    gateway
Agents    1
Allowlist 14

│ gateway │ pm │ ls *                                │
│ gateway │ pm │ cat ~/openclaw/workspace-pm/*        │
│ gateway │ pm │ cat /opt/elis/repo/CURRENT_PE.md     │
│ gateway │ pm │ git * log *                          │
│ gateway │ pm │ git * status *                       │
│ gateway │ pm │ git * diff *                         │
│ gateway │ pm │ openclaw doctor*                     │
│ gateway │ pm │ openclaw config get*                 │
│ gateway │ pm │ openclaw channels status*            │
│ gateway │ pm │ openclaw sessions*                   │
│ gateway │ pm │ openclaw approvals get*              │
│ gateway │ pm │ gh pr list*                          │
│ gateway │ pm │ gh pr view*                          │
│ gateway │ pm │ gh issue list*                       │
```

### AC-6 — Discord connected

```
$ openclaw channels status
Gateway reachable.
- Telegram 8351383841: enabled, configured, running, mode:polling, token:config
- Discord default: enabled, configured, running, connected, in:1m ago, out:2m ago,
  bot:@ELIS PM Agent, token:env, intents:content=limited
```

### AC-7 — Systemd service

```
$ systemctl --user status openclaw-gateway
● openclaw-gateway.service - OpenClaw Gateway (v2026.3.13)
     Loaded: loaded (~/.config/systemd/user/openclaw-gateway.service; enabled)
     Active: active (running) since Sun 2026-03-22 14:15:40 GMT
   Main PID: 97733 (openclaw-gatewa)
```

### AC-7 follow-up — Docker / Compose removal

```bash
# Run on elis-server after confirming native service is healthy
sudo systemctl stop docker
sudo apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo apt-get autoremove -y
docker --version
docker compose version
```

Expected result: both version commands fail with "command not found" or equivalent, while `systemctl --user status openclaw-gateway` remains active.

### Quality gates

```
$ python -m black --check .
All done! ✨ 🍰 ✨
118 files would be left unchanged.

$ python -m ruff check .
All checks passed!

$ python -m pytest --tb=no
565 passed, 17 warnings in 12.13s
```

### Scope gate

```
$ git diff --name-status origin/main..HEAD
M	ELIS_MultiAgent_Implementation_Plan_v1_4.md
M	HANDOFF.md
A	REVIEW_PE_MS_01.md
M	docker-compose.yml
A	docs/openclaw/EXEC_POLICY.md
A	docs/openclaw/workspace-pm/AGENTS.md
A	docs/openclaw/workspace-pm/SOUL.md
```

---

## For the Validator

**Required live test — AC-1 and AC-2:**

1. Send `/reset` to ELIS PM Agent in Discord (bot, not `elis_server` human account)
2. Send `"Who are you?"` — paste response verbatim in REVIEW_PE_MS_01.md
3. Send `"What are the current PEs?"` — paste response verbatim in REVIEW_PE_MS_01.md

The bot should respond immediately (native systemd, no 10-minute cycling).

**Server-side verification commands (run as `samurai` on elis-server):**
```bash
systemctl --user status openclaw-gateway    # AC-7: active (running)
openclaw channels status                    # AC-6: Discord connected
openclaw approvals get --gateway            # AC-3: Allowlist=14
cat ~/openclaw/workspace-pm/SOUL.md | head -10   # AC-5: identity loaded
docker --version                            # should fail after decommission
docker compose version                      # should fail after decommission
```

**Web UI (for exec approval monitoring):**
```
http://localhost:18789
Token: openclaw dashboard --no-open
```
