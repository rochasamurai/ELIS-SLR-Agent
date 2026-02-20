# PM Agent Rules — Source-Controlled Reference

> **Source:** `openclaw/workspaces/workspace-pm/AGENTS.md`
> **Deployed to:** `~/openclaw/workspace-pm/AGENTS.md` (via `scripts/deploy_openclaw_workspaces.sh`)
> **Last updated:** PE-OC-02

This file is the source-controlled reference copy of the PM Agent orchestration rules.
The canonical file is `openclaw/workspaces/workspace-pm/AGENTS.md`. Any edit to PM Agent
rules must go through a PE, be reviewed by CODEX, and be merged to main before deployment.

---

## Summary of PM Agent Authority

| Authority | Autonomous | Requires PO |
|---|---|---|
| Assign PEs (alternation rule enforced) | Yes | No |
| Gate 1 approval | Yes (conditions met) | No |
| Gate 2 merge | Yes (PASS + green CI) | No |
| Escalation to PO | Yes (auto-triggers) | — |
| Scope changes | No | Yes |
| Rollback merged PEs | No | Yes |
| Security findings | No | Yes |
| Install ClawHub skills | Never | Never |

## Key Rules Reference

- Implementer alternates engines on consecutive same-domain PEs (CODEX ↔ Claude Code)
- Validator is always the engine opposite to the Implementer
- Gate 1 requires: CI green + HANDOFF.md present + Status Packet complete
- Gate 2 requires: REVIEW verdict = PASS + CI green + no `pm-review-required` label
- Stall threshold: 48 hours in same status triggers auto-escalation
- Iteration threshold: > 2 validator rounds triggers PO escalation
- `exec.ask: on` enforced — PM Agent confirms before executing shell commands
- `skills.hub.autoInstall: false` — no ClawHub skills permitted

## Full Rules

See `openclaw/workspaces/workspace-pm/AGENTS.md` for the complete rule set.
