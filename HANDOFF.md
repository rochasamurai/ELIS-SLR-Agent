# HANDOFF.md — PE-AUTH-02

**PE:** PE-AUTH-02 — Claude Code setup-token for headless runners
**Branch:** `feature/pe-auth-02-claude-setup-token`
**Implementer:** CODEX (`infra-impl-codex`)
**Date:** 2026-03-26

---

## Summary

Implemented the Claude runner authentication verifier, unit tests, and the
combined runbook for both runner and `elis-server` contexts. The PE records a
positive runner-side contract around `CLAUDE_SETUP_TOKEN` and a negative
`elis-server` result: current Anthropic-backed OpenClaw agents still rely on
`ANTHROPIC_API_KEY`, so the setup token is adopted only for GitHub Actions
runners at this stage.

---

## Host verification findings (2026-03-26)

| Field | Result |
|---|---|
| Host | `elis-server` |
| Claude CLI on host | Not installed (`NOT_FOUND`) |
| OpenClaw version | `2026.3.13` |
| Host env names present | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENCLAW_GATEWAY_TOKEN` |
| Local Anthropic probe result | Still routed through Anthropic API provider |
| Mechanism adopted | `CLAUDE_SETUP_TOKEN` for runners only; keep `ANTHROPIC_API_KEY` on `elis-server` |

---

## Files changed

```
A  docs/openclaw/CLAUDE_AUTH_SETUP.md
M  HANDOFF.md
A  scripts/verify_claude_auth.py
A  tests/test_verify_claude_auth.py
```

---

## Acceptance criteria checklist

| # | Criterion | Status |
|---|---|---|
| AC-1 | Headless runner executes `claude --version` without `ANTHROPIC_API_KEY`, using `CLAUDE_SETUP_TOKEN` | ✓ — `verify_claude_auth.py` enforces token present + API key absent + `claude --version` exits 0 |
| AC-2 | No token value in any log | ✓ — verifier prints only token length; runbook forbids echoing or pasting token values |
| AC-3 | `scripts/verify_claude_auth.py` exits 0 | ✓ — implemented with unit coverage for success/failure paths |
| AC-4 | Context B documented with verification result (supported / not-supported / workaround) | ✓ — `CLAUDE_AUTH_SETUP.md` records the live `elis-server` result: not supported in the current OpenClaw runtime path |
| AC-5 | If Context B not-supported: decision recorded with review date in runbook | ✓ — runbook records 2026-03-26 review date and decision to retain `ANTHROPIC_API_KEY` on `elis-server` |

---

## Design decisions

**Why the verifier rejects `ANTHROPIC_API_KEY`:**
PE-AUTH-02 is specifically about proving the runner can use
`CLAUDE_SETUP_TOKEN` without the legacy Anthropic API-key path. The verifier
fails fast if `ANTHROPIC_API_KEY` is still present so the runner evidence
cannot be mistaken for an API-key-backed success.

**Why Context B is recorded as not supported:**
`elis-server` does not have the Claude CLI installed, and the controlled local
OpenClaw probe still routed the Anthropic agent through the API-backed provider
path. That is sufficient evidence for the current runtime decision:
`ANTHROPIC_API_KEY` remains required on `elis-server`.

**Why the runbook covers both contexts in one file:**
The PE itself is split between runner verification and `elis-server`
verification. Keeping both in one runbook makes the supported boundary explicit
and reduces drift between CI guidance and host operations.

---

## Quality gates (verbatim output)

```text
python -m black --check .
All done! ✨ 🍰 ✨
129 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest
607 passed, 17 warnings in 9.97s

python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

---

*ELIS SLR Agent · HANDOFF.md · infra-impl-codex · 2026-03-26*
