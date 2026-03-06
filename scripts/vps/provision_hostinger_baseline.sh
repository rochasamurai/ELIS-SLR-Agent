#!/usr/bin/env bash
set -euo pipefail

# PE-VPS-00 baseline provisioning for Hostinger Ubuntu 24 LTS hosts.
# This script hardens SSH, enables UFW/fail2ban, installs Docker/Compose,
# and prepares /opt/elis directory layout.

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo bash scripts/vps/provision_hostinger_baseline.sh <deploy_user> <ssh_pubkey_file>"
  exit 1
fi

DEPLOY_USER="${1:-elis}"
SSH_PUBKEY_FILE="${2:-}"
TIMEZONE="${TIMEZONE:-Europe/London}"

if [[ -z "${SSH_PUBKEY_FILE}" || ! -f "${SSH_PUBKEY_FILE}" ]]; then
  echo "Missing SSH public key file. Usage: $0 <deploy_user> <ssh_pubkey_file>"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "[1/9] Installing base security packages..."
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates curl gnupg lsb-release ufw fail2ban unattended-upgrades apt-transport-https

echo "[2/9] Configuring timezone (${TIMEZONE})..."
timedatectl set-timezone "${TIMEZONE}"

echo "[3/9] Creating deploy user (${DEPLOY_USER})..."
if ! id -u "${DEPLOY_USER}" >/dev/null 2>&1; then
  adduser --disabled-password --gecos "" "${DEPLOY_USER}"
fi
usermod -aG sudo "${DEPLOY_USER}"

install -d -m 700 "/home/${DEPLOY_USER}/.ssh"
install -m 600 "${SSH_PUBKEY_FILE}" "/home/${DEPLOY_USER}/.ssh/authorized_keys"
chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "/home/${DEPLOY_USER}/.ssh"

echo "[4/9] Hardening SSH (key-only auth, root login disabled)..."
install -d -m 755 /etc/ssh/sshd_config.d
cat >/etc/ssh/sshd_config.d/99-elis-hardening.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
UsePAM yes
PubkeyAuthentication yes
PermitRootLogin no
EOF
sshd -t
systemctl restart ssh

echo "[5/9] Enabling UFW least-privilege policy..."
ufw --force default deny incoming
ufw --force default allow outgoing
ufw --force allow OpenSSH
ufw --force allow 80/tcp
ufw --force allow 443/tcp
ufw --force enable

echo "[6/9] Installing Docker Engine + Compose plugin..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
ARCH="$(dpkg --print-architecture)"
CODENAME="$(. /etc/os-release && echo "${VERSION_CODENAME}")"
cat >/etc/apt/sources.list.d/docker.list <<EOF
deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${CODENAME} stable
EOF
apt-get update
apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
usermod -aG docker "${DEPLOY_USER}"

echo "[7/9] Enabling fail2ban SSH jail..."
cat >/etc/fail2ban/jail.d/sshd.local <<'EOF'
[sshd]
enabled = true
backend = systemd
maxretry = 5
findtime = 10m
bantime = 1h
EOF
systemctl enable --now fail2ban

echo "[8/9] Enabling unattended security upgrades..."
dpkg-reconfigure -f noninteractive unattended-upgrades

echo "[9/9] Preparing ELIS directories under /opt/elis..."
install -d -m 750 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" /opt/elis/config
install -d -m 700 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" /opt/elis/secrets
install -d -m 750 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" /opt/elis/data
install -d -m 750 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" /opt/elis/logs

echo
echo "Baseline provisioning complete."
echo "Next step: run scripts/vps/verify_hostinger_baseline.sh ${DEPLOY_USER}"
echo "Note: keep OpenClaw gateway bound to localhost/Tailscale only; do not open port 18789 publicly."
