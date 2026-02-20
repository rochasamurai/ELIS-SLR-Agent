#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACES_DIR="$ROOT_DIR/openclaw/workspaces"

mkdir -p "$WORKSPACES_DIR/workspace-pm"
echo "OpenClaw workspaces scaffold ready at: $WORKSPACES_DIR"
