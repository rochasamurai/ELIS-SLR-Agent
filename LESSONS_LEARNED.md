# LESSONS_LEARNED.md — Agent Error Log

Both agents read this file at Step 0 (after `AGENTS.md`).
Each entry records an error pattern observed during the PE-OC series,
the rule added to prevent recurrence, and how it was detected.

---

## LL-01 — PR opened before HANDOFF committed

| Field | Value |
|---|---|
| First seen | PE-OC-08 |
| Agent | CODEX |
| AGENTS.md rule | §2.7 — HANDOFF.md must be committed before `git push` and PR creation |

**Error:** PR was opened on the feature branch before `HANDOFF.md` was committed. Gate 1 CI fired on a branch with no Status Packet.

**Root cause:** Implementer pushed after implementation commits but before writing HANDOFF, treating HANDOFF as an afterthought rather than a required deliverable.

**Detection:** Gate 1 `check_status_packet.py` failed — `## Status Packet` section absent.

**Rule added:** §2.7 and §8 do-not: *"Do not open a final (ready) PR before HANDOFF.md is committed on the branch."*

---

## LL-02 — Fabricated test counts — no pasted output

| Field | Value |
|---|---|
| First seen | PE-OC-13 |
| Agent | CODEX |
| AGENTS.md rule | §2.4 — every claim must be supported by pasted command output |

**Error:** HANDOFF claimed "+8 new tests" with no corresponding new test files. Test count in Status Packet did not match actual pytest output.

**Root cause:** Long session context drift — agent generated plausible-sounding numbers without running the command.

**Detection:** Validator ran `pytest` independently; count did not match HANDOFF claim. No new test files in scope diff.

**Rule added:** §2.4 evidence-first: *"Within a session, each step must be confirmed with pasted command output before marking it complete."*

---

## LL-03 — Duplicate YAML job key (last-wins silent drop)

| Field | Value |
|---|---|
| First seen | PE-OC-13 |
| Agent | CODEX |
| AGENTS.md rule | §5.1 — scope gate before every commit |

**Error:** `ci.yml` contained two `slr-quality-check:` job keys. GitHub Actions (js-yaml) uses last-wins semantics — the first job definition was silently dropped, meaning the CI job ran from the wrong definition.

**Root cause:** Iterative edits appended a second job block without removing the first. Scope gate was not run before committing.

**Detection:** Validator ran `grep -c "slr-quality-check:" .github/workflows/ci.yml` — returned 2.

**Rule added:** Pre-commit scope gate in §5.1; mid-session checkpoint §2.9.

---

## LL-04 — Stale HANDOFF HEAD SHA

| Field | Value |
|---|---|
| First seen | PE-OC-13 |
| Agent | CODEX |
| AGENTS.md rule | §6.2 — Status Packet §6.2 must show `git rev-parse HEAD` output |

**Error:** HANDOFF §6.2 showed a HEAD SHA that did not match the actual branch tip. Validator could not reconcile reported state with actual commit history.

**Root cause:** HANDOFF was written from memory / earlier session state rather than from live command output.

**Detection:** Validator ran `git rev-parse HEAD` on the branch — SHA did not match HANDOFF §6.2.

**Rule added:** Status Packet §6.2 must paste verbatim output of `git rev-parse HEAD` and `git log -5`.

---

## LL-05 — PE skipped in registry

| Field | Value |
|---|---|
| First seen | PE-OC-13 → PE-OC-14 transition |
| Agent | PM (registry maintenance error) |
| AGENTS.md rule | §5.1 — CURRENT_PE.md must be updated before agents start |

**Error:** After PE-OC-13 merged, CURRENT_PE.md was advanced directly to PE-OC-15, skipping PE-OC-14 entirely. PE-OC-15 depended on PE-OC-14, so the dependency chain was broken.

**Root cause:** PM incremented PE number without checking the plan's dependency table.

**Detection:** PM review of plan identified PE-OC-14 as a prerequisite for PE-OC-15 with no registry entry.

**Rule added:** Check plan dependency table before updating Current PE field in CURRENT_PE.md.

---

## LL-06 — New AGENTS.md rules not followed mid-session

| Field | Value |
|---|---|
| First seen | PE-OC-14 → PE-OC-15 transition |
| Agent | CODEX |
| AGENTS.md rule | §5.1 Progress Tracking — TodoWrite rule applies to both agents |

