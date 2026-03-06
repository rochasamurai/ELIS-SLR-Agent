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
