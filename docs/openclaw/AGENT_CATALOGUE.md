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

### PM
- `pm` — Orchestrator — `deepseek/deepseek-v4-pro` — `/home/samurai/openclaw/workspace-pm`

### Prog
- `prog-impl-a` — Implementer — `qwen/qwen3-coder-flash` — `/home/samurai/openclaw/workspace-prog-impl`
- `prog-impl-b` — Implementer — `deepseek/deepseek-v4-flash` — `/home/samurai/openclaw/workspace-prog-impl`
- `prog-val-a` — Validator — `deepseek/deepseek-v4-pro` — `/home/samurai/openclaw/workspace-prog-val`
- `prog-val-b` — Validator — `z-ai/glm-5.1` — `/home/samurai/openclaw/workspace-prog-val`

### Infra
- `infra-impl-a` — Implementer — `qwen/qwen3-coder-flash` — `/home/samurai/openclaw/workspace-infra-impl`
- `infra-impl-b` — Implementer — `deepseek/deepseek-v4-flash` — `/home/samurai/openclaw/workspace-infra-impl`
- `infra-val-a` — Validator — `deepseek/deepseek-v4-pro` — `/home/samurai/openclaw/workspace-infra-val`
- `infra-val-b` — Validator — `z-ai/glm-5.1` — `/home/samurai/openclaw/workspace-infra-val`

### SLR — Harvest
- `harvest-impl-a` — Implementer — `qwen/qwen3-coder-flash` — `/home/samurai/openclaw/workspace-slr-harvest`
- `harvest-val-b` — Validator — `z-ai/glm-5.1` — `/home/samurai/openclaw/workspace-slr-harvest`

### SLR — Screen
- `screen-impl-b` — Implementer — `deepseek/deepseek-v4-flash` — `/home/samurai/openclaw/workspace-slr-screen`
- `screen-val-a` — Validator — `deepseek/deepseek-v4-pro` — `/home/samurai/openclaw/workspace-slr-screen`

### SLR — Extract
- `extract-impl-a` — Implementer — `qwen/qwen3-coder-flash` — `/home/samurai/openclaw/workspace-slr-extract`
- `extract-val-b` — Validator — `z-ai/glm-5.1` — `/home/samurai/openclaw/workspace-slr-extract`

### SLR — Synth
- `synth-impl-b` — Implementer — `deepseek/deepseek-v4-flash` — `/home/samurai/openclaw/workspace-slr-synth`
- `synth-val-a` — Validator — `deepseek/deepseek-v4-pro` — `/home/samurai/openclaw/workspace-slr-synth`

### SLR — Prisma
- `prisma-impl-b` — Implementer — `deepseek/deepseek-v4-flash` — `/home/samurai/openclaw/workspace-slr-prisma`
- `prisma-val-a` — Validator — `deepseek/deepseek-v4-pro` — `/home/samurai/openclaw/workspace-slr-prisma`

Notes:

- PM remains in contingency mode on `deepseek/deepseek-v4-pro`.
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

## 6. Governance

Token usage policy and implementation guidance for all agents:

- `docs/governance/ELIS_Token_Usage_Guidelines_for_Multi_AI_Agents.md`
- `docs/governance/ELIS_Token_Usage_Guidelines_Implementation_Plan.md`

---

*OpenClaw Agent Catalogue · Source-controlled target roster · 2026-03-25*
