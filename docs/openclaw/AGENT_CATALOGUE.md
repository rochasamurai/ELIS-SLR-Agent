# OpenClaw Agent Catalogue

> Updated 2026-03-25 for PE-MS-06.
> Source-config reference: `docs/openclaw/openclaw_sanitised.json`
> Architecture target: `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_6.md` §4.2

---

## 1. Purpose

This document records the source-controlled native OpenClaw roster that should be
deployed to `elis-server` after PE-MS-06.

It now reflects the full 19-agent Architecture v1.6 topology in repo config.
The live host may still be on the previous 13-agent baseline until the next
deployment run is executed.

---

## 2. Source-Controlled Runtime Target (19 agents)

| ID | Domain | Role | Model | Workspace |
|---|---|---|---|---|
| `pm` | PM | Orchestrator | `openai/gpt-5-mini` | `/home/samurai/openclaw/workspace-pm` |
| `prog-impl-codex` | Programs | Implementer | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-prog-impl` |
| `prog-impl-claude` | Programs | Implementer | `anthropic/claude-sonnet-4-6` | `/home/samurai/openclaw/workspace-prog-impl` |
| `prog-val-codex` | Programs | Validator | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-prog-val` |
| `prog-val-claude` | Programs | Validator | `anthropic/claude-sonnet-4-6` | `/home/samurai/openclaw/workspace-prog-val` |
| `infra-impl-codex` | Infrastructure | Implementer | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-infra-impl` |
| `infra-impl-claude` | Infrastructure | Implementer | `anthropic/claude-sonnet-4-6` | `/home/samurai/openclaw/workspace-infra-impl` |
| `infra-val-codex` | Infrastructure | Validator | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-infra-val` |
| `infra-val-claude` | Infrastructure | Validator | `anthropic/claude-sonnet-4-6` | `/home/samurai/openclaw/workspace-infra-val` |
| `harvest-impl-codex` | Harvest | Implementer | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-slr-harvest` |
| `harvest-val-claude` | Harvest | Validator | `anthropic/claude-sonnet-4-6` | `/home/samurai/openclaw/workspace-slr-harvest` |
| `screen-impl-claude` | Screen | Implementer | `anthropic/claude-opus-4-6` | `/home/samurai/openclaw/workspace-slr-screen` |
| `screen-val-codex` | Screen | Validator | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-slr-screen` |
| `extract-impl-codex` | Extraction | Implementer | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-slr-extract` |
| `extract-val-claude` | Extraction | Validator | `anthropic/claude-opus-4-6` | `/home/samurai/openclaw/workspace-slr-extract` |
| `synth-impl-claude` | Synthesis | Implementer | `anthropic/claude-opus-4-6` | `/home/samurai/openclaw/workspace-slr-synth` |
| `synth-val-codex` | Synthesis | Validator | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-slr-synth` |
| `prisma-impl-claude` | PRISMA | Implementer | `anthropic/claude-sonnet-4-6` | `/home/samurai/openclaw/workspace-slr-prisma` |
| `prisma-val-codex` | PRISMA | Validator | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-slr-prisma` |

Notes:

- PM remains in contingency mode on `openai/gpt-5-mini`.
- Generic `workspace-slr-impl` / `workspace-slr-val` are removed from the source-controlled runtime.
- Production runtime remains native `systemd`, not Docker.

---

## 3. Runtime Guarantees After PE-MS-06

- no agent workspace points to `/app/...`
- no runtime workspace path is relative in the source-controlled config
- PM remains the only externally bound agent
- Discord and Telegram plugins remain enabled
- the 10 phase-specialized SLR agents replace the 4 generic SLR agents
- all 5 phase-specialized SLR workspaces are provisioned in repo and ready for deployment

---

## 4. Canonical Path Contract

Source-controlled runtime config must use canonical host paths:

- `/home/samurai/openclaw/workspace-pm`
- `/home/samurai/openclaw/workspace-prog-impl`
- `/home/samurai/openclaw/workspace-prog-val`
- `/home/samurai/openclaw/workspace-infra-impl`
- `/home/samurai/openclaw/workspace-infra-val`
- `/home/samurai/openclaw/workspace-slr-harvest`
- `/home/samurai/openclaw/workspace-slr-screen`
- `/home/samurai/openclaw/workspace-slr-extract`
- `/home/samurai/openclaw/workspace-slr-synth`
- `/home/samurai/openclaw/workspace-slr-prisma`

This prevents drift back to:

- container-only `/app/...` paths
- ambiguous relative workspace names in the source-controlled config
- obsolete generic SLR workspace declarations

---

## 5. Source of Truth

Use these artifacts together:

- `openclaw/openclaw.json`
- `docs/openclaw/openclaw_sanitised.json`
- `docs/openclaw/SLR_PHASE_WORKSPACE_PROVISIONING_2026-03-25.md`
- `docs/openclaw/TARGET_LAYOUT.md`
- `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_6.md`

---

*OpenClaw Agent Catalogue · Source-controlled target roster · 2026-03-25*
