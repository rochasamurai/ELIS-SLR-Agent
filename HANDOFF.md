# HANDOFF — PE-AGT-00 Ready Pending PO OAuth Confirmation

**Status:** Active PE opened; implementer start blocked pending PO pre-flight  
**Date:** 2026-04-26  
**Base branch:** main  
**Plan file:** `ELIS_MultiAgent_Implementation_Plan_v2_0.md`

---

## Current PE

- **PE:** `PE-AGT-00`
- **Title:** Model Authentication Setup (Codex + Claude Code)
- **Branch:** `feature/pe-agt-00-model-authentication-setup`
- **Implementer:** `infra-impl-a` (CODEX)
- **Validator:** `infra-val-b` (Claude Code)
- **Dependency:** none

---

## Acceptance Criteria

1. `scripts/verify_codex_auth.py` checks `~/.codex/auth.json` as the primary credential source.
2. `scripts/verify_codex_auth.py` falls back to `OPENAI_API_KEY` with a `WARN` line and exits 0 when the key is present.
3. `scripts/verify_codex_auth.py` exits 1 only when both OAuth credential and API key are absent.
4. `scripts/verify_claude_auth.py` checks `~/.claude/.credentials.json` for `claudeAiOauth` as the primary credential source.
5. `scripts/verify_claude_auth.py` falls back to `ANTHROPIC_API_KEY` with a `WARN` line and exits 0 when the key is present.
6. `scripts/verify_claude_auth.py` exits 1 only when both OAuth credential and API key are absent.
7. Tests cover OAuth-present, fallback-present, and both-absent paths for both verification scripts.
8. `docs/openclaw/AUTH_STRATEGY.md` documents OAuth-primary, API-key-fallback, why this contract exists, and how to re-run OAuth on elis-server.

---

## Notes for the Implementer

- **Do not start branch work yet.** The plan requires PO pre-flight completion before implementation begins.
- PO must run `claude` interactively on elis-server, complete login, then confirm `python scripts/verify_claude_auth.py` exits 0.
- PO must run `codex` interactively on elis-server, complete login, then confirm `python scripts/verify_codex_auth.py` exits 0.
- PM will notify the Implementer once Carlos posts both successful confirmations.
- This PE changes only the two auth verify scripts, their tests, and `docs/openclaw/AUTH_STRATEGY.md`.
- This PE does **not** change runner workflows or openclaw config.

---

## PM Note to PO

Before assigning the Implementer to begin work, please run the Claude Code and Codex OAuth logins on `elis-server` and confirm both verify scripts exit 0.
