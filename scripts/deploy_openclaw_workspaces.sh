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

# Deploy openclaw config to container state directory.
# Merges repo config (agents, bindings, commands, plugins) with the live state dir config,
# preserving the `channels` and `meta` keys which contain runtime secrets (botToken etc.)
# that must NEVER be committed to the repository.
CONFIG_SRC="$ROOT_DIR/openclaw/openclaw.json"
CONFIG_DEST="$HOME/.openclaw/openclaw.json"
mkdir -p "$(dirname "$CONFIG_DEST")"
python3 - "$CONFIG_SRC" "$CONFIG_DEST" <<'PYEOF'
import json, pathlib, sys

src = pathlib.Path(sys.argv[1])
dest = pathlib.Path(sys.argv[2])

repo_cfg = json.loads(src.read_text(encoding="utf-8"))

if dest.exists():
    try:
        state_cfg = json.loads(dest.read_text(encoding="utf-8"))
        # Preserve runtime-only keys that hold secrets
        for key in ("channels", "meta"):
            if key in state_cfg:
                repo_cfg[key] = state_cfg[key]
    except (json.JSONDecodeError, OSError):
        pass  # corrupt/missing state config — overwrite fully

dest.write_text(json.dumps(repo_cfg, indent=2) + "\n", encoding="utf-8")
PYEOF
echo "OpenClaw config deployed to: $CONFIG_DEST (channels/meta preserved)"
echo ""
echo "Restart the container to apply the new config:"
echo "  docker compose down && docker compose up -d"
