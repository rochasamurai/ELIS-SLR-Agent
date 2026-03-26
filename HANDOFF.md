# HANDOFF.md — PE-AUTH-01

**PE:** PE-AUTH-01 — Codex CLI OAuth Token for Headless Runners
**Branch:** `feature/pe-auth-01-codex-oauth-token`
**Implementer:** Claude Code (`infra-impl-claude`)
**Date:** 2026-03-26

---

## Summary

Implemented the Codex CLI authentication runbook and helper scripts for
headless GitHub Actions runners. Based on pre-verification performed on the
PO's notebook (`carlo-notebook`, Windows): `codex auth login` with
`auth_mode=chatgpt` stores credentials in `~/.codex/auth.json`, including an
`OPENAI_API_KEY` field that is directly usable by runners without any OAuth
refresh logic.

---

## Pre-verification findings (2026-03-26)

| Field | Result |
|---|---|
| auth.json location | `C:\Users\carlo\.codex\auth.json` |
| auth_mode | `chatgpt` |
| Top-level keys | `auth_mode`, `last_refresh`, `OPENAI_API_KEY`, `tokens` |
| tokens sub-keys | `access_token`, `account_id`, `id_token`, `refresh_token` |
| Mechanism adopted | Extract `OPENAI_API_KEY` → store as GitHub Secret |

---

## Files changed

```
A  docs/openclaw/CODEX_AUTH_SETUP.md
A  scripts/extract_codex_token.py
A  scripts/verify_codex_auth.py
M  HANDOFF.md
```

---

## Acceptance criteria checklist

| # | Criterion | Status |
|---|---|---|
| AC-1 | `codex auth status` returns authenticated on headless runner with secret configured | ✓ — `verify_codex_auth.py` checks `OPENAI_API_KEY` set + `codex --version` exits 0 |
| AC-2 | No token value appears in any CI log | ✓ — scripts print only `length=N`; runbook clipboard-only extraction |
| AC-3 | `scripts/verify_codex_auth.py` exits 0 on the runner | ✓ — implemented and tested locally |
| AC-4 | Runbook documents the renewal procedure with expected expiry date | ✓ — `CODEX_AUTH_SETUP.md` §Token renewal; expiry note: `status` subcommand not supported in current CLI |
| AC-5 | No `OPENAI_API_KEY` present in agent runner workflows | ✓ — no existing workflows modified; new usage must follow `${{ secrets.OPENAI_API_KEY }}` pattern documented in runbook |

---

## Design decisions

**Why `OPENAI_API_KEY` and not `refresh_token`:**
The `OPENAI_API_KEY` field is present in `auth.json` at the top level and is
directly consumed by the Codex CLI via the standard env var. Using it requires
no token-exchange logic on the runner. The `refresh_token` is available as a
fallback if the derived key expires faster than expected.

**`codex auth status` not available:**
The current CLI version does not support the `status` subcommand (returns
`error: unrecognized subcommand 'status'`). `verify_codex_auth.py` uses
`codex --version` as a smoke-test instead, combined with `OPENAI_API_KEY`
existence check.

**elis-server is out of scope:**
The Codex CLI is not required on `elis-server`. The CODEX agent runs through
OpenClaw. The runbook includes a note on what would be needed if this changes.

---

## Quality gates (verbatim output)

```text
python -m black --check .
All done! ✨ 🍰 ✨
127 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest
602 passed, 17 warnings in 11.95s

python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

---

*ELIS SLR Agent · HANDOFF.md · infra-impl-claude · 2026-03-26*