**Error:** AGENTS.md was updated with draft PR, milestone comments, and TodoWrite rules (PR #277). CODEX's next session did not follow them because the "Tool note" label read "Claude Code" only, and CODEX interpreted it as not applying to itself.

**Root cause:** Label `Tool note — Claude Code:` was too narrow; CODEX correctly (but unfortunately) excluded itself.

**Detection:** PM observed CODEX's todo list showing all tasks as `pending` while actively working; no draft PR opened at first commit.

**Rule added:** Label changed to `Tool note (both agents):` in §5.1 and §5.2 Progress Tracking.

---

## LL-07 — Host prerequisites assumed but not scoped

| Field | Value |
|---|---|
| First seen | PE-OC-15 |
| Agent | Plan (scoping omission) |
| AGENTS.md rule | §3.4 — verify host prerequisites before running discovery probes |

**Error:** PE-OC-15 required `docker pull ghcr.io/openclaw/openclaw:latest` as a discovery probe. Docker Desktop was not installed on the host machine. The probe timed out (124 s, then 184 s) and the PE was initially classified as `BLOCKED (env)`.

**Root cause:** The plan assumed Docker Desktop as a pre-existing prerequisite, like `git` or `Python`, without explicitly listing it or verifying it at PE start.

**Detection:** `where.exe docker` returned not found; `docker pull` timed out.

**Rule added:** `docs/openclaw/DOCKER_SETUP.md` updated with explicit host prerequisites section. Discovery probes must verify tool availability before running.

---

## LL-08 — `channels add` without `--account <BOT_ID>` causes permanent token:none

| Field | Value |
|---|---|
| First seen | PE-OC-17 post-merge ops (2026-02-26) |
| Agent | CODEX (initial setup) + Claude Code (diagnosis) |
| AGENTS.md rule | §3.4 — verify channel status after every config change |

**Error:** `openclaw channels add --channel telegram --token <TOKEN>` was run without
`--account <BOT_ID>`. The token was stored under account name `"default"`. The binding's
`match.accountId` was a numeric Telegram bot ID. The gateway searched for an account
matching the numeric ID and found none → `token:none` on every startup.

**Root cause:** The `--account` flag is not documented prominently; omitting it silently
creates a `"default"` account that never matches a numeric binding accountId. The
gateway reports `token:none` rather than `account not found`, making the root cause hard
to trace.

**Detection:** `channels status` showed `token:none` despite `channels.telegram.botToken`
being present in the config. Only after reading `channels add --help` was the `--account`
flag discovered.

**Rule added:** When registering a Telegram bot, always use:
`channels add --channel telegram --token <TOKEN> --account <BOT_ID>`
where `BOT_ID` = numeric prefix of the token (digits before the first colon).
The binding's `match.accountId` must equal `BOT_ID`.

---

## LL-09 — Docker Compose `environment:` overrides `env_file:` with empty strings

| Field | Value |
|---|---|
| First seen | PE-OC-17 post-merge ops (2026-02-26) |
| Agent | CODEX (docker-compose.yml author) |
| AGENTS.md rule | §3.4 — verify container env after every compose change |

**Error:** `docker-compose.yml` listed `TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}` in
the `environment:` block. The same variable was also supplied by `env_file`. Docker
Compose resolves `${VAR}` in `environment:` from the **host shell**, not from
`env_file`. Because the host PowerShell session did not export `TELEGRAM_BOT_TOKEN`,
Compose substituted an empty string. The `environment:` entry then **overrode** the
correct value from `env_file`, so the container received an empty token.

**Root cause:** Docker Compose precedence: `environment:` > `env_file:`. Listing a
variable in both places with a host-shell expansion in `environment:` silently wins
with an empty value when the host shell has no export.

**Detection:** `channels status` showed `token:none`. Checking container env (existence
only, not value) confirmed `TELEGRAM_BOT_TOKEN` was set but the gateway rejected it.

**Rule added:** Do not list secrets in both `env_file:` and `environment:`. Use
`env_file:` exclusively for all secrets. Only non-secret, hardcoded constants (like
`OPENCLAW_STATE_DIR`) belong in `environment:`.

---

## LL-10 — Agent must never run commands that print secret values

| Field | Value |
|---|---|
| First seen | PE-OC-17 post-merge ops (2026-02-26) |
| Agent | Claude Code |
| AGENTS.md rule | §13 Secrets isolation |

**Error:** Claude Code ran `docker exec openclaw printenv | grep -E 'TELEGRAM|OPENAI|ANTHROPIC'`
as a diagnostic step. The command printed the full values of `TELEGRAM_BOT_TOKEN`,
`OPENAI_API_KEY`, and `ANTHROPIC_API_KEY` into the conversation context.

**Root cause:** The diagnostic intent was to verify that secrets were present in the
container. A filtered `printenv` was chosen over a safe existence check. Even though
the filter was narrow, the output contained full secret values.

**Detection:** User interrupted the session and requested a hard rule be registered.

**Rule added (user-mandated):** Agents must NEVER run any command that prints, reads,
or exposes secret values. Use existence checks only:
- Shell: `[ -n "$VAR" ] && echo set || echo unset`
- Docker: `MSYS_NO_PATHCONV=1 docker exec <c> /bin/sh -c '[ -n "$(printenv VAR)" ] && echo set || echo unset'`
- Python: `bool(os.environ.get("VAR"))`

Do not use `printenv`, `env`, `cat .env`, `Get-Content .env`, or any grep/filter on
env output — even filtered output can expose values. Recorded in Claude Code memory.
