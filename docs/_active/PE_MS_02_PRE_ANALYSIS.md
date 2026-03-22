# PE-MS-02 Pre-Analysis — Agent Model Registry

**Prepared by:** Claude Code (parallel work during PE-MS-01 validation)
**Date:** 2026-03-22
**For:** CODEX Implementer (`infra-impl-codex`) — PE-MS-02

---

## Purpose

This document captures the current state of `openclaw.json` and the workspace inventory on elis-server so PE-MS-02 begins with a concrete diff rather than a discovery exercise.

---

## Current `openclaw.json` State (as of 2026-03-22)

### Agent count: 13 (target: 19)

| Agent ID | Workspace | Model | Status |
|---|---|---|---|
| `pm` | workspace-pm | `anthropic/claude-opus-4-6` | ✅ Correct |
| `slr-impl-codex` | workspace-slr-impl | `openai/gpt-5.1-codex` | ❌ Wrong model + wrong agent ID |
| `slr-impl-claude` | workspace-slr-impl | `anthropic/claude-sonnet-4-6` | ❌ Wrong agent ID |
| `slr-val-codex` | workspace-slr-val | `openai/gpt-5.1-codex` | ❌ Wrong model + wrong agent ID |
| `slr-val-claude` | workspace-slr-val | `anthropic/claude-sonnet-4-6` | ❌ Wrong agent ID |
| `prog-impl-codex` | workspace-prog-impl | `openai/gpt-5.1-codex` | ❌ Wrong model |
| `prog-impl-claude` | workspace-prog-impl | `anthropic/claude-sonnet-4-6` | ✅ Correct |
| `prog-val-codex` | workspace-prog-val | `openai/gpt-5.1-codex` | ❌ Wrong model |
| `prog-val-claude` | workspace-prog-val | `anthropic/claude-sonnet-4-6` | ✅ Correct |
| `infra-impl-codex` | workspace-infra-impl | `openai/gpt-5.1-codex` | ❌ Wrong model |
| `infra-impl-claude` | workspace-infra-impl | `anthropic/claude-sonnet-4-6` | ✅ Correct |
| `infra-val-codex` | workspace-infra-val | `openai/gpt-5.1-codex` | ❌ Wrong model |
| `infra-val-claude` | workspace-infra-val | `anthropic/claude-sonnet-4-6` | ✅ Correct |

### Missing agents (6 to add, replacing 4 stale SLR IDs)

The v1.3 generic SLR agents (`slr-impl-codex`, `slr-impl-claude`, `slr-val-codex`, `slr-val-claude`) must be **replaced** with the 10 v1.5 phase-specialized agents:

| Agent ID | Workspace | Model | Action |
|---|---|---|---|
| `harvest-impl-codex` | workspace-slr-harvest | `openai/gpt-4o` | ADD |
| `harvest-val-claude` | workspace-slr-harvest | `anthropic/claude-sonnet-4-6` | ADD |
| `screen-impl-claude` | workspace-slr-screen | `anthropic/claude-sonnet-4-6` | ADD |
| `screen-val-codex` | workspace-slr-screen | `openai/gpt-4o` | ADD |
| `extract-impl-codex` | workspace-slr-extract | `openai/gpt-4o` | ADD |
| `extract-val-claude` | workspace-slr-extract | `anthropic/claude-sonnet-4-6` | ADD |
| `synth-impl-claude` | workspace-slr-synth | `anthropic/claude-sonnet-4-6` | ADD |
| `synth-val-codex` | workspace-slr-synth | `openai/gpt-4o` | ADD |
| `prisma-impl-claude` | workspace-slr-prisma | `anthropic/claude-sonnet-4-6` | ADD |
| `prisma-val-codex` | workspace-slr-prisma | `openai/gpt-4o` | ADD |

### Model corrections (existing agents)

All `*-codex` agents currently use `openai/gpt-5.1-codex` which is rate-limited.
Per plan v1.4 §6 Risk R-01, replace with `openai/gpt-4o`:

| Agent | Current model | Target model |
|---|---|---|
| `prog-impl-codex` | `openai/gpt-5.1-codex` | `openai/gpt-4o` |
| `prog-val-codex` | `openai/gpt-5.1-codex` | `openai/gpt-4o` |
| `infra-impl-codex` | `openai/gpt-5.1-codex` | `openai/gpt-4o` |
| `infra-val-codex` | `openai/gpt-5.1-codex` | `openai/gpt-4o` |

---

## Workspace Inventory on elis-server

| Workspace | Exists | Files | Notes |
|---|---|---|---|
| `workspace-pm` | ✅ | AGENTS.md, SOUL.md, docs/ | Updated by PE-MS-01 |
| `workspace-prog-impl` | ✅ | AGENTS.md, CLAUDE.md, CODEX.md | Needs audit (PE-MS-03) |
| `workspace-prog-val` | ✅ | AGENTS.md, CLAUDE.md, CODEX.md | Needs audit (PE-MS-03) |
| `workspace-infra-impl` | ✅ | AGENTS.md, CLAUDE.md, CODEX.md | Needs audit (PE-MS-03) |
| `workspace-infra-val` | ✅ | AGENTS.md, CLAUDE.md, CODEX.md | Needs audit (PE-MS-03) |
| `workspace-slr-impl` | ✅ | AGENTS.md, CLAUDE.md, CODEX.md | **STALE** — generic v1.3 agents, no v1.5 IDs |
| `workspace-slr-val` | ✅ | AGENTS.md, CLAUDE.md, CODEX.md | **STALE** — generic v1.3 agents, no v1.5 IDs |
| `workspace-slr-harvest` | ❌ | — | MISSING — PE-MS-04 creates |
| `workspace-slr-screen` | ❌ | — | MISSING — PE-MS-04 creates |
| `workspace-slr-extract` | ❌ | — | MISSING — PE-MS-05 creates |
| `workspace-slr-synth` | ❌ | — | MISSING — PE-MS-05 creates |
| `workspace-slr-prisma` | ❌ | — | MISSING — PE-MS-05 creates |

> **Note for PE-MS-02 Implementer:** The 10 new SLR phase agents point to workspaces that don't yet exist on elis-server. `openclaw doctor` will flag workspace-not-found errors for those agents until PE-MS-04 and PE-MS-05 create the directories. This is expected and not a PE-MS-02 blocking issue — document it in HANDOFF.md.

---

## PE-MS-02 Implementation Checklist (for CODEX)

1. Remove 4 stale SLR agent entries (`slr-impl-codex`, `slr-impl-claude`, `slr-val-codex`, `slr-val-claude`)
2. Update 4 codex model strings from `openai/gpt-5.1-codex` → `openai/gpt-4o`
3. Add 10 phase-specialized SLR agents with correct workspace paths and models
4. Verify total agent count = 19
5. Run `openclaw config validate` — must pass
6. Run `openclaw doctor` — expected: 19 agents listed, workspace-not-found warnings for 5 new SLR workspaces are acceptable (documented above)
7. Commit sanitised `openclaw.json` copy to `docs/openclaw/openclaw_sanitised.json`

---

## PM Agent Session Note (Item 1)

The PM Agent's current Discord session (`agent:pm:main`) is 2 hours old and predates the new SOUL.md deployment. OpenClaw loads workspace files at session start — the new identity will not be active until the session is reset.

**To reset:** The PO should send `/reset` or start a fresh Discord DM conversation with the PM Agent. This forces a new session that loads the updated SOUL.md and AGENTS.md.

Alternatively: `docker exec openclaw openclaw sessions` shows the session key. A future OpenClaw version may support `openclaw sessions reset <key>`.
