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
- Public IPv4: `<fill-from-host>`
- Operator: `<fill-during-execution>`
- Execution date (UTC): `<fill-during-execution>`

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
<PASTE OUTPUT>
```

2. UFW active with least-privilege ingress (22/80/443 only where required).
- Evidence command:
```bash
ufw status numbered
```
- Evidence output:
```text
<PASTE OUTPUT>
```

3. fail2ban jail active for SSH.
- Evidence command:
```bash
fail2ban-client status sshd
```
- Evidence output:
```text
<PASTE OUTPUT>
```

4. Docker + Compose installed and functional.
- Evidence commands:
```bash
sudo -u elis -H docker info
sudo -u elis -H docker compose version
```
- Evidence output:
```text
<PASTE OUTPUT>
```

5. OpenClaw gateway not internet-exposed (localhost-only access) and baseline artefact committed.
- Evidence command:
```bash
ss -lntp | grep -E '18789|:80|:443' || true
```
- Evidence output:
```text
<PASTE OUTPUT>
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
