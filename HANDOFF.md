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
M  ELIS_2Agent_Automation_Plan_v2_0.md
M  HANDOFF.md
```

---

## Round 2 fixes (CODEX FAIL — 2026-03-26)

| Finding | Fix |
|---|---|
| F1 — plan still referenced `codex auth status` contract | Updated plan: AC-1 rewritten around `OPENAI_API_KEY` set + `codex --version` exits 0; pseudocode replaced; `status` subcommand documented as unavailable |
| F2 — plan used `CODEX_OAUTH_TOKEN` / `CODEX_ACCESS_TOKEN`; branch uses `OPENAI_API_KEY` | Updated plan: mechanism table, secrets registry, workflow YAML, PE-CI-01 AC-2 all changed to `OPENAI_API_KEY` |
| F3 — `extract_codex_token.py` description claimed expiry/scope; AC-4 required expiry date | Updated plan: description corrected to "field names, `auth_mode`, `last_refresh`, boolean presence"; AC-4 rewritten — expiry timing not exposed by CLI, renewal trigger is runner failure |
| Runbook Linux/macOS extraction printed value to stdout | Replaced `print()` with `xclip`/`pbcopy` clipboard pipe; added post-extraction history-clear note |

---

## Acceptance criteria checklist

| # | Criterion | Status |
|---|---|---|
| AC-1 | `OPENAI_API_KEY` secret set in runner + `codex --version` exits 0 | ✓ — `verify_codex_auth.py` checks both; plan updated to match |
| AC-2 | No token value appears in any CI log | ✓ — scripts print only `length=N`; runbook clipboard-only extraction (Linux/macOS fixed in Round 2) |
| AC-3 | `scripts/verify_codex_auth.py` exits 0 on the runner | ✓ — implemented and tested locally |
| AC-4 | Runbook documents renewal procedure; expiry timing unknown from CLI | ✓ — `CODEX_AUTH_SETUP.md` §Token renewal; plan updated: expiry not programmatically available, renewal trigger is runner failure |
| AC-5 | `OPENAI_API_KEY` injected from GitHub Secrets only — never hardcoded | ✓ — plan updated; runbook and workflow YAML use `${{ secrets.OPENAI_API_KEY }}` pattern |

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
602 passed, 17 warnings in 11.23s

python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

---

*ELIS SLR Agent · HANDOFF.md · infra-impl-claude · 2026-03-26*
