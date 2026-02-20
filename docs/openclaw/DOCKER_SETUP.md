# OpenClaw Docker Setup (PE-OC-01)

This PE provides only OpenClaw bootstrap scaffolding.
Workspace content is intentionally deferred to PE-OC-02 through PE-OC-05.

## Files created
- `docker-compose.yml`
- `openclaw/openclaw.json` (stub)
- `openclaw/workspaces/workspace-pm/` (scaffold)
- `scripts/deploy_openclaw_workspaces.sh`

## Start OpenClaw
```bash
docker compose up -d
```

## Prepare workspaces scaffold
```bash
bash scripts/deploy_openclaw_workspaces.sh
```

## Notes
- `openclaw/openclaw.json` is a placeholder config for bootstrap validation only.
- Populate workspace contents in subsequent PEs.
