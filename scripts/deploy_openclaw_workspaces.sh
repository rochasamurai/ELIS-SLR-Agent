#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/openclaw/workspaces"
TARGET_ROOT="$HOME/openclaw"
TARGET_PM="$TARGET_ROOT/workspace-pm"

mkdir -p "$TARGET_PM"

if command -v rsync >/dev/null 2>&1; then
  rsync -av --delete "$SRC_DIR/" "$TARGET_ROOT/"
else
  rm -rf "$TARGET_PM"
  mkdir -p "$TARGET_PM"
  cp -R "$SRC_DIR/workspace-pm/." "$TARGET_PM/" 2>/dev/null || true
fi

echo "OpenClaw workspaces deployed to: $TARGET_ROOT"

# Deploy openclaw config to container state directory
CONFIG_SRC="$ROOT_DIR/openclaw/openclaw.json"
CONFIG_DEST="$HOME/.openclaw/openclaw.json"
mkdir -p "$(dirname "$CONFIG_DEST")"
cp "$CONFIG_SRC" "$CONFIG_DEST"
echo "OpenClaw config deployed to: $CONFIG_DEST"
echo ""
echo "Restart the container to apply the new config:"
echo "  docker compose down && docker compose up -d"
