## Agent update — Claude Code / PE-OC-01 / 2026-02-20

### Verdict
FAIL

### Gate results
black: N/A (no Python added)
ruff: N/A (no Python added)
pytest: N/A (no Python added)

### Scope
M HANDOFF.md
A docker-compose.yml
A docs/openclaw/DOCKER_SETUP.md
A openclaw/openclaw.json
A openclaw/workspaces/workspace-pm/.gitkeep
A scripts/deploy_openclaw_workspaces.sh

### Required fixes

F1: `docker-compose.yml` — port 3000:3000 with no localhost restriction. Plan §2.4 requires
port 18789 on 127.0.0.1 only. Fix: `ports: ["127.0.0.1:18789:<INTERNAL_PORT>"]`.

F2: `docker-compose.yml` — ELIS repo directories mounted directly into container via
`./openclaw/openclaw.json` and `./openclaw/workspaces`. Plan §2.4/§5.4 hard prohibition.
Fix: `docker-compose.yml` must mount from `~/openclaw/` (host), not from the repo.
`deploy_openclaw_workspaces.sh` must rsync `openclaw/workspaces/` → `~/openclaw/` on the host.

F3: `scripts/check_openclaw_health.py` absent. Explicitly listed as a PE-OC-01 deliverable
in the plan. Must be created and wired into CI.

### Findings

Non-blocking NB1: Image `openclaw/openclaw:latest` (Docker Hub) vs plan's
`ghcr.io/openclaw/openclaw:latest` (GHCR). Confirm correct registry; update if plan is
authoritative.

Non-blocking NB2: `openclaw.json` format deviates from plan §2.5 schema (`agents.list` +
`bindings`). Acceptable placeholder for PE-OC-01; PE-OC-02 must migrate to plan schema.

### Evidence

#### Files read

| File | Lines | What was checked |
|------|-------|-----------------|
| `docker-compose.yml` | 12 | Service definition, image, port binding, volume mounts, restart policy |
| `openclaw/openclaw.json` | 13 | Agent config format, workspace registration, secret handling |
| `docs/openclaw/DOCKER_SETUP.md` | 24 | Runbook completeness, accuracy of commands |
| `scripts/deploy_openclaw_workspaces.sh` | 8 | Script logic, safety flags, deploy target |
| `openclaw/workspaces/workspace-pm/.gitkeep` | 1 | Scaffold presence |
| `HANDOFF.md` | full | Scope claims, AC checklist, validation commands |

#### Commands run

```text
git fetch origin feature/pe-oc-01-docker-setup

gh api repos/rochasamurai/ELIS-SLR-Agent/compare/main...feature/pe-oc-01-docker-setup \
  --jq '{ahead_by, behind_by, merge_base_commit: .merge_base_commit.sha, files: [.files[].filename]}'
# → ahead_by: 1, behind_by: 0
# → merge_base: 63277027af52086ccf6a89f3796b14b720b47ba0 (current main tip)
# → files: ["HANDOFF.md","docker-compose.yml","docs/openclaw/DOCKER_SETUP.md",
#            "openclaw/openclaw.json","openclaw/workspaces/workspace-pm/.gitkeep",
#            "scripts/deploy_openclaw_workspaces.sh"]
```

#### Key claims verified

| Claim | Source | Result |
|-------|--------|--------|
| Scope = 6 files vs main | GitHub compare API | PASS — 6 files, 1 ahead 0 behind |
| `docker-compose.yml` created | File read | PASS |
| Port 18789 on localhost only (plan §2.4, AC#3) | `docker-compose.yml` ports | FAIL — `3000:3000`, no 127.0.0.1 binding |
| ELIS repo NOT mounted in container (plan §5.4, AC#4) | `docker-compose.yml` volumes | FAIL — `./openclaw/...` paths are ELIS repo |
| `scripts/check_openclaw_health.py` present | Glob | FAIL — file absent |
| `openclaw/openclaw.json` created | File read | PASS — stub present |
| `docs/openclaw/DOCKER_SETUP.md` created | File read | PASS |
| `scripts/deploy_openclaw_workspaces.sh` created | File read | PASS |
| `HANDOFF.md` updated with PE-OC-01 content | File read | PASS |
