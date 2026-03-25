# REVIEW_PE_MS_08.md — PE-MS-08 Validation

**PE:** `PE-MS-08`
**Title:** PM Agent End-to-End Operational Validation and Native Runbooks
**Implementer:** CODEX (`infra-impl-codex`)
**Validator:** Claude Code (`infra-val-claude`)
**Branch:** `feature/pe-ms-08-e2e-validation`
**Date:** 2026-03-25

---

### Verdict

FAIL

---

### Gate results

```text
python -m black --check .
All done! ✨ 🍰 ✨
125 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
601 passed, 17 warnings in 10.90s

python -m pytest tests/test_pm_runbooks.py -v
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.1, pluggy-1.6.0
collected 3 items

tests\test_pm_runbooks.py ...                                            [100%]

============================== 3 passed in 0.07s ==============================

python scripts/check_agent_scope.py
Agent scope clean - no secret-pattern files detected in worktree.
```

---

### Scope

8 files changed — the branch stays within PE-MS-08 scope:

```text
M	HANDOFF.md
M	docs/openclaw/DEPLOYMENT.md
M	docs/openclaw/NATIVE_INSTALL.md
A	docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md
M	docs/openclaw/PM_AGENT_RULES.md
A	docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md
M	docs/openclaw/PM_SESSION_RESET.md
A	tests/test_pm_runbooks.py

8 files changed, 567 insertions(+), 64 deletions(-)
```

No unrelated files in diff.

---

### Host evidence collected on elis-server

```text
systemctl --user status openclaw-gateway --no-pager
● openclaw-gateway.service - OpenClaw Gateway (v2026.3.13)
     Loaded: loaded (/home/samurai/.config/systemd/user/openclaw-gateway.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-03-23 15:54:49 GMT; 2 days ago
   Main PID: 142624 (openclaw-gatewa)
     Memory: 457.2M
        CPU: 14min 29.821s

openclaw doctor (summary)
Telegram: ok (@elis_pm_agent_bot) (155ms)
Discord: ok (@ELIS PM Agent) (597ms)
Agents: pm (default), slr-impl-codex, slr-impl-claude, … infra-val-claude
Heartbeat interval: 30m (pm)
Session store (pm): 1 entry (1094m ago)

openclaw channels status --probe
- Telegram 8351383841: enabled, configured, running, mode:polling, works
- Discord default: enabled, configured, running, disconnected, in:18h ago, out:2d ago, works

openclaw approvals get --gateway
Allowlist: 29 entries for agent pm (cat, ls, git, openclaw, gh patterns)

ls -l ~/openclaw/workspace-pm
-rw-rw-r--  AGENTS.md          (3996 bytes, Mar 23 15:43)
lrwxrwxrwx  CURRENT_PE.md   -> /opt/elis/repo/CURRENT_PE.md
drwxr-xr-x  docs/
-rw-rw-r--  MEMORY.md
-rw-rw-r--  SOUL.md

ls -l ~/openclaw/workspace-pm/docs
-rw-rw-r--  AGENTS.md          (symlink -> /opt/elis/repo/AGENTS.md)
-rw-rw-r--  EXEC_POLICY.md
-rw-rw-r--  PLAN_v1_4.md
lrwxrwxrwx  PLAN_v1_5.md    -> /opt/elis/repo/ELIS_MultiAgent_Implementation_Plan_v1_5.md
drwxrwxr-x  _stale_backup/

git -C /opt/elis/repo worktree list
/opt/elis/repo  a647776 [main]

git -C /opt/elis/repo log --oneline -5
a647776 docs(pm): define GPT-5.4 contingency model
9b55cd2 chore(pm): publish architecture v1.6 and implementation plan v1.5
ce1c29c docs: add PE-MS-02 pre-analysis — agent registry gaps and workspace inventory
f1d6509 chore(pm): open PE-MS-01 — PM agent identity & exec config (PM-CHORE-07)
7e77254 chore(pm): draft plan v1.4 — MiniServer functional PE series (PM-CHORE-07)

cat ~/openclaw/workspace-pm/CURRENT_PE.md (excerpt)
Plan file: ELIS_MultiAgent_Implementation_Plan_v1_5.md
PE: PE-MS-01 · Branch: feature/pe-ms-01-pm-agent-identity

cat ~/openclaw/workspace-pm/AGENTS.md | tail -1
*ELIS PM Agent · AGENTS.md · v1.2 · 2026-03-23*
```

---

### Required fixes

**Operator action required — not a CODEX code change:**

1. Update elis-server to current main:
   ```bash
   cd /opt/elis/repo && git pull
   bash scripts/deploy_openclaw_workspaces.sh
   systemctl --user restart openclaw-gateway
   ```
