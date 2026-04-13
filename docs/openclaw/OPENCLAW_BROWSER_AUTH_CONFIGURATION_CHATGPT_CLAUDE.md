# OpenClaw Configuration Guide — Browser-Based Auth (ChatGPT + Claude)

## Overview

This document provides a **production-ready configuration** for using OpenClaw with:

- ChatGPT (via Codex OAuth — browser login)
- Claude (via setup-token — subscription reuse)

Objective:

- Avoid API keys
- Reuse existing subscriptions (ChatGPT Plus / Claude)
- Integrate seamlessly with VS Code + OpenClaw multi-agent workflows

---

## Architecture

```
VS Code (UI / supervision)
        ↓
Claude Code / Codex CLI (execution layer)
        ↓
OpenClaw (agent orchestration)
        ↓
Multi-agent workflows (ELIS, automation, etc.)
```

Key principle:

> OpenClaw orchestrates agents; VS Code remains the development interface.

---

## Authentication Model

### 1. ChatGPT (OpenAI Codex) — Browser OAuth

- Uses official OAuth flow
- Opens browser for login
- Stores token locally
- Fully supported and stable

Command:

```bash
openclaw models auth login --provider openai-codex
```

Result:

- Uses your ChatGPT subscription
- No API key required

---

### 2. Claude — Setup Token (Subscription Reuse)

Claude does NOT use open OAuth in OpenClaw.

Instead:

```bash
claude setup-token
```

Then register in OpenClaw:

```bash
openclaw models auth paste-token --provider anthropic
```

Notes:

- Token generated from Claude Code environment
- Does NOT reuse browser session directly
- Officially supported path for subscription usage

---

## Configuration File

Location:

```
~/.openclaw/openclaw.json
```

---

## Full Configuration

```json
{
  "$schema": "https://docs.openclaw.ai/schema/openclaw.json",

  "agents": {
    "defaults": {
      "model": {
        "primary": "openai-codex/gpt-5.4",
        "fallbacks": [
          "anthropic/claude-sonnet-4-6",
          "openai/gpt-5-mini"
        ]
      },

      "models": {
        "openai-codex/gpt-5.4": {
          "alias": "codex-main",
          "params": {
            "transport": "auto"
          }
        },

        "anthropic/claude-sonnet-4-6": {
          "alias": "claude-main",
          "params": {
            "thinking": "adaptive",
            "context1m": false
          }
        },

        "openai/gpt-5-mini": {
          "alias": "gpt-mini",
          "params": {}
        }
      }
    },

    "maxConcurrent": 2
  },

  "sessions": {
    "history": {
      "persist": true
    }
  },

  "tools": {
    "shell": {
      "enabled": true
    },
    "fs": {
      "enabled": true
    }
  }
}
```

---

## Model Strategy

### Primary Model

**openai-codex/gpt-5.4**

Use cases:
- Code generation
- Refactoring
- Automation
- Fast execution

---

### Fallback 1

**anthropic/claude-sonnet-4-6**

Use cases:
- Complex reasoning
- Multi-file analysis
- Architecture decisions

---

### Fallback 2

**openai/gpt-5-mini**

Use cases:
- Low-cost tasks
- Background processing

---

## Key Parameters

### Codex

```json
"transport": "auto"
```

- Automatically selects best communication channel

---

### Claude

```json
"thinking": "adaptive",
"context1m": false
```

- Adaptive reasoning depth
- Disables extended context to avoid rate limits in subscription mode

---

## Running OpenClaw

Start services:

```bash
openclaw gateway status
openclaw dashboard
```

Or initial setup:

```bash
openclaw onboard
```

---

## Integration with VS Code

No changes required in VS Code.

Existing setup:

- Claude Code extension
- Codex CLI / ChatGPT login

OpenClaw automatically reuses:

- Codex OAuth token
- Claude setup-token

---

## Recommended Workflow (ELIS Project)

### Role Distribution

| Component | Role |
|----------|------|
| Codex | Implementation engine |
| Claude | Reasoning / validation |
| OpenClaw | Orchestration |
| VS Code | Human supervision |

---

### Execution Flow

```
User request
   ↓
OpenClaw PM Agent
   ↓
Codex → implement
Claude → review
   ↓
Commit / output
```

---

## Limitations

### ChatGPT / Codex

- Subject to ChatGPT usage limits
- Not equivalent to API throughput

### Claude

- Setup-token may change or expire
- Dependent on Anthropic policy

---

## Security Notes

Do NOT:

- Copy browser cookies
- Scrape session tokens
- Intercept web traffic

Use only:

- Official OAuth (OpenAI)
- Setup-token (Claude)

---

## Summary

This configuration provides:

- Full OpenClaw operation without API keys
- Reuse of ChatGPT and Claude subscriptions
- Stable multi-agent architecture
- Compatibility with VS Code workflow

---

## Next Steps (Optional Enhancements)

- Add Telegram/Discord integration
- Add agent routing (PM / Implementer / Validator)
- Add Docker sandbox execution layer
- Add cost-aware routing policies

---

**End of Document**

