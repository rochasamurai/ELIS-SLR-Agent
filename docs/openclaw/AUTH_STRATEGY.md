# OpenClaw Authentication Strategy

## Purpose

OpenClaw agent authentication on `elis-server` follows a simple resilience rule:

1. **OAuth credential files are the primary path.**
2. **Environment-variable API keys are the documented fallback.**

This keeps the preferred interactive login flow in place while still allowing the host
to verify provider access when OAuth has not yet been refreshed.

## Contract

- `scripts/verify_codex_auth.py` checks `~/.codex/auth.json` first.
  - If that file is absent, unreadable, or does not contain OAuth markers, the script falls back to `OPENAI_API_KEY`.
  - If the fallback is used, the script exits `0` and prints a `WARN:` line.
  - The script exits `1` only when neither a valid OAuth state nor `OPENAI_API_KEY` is available.
- `scripts/verify_claude_auth.py` checks `~/.claude/.credentials.json` first.
  - OAuth is valid when the file contains `claudeAiOauth`.
  - If OAuth cannot be verified, the script falls back to `ANTHROPIC_API_KEY`.
  - If the fallback is used, the script exits `0` and prints a `WARN:` line.
  - The script exits `1` only when neither a valid OAuth state nor `ANTHROPIC_API_KEY` is available.
- The verify scripts must never print token values, API keys, or secret file contents.

## Why this exists

`elis-server` is the control host for agent operations. It must be able to confirm that
provider authentication is usable without weakening secret handling.

Using OAuth as the default path preserves the intended interactive login model for both
Codex and Claude Code. Allowing an API-key fallback means health checks and PE
pre-flight checks can still succeed when OAuth has not yet been re-run.

## Re-running OAuth on `elis-server`

When OAuth needs to be refreshed:

### Claude Code

1. Run `claude` interactively on `elis-server`.
2. Complete the login flow.
3. Confirm that `~/.claude/.credentials.json` contains `claudeAiOauth`.
4. Re-run `python scripts/verify_claude_auth.py` and confirm exit code `0`.

### Codex

1. Run `codex` interactively on `elis-server`.
2. Complete the login flow.
3. Confirm that `~/.codex/auth.json` exists.
4. Re-run `python scripts/verify_codex_auth.py` and confirm exit code `0`.

## Operational notes

- The presence of a provider CLI on `PATH` is informational for these checks, not a blocker on its own.
- Fallback warnings are expected when API keys are being used instead of OAuth.
- Use the fallback only as a resilience path; restore OAuth when practical.
- Never paste secret values into logs, HANDOFF files, PR bodies, or review comments.
