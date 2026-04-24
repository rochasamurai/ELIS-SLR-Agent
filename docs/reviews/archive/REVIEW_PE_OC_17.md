# REVIEW_PE_OC_17.md — Validator Verdict

**PE:** PE-OC-17 · Live Telegram Integration
**Validator:** Claude Code (`prog-val-claude`)
**Date:** 2026-02-24
**PR:** #280 — `feature/pe-oc-17-live-telegram-integration` → `main`

---

### Verdict
FAIL

---

### Gate results
black: PASS
ruff: PASS
pytest: 547 passed, 17 warnings (pre-existing `utcnow` deprecation — tracked §11)
check_openclaw_doctor: PASS (exit 0)

---

### Scope
```
M	HANDOFF.md
M	docker-compose.yml
M	docs/openclaw/TELEGRAM_SETUP.md
M	openclaw/openclaw.json
M	scripts/check_openclaw_health.py
```
5 files. All are PE-OC-17 deliverables. No unrelated files detected.

---

### Required fixes

1. **[BLOCKING] HANDOFF.md "Files Changed" omits `docs/openclaw/TELEGRAM_SETUP.md`.**
   The PR diff shows 84 additions + 62 deletions in that file. AGENTS.md §5.1 step 7 requires a *complete* changed-file list. Add the missing entry with a brief description of what changed.

2. **[BLOCKING] `docs/openclaw/TELEGRAM_SETUP.md` Security notes contradict `openclaw/openclaw.json` and AC-4.**
   The Security notes state: *"The bot token and paired Telegram account ID must never be committed; they live only in host files."*
   But the plan (AC-4) and the committed `openclaw/openclaw.json` both mandate committing the real `accountId` (`8351383841`). Only the bot token is a secret credential and must not be committed. Correct the security note to read: *"The bot token must never be committed to the repo; it lives only in `~/.openclaw/.env` on the host. The paired Telegram account ID is committed in `openclaw/openclaw.json` as required by AC-4."*

---

### Non-blocking findings (advisory only — do not block merge if blocking items are fixed)

- **`openclaw/openclaw.json` `notes` field is stale.** Still says "Replace `<PO_TELEGRAM_ACCOUNT_ID>` with the paired Telegram user ID" — but the ID is already set. Update or remove.
- **PR title retains "WIP:" prefix** even though the PR is no longer a draft. Update to `feat(pe-oc-17): live telegram integration`.

---

### Evidence

```
# Scope diff (origin/main → feature branch)
$ git diff --name-status origin/main..origin/feature/pe-oc-17-live-telegram-integration
M       HANDOFF.md
M       docker-compose.yml
M       docs/openclaw/TELEGRAM_SETUP.md
M       openclaw/openclaw.json
M       scripts/check_openclaw_health.py

# Quality gates
$ python -m black --check .
All done! ✨ 🍰 ✨
116 files would be left unchanged.

$ python -m ruff check .
All checks passed!

$ python -m pytest --tb=no 2>&1 | tail -3
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
547 passed, 17 warnings in 10.29s

# AC-2: health probe exits 0
$ python scripts/check_openclaw_health.py
OpenClaw WebSocket handshake received unexpected response:  … still non-blocking in CI.
exit=0

# AC-4: accountId in openclaw.json
$ git show origin/feature/pe-oc-17-live-telegram-integration:openclaw/openclaw.json | grep accountId
        "accountId": "8351383841"
# Real PO Telegram user ID set (not placeholder). AC-4 PASS.

# AC-5: openclaw doctor
$ python scripts/check_openclaw_doctor.py
OK: openclaw doctor configuration meets expected policies
exit=0

# docker-compose.yml — AC-1 port mapping and bind mode
$ git show origin/feature/pe-oc-17-live-telegram-integration:docker-compose.yml
ports:
  - "127.0.0.1:18789:18789"
command:
  - node
  - openclaw.mjs
  - gateway
  - --allow-unconfigured
  - --bind
  - lan
# Port remap and --bind lan confirmed. AC-1 PASS.

# Blocking finding #1 — HANDOFF Files Changed section (verbatim)
## Files Changed
- `docker-compose.yml` (port remap, lan bind, environment variables)
- `scripts/check_openclaw_health.py` (WebSocket probe + formatting)
- `openclaw/openclaw.json` (Telegram binding uses the real PO Telegram user ID)
# docs/openclaw/TELEGRAM_SETUP.md is ABSENT from this list.

# Blocking finding #2 — TELEGRAM_SETUP.md security note (verbatim)
## Security notes
- The bot token and paired Telegram account ID must never be committed;
  they live only in host files.
# But openclaw/openclaw.json commits accountId: "8351383841" per AC-4.
# Contradiction — security note must be corrected.
```

