# HANDOFF - PE-VPS-00: MiniServer Baseline Provisioning

**PE:** PE-VPS-00  
**Branch:** feature/pe-vps-00-hostinger-baseline  
**Implementer:** CODEX (prog-impl-codex)  
**Validator:** Claude Code (prog-val-claude)  
**Date:** 2026-03-21

---

## Summary

PE-VPS-00 has been rebased onto current `origin/main` and rescoped from the old Hostinger/VPS baseline to the current MiniServer target defined in plan v1.3:

- Renamed the active baseline artefact to `docs/_active/MINISERVER_BASELINE.md`
- Renamed the host scripts to `scripts/vps/provision_miniserver_baseline.sh` and `scripts/vps/verify_miniserver_baseline.sh`
- Updated those artefacts to target the ELIS MiniServer (`elis-server`, NUC8i7BEH, Ubuntu 24.04.4 LTS)
- Extended the scripts to create `/opt/elis/repo` and verify `elis --help`

Live host evidence is still pending because SSH access to `elis-server` is currently blocked from this environment.

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
4. Did not fabricate host evidence; live output will only be pasted after successful SSH access to `elis-server`.

---

## Acceptance Criteria

Source: `ELIS_MultiAgent_Implementation_Plan_v1_3.md` (PE-VPS-00 section).

- [ ] AC1 - Host reachable via SSH key auth only; password auth disabled.  
  Status: Pending live host evidence from `elis-server`.
- [ ] AC2 - UFW policy active with least-privilege ingress (22/80/443 only where required).  
  Status: Pending live host evidence from `elis-server`.
- [ ] AC3 - fail2ban jail active for SSH.  
  Status: Pending live host evidence from `elis-server`.
- [ ] AC4 - Docker + Compose installed and functional (`docker info`, `docker compose version`).  
  Status: Pending live host evidence from `elis-server`.
- [ ] AC5 - Baseline verification artefact committed and reviewed (`docs/_active/MINISERVER_BASELINE.md`, `REVIEW_PE_VPS_00.md`).  
  Status: Artefact renamed and updated; live evidence still pending before re-validation.

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

### Live evidence blocker

```text
ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new elis-server "hostname && uname -a"
carlo@elis-server: Permission denied (publickey,password).

ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new elis@elis-server "hostname && uname -a"
elis@elis-server: Permission denied (publickey,password).

ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new root@elis-server "hostname && uname -a"
root@elis-server: Permission denied (publickey,password).
```

### Next required live commands

```text
sudo bash scripts/vps/provision_miniserver_baseline.sh elis /root/elis_deploy_key.pub
sudo bash scripts/vps/verify_miniserver_baseline.sh elis

sshd -T | grep -E 'passwordauthentication|permitrootlogin'
ufw status numbered
fail2ban-client status sshd
sudo -u elis -H docker info
sudo -u elis -H docker compose version
ss -lntp | grep -E '18789|:80|:443' || true
```

---

## Next

1. Obtain a working SSH path to `elis-server` from this environment.
2. Run the provisioning and verification commands on-host.
3. Paste verbatim host output into `docs/_active/MINISERVER_BASELINE.md`.
4. Run local quality gates and refresh the full HANDOFF status packet.
5. Push the branch and request re-validation on PR #290.