2. Verify `PLAN_CURRENT.md` is created by the deploy script; if not, create the symlink manually.
3. Reset PM session per `docs/openclaw/PM_SESSION_RESET.md`.
4. Execute Scenarios 1–5 from `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md` in Discord DM and capture transcript/screenshots in re-validation round.

---

### Evidence

#### Finding 1 — elis-server repo is 6+ PRs behind main (PE-MS-01 era)

The repo on elis-server is at commit `a647776`, which predates the entire MiniServer
functional series (PE-MS-01 through PE-MS-07 were all merged after this commit). The
`CURRENT_PE.md` symlink therefore resolves to a stale state showing PE-MS-01 as current.

```text
git -C /opt/elis/repo rev-parse HEAD
a647776e5c4be5dfeb7ef72959ba32d787f9f964

cat ~/openclaw/workspace-pm/CURRENT_PE.md | grep "Plan file\|PE "
Plan file: ELIS_MultiAgent_Implementation_Plan_v1_5.md
PE:        PE-MS-01
```

GitHub main HEAD is `caa843f` (PM-CHORE-15, PE-MS-08 opened). The server is missing
PE-MS-01 through PE-MS-07 prompt updates and PM-CHORE changes.

Why this blocks:
- Scenario 2 (AC-1): a "What are the current PEs?" question will produce PE-MS-01
  state, not PE-MS-08. The evidence would not reflect canonical governance state.
- AC-1 to AC-3 all depend on the PM Agent reading current governance files; with a
  stale repo the evidence is misleading, not probative.

#### Finding 2 — deployed PM AGENTS.md is v1.2 (missing §5.1–§5.3 Discord rules)

The workspace-pm AGENTS.md on elis-server is the v1.2 file deployed during the
PE-MS-01 era. It predates the Discord-safe formatting rules added in PE-MS-03:

```text
cat ~/openclaw/workspace-pm/AGENTS.md | tail -1
*ELIS PM Agent · AGENTS.md · v1.2 · 2026-03-23*

grep -in 'discord\|registry\|worktree\|chunk\|bullet' ~/openclaw/workspace-pm/AGENTS.md
(no matches for §5.1 Discord-safe format / §5.2 chunked registry / §5.3 worktree rules)
```

The deployed prompt does NOT contain:
- `§5.1 PE Status — Discord-Safe Format` (bullet list, non-merged only by default)
- `§5.2 Full Registry — Compact Chunked Format`
- `§5.3 Worktree Reporting` (no inference from registry branch names)

Why this blocks:
- AC-2 and AC-3 test behaviors that are defined only in §5.2 and §5.3 of v2.2.
  A PM session running v1.2 cannot pass Scenarios 3 and 4 of the runbook.
- Discord test evidence from the current session would validate v1.2 behavior, not
  the post-PE-MS-03 contract.

#### Finding 3 — PLAN_CURRENT.md missing from workspace docs

The `~/openclaw/workspace-pm/docs/` entrypoint required by AGENTS.md §2 is absent:

```text
ls ~/openclaw/workspace-pm/docs/
AGENTS.md  EXEC_POLICY.md  PLAN_v1_4.md  PLAN_v1_5.md  _stale_backup/
```

`PLAN_CURRENT.md` is referenced by AGENTS.md §2 (Session Start step 4) and §5
(source table). The deploy script must create this entrypoint or a symlink to it.
This is a pre-existing gap (not introduced by PE-MS-08) but it is exposed directly
by the new runbook's precondition check:

```text
docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md
Required host checks before Discord validation:
  ls -l ~/openclaw/workspace-pm/docs
Expected: PM entrypoints exist: CURRENT_PE.md, docs/AGENTS.md, docs/PLAN_CURRENT.md
```

---

### AC assessment

| # | Criterion | Verdict | Notes |
|---|---|---|---|
| AC-1 | PM Agent identifies current PE state correctly from canonical files | BLOCKED | Cannot collect valid Discord evidence — server repo stale, deployed PM at v1.2 |
| AC-2 | PM Agent reports worktrees only from explicit host evidence | BLOCKED | §5.3 worktree rules not present in deployed v1.2 AGENTS.md |
| AC-3 | PM Agent produces Discord-safe registry reporting | BLOCKED | §5.1/§5.2 formatting rules not present in deployed v1.2 AGENTS.md |
| AC-4 | Native ops and restore runbooks committed and validated | PASS | 601/601 tests pass; test_pm_runbooks.py 3/3; all cross-links present |

---

*ELIS SLR Agent · REVIEW_PE_MS_08.md · infra-val-claude · 2026-03-25*
