# MEMORY.md — ELIS PM Agent Operational Memory

This file records the durable corrections that must survive session drift.

---

## Current Invariants

- Read governance through workspace entrypoints, not ad-hoc host paths.
- `CURRENT_PE.md` is the source for active PE and release metadata.
- `PLAN_CURRENT.md` is the source for active plan details.
- Worktrees must be reported only from `git -C /opt/elis/repo worktree list`.
- PR status must be reported only from `gh pr`.

---

## Session Reset Rule

If `SOUL.md`, `AGENTS.md`, `MEMORY.md`, workspace entrypoints, or PM exec policy changed,
the current PM session is untrusted until reset.

Do not claim new prompt behavior is active until a fresh session starts.

---

## Never Reintroduce

- hardcoded `PLAN_v1_5.md` as the active plan path
- direct `/opt/elis/repo/...` reads as the normal Discord flow
- worktree answers inferred from registry branch names
- stale copied files used silently when entrypoints fail

---

*ELIS PM Agent · MEMORY.md · v1.0 · 2026-03-23*
