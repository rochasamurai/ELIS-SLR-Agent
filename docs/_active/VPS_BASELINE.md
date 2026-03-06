# VPS Baseline - PE-VPS-00 (Hostinger Ubuntu 24 LTS)

## Scope

This artifact defines the required host baseline for PE-VPS-00 and captures evidence for validator review.

Controls covered:
- SSH key-only access (password login disabled, root SSH disabled)
- UFW least-privilege ingress policy
- fail2ban SSH jail
- Docker Engine + Docker Compose runtime
- OpenClaw exposure constraint (localhost/Tailscale-only)
- ELIS filesystem baseline under `/opt/elis`

## Host Metadata

- Provider: Hostinger VPS
- OS target: Ubuntu 24 LTS
- Hostname: `<set-during-execution>`
- Public IPv4: `<set-during-execution>`
- Operator: `<name>`
- Execution date (UTC): `<YYYY-MM-DDTHH:MM:SSZ>`

## Provisioning Procedure

Run on the host as root:

```bash
sudo bash scripts/vps/provision_hostinger_baseline.sh elis /root/elis_deploy_key.pub
```

## Verification Procedure

Run on the host after provisioning:

```bash
sudo bash scripts/vps/verify_hostinger_baseline.sh elis
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

5. OpenClaw gateway not internet-exposed (localhost/Tailscale-only).
- Evidence command:
```bash
ss -lntp | grep -E '18789|:80|:443' || true
```
- Evidence output:
```text
<PASTE OUTPUT>
```

## Security Notes

- Do not expose OpenClaw gateway port `18789` on public interfaces.
- Keep VPS timezone at `Europe/London` (VPS policy) while manifests remain UTC.
- Keep secrets out of repo and out of this artifact.

## Validator Guidance

Validator should treat this file plus host command outputs as authoritative evidence for PE-VPS-00 acceptance review.
