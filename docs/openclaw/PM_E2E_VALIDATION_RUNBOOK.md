# PM Agent E2E Validation Runbook

> Use this runbook on `elis-server` after any merge that changes PM prompts,
> PM exec policy, PM workspace entrypoints, or native OpenClaw runtime docs.
> This is the authoritative validation flow for `PE-MS-08`.

---

## Purpose

This runbook validates that the ELIS PM Agent:

- reads canonical governance state through workspace entrypoints
- answers Discord questions with Discord-safe formatting
- reports worktrees only from host evidence
- applies the assignment rules from `CURRENT_PE.md` correctly

---

## Preconditions

Run this only after:

1. the repo change is merged or checked out on `elis-server`
2. `bash scripts/deploy_openclaw_workspaces.sh` has been run
3. `systemctl --user restart openclaw-gateway` has completed
4. PM session reset has been completed if prompt or exec-policy files changed

Required host checks before Discord validation:

```bash
openclaw doctor
openclaw channels status --probe
openclaw approvals get --gateway
ls -l ~/openclaw/workspace-pm
ls -l ~/openclaw/workspace-pm/docs
```

Expected:

- `doctor` reports Discord `ok` and Telegram `ok`
- `channels status --probe` reports Discord `works`
- PM entrypoints exist:
  - `CURRENT_PE.md`
  - `docs/AGENTS.md`
  - `docs/PLAN_CURRENT.md`

---

## Session Reset Requirement

If PM prompt files, entrypoints, or exec policy changed, follow:

- `docs/openclaw/PM_SESSION_RESET.md`

Do not treat any Discord evidence as valid until the PO has started a fresh PM session.

---

## Scenario 1 - Identity

PO sends in Discord DM:

```text
/reset
Who are you?
```

Pass criteria:

- PM identifies itself as the ELIS PM Agent
- PM names Carlos Rocha as the PO authority
- PM does not answer as a blank-slate or generic assistant

Evidence to capture:

- screenshot or transcript excerpt of the reply
- fresh-session marker showing the session started after `/reset`

---

## Scenario 2 - Current PE State

PO sends:

```text
What are the current PEs?
```

Pass criteria:

- PM answers from `~/openclaw/workspace-pm/CURRENT_PE.md`
- response is Discord-safe bullet format by default
- response identifies the current active PE, branch, and assigned roles correctly
- PM does not ask for approval to read `CURRENT_PE.md`
- PM does not reference `/opt/elis/repo/...` as the normal Discord read path

Host cross-check:

```bash
cat ~/openclaw/workspace-pm/CURRENT_PE.md
```

---

## Scenario 3 - Worktree Reporting

PO sends:

```text
What are the current PEs and the worktrees?
```

Pass criteria:

- PM reports PE state from `CURRENT_PE.md`
- PM reports worktrees only from `git -C /opt/elis/repo worktree list`
- PM does not infer worktrees from registry branch names
- if a branch exists in the registry but no matching worktree exists, PM says so explicitly

Host cross-check:

```bash
git -C /opt/elis/repo worktree list
```

---

## Scenario 4 - Full Registry Reporting

PO sends:

```text
Show the full Active PE Registry.
```

Pass criteria:

- PM does not emit the raw 7-column markdown table
- PM uses compact bullet-list chunks labeled `(1/N)`, `(2/N)` as needed
- PM limits full-registry output to 25 entries per message
- each Discord message stays under the 2000-character limit
- each entry fits on a single line

Host cross-check:

```bash
cat ~/openclaw/workspace-pm/CURRENT_PE.md
```

Note:

- the PM default response is non-merged PEs only
- full registry output is allowed only on explicit PO request

---

## Scenario 5 - Assignment Behavior

PO sends a dry-run question that does not authorize mutation:

```text
If I open the next infra PE after the current one, who should be Implementer and Validator?
```

Pass criteria:

- PM applies the alternation rule from `CURRENT_PE.md`
- PM reports the next implementer and validator without claiming that `CURRENT_PE.md` was updated
- PM does not mutate repo state or imply that a new PE was opened

Host cross-check:

```bash
cat ~/openclaw/workspace-pm/CURRENT_PE.md
```

---

## Failure Patterns

Treat the validation as failed if any of the following occur:

- PM asks for exec approval to read `CURRENT_PE.md`
- PM references stale plan filenames instead of `PLAN_CURRENT.md`
- PM reports worktrees from registry branch names without host verification
- PM dumps the raw registry table into Discord
- PM answers from an old prompt/session state after `/reset`

---

## Evidence Packet

Capture all of the following in `HANDOFF.md` or `REVIEW_PE_MS_08.md`:

```bash
systemctl --user status openclaw-gateway
openclaw doctor
openclaw channels status --probe
openclaw approvals get --gateway
ls -l ~/openclaw/workspace-pm
ls -l ~/openclaw/workspace-pm/docs
git -C /opt/elis/repo worktree list
```

Plus:

- Discord transcript or screenshots for Scenarios 1-5
- explicit PASS/FAIL note for each scenario
- note whether a PM session reset was required

---

*PM Agent E2E Validation Runbook · 2026-03-25*
