# HANDOFF - PE-VPS-00: MiniServer Baseline Provisioning

**PE:** PE-VPS-00  
**Branch:** feature/pe-vps-00-hostinger-baseline  
**Implementer:** CODEX (prog-impl-codex)  
**Validator:** Claude Code (prog-val-claude)  
**Date:** 2026-03-21

---

## Summary

PE-VPS-00 has been rebuilt on top of current `origin/main` and rescoped from the old Hostinger/VPS baseline to the current MiniServer target defined in plan v1.3:

- Renamed the active baseline artefact to `docs/_active/MINISERVER_BASELINE.md`
- Renamed the host scripts to `scripts/vps/provision_miniserver_baseline.sh` and `scripts/vps/verify_miniserver_baseline.sh`
- Updated those artefacts to target the ELIS MiniServer (`elis-server`, NUC8i7BEH, Ubuntu 24.04.4 LTS)
- Extended the scripts to create `/opt/elis/repo` and verify `elis --help`
- Added host evidence showing `/opt/elis/repo` is current on `elis-server` and that `elis` resolves via `/usr/local/bin/elis`

Live host evidence from `elis-server` has now been supplied in the PR thread by the PM/operator and pasted verbatim into `docs/_active/MINISERVER_BASELINE.md`.

---

## Files Changed

- `docs/_active/MINISERVER_BASELINE.md`
- `scripts/vps/provision_miniserver_baseline.sh`
- `scripts/vps/verify_miniserver_baseline.sh`
- `HANDOFF.md`

---

## Design Decisions

1. Followed plan v1.3 rather than the older v1.2/current-PE label mismatch, because the validator review explicitly required MiniServer rescoping.
2. Kept the `scripts/vps/` directory for continuity, but renamed the file stems from `hostinger` to `miniserver`.
3. Added `/opt/elis/repo` and `elis --help` checks because they are part of the PE-VPS-00 MiniServer scope, even though the current validator FAIL focused primarily on AC1-AC5.
4. Used the PM/operator's verbatim `elis-server` evidence from PR #290 rather than fabricating or paraphrasing host output.
5. Documented explicitly that live SSH/UFW hardening on `elis-server` was performed directly by the PM/operator; the provision script remains a reproducibility artefact for future rebuilds.
6. Updated the provision script to fast-forward `/opt/elis/repo` when a checkout already exists, matching the validator's operational finding.

---

## Acceptance Criteria

Source: `ELIS_MultiAgent_Implementation_Plan_v1_3.md` (PE-VPS-00 section).

- [x] AC1 - Host reachable via SSH key auth only; password auth disabled.  
  Status: PASS — `sshd -T` evidence pasted in `docs/_active/MINISERVER_BASELINE.md`.
- [x] AC2 - UFW policy active with least-privilege ingress (22/80/443 only where required).  
  Status: PASS — `ufw status numbered` evidence pasted in `docs/_active/MINISERVER_BASELINE.md`.
- [x] AC3 - fail2ban jail active for SSH.  
  Status: PASS — `fail2ban-client status sshd` evidence pasted in `docs/_active/MINISERVER_BASELINE.md`.
- [x] AC4 - Docker + Compose installed and functional (`docker info`, `docker compose version`).  
  Status: PASS — Docker 28.2.2 and Compose 2.37.1 evidence pasted in `docs/_active/MINISERVER_BASELINE.md`.
- [x] AC5 - Baseline verification artefact committed and reviewed (`docs/_active/MINISERVER_BASELINE.md`, `REVIEW_PE_VPS_00.md`).  
  Status: PASS — artefact renamed and updated; validator review file already present on branch.

Note: `REVIEW_PE_VPS_00.md` is validator-owned and retained on-branch for continuity.

---

## Validation Commands

### Rebase / branch state

```text
git fetch origin
git checkout -B feature/pe-vps-00-hostinger-baseline origin/main
git cherry-pick 7b84752
git cherry-pick 3d47143
```

### Live evidence source

```text
## PM evidence — elis-server live AC output / 2026-03-21

$ sudo sshd -T | grep -E 'passwordauthentication|permitrootlogin'
permitrootlogin no
passwordauthentication no

$ sudo ufw status numbered
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    Anywhere                   # SSH
[ 2] 80/tcp                     ALLOW IN    Anywhere                   # HTTP
[ 3] 443/tcp                    ALLOW IN    Anywhere                   # HTTPS
[ 4] 22/tcp (v6)                ALLOW IN    Anywhere (v6)              # SSH
[ 5] 80/tcp (v6)                ALLOW IN    Anywhere (v6)              # HTTP
[ 6] 443/tcp (v6)               ALLOW IN    Anywhere (v6)              # HTTPS

$ sudo fail2ban-client status sshd
Status for the jail: sshd
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	3
|  `- Journal matches:	_SYSTEMD_UNIT=sshd.service + _COMM=sshd
`- Actions
   |- Currently banned:	0
   |- Total banned:	0
   `- Banned IP list:

$ docker info 2>&1 | grep -E 'Server Version|Operating System|Architecture'
 Server Version: 28.2.2
 Operating System: Ubuntu 24.04.4 LTS
 Architecture: x86_64

$ docker compose version
Docker Compose version 2.37.1+ds1-0ubuntu2~24.04.1

$ ss -lntp | grep 18789 || echo 'port 18789 not bound (expected)'
port 18789 not bound (expected)

$ cd /opt/elis/repo && git pull --ff-only
Updating 3e4b778..840ab65
Fast-forward
 .../MINISERVER_BASELINE_VALIDATION_RUNBOOK.md      | 209 +++++++++++++++++++++
 1 file changed, 209 insertions(+)
 create mode 100644 docs/_active/MINISERVER_BASELINE_VALIDATION_RUNBOOK.md
From https://github.com/rochasamurai/ELIS-SLR-Agent
   3e4b778..840ab65  main       -> origin/main

$ command -v elis
/usr/local/bin/elis

$ cd /opt/elis/repo && .venv/bin/elis --help | head -n 2
usage: elis [-h]
            {validate,harvest,merge,dedup,screen,agentic,export-latest} ...
```

### Quality gates

```text
python -m black --check .
All done! ✨ 🍰 ✨
118 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
565 passed, 17 warnings in 20.8s

python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

---

## Next

1. Run the final local quality gates and scope checks.
2. Push the rebased branch with the MiniServer artefacts and updated handoff.
3. Convert PR #290 from draft to ready.
4. Request re-validation on PR #290, pointing the validator to `docs/_active/MINISERVER_BASELINE.md`.
