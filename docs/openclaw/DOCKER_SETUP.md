# OpenClaw Docker Setup (PE-OC-01)

This PE provides only OpenClaw bootstrap scaffolding.
Workspace content is intentionally deferred to PE-OC-02 through PE-OC-05.

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
