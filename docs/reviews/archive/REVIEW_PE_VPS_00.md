# REVIEW_PE_VPS_00.md

**Validator:** prog-val-claude (Claude Code)
**Date:** 2026-03-06
**PR:** #290
**Branch:** feature/pe-vps-00-hostinger-baseline
**Base:** main

---

### Verdict

FAIL

---

### Gate results

```
black --check .:  All done! 236 files would be left unchanged.
ruff check .:     All checks passed!
pytest (full):    565 passed, 17 warnings, 0 failures
bash -n provision_hostinger_baseline.sh: OK (syntax valid)
bash -n verify_hostinger_baseline.sh:   OK (syntax valid)
```

---

### Scope

```
git diff --name-status origin/main...origin/feature/pe-vps-00-hostinger-baseline

A       docs/_active/VPS_BASELINE.md
A       scripts/vps/provision_hostinger_baseline.sh
A       scripts/vps/verify_hostinger_baseline.sh
M       HANDOFF.md
```

4 files. All within PE-VPS-00 scope. No unrelated changes.

---

### Required fixes

**Blocking — AC1–AC4 lack live host evidence.**

`docs/_active/VPS_BASELINE.md` contains 5 `<PASTE OUTPUT>` placeholders. The plan (`ELIS_MultiAgent_Implementation_Plan_v1_2.md` §PE-VPS-00 AC1–AC4) requires actual host execution and verified output before PASS can be issued.

**Required action (PM/operator):**

1. SSH into the Hostinger VPS.
2. Execute: `sudo bash scripts/vps/provision_hostinger_baseline.sh elis /root/elis_deploy_key.pub`
3. Execute: `sudo bash scripts/vps/verify_hostinger_baseline.sh elis`
4. Paste the verbatim output of each evidence command into the corresponding `<PASTE OUTPUT>` block in `docs/_active/VPS_BASELINE.md`:
   - AC1: `sshd -T | grep -E 'passwordauthentication|permitrootlogin'`
   - AC2: `ufw status numbered`
   - AC3: `fail2ban-client status sshd`
   - AC4: `docker info` + `docker compose version`
   - AC5: `ss -lntp | grep -E '18789|:80|:443'` (or empty output confirming no public binding)
5. Commit the updated `docs/_active/VPS_BASELINE.md` to the branch.
6. Request re-validation.

---

### Evidence

```
# Repository deliverables — assessed PASS
provision_hostinger_baseline.sh: bash syntax OK
  - Steps 1–9 correctly implement all AC1–AC4 controls
  - SSH hardening (PasswordAuthentication no, PermitRootLogin no, sshd_config.d drop-in)
  - UFW least-privilege (default deny, allow OpenSSH/80/443)
  - fail2ban sshd.local jail (maxretry=5, findtime=10m, bantime=1h)
  - Docker Engine + Compose plugin from official docker.com APT repo
  - /opt/elis directory layout (700 secrets, 750 config/data/logs)

verify_hostinger_baseline.sh: bash syntax OK
  - Exit code 1 on any failed check (FAIL=1 accumulation pattern correct)
  - All 11 checks map directly to plan AC1–AC4 + OpenClaw exposure constraint
  - "OpenClaw port not public" check uses negated pattern — correct

docs/_active/VPS_BASELINE.md: committed, 5 evidence blocks empty
  - grep -c "<PASTE OUTPUT>" → 5 (all AC1–AC5 evidence missing)
```

```
# Quality gates
python -m black --check .   → All done! 236 files would be left unchanged.
python -m ruff check .      → All checks passed!
python -m pytest            → 565 passed, 17 warnings, 0 failures
```

---

### Notes

**Non-blocking observations (informational):**

- `scripts/vps/` directory is a new addition — no `__init__.py` needed (bash scripts, not Python).
- `check_agent_scope.py` returns clean in CODEX's environment (worktree owned by CodexSandboxOffline user). Pre-existing `.env`/`.claude/settings.local.json` warnings are not visible from the CODEX sandbox — confirmed consistent with prior PE pattern.
- The provisioning script uses `DEBIAN_FRONTEND=noninteractive` and `apt-get -y --no-install-recommends` — correct for automated provisioning.
- No manifest compliance check required: PE-VPS-00 generates no ELIS run artifacts (infrastructure PE only).

