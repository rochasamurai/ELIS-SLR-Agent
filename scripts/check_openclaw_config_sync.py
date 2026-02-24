"""check_openclaw_config_sync.py — verify live container agent list matches repo config.

Compares agent IDs declared in ``openclaw/openclaw.json`` against the agent list
reported by the running OpenClaw container.  Exits 1 if any declared agent is
absent from the live list.  Exits 0 when in sync or when Docker is unreachable
(non-blocking in CI where no container runs).
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "openclaw" / "openclaw.json"
CONTAINER_NAME = "openclaw"


def _declared_agent_ids(config_path: pathlib.Path) -> list[str]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return [a["id"] for a in data.get("agents", {}).get("list", [])]


def _live_agent_ids(container: str) -> list[str] | None:
    """Return agent IDs from the running container, or None if unreachable."""
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                container,
                "node",
                "/app/openclaw.mjs",
                "agents",
                "list",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(f"Docker not available: {exc}. Skipping live sync check.")
        return None

    if result.returncode != 0:
        print(
            f"Container '{container}' not reachable "
            f"(exit {result.returncode}). Skipping live sync check."
        )
        return None

    ids: list[str] = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and not stripped.startswith("- -"):
            # Lines like "- pm" or "- slr-impl-codex"
            agent_id = stripped[2:].split()[0]
            ids.append(agent_id)
        elif stripped.startswith("* "):
            # Lines like "* main (default)"
            agent_id = stripped[2:].split()[0]
            ids.append(agent_id)
    return ids


def main() -> int:
    if not CONFIG_PATH.exists():
        print(f"FAIL: config not found at {CONFIG_PATH}", file=sys.stderr)
        return 1

    declared = _declared_agent_ids(CONFIG_PATH)
    print(f"Declared agents ({len(declared)}): {', '.join(declared)}")

    live = _live_agent_ids(CONTAINER_NAME)
    if live is None:
        print("Non-blocking: Docker unreachable — skipping sync verification.")
        return 0

    print(f"Live agents ({len(live)}): {', '.join(live)}")

    missing = [aid for aid in declared if aid not in live]
    if missing:
        print(
            f"FAIL: {len(missing)} agent(s) declared in openclaw.json but missing "
            f"from live container: {', '.join(missing)}",
            file=sys.stderr,
        )
        print(
            "Run: bash scripts/deploy_openclaw_workspaces.sh && "
            "docker compose down && docker compose up -d",
            file=sys.stderr,
        )
        return 1

    print("OK: all declared agents are present in the live container.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
