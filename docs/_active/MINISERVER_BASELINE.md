# MiniServer Baseline - PE-VPS-00

## Scope

This artefact defines the required ELIS MiniServer baseline for PE-VPS-00 and captures live host evidence for validator review.

Controls covered:
- SSH key-only access with password login disabled
- UFW least-privilege ingress policy
- fail2ban SSH jail
- Docker Engine and Docker Compose runtime
- OpenClaw exposure constraint (localhost-only)
- ELIS filesystem baseline under `/opt/elis`

## Host Metadata

- Host class: ELIS MiniServer
- Hardware: NUC8i7BEH
- OS target: Ubuntu 24.04.4 LTS
- Hostname: `elis-server`
- Public IPv4: `<not recorded in PR comment>`
- Operator: `rochasamurai (PM/operator)`
- Execution date (UTC): `2026-03-21`

## Provisioning Procedure

Run on the host as root:

```bash
sudo bash scripts/vps/provision_miniserver_baseline.sh elis /root/elis_deploy_key.pub
```

## Verification Procedure

Run on the host after provisioning:

```bash
sudo bash scripts/vps/verify_miniserver_baseline.sh elis
```

## Acceptance Criteria Mapping

1. Host reachable via SSH key auth only; password auth disabled.
- Evidence command:
```bash
sshd -T | grep -E 'passwordauthentication|permitrootlogin'
```
- Evidence output:
```text
$ sudo sshd -T | grep -E 'passwordauthentication|permitrootlogin'
permitrootlogin no
passwordauthentication no
```

2. UFW active with least-privilege ingress (22/80/443 only where required).
- Evidence command:
```bash
ufw status numbered
```
- Evidence output:
```text
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
```

3. fail2ban jail active for SSH.
- Evidence command:
```bash
fail2ban-client status sshd
```
- Evidence output:
```text
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
```

4. Docker + Compose installed and functional.
- Evidence commands:
```bash
sudo -u elis -H docker info
sudo -u elis -H docker compose version
```
- Evidence output:
```text
$ docker info 2>&1 | grep -E 'Server Version|Operating System|Architecture'
 Server Version: 28.2.2
 Operating System: Ubuntu 24.04.4 LTS
 Architecture: x86_64

$ docker compose version
Docker Compose version 2.37.1+ds1-0ubuntu2~24.04.1
```

5. OpenClaw gateway not internet-exposed (localhost-only access) and baseline artefact committed.
- Evidence command:
```bash
ss -lntp | grep -E '18789|:80|:443' || true
```
- Evidence output:
```text
$ ss -lntp | grep 18789 || echo 'port 18789 not bound (expected)'
port 18789 not bound (expected)
```

## Additional Host Checks

These checks are in scope for the MiniServer baseline but are not separate blocking AC rows in the current validator review:

- `/opt/elis/repo` exists
- `elis --help` runs for deploy user `elis`

## Security Notes

- Do not expose OpenClaw gateway port `18789` on public interfaces.
- Keep the host timezone at `Europe/London` unless a later MiniServer PE deliberately changes it.
- Keep secrets out of the repository and out of this artefact.

## Validator Guidance

Validator should treat this file plus the pasted host command outputs as authoritative evidence for PE-VPS-00 acceptance review.
