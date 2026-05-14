#!/usr/bin/env bash
set -euo pipefail

SECRET_FILE="${SECRET_FILE:-/run/secrets/elis-advisor.env}"

if [[ -n "${SECRET_FILE:-}" && -r "$SECRET_FILE" ]]; then
  # Intentionally do not print secret contents.
  :
fi

exec "$@"
