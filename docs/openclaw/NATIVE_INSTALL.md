# OpenClaw Native Install Notes

**Status:** active runtime on `elis-server`
**Runtime:** native `systemd --user` service
**Introduced:** PE-MS-01

---

## Runtime Layout

- App directory: `/opt/openclaw/`
- CLI entrypoint: `/usr/local/bin/openclaw`
- Canonical platform repo: `/opt/elis/repo/`
- State directory: `~/.openclaw/`
- PM workspace: `~/openclaw/workspace-pm/`
- Programs workspaces: `~/openclaw/workspace-prog-impl/`, `~/openclaw/workspace-prog-val/`
- Infrastructure workspaces: `~/openclaw/workspace-infra-impl/`, `~/openclaw/workspace-infra-val/`
- SLR phase workspaces:
  - `~/openclaw/workspace-slr-harvest/`
  - `~/openclaw/workspace-slr-screen/`
  - `~/openclaw/workspace-slr-extract/`
  - `~/openclaw/workspace-slr-synth/`
  - `~/openclaw/workspace-slr-prisma/`
- SLR project root: `/opt/elis/projects/`
- Service file: `~/.config/systemd/user/openclaw-gateway.service`

## Day-to-Day Commands

```bash
systemctl --user status openclaw-gateway
systemctl --user restart openclaw-gateway
journalctl --user -u openclaw-gateway -n 100
openclaw doctor
openclaw channels status
openclaw approvals get --gateway
```

Authoritative operating procedures:

- `docs/openclaw/DEPLOYMENT.md` for deploy + restart flow
- `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md` for Discord-side PM validation
- `docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md` for routine operations and restore

## Docker Decommission On `elis-server`

Perform this only after the native service is verified healthy:

```bash
systemctl --user status openclaw-gateway
openclaw doctor
openclaw channels status
docker ps -a
sudo systemctl stop docker
sudo apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo apt-get autoremove -y
docker --version
docker compose version
```

Expected end state:

- `openclaw-gateway.service` remains active
- `openclaw doctor` still succeeds
- `docker` and `docker compose` are no longer available on `elis-server`
- No legacy `openclaw` container remains

## Workspace Conventions

- PM Agent instructions must use host paths, not `/app/...` container paths.
- Runtime docs must reference `systemctl --user` service management, not `docker compose`.
- PM reads governance state through workspace entrypoints (`~/openclaw/workspace-pm/CURRENT_PE.md`, `~/openclaw/workspace-pm/MEMORY.md`, `~/openclaw/workspace-pm/docs/PLAN_CURRENT.md`). These entrypoints resolve the active release state without hardcoding an obsolete plan version and avoid Discord elevated-exec approval timeouts.
- Do not instruct the PM Agent to read `/opt/elis/repo/...` directly in Discord sessions.
- SLR review artifacts belong under `/opt/elis/projects/<review-id>/`, not in OpenClaw runtime state.
- Generic `workspace-slr-impl` / `workspace-slr-val` are retired after PE-MS-06 and must not be redeployed.
- After updating the repo config, run `bash scripts/deploy_openclaw_workspaces.sh` and `systemctl --user restart openclaw-gateway` so the 19-agent source-controlled roster becomes live on `elis-server`.

## Migration Note

`docker-compose.yml` is retained in the repo only as a historical migration artifact. The production runtime on `elis-server` is native, and Docker/Compose should be removed from the host once the native service is verified.
