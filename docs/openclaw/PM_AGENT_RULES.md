# PM Agent Rules — Source-Controlled Reference

> **Canonical deploy source:** `openclaw/workspaces/workspace-pm/`
> **Deployed to:** `~/openclaw/workspace-pm/` via `scripts/deploy_openclaw_workspaces.sh`
> **Mirrored docs copy:** `docs/openclaw/workspace-pm/`
> **Runtime:** native `systemd --user` service on `elis-server`

This document explains where the PM prompt set lives and how it should be maintained.

---

## Canonical Prompt Set

The PM prompt stack is the deployable workspace tree:

- `openclaw/workspaces/workspace-pm/SOUL.md`
- `openclaw/workspaces/workspace-pm/AGENTS.md`
- `openclaw/workspaces/workspace-pm/MEMORY.md`

The docs mirror:

- `docs/openclaw/workspace-pm/SOUL.md`
- `docs/openclaw/workspace-pm/AGENTS.md`
- `docs/openclaw/workspace-pm/MEMORY.md`

must remain byte-aligned with the deploy source.

---

## Workspace Entrypoints On Host

After deployment, the PM workspace must expose:

- `~/openclaw/workspace-pm/CURRENT_PE.md`
- `~/openclaw/workspace-pm/docs/AGENTS.md`
- `~/openclaw/workspace-pm/docs/PLAN_CURRENT.md`

These are host entrypoints to canonical repo truth and are part of the PM runtime contract.

---

## Maintenance Rules

- edit the deploy source under `openclaw/workspaces/workspace-pm/`
- keep the docs mirror aligned in the same PR
- if prompt or exec-policy files change, reset the PM session before taking validation evidence
- use `docs/openclaw/PM_SESSION_RESET.md` for the reset procedure

---

## Deployment Rule

Deployment is native, not Docker-based:

1. run `bash scripts/deploy_openclaw_workspaces.sh`
2. restart `openclaw-gateway.service`
3. verify PM entrypoints and health
4. reset the PM session if prompt files changed

---

## Discord Reporting Rules

These rules prevent malformed or oversized output in Discord (2000-character limit).

| Situation | Required format |
|---|---|
| PE status (default) | bullet list, non-merged PEs only |
| Full registry (explicit PO request) | compact single-line-per-PE bullet list |
| Worktree state | bullet list from `git worktree list` output |
| PR state | one line per PR |
| Any table > 5 rows | switch to bullet list |
| Full 7-column registry table | **never** in Discord |

**Worktree vs registry distinction:** registry entries record branch names; they do not prove a worktree exists. Always verify with `git -C /opt/elis/repo worktree list`.

Full rules in `openclaw/workspaces/workspace-pm/AGENTS.md` §5.1–5.3 and §8.

---

*ELIS PM Agent · Rules Reference · 2026-03-23*