---

## Re-validation Round 2 — 2026-03-21

### Evidence

```text
--- Branch state ---
git log -3 --oneline
e2e3f18 fix(pe-vps-00): close validator follow-up findings
456b457 fix(pe-vps-00): add miniserver live evidence
046c37c wip(pe-vps-00): rescope baseline artifacts to miniserver

--- Quality gates ---
python -m black --check .:  All done! 118 files would be left unchanged.
python -m ruff check .:     All checks passed!
python -m pytest:           565 passed, 17 warnings in 9.96s
python scripts/check_agent_scope.py: Agent scope clean

--- AC1: SSH hardening ---
permitrootlogin no
passwordauthentication no

--- AC2: UFW ---
Status: active
[ 1] 22/tcp  ALLOW IN  Anywhere  # SSH
[ 2] 80/tcp  ALLOW IN  Anywhere  # HTTP
[ 3] 443/tcp ALLOW IN  Anywhere  # HTTPS
(+ IPv6 equivalents)

--- AC3: fail2ban ---
Status for the jail: sshd — active, 0 currently banned

--- AC4: Docker ---
Server Version: 28.2.2
Docker Compose version 2.37.1+ds1-0ubuntu2~24.04.1

--- AC5: OpenClaw + artefact ---
port 18789 not bound (expected)
docs/_active/MINISERVER_BASELINE.md: committed

--- Additional (plan v1.3 scope) ---
/opt/elis/repo: present and current (git pull to 840ab65)
elis CLI: /usr/local/bin/elis resolves correctly

--- Scope fix (Validator-applied) ---
CURRENT_PE.md, docs/_active/ROADMAP.md, REVIEW_PE_VPS_00.md:
restored to origin/main state — reverted by CODEX rebase artefact,
corrected by Validator as minimal scope-safe fix (AGENTS.md §2.3).
```

### Verdict

PASS

### Gate results

```text
black --check .: PASS
ruff check .:    PASS
pytest:          PASS — 565 passed, 0 failed, 17 warnings (pre-existing)
check_agent_scope.py: PASS
```

### Scope

```text
git diff --name-status origin/main..HEAD (after Validator scope fix)

M    CURRENT_PE.md                              ← restored to main
A    docs/_active/MINISERVER_BASELINE.md        ← PE deliverable
A    docs/_active/MINISERVER_BASELINE_VALIDATION_RUNBOOK.md ← restored from main
M    docs/_active/ROADMAP.md                    ← restored to main
M    HANDOFF.md                                 ← PE deliverable
M    REVIEW_PE_VPS_00.md                        ← Validator-owned
A    scripts/vps/provision_miniserver_baseline.sh ← PE deliverable
A    scripts/vps/verify_miniserver_baseline.sh    ← PE deliverable
```

PE-owned artefacts: MINISERVER_BASELINE.md, both scripts, HANDOFF.md — all correct.
Scope fix applied by Validator to 3 out-of-scope files reverted by rebase artefact.

### Required fixes

None.

### Notes

1. **Scope violation (resolved):** CODEX's cherry-pick rebase approach omitted PM-CHORE-03,
   causing CURRENT_PE.md and ROADMAP.md to revert to pre-PM-CHORE-03 state. CODEX also
   modified Validator-owned REVIEW_PE_VPS_00.md. All three restored to origin/main by
   Validator as a scope-safe fix. CODEX should adopt `git rebase origin/main` (not cherry-pick)
   for future PEs to avoid this class of artefact.
2. **Hardening performed by PM directly** — not via provision script. Documented correctly
   in MINISERVER_BASELINE.md and HANDOFF.md.
3. **ELIS CLI** — functional via symlink at /usr/local/bin/elis. Acceptable.
