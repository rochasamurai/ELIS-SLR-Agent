# OpenClaw Docker Setup (PE-OC-01)

This PE provides only OpenClaw bootstrap scaffolding.
Workspace content is intentionally deferred to PE-OC-02 through PE-OC-05.

## Host prerequisites (required before any `docker` command)

These must be installed on the host machine before running any step in this runbook.
Confirm each with the verification command before proceeding.

| Prerequisite | Minimum version | Verify |
|---|---|---|
| Docker Desktop for Windows | 4.x | `docker --version` |
| WSL 2 (auto-installed by Docker Desktop) | kernel ≥ 5.10 | `wsl --status` |

**Install Docker Desktop:**
1. Download from https://www.docker.com/products/docker-desktop/
2. Run the installer (requires administrator privileges)
3. Restart Windows when prompted
4. Open Docker Desktop and complete the WSL 2 setup if prompted
5. Verify: `docker --version` and `docker compose version` both return successfully

> **Note:** If `docker` is not found in Git Bash after installation, open a new terminal
> session — Docker Desktop adds itself to the Windows PATH on install but existing
> sessions do not pick it up automatically.

**Security note (§5.4):** The ELIS repository must **never** be mounted as a Docker volume.
See Volume policy below.

## Files created
- `docker-compose.yml`
- `openclaw/openclaw.json` (stub)
- `openclaw/workspaces/workspace-pm/` (scaffold)
- `scripts/deploy_openclaw_workspaces.sh`
- `scripts/check_openclaw_health.py`

## Port and exposure policy
- Host binding: `127.0.0.1:18789:3000`
- OpenClaw is exposed on localhost only.

## Volume policy
- ELIS repository paths are **not** mounted into the container.
- Docker volumes mount from `${HOME}`-based host OpenClaw paths:
  - `${HOME}/.openclaw` -> `/app/.openclaw`
  - `${HOME}/openclaw/workspace-pm` -> `/app/workspaces/workspace-pm`

## Start OpenClaw
```bash
docker compose up -d
```

## Deploy workspace scaffold to host
```bash
bash scripts/deploy_openclaw_workspaces.sh
```

## Health check
```bash
python scripts/check_openclaw_health.py
```

## Notes
- `openclaw/openclaw.json` is a PE-OC-01 stub and follows `agents.list` + `bindings` shape.
- Full workspace contents and agent wiring are implemented in subsequent PEs.
