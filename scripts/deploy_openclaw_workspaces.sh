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
