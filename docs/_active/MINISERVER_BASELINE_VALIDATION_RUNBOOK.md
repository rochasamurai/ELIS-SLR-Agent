# elis-server Baseline Validation Runbook

**Host:** elis-server (NUC8i7BEH · Ubuntu 24.04.4 LTS · x86_64)  
**SSH user:** samurai  
**Key:** `~/.ssh/id_ed25519`  
**Repo path:** `/opt/elis/repo`  
**Maintained by:** Claude Code (Validator)  
**Last verified:** 2026-03-21 · PE-VPS-00  

> This runbook is reusable across all future elis-server PEs.
> Run the full checklist at the start of any PE that touches the host baseline,
> and paste verbatim output into the relevant REVIEW or HANDOFF artefact.

---

## 0. Connectivity check

```bash
ssh elis-server "echo connected && whoami && hostname && uname -r"
```

Expected:
```text
connected
samurai
elis-server
6.17.0-19-generic
```

---

## 1. SSH hardening (AC1)

```bash
ssh elis-server "sudo sshd -T | grep -E 'passwordauthentication|permitrootlogin'"
```

Expected PASS output:
```text
permitrootlogin no
passwordauthentication no
```

FAIL condition: any value other than `no` for either line.

---

## 2. UFW firewall (AC2)

```bash
ssh elis-server "sudo ufw status numbered"
```

Expected PASS output:
```text
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    Anywhere                   # SSH
[ 2] 80/tcp                     ALLOW IN    Anywhere                   # HTTP
[ 3] 443/tcp                    ALLOW IN    Anywhere                   # HTTPS
[ 4] 22/tcp (v6)                ALLOW IN    Anywhere (v6)              # SSH
[ 5] 80/tcp (v6)                ALLOW IN    Anywhere (v6)              # HTTP
[ 6] 443/tcp (v6)               ALLOW IN    Anywhere (v6)              # HTTPS
```

FAIL conditions: `Status: inactive` or any unexpected ALLOW rules.

---

## 3. fail2ban SSH jail (AC3)

```bash
ssh elis-server "sudo fail2ban-client status sshd"
```

Expected PASS output:
```text
Status for the jail: sshd
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	<N>
|  `- Journal matches:	_SYSTEMD_UNIT=sshd.service + _COMM=sshd
`- Actions
   |- Currently banned:	0
   |- Total banned:	<N>
   `- Banned IP list:
```

FAIL condition: error response or jail not found.

---

## 4. Docker + Compose versions (AC4)

```bash
ssh elis-server "docker info 2>&1 | grep -E 'Server Version|Operating System|Architecture' && echo '---' && docker compose version"
```

Expected PASS output:
```text
 Server Version: 28.2.2
 Operating System: Ubuntu 24.04.4 LTS
 Architecture: x86_64
---
Docker Compose version 2.37.1+ds1-0ubuntu2~24.04.1
```

FAIL condition: version below 28.2.2 / 2.37.1, or command not found.

---

## 5. OpenClaw not internet-exposed (AC5)

```bash
ssh elis-server "ss -lntp | grep 18789 || echo 'port 18789 not bound (expected)'"
```

Expected PASS output:
```text
port 18789 not bound (expected)
```

FAIL condition: any output showing `18789` bound to `0.0.0.0` or `*`.

---

## 6. /opt/elis/ structure (AC6)

```bash
ssh elis-server "ls /opt/elis/"
```

Expected PASS output:
```text
repo
```

FAIL condition: directory absent or `repo` missing.

---

## 7. ELIS repo — branch and currency (AC6)

```bash
ssh elis-server "cd /opt/elis/repo && git branch --show-current && git log -1 --oneline && git fetch origin && git status -sb"
```

Expected PASS: on `main`, up to date with `origin/main`.

FAIL condition: detached HEAD, or behind origin by more than 0 commits without documented reason.

**To update if stale:**
```bash
ssh elis-server "cd /opt/elis/repo && git pull"
```

---

## 8. ELIS CLI functional (AC6)

```bash
ssh elis-server "elis --help 2>&1 | head -2"
```

Expected PASS output:
```text
usage: elis [-h]
            {validate,harvest,merge,dedup,screen,agentic,export-latest} ...
```

FAIL condition: `command not found`.

> **Note:** CLI is installed via `/opt/elis/repo/.venv/bin/elis` with a system symlink at
> `/usr/local/bin/elis`. If the symlink is missing, restore with:
> ```bash
> ssh elis-server "sudo ln -sf /opt/elis/repo/.venv/bin/elis /usr/local/bin/elis"
> ```

---

## Quick full run (all ACs in one pass)

```bash
ssh elis-server "
  echo '=== AC1 SSH ===' && sudo sshd -T | grep -E 'passwordauthentication|permitrootlogin'
  echo '=== AC2 UFW ===' && sudo ufw status numbered
  echo '=== AC3 fail2ban ===' && sudo fail2ban-client status sshd
  echo '=== AC4 Docker ===' && docker info 2>&1 | grep 'Server Version' && docker compose version
  echo '=== AC5 OpenClaw ===' && (ss -lntp | grep 18789 || echo 'port 18789 not bound (expected)')
  echo '=== AC6 /opt/elis ===' && ls /opt/elis/
  echo '=== AC6 repo ===' && cd /opt/elis/repo && git log -1 --oneline && git status -sb
  echo '=== AC6 CLI ===' && elis --help 2>&1 | head -2
"
```

---

## Remediation reference

| Symptom | Fix |
|---|---|
| `passwordauthentication yes` | `sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config && sudo systemctl restart sshd` |
| `permitrootlogin` not `no` | `sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && sudo systemctl restart sshd` |
| UFW inactive | `sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw --force enable` |
| fail2ban jail missing | `sudo systemctl enable fail2ban && sudo systemctl start fail2ban` |
| `elis` not found | `sudo ln -sf /opt/elis/repo/.venv/bin/elis /usr/local/bin/elis` |
| Repo stale | `cd /opt/elis/repo && git pull` |
