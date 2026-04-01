# ELIS TODO — Improvements Backlog

Items that are known limitations or future improvements, not blocking current workflow.

---

## CI / Bot automation

### AUTO-02 — gate-1 commit status lost on branch update

**Status:** Open
**Priority:** Medium (manual workaround: re-post via `gh api` after every branch update)
**Logged:** 2026-04-01

**Description:**
`gate-1` is a required branch-protection status posted as a commit status on a specific
SHA. Every time the feature branch is updated (GitHub "Update branch" button or
`gh api .../update-branch`), a new merge commit is created with a new SHA — the
`gate-1` status on the old SHA is no longer visible to branch protection, which resets
it to "Expected — Waiting for status to be reported".

**Impact:**
Manual `gh api .../statuses/$HEAD` call required after every branch update. Observed on
PR #306, #308, and #309.

**Resolution:**
PE-AUTO-06 (PE Sequencer) posts `gate-1` as part of the automatic advance workflow.
Once PE-AUTO-06 is merged, the sequencer will always post `gate-1` on the correct HEAD
immediately after branch operations, eliminating the manual step.

---

### AUTO-01 — Live API auth verification for Codex and Claude Code tokens

**Status:** Open
**Priority:** Medium (Level 1 structural checks pass; Level 2 live auth not yet implemented)
**Logged:** 2026-03-27
**Parent PE:** PE-AUTO-01

**Description:**
`verify_codex_auth.py` and `verify_claude_auth.py` confirm secrets are set and CLIs are
installed (`--version`), but do not make authenticated API calls. A token that is present
but revoked or expired would pass the current checks.

**Recommended fix (PE-AUTO-02):**
Add a `verify-live-auth` job to `bot-auth-verify.yml` triggered only on `workflow_dispatch`:

```yaml
verify-live-auth:
  name: Live auth smoke test (manual only)
  if: github.event_name == 'workflow_dispatch'
  steps:
    - name: Claude live check
      env:
        CLAUDE_SETUP_TOKEN: ${{ secrets.CLAUDE_SETUP_TOKEN }}
      run: echo "ok" | claude -p "Reply with the single word: authenticated"
    - name: Codex live check
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: echo "ok" | codex -q "Reply with the single word: authenticated"
```

Run manually after initial setup and after every token renewal.

**References:**
- `docs/openclaw/BOT_ACCOUNTS_SETUP.md` — Step 8, PAT renewal section
- `docs/openclaw/CLAUDE_AUTH_SETUP.md` — runner auth section
- HANDOFF.md (PE-AUTO-01) — Design decisions § AC-3

---

## OpenClaw / elis-server

### DISCORD-01 — Discord server channel messages not received by PM Agent

**Status:** Open
**Priority:** Low (DMs work; server channels are not part of current workflow)
**Logged:** 2026-03-22

**Description:**
Messages posted in Discord server channels (e.g. `#general`) are not received by ELIS PM Agent. Only DMs work.

**Root cause:**
OpenClaw is not requesting the `MESSAGE_CONTENT` privileged intent in its Discord Gateway connection, despite the intent being enabled in the Discord Developer Portal. OpenClaw logs report `intents:content=limited` on every startup cycle.

**Impact:**
- Bot ignores messages in `#general` and other server channels.
- DM communication with PM Agent (the primary workflow) is unaffected.

**Possible fixes:**
1. Check if OpenClaw has a config key (e.g. `channels.discord.intents`) to explicitly request `MESSAGE_CONTENT`, `GUILD_MEMBERS`, and `PRESENCE` at the Gateway level.
2. File a bug report with the OpenClaw project if no config key exists.

---

### DISCORD-02 — Discord Gateway cycling every 10 minutes

**Status:** Open
**Priority:** Low (bot reconnects automatically; DMs are not lost)
**Logged:** 2026-03-22

**Description:**
The Discord Gateway WebSocket disconnects approximately every 10 minutes. The health-monitor restarts the channel, and `gatewayConnected=true` is restored within ~2 seconds. No messages are lost during this window for DM workflows.

**Root cause:**
Unknown. Suspected keepalive / heartbeat issue in this version of OpenClaw running in a Docker container. May be related to the limited intents above.

**Possible fixes:**
1. Investigate OpenClaw heartbeat config.
2. Check if enabling full privileged intents (DISCORD-01) resolves the cycling.
3. Upgrade OpenClaw image if a newer version addresses gateway stability.

---