---

### AC summary

| AC | Description | Result |
|---|---|---|
| AC-1 | `docker compose up -d`; gateway log shows `--bind lan` / `ws://0.0.0.0:18789` | PASS (config verified) |
| AC-2 | `check_openclaw_health.py` exits 0 (WebSocket probe) | PASS (exits 0, non-blocking design) |
| AC-3 | PO sends `status`; PM Agent responds | PASS (HANDOFF evidence accepted) |
| AC-4 | `openclaw.json` `accountId` = real PO Telegram ID | PASS (`8351383841` set) |
| AC-5 | `check_openclaw_doctor.py` exits 0 | PASS |

---

## Re-validation — Round 2 — 2026-02-24

### Verdict
PASS

### Fixes verified

1. **HANDOFF.md "Files Changed" — RESOLVED.** `docs/openclaw/TELEGRAM_SETUP.md` entry now present: `(updated runbook + clarified security guidance)`.
2. **TELEGRAM_SETUP.md security note contradiction — RESOLVED.** Note now reads: *"The bot token must stay on the host and **never** be committed. The paired Telegram account ID is safe to record inside `openclaw/openclaw.json` so the binding survives container restarts."* Consistent with AC-4 and `openclaw/openclaw.json`.

### Gate results (re-run)
black: PASS
ruff: PASS
pytest: 547 passed, 17 warnings (pre-existing — unchanged)

### Scope (re-check)
```
M	HANDOFF.md
A	REVIEW_PE_OC_17.md
M	docker-compose.yml
M	docs/openclaw/TELEGRAM_SETUP.md
M	openclaw/openclaw.json
M	scripts/check_openclaw_health.py
```
6 files. 5 implementation + 1 Validator-owned REVIEW. Correct.

### Required fixes
None.

### Evidence

```
# Re-validation quality gates
$ python -m black --check . && python -m ruff check .
All done! ✨ 🍰 ✨
116 files would be left unchanged.
All checks passed!

$ python -m pytest --tb=no 2>&1 | tail -2
547 passed, 17 warnings in 7.76s

# Fix #1 — HANDOFF Files Changed (updated, verbatim)
## Files Changed
- `docker-compose.yml` (port remap, lan bind, environment variables)
- `scripts/check_openclaw_health.py` (WebSocket probe + formatting)
- `openclaw/openclaw.json` (Telegram binding uses the real PO Telegram user ID, resaved by the agent update)
- `docs/openclaw/TELEGRAM_SETUP.md` (updated runbook + clarified security guidance)

# Fix #2 — TELEGRAM_SETUP.md Security notes (updated, verbatim)
- The bot token must stay on the host and **never** be committed.
  The paired Telegram account ID is safe to record inside openclaw/openclaw.json
  so the binding survives container restarts.

# Scope diff
$ git diff --name-status origin/main..origin/feature/pe-oc-17-live-telegram-integration
M       HANDOFF.md
A       REVIEW_PE_OC_17.md
M       docker-compose.yml
M       docs/openclaw/TELEGRAM_SETUP.md
M       openclaw/openclaw.json
M       scripts/check_openclaw_health.py
```
