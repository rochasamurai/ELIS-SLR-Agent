# HANDOFF.md — PE-OC-20

## Summary

- Extended `scripts/deploy_openclaw_workspaces.sh` to copy `openclaw/openclaw.json` → `~/.openclaw/openclaw.json` and print a `docker compose down && docker compose up -d` restart reminder after syncing workspaces.
- Added `scripts/check_openclaw_config_sync.py` — compares declared agent IDs in `openclaw/openclaw.json` against the live container's agent list via `docker exec`; exits 1 on mismatch, exits 0 when in sync or Docker unreachable (non-blocking).
- Added `tests/test_check_openclaw_config_sync.py` — 9 unit tests covering in-sync, missing-agent, Docker-not-found, container-not-running, and timeout cases; all pass.
- Added CI job `openclaw-config-sync-check` to `.github/workflows/ci.yml` — non-blocking (Docker unavailable in GitHub Actions); serves as a local-dev gate when PM runs it on the host after deployment.
- Added `docs/openclaw/DEPLOYMENT.md` — full deployment runbook: why manual deployment is needed, 4-step procedure (deploy script → restart → sync verify → Telegram confirm), and troubleshooting table.

## Files Changed

- `.github/workflows/ci.yml` — `openclaw-config-sync-check` job added
- `docs/openclaw/DEPLOYMENT.md` — new deployment runbook
- `scripts/check_openclaw_config_sync.py` — new sync verifier
- `scripts/deploy_openclaw_workspaces.sh` — config copy step added
- `tests/test_check_openclaw_config_sync.py` — 9 new unit tests

## Design Decisions

- **Non-blocking in CI**: `check_openclaw_config_sync.py` follows the same pattern as `check_openclaw_health.py` — exits 0 when Docker is unreachable. This keeps CI green while providing a meaningful local gate.
- **Exit 1 on local mismatch**: When Docker IS available (on the host), the script properly exits 1 if declared agents are absent from the live container, guiding PM to run the deploy script.
- **Deploy script extended, not replaced**: The existing `deploy_openclaw_workspaces.sh` is the natural entry point PM already knows. Adding the config copy step here keeps the deployment atomic — workspaces and config are always in sync together.
- **No container restart in script**: The script prints the restart command but does not run it automatically — restart is a deliberate action that takes the live PM Agent offline.

## Acceptance Criteria

| AC | Result |
|---|---|
| AC-1: `deploy_openclaw_workspaces.sh` copies `openclaw/openclaw.json` → `~/.openclaw/openclaw.json` and prints restart reminder | PASS |
| AC-2: `check_openclaw_config_sync.py` exits 1 on missing agents; exits 0 when in sync; exits 0 when Docker unreachable | PASS |
| AC-3: CI job `openclaw-config-sync-check` exits 0 in CI (non-blocking) | PASS |
| AC-4: `tests/test_check_openclaw_config_sync.py` — 9 tests all pass | PASS |
| AC-5: `docs/openclaw/DEPLOYMENT.md` documents deploy + verify procedure | PASS |

## Validation Commands

```text
python -m black --check .
All done! ✨ 🍰 ✨
118 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest --tb=no 2>&1 | grep -E "passed|failed"
556 passed, 17 warnings in 6.89s

python -m pytest tests/test_check_openclaw_config_sync.py -v 2>&1 | tail -3
tests/test_check_openclaw_config_sync.py .........   [100%]
9 passed in 0.14s

python scripts/check_openclaw_doctor.py
OK: openclaw doctor configuration meets expected policies
exit=0

python scripts/check_openclaw_config_sync.py
Declared agents (13): pm, slr-impl-codex, slr-impl-claude, slr-val-codex, slr-val-claude, prog-impl-codex, prog-impl-claude, prog-val-codex, prog-val-claude, infra-impl-codex, infra-impl-claude, infra-val-codex, infra-val-claude
Live agents (2): main, pm
FAIL: 12 agent(s) declared in openclaw.json but missing from live container: ...
exit=1  (expected — container is stale; script correctly detects the gap this PE closes)

git diff --name-status origin/main..HEAD
M       .github/workflows/ci.yml
A       docs/openclaw/DEPLOYMENT.md
M       HANDOFF.md
A       scripts/check_openclaw_config_sync.py
M       scripts/deploy_openclaw_workspaces.sh
A       tests/test_check_openclaw_config_sync.py
```
