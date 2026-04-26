# OpenClaw Auth Strategy

## Purpose

OpenClaw agents on `elis-server` use a two-path authentication contract:

1. **OAuth is the primary path** for the provider-backed credential file.
2. **Environment-variable API keys are the fallback path** when OAuth credentials are unavailable.

This keeps the control host stable while still allowing valid cloud auth to work without local browser tooling on the server.

## Contract

- Prefer OAuth-backed credentials first.
- If OAuth credentials are missing or unreadable, fall back to the documented API key.
- The verify scripts should exit `0` when either valid path is present.
- The verify scripts should exit `1` only when both paths are unavailable or invalid.
- No token or secret values should ever be printed.

## Why this exists

`elis-server` is a control and validation host, not the place where every provider CLI must be installed.

The auth check therefore needs to answer one question only:

> Is the provider auth state usable right now?

It should not require local CLI installation just to confirm that auth exists.

## How to re-run OAuth on `elis-server`

When OAuth credentials need to be refreshed:

1. Use a machine with browser access to complete the provider's browser-based OAuth flow.
2. Copy or refresh the resulting credential state into the documented local file or secret source.
3. Re-run the relevant verify script on `elis-server`.
4. Confirm the script exits `0`.

## Verification targets

- Codex auth state is checked by `scripts/verify_codex_auth.py`.
- Claude auth state is checked by `scripts/verify_claude_auth.py`.

Both scripts should accept either valid OAuth credentials or the documented API-key fallback.

## Operational notes

- Treat missing provider CLIs on `elis-server` as informational, not as a failure by itself.
- Keep any provider-specific setup on browser-capable machines or in the secret source.
- Do not expose secret material in logs, PR comments, or test output.
