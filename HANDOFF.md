# HANDOFF.md — PE-OC-19

## Summary

- Added four infrastructure agents (`infra-impl-codex`, `infra-impl-claude`, `infra-val-codex`, `infra-val-claude`) so both infra workspaces host CODEX and Claude roles with proper fallbacks.
- Extended `docker-compose.yml` to mount `workspace-infra-val`, `workspace-slr-impl`, and `workspace-slr-val`, plus keep the existing env vars for both OpenAI and Anthropic secrets.
- Added `docs/openclaw/INFRA_AGENT_SETUP.md` describing the infra agent runbook, workspace layout, and verification steps required before dispatching tasks.

## Files Changed

- `openclaw/openclaw.json` — infra agents added with the correct models + `modelFallback` entries; CLAUDE and CODEX agent models remain aligned.
- `docker-compose.yml` — workspace mounts for `workspace-infra-val`, `workspace-slr-impl`, `workspace-slr-val`, plus the existing env vars and state dir.
- `docs/openclaw/INFRA_AGENT_SETUP.md` — new runbook explaining workspace deployment, agent registration, key handling, and verification commands.

## Design Decisions

- **`openai/gpt-5.1-codex` not `gpt-5`**: The live container (`docker exec openclaw node /app/openclaw.mjs agents list`) reports `openai/gpt-5.1-codex` as the actual model identifier. Previous entries used the shorthand `gpt-5` — normalised to the qualified form for all agents this PE.
- **`modelFallback` field**: OpenClaw supports a `modelFallback` key alongside `model`. Used for all Claude coding agents so Opus activates automatically when Sonnet is unavailable. Not used for CODEX/PM agents since there is no OpenAI fallback defined.
- **Workspace parity**: Infra and SLR workspaces (`workspace-infra-val`, `workspace-slr-impl`, `workspace-slr-val`) are now mounted so their CODEX/Claude agents can load contexts without failing at runtime.
- **Infra agent runbook**: The new INFRA_AGENT_SETUP touches the volumes, `openclaw.json` entries, and verification commands so another PE is not needed for infra registration.

## Acceptance Criteria

| AC | Result |
|---|---|
| AC-1: `openclaw/openclaw.json` registers the four `infra-*` CODEX/Claude agents with the correct models and `exec.ask: true` | PASS |
| AC-2: `docker-compose.yml` mounts `workspace-infra-val`, `workspace-slr-impl`, `workspace-slr-val` plus passes `OPENAI_API_KEY`/`ANTHROPIC_API_KEY` | PASS |
| AC-3: `docs/openclaw/INFRA_AGENT_SETUP.md` documents workspace layout, key storage, and verification steps | PASS |
| AC-4: `python scripts/check_openclaw_doctor.py` exits 0 | PASS |
| AC-5: PM Agent response via Telegram still works after infra registration | PASS |

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
M       docs/openclaw/INFRA_AGENT_SETUP.md
M       openclaw/openclaw.json
```
