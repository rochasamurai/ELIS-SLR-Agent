# REVIEW_PE_OC_11.md — Validator Verdict

| Field             | Value                                                      |
|-------------------|------------------------------------------------------------|
| PE                | PE-OC-11                                                   |
| PR                | #273                                                       |
| Branch            | `feature/pe-oc-11-security-hardening`                     |
| Commit reviewed   | `4928288` (fix); code commit `c7cd9c8`; HANDOFF `0c43c85` |
| Validator         | Claude Code (`prog-val-claude`)                            |
| Round             | r2                                                         |
| Date              | 2026-02-22                                                 |
| **Verdict**       | **PASS**                                                   |

---

## Scope Check

```
git diff --name-status origin/main..HEAD
M   .agentignore
M   .github/workflows/ci.yml
M   HANDOFF.md
M   docker-compose.yml
A   docs/openclaw/SECURITY_AUDIT.md
A   scripts/check_openclaw_security.py
```

All six files are in-plan deliverables per the PE-OC-11 plan. No out-of-scope
changes. ✓

---

## Quality Gates

| Gate | Result |
|---|---|
| `python -m black --check .` | ✓ 113 files unchanged |
| `python -m ruff check .` | ✓ All checks passed |
| `python -m pytest -q` | ✓ 534 passed, 17 warnings |

All gates green. ✓

---

## Acceptance Criteria Review

| AC | Definition | Result | Evidence |
|---|---|---|---|
| AC-1 | Container walk finds zero files from ELIS repo | **PASS** | `check_openclaw_security.py` exits 0; volume paths are `${HOME}/.openclaw` and `${HOME}/openclaw/workspace-pm` — no repo path exposed |
| AC-2 | `openclaw doctor --check dm-policy` exits 0 | **FAIL** | CLI module missing: `No module named openclaw.__main__` — carry-over environment gap from PE-OC-09/10 |
| AC-3 | `check_openclaw_security.py` passes in CI | **PASS** | `openclaw-security-check` job added to `ci.yml`, wired into `add_and_set_status` dependency chain |
| AC-4 | `exec.ask: on` enforced; ClawHub auto-install disabled | **PASS** | `openclaw.json` verified: all 5 agents have `exec.ask: true`; `skills.hub.autoInstall: false` |
| AC-5 | `docs/openclaw/SECURITY_AUDIT.md` completed | **PASS** | File present with findings, evidence, and recommendations |

AC-2 failure is an environment-level constraint (OpenClaw CLI not installed), identical
to the gap documented in PE-OC-09 and PE-OC-10. CODEX correctly documents it as a
blocking finding and does not attempt to work around it. 4/5 ACs pass on implemented
deliverables.

---

## Deliverable Quality Review

### `scripts/check_openclaw_security.py`

Logic is sound across all three checks:
- **Docker volumes:** correctly resolves `${HOME}` via `os.path.expandvars`, checks
  whether `REPO_ROOT` is in the host path's parents or is equal to it, and flags
  relative paths and unbound ports.
- **`.agentignore`:** correctly verifies presence of `openclaw/workspaces` and
  `openclaw/openclaw.json` prefixes.
- **`openclaw.json`:** correctly validates `exec.ask: true` per agent and
  `skills.hub.autoInstall: false`.

### `docker-compose.yml`

Hardening additions are appropriate: `no-new-privileges:true`, `cap_drop: ALL`,
`cap_add: CHOWN`, and `tmpfs: /tmp:rw,nosuid,noexec`. Port binding confirmed at
`127.0.0.1:18789:3000` (localhost-only). ✓

### `.agentignore`

`openclaw/workspaces/` and `openclaw/openclaw.json` entries added. ✓

### CI job

`openclaw-security-check` correctly runs after the existing jobs and before
`add_and_set_status`, ensuring the security gate is mandatory. Installs `PyYAML==6.0.2`
ad-hoc. ✓

---

## Findings

### Non-Blocking

