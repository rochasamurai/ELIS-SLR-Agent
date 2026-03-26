# Claude Code Authentication Setup

> Runbook for PE-AUTH-02: runner-side `CLAUDE_SETUP_TOKEN` verification and the
> current OpenClaw / `elis-server` decision for Anthropic-backed agents.

---

## Background

PE-AUTH-02 separates two different authentication contexts:

1. **Context A — GitHub Actions runners**
   Headless verification for Claude Code using `CLAUDE_SETUP_TOKEN`.
2. **Context B — OpenClaw on `elis-server`**
   Verification of whether Anthropic-backed OpenClaw agents can stop relying on
   `ANTHROPIC_API_KEY`.

The accepted ELIS outcome for this PE is:

- **Context A:** implement and verify a token-only runner check around
  `CLAUDE_SETUP_TOKEN`.
- **Context B:** document the live result on `elis-server`, including the case
  where the current runtime still requires `ANTHROPIC_API_KEY`.

---

## Context A — GitHub Actions runners

### Preconditions

- Claude Code CLI installed on the operator machine that generates the token
- Claude Code CLI installed on the target runner
- A valid Claude subscription or Anthropic billing-backed login for the
  operator machine

Anthropic's official Claude Code setup documentation covers installation and
basic authentication for the CLI. For Linux runners, the documented install
command is:

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version
claude doctor
```

Source: Anthropic Claude Code setup documentation
(`https://docs.anthropic.com/en/docs/claude-code/setup`)

### One-time operator flow

On a machine where the Claude Code CLI is installed and authenticated, generate
the headless token:

```bash
claude setup-token
```

Store the resulting token as the GitHub Actions repository secret
`CLAUDE_SETUP_TOKEN`.

> Do not paste the token into chat, PR comments, commit messages, terminal
> history screenshots, or HANDOFF/REVIEW files.

### Repository secret

1. Navigate to the repository → **Settings** → **Secrets and variables** →
   **Actions**
2. Click **New repository secret**
3. Name: `CLAUDE_SETUP_TOKEN`
4. Value: paste the generated token
5. Click **Add secret**

### Runner verification contract

The runner must verify the token-only path with:

```yaml
- name: Install Claude Code CLI
  run: curl -fsSL https://claude.ai/install.sh | bash

- name: Verify Claude auth
  env:
    CLAUDE_SETUP_TOKEN: ${{ secrets.CLAUDE_SETUP_TOKEN }}
  run: python scripts/verify_claude_auth.py
```

`scripts/verify_claude_auth.py` enforces:

- `CLAUDE_SETUP_TOKEN` present
- `ANTHROPIC_API_KEY` absent
- `claude` on `PATH`
- `claude --version` exits 0

### Security rule

The verifier prints only token length, never token value. The secret must never
be echoed in workflow logs.

---

## Context B — OpenClaw on `elis-server`

### Live verification result

**Review date:** 2026-03-26  
**Host:** `elis-server`  
**OpenClaw version:** `2026.3.13`

#### Evidence summary

| Check | Result |
|---|---|
| `claude` CLI installed on `elis-server` | No — `command -v claude` returned `NOT_FOUND` |
| OpenClaw Anthropic agents present | Yes — `infra-impl-claude`, `infra-val-claude`, etc. |
| Host env still includes `ANTHROPIC_API_KEY` | Yes |
| Token-only local probe | Not supported in current runtime path |

#### Commands used

```bash
ssh elis-server "command -v claude || which claude || echo NOT_FOUND"
ssh elis-server "openclaw --version || true"
ssh elis-server "grep -E '^(ANTHROPIC_API_KEY|OPENAI_API_KEY|OPENCLAW_GATEWAY_TOKEN)=' ~/.openclaw/.env | cut -d= -f1"
ssh elis-server "openclaw agents list"
ssh elis-server "bash -lc 'env -u ANTHROPIC_API_KEY CLAUDE_SETUP_TOKEN=dummy openclaw agent --local --agent infra-impl-claude --message ping --timeout 10 --json'"
```

#### Observed behaviour

The token-only OpenClaw probe still executed the Anthropic provider path and
returned:

```text
LLM request rejected: Your credit balance is too low to access the Anthropic API.
...
"provider": "anthropic",
"model": "claude-sonnet-4-6"
```

This shows that the current OpenClaw local Anthropic agent path on
`elis-server` is still API-backed and does **not** switch to a Claude
CLI/setup-token path merely because `CLAUDE_SETUP_TOKEN` is present.

### Decision

**Current decision (PE-AUTH-02):**
`ANTHROPIC_API_KEY` remains required on `elis-server` for Anthropic-backed
OpenClaw agents.

`CLAUDE_SETUP_TOKEN` is adopted **only for GitHub Actions runners** in Context A.

### Review trigger

Revisit this decision only if one of the following changes:

- OpenClaw adds documented support for Claude Code setup-token authentication
  for Anthropic-backed agents
- Claude Code adds a documented token-to-API bridge suitable for unattended
  server use
- ELIS adopts a different Anthropic backend (for example Bedrock/Vertex) for
  the affected agents

Until then, `ANTHROPIC_API_KEY` must remain in the host-side OpenClaw
environment for Claude-backed agents on `elis-server`.

---

## Troubleshooting

| Symptom | Meaning | Action |
|---|---|---|
| `FAIL: CLAUDE_SETUP_TOKEN is not set` | Runner secret missing | Add `CLAUDE_SETUP_TOKEN` to GitHub Actions secrets |
| `FAIL: ANTHROPIC_API_KEY is set in environment` | Runner still using legacy API-key path | Remove `ANTHROPIC_API_KEY` from the runner job environment for PE-AUTH-02 verification |
| `FAIL: 'claude' CLI not found on PATH` | Runner missing Claude Code CLI | Install Claude Code with the official Anthropic installer before running the verifier |
| `claude --version` exits non-zero | CLI install or login problem | Reinstall/update Claude Code and regenerate the setup token if needed |
| `elis-server` Anthropic agent still hits API billing | Current runtime is still API-key based | Keep `ANTHROPIC_API_KEY`; this is the accepted PE-AUTH-02 result |

---

*ELIS SLR Agent · docs/openclaw/CLAUDE_AUTH_SETUP.md · PE-AUTH-02 · 2026-03-26*
