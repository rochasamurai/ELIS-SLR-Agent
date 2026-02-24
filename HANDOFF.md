# HANDOFF.md — PE-OC-18

## Summary

- Promoted `pm` agent model from `claude-opus-4-6` to `openai/gpt-5.1-codex` (full OpenClaw model identifier, matching the live container's `main` agent).
- Registered four new `prog-*` worker agents (`prog-impl-codex`, `prog-impl-claude`, `prog-val-codex`, `prog-val-claude`) in `openclaw/openclaw.json`.
- Updated all existing `slr-*-claude` agents from `claude-opus-4-6` to `anthropic/claude-sonnet-4-6` (with `anthropic/claude-opus-4-6` fallback) — corrected model identifier format and applied Sonnet-primary tier policy.
- Updated all `*-codex` agent models from `gpt-5` shorthand to `openai/gpt-5.1-codex` (confirmed live model name from `docker exec openclaw node /app/openclaw.mjs agents list`).
- Added `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` env vars to `docker-compose.yml` (read from host `~/.openclaw/.env`).
- Created `docs/openclaw/CODEX_AGENT_SETUP.md` — model tier policy, key storage, agent verification, and troubleshooting runbook.

## Files Changed

- `openclaw/openclaw.json` — `pm` model updated to `openai/gpt-5.1-codex`; 4 `prog-*` agents added; `slr-*-claude` models corrected to Sonnet; all `*-codex` model identifiers normalised to `openai/gpt-5.1-codex`
- `docker-compose.yml` — `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` added to environment block
- `docs/openclaw/CODEX_AGENT_SETUP.md` — new runbook (model tier policy, key storage, verification steps)

## Design Decisions

- **`openai/gpt-5.1-codex` not `gpt-5`**: The live container (`docker exec openclaw node /app/openclaw.mjs agents list`) reports `openai/gpt-5.1-codex` as the actual model identifier. Previous entries used the shorthand `gpt-5` — normalised to the qualified form for all agents this PE.
- **`modelFallback` field**: OpenClaw supports a `modelFallback` key alongside `model`. Used for all Claude coding agents so Opus activates automatically when Sonnet is unavailable. Not used for CODEX/PM agents since there is no OpenAI fallback defined.
- **`ANTHROPIC_API_KEY` added now**: Claude coding agents (`*-impl-claude`, `*-val-claude`) require it at runtime. Adding it to `docker-compose.yml` now avoids a separate PE when those agents are first dispatched.

## Acceptance Criteria

| AC | Result |
|---|---|
| AC-1: `pm` agent model is `openai/gpt-5.1-codex` | PASS |
| AC-2: all 4 `prog-*` agents registered; claude agents use `anthropic/claude-sonnet-4-6` with fallback; codex agents use `openai/gpt-5.1-codex`; all `exec.ask: true` | PASS |
| AC-3: `slr-impl-claude` and `slr-val-claude` updated to `anthropic/claude-sonnet-4-6` with fallback | PASS |
| AC-4: `docker-compose.yml` passes `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` | PASS |
| AC-5: `python scripts/check_openclaw_doctor.py` exits 0 | PASS |
| AC-6: `docs/openclaw/CODEX_AGENT_SETUP.md` documents key storage, model tier policy, verification | PASS |

## Validation Commands

```text
python -m black --check .
All done! ✨ 🍰 ✨
116 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest --tb=no 2>&1 | tail -2
547 passed, 17 warnings in 10.43s

python scripts/check_openclaw_doctor.py
OK: openclaw doctor configuration meets expected policies
exit=0

git diff --name-status origin/main..HEAD
M       HANDOFF.md
M       docker-compose.yml
M       docs/openclaw/CODEX_AGENT_SETUP.md
M       openclaw/openclaw.json
```
