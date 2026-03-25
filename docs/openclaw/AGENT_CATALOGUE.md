# OpenClaw Agent Catalogue

> Updated 2026-03-24 for PE-MS-04.
> Runtime reference: `docs/openclaw/openclaw_sanitised.json`
> Architecture target: `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_6.md` §4.2

---

## 1. Purpose

This document records the current native OpenClaw runtime roster on `elis-server`
and the remaining gap to the Architecture v1.6 target.

It is intentionally split into:

- current runtime state: what is configured and operating now
- target architecture: what later PEs still need to provision

---

## 2. Current Runtime Snapshot (13 agents)

As of 2026-03-24, the native runtime is still operating a 13-agent roster.
This snapshot was taken from live `openclaw config get agents.list --json` output
and normalized to canonical host workspace paths.

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
| `slr-impl-codex` | SLR | Implementer | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-slr-impl` |
| `slr-impl-claude` | SLR | Implementer | `anthropic/claude-sonnet-4-6` | `/home/samurai/openclaw/workspace-slr-impl` |
| `slr-val-codex` | SLR | Validator | `openai/gpt-5.1-codex` | `/home/samurai/openclaw/workspace-slr-val` |
| `slr-val-claude` | SLR | Validator | `anthropic/claude-sonnet-4-6` | `/home/samurai/openclaw/workspace-slr-val` |

Notes:

- PM is currently in contingency mode on `openai/gpt-5-mini`.
- Generic `workspace-slr-impl` / `workspace-slr-val` are still present in runtime.
- Current runtime is native `systemd`, not Docker.

---

## 3. Current Runtime Guarantees

PE-MS-04 normalizes the source-controlled runtime reference to canonical host paths:

- no agent workspace points to `/app/...`
- no runtime workspace path is relative in the source-controlled config
- PM remains the only externally bound agent
- Discord and Telegram plugins remain enabled

This PE does **not** yet expand the runtime to the full 19-agent Architecture v1.6 target.

---

## 4. Gap to Architecture v1.6

Architecture v1.6 defines a 19-agent topology:

- 1 PM agent
- 4 Programs agents
- 4 Infrastructure agents
- 10 phase-specialized SLR agents

The current runtime differs in two ways:

1. It still runs 4 generic SLR agents:
   - `slr-impl-codex`
   - `slr-impl-claude`
   - `slr-val-codex`
   - `slr-val-claude`
2. It does not yet register the 10 phase-specialized SLR agents:
   - `harvest-impl-codex`
   - `harvest-val-claude`
   - `screen-impl-claude`
   - `screen-val-codex`
   - `extract-impl-codex`
   - `extract-val-claude`
   - `synth-impl-claude`
   - `synth-val-codex`
   - `prisma-impl-claude`
   - `prisma-val-codex`

That gap is expected to close in later PEs:

- `PE-MS-05` workspace audit and segmentation check
- `PE-MS-06` SLR phase workspace provisioning
- `PE-MS-07` project-store layout and PM visibility rules

---

## 5. Canonical Path Contract

Source-controlled runtime config must use canonical host paths:

- `/home/samurai/openclaw/workspace-pm`
- `/home/samurai/openclaw/workspace-prog-impl`
- `/home/samurai/openclaw/workspace-prog-val`
- `/home/samurai/openclaw/workspace-infra-impl`
- `/home/samurai/openclaw/workspace-infra-val`
- `/home/samurai/openclaw/workspace-slr-impl`
- `/home/samurai/openclaw/workspace-slr-val`

This makes runtime intent explicit and prevents drift back to:

- container-only `/app/...` paths
- ambiguous relative workspace names in the source-controlled config

---

## 6. Source of Truth

Use these artifacts together:

- `openclaw/openclaw.json`
  source-controlled runtime config to deploy
- `docs/openclaw/openclaw_sanitised.json`
  redacted reviewable copy of the runtime config
- `docs/openclaw/TARGET_LAYOUT.md`
  canonical host layout and workspace strategy
- `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_6.md`
  architecture target and agent-topology invariants

---

*OpenClaw Agent Catalogue · Native runtime snapshot · 2026-03-24*
