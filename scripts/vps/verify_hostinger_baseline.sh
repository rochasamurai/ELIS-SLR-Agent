#!/usr/bin/env bash
set -euo pipefail

# PE-VPS-00 verification script for Hostinger baseline controls.

DEPLOY_USER="${1:-elis}"
FAIL=0

check() {
  local label="$1"
  local cmd="$2"
  if bash -lc "$cmd" >/tmp/elis_check.out 2>/tmp/elis_check.err; then
    echo "[OK] ${label}"
  else
    echo "[ERR] ${label}"
    if [[ -s /tmp/elis_check.out ]]; then
      cat /tmp/elis_check.out
    fi
    if [[ -s /tmp/elis_check.err ]]; then
      cat /tmp/elis_check.err
    fi
    FAIL=1
  fi
}

check "SSH password auth disabled" "sshd -T | grep -E '^passwordauthentication no$'"
check "Root SSH login disabled" "sshd -T | grep -E '^permitrootlogin no$'"
check "UFW active" "ufw status | grep -E '^Status: active$'"
check "UFW allows SSH" "ufw status numbered | grep -E '22|OpenSSH'"
check "UFW allows HTTP" "ufw status numbered | grep -E '80/tcp'"
check "UFW allows HTTPS" "ufw status numbered | grep -E '443/tcp'"
check "fail2ban sshd jail active" "fail2ban-client status sshd | grep -E 'Status for the jail: sshd'"
check "Docker engine available" "sudo -u ${DEPLOY_USER} -H docker info >/dev/null"
check "Docker Compose available" "sudo -u ${DEPLOY_USER} -H docker compose version"
check "OpenClaw port not public" "! ss -lntp | grep -E ':(18789)\s' | grep -E '0\.0\.0\.0|\[::\]'"
check "ELIS directory layout present" "test -d /opt/elis/config && test -d /opt/elis/secrets && test -d /opt/elis/data && test -d /opt/elis/logs"

if [[ "${FAIL}" -ne 0 ]]; then
  echo "PE-VPS-00 baseline verification FAILED"
  exit 1
fi

echo "PE-VPS-00 baseline verification PASSED"