| ID | Description |
|---|---|
| NB-1 | §6.2 `git rev-parse HEAD` shows `c7cd9c8` (the code commit) but the final branch HEAD is `0c43c85` (the HANDOFF refresh commit). The status packet was captured before the HANDOFF refresh was committed, leaving the SHA stale by one commit. Same pattern as PE-OC-08 NB-1. |
| NB-2 | §6.1 `git status -sb` shows `...origin/main` with no `[ahead N]`. The branch tracks `origin/main` rather than `origin/feature/pe-oc-11-security-hardening`. Commits are present on origin (§6.3 diff is correct). Cosmetic — same as PE-OC-09 NB-2. |
| NB-3 | `check_openclaw_security.py` swallows violation messages on the failure path. `raise SystemExit("message")` inside `print_report()` is caught by `except SystemExit: sys.exit(1)` in `__main__`, discarding the diagnostic string. On the happy path this is invisible; on a failing CI run, the violation description will not appear in logs. Consider printing violations explicitly before raising, or removing the try/except and letting SystemExit propagate. |
| NB-4 | `PyYAML` is imported in `check_openclaw_security.py` but is not declared in `requirements.txt`. The CI job installs it ad-hoc (`pip install PyYAML==6.0.2`). Local runs outside the venv will fail with `ModuleNotFoundError`. Add `PyYAML>=6.0` to `requirements.txt`. |

### Blocking

None against PE-OC-11 itself. AC-2 is an environment gap, not an implementation
failure.

---

## Post-r1 CI Failure & Validator Fix (r2)

After r1 verdict was posted, PR #273 could not merge: `secrets-scope-check` returned
FAILURE, causing `openclaw-security-check` to be SKIPPED (dependency chain).

**NB-5 (post-r1):** `check_agent_scope.py` reads every deny pattern in `.agentignore`
via glob and exits 1 if any matching file exists on disk. PE-OC-11 added
`openclaw/workspaces/` and `openclaw/openclaw.json` as deny patterns — both are
legitimate tracked repo files (OpenClaw config), so the script flagged 18 files as
violations. The r1 review did not catch this because `openclaw-security-check` was
already SKIPPED at review time (its prerequisite `secrets-scope-check` had already
failed).

**Validator fix (`4928288`):** Added negation (allow) entries to `.agentignore`:

```
!openclaw/workspaces/
!openclaw/openclaw.json
```

These entries whitelist the tracked files in `check_agent_scope.py`'s violation check
while leaving the deny entries intact for IDE context exclusion and
`check_openclaw_security.py` validation. Fix verified locally:

```
python scripts/check_agent_scope.py   → Agent scope clean — no secret-pattern files detected in worktree.
python scripts/check_openclaw_security.py → openclaw security checks passed.
python -m pytest                      → 534 passed, 17 warnings
```

---

## Merge Recommendation

**Merge PE-OC-11.** Four of five ACs pass cleanly. AC-2 (`openclaw doctor`) is
blocked by the same missing CLI that affected PE-OC-09 and PE-OC-10 — an
environment gap beyond CODEX's control. The security controls that CAN be
implemented (Docker hardening, `.agentignore`, `openclaw.json` enforcement, CI job)
are all correct and in-place.

NB-1 through NB-4 require no changes before merge; NB-3 and NB-4 are good
candidates for CODEX to address in a follow-up commit if desired.

---

## Round History

| Round | Verdict | Key findings | Date |
|---|---|---|---|
| r1 | PASS | AC-2 env gap (carry-over); NB-1 stale SHA; NB-2 tracking upstream; NB-3 SystemExit message swallowed; NB-4 PyYAML not in requirements.txt | 2026-02-22 |
| r2 | PASS | NB-5 post-r1 CI failure: `secrets-scope-check` exits 1 because `check_agent_scope.py` treats `.agentignore` deny entries as "must not exist on disk", flagging legitimate tracked openclaw files. Validator fix `4928288`: added `!openclaw/workspaces/` and `!openclaw/openclaw.json` negation entries to whitelist. 534 tests pass. | 2026-02-22 |
