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
