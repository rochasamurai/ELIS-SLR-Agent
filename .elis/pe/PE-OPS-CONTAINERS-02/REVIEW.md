# REVIEW — PE-OPS-CONTAINERS-02 Phase A (Build/Preflight)

**Validator:** infra-val-b  
**Date:** 2026-05-14T15:42Z  
**Branch:** feature/pe-ops-containers-02-elis-advisor-hermes-container-pilot  
**Base HEAD:** 1b5d0958144f343cc89d8ab4e3b5d1a8d0f7ad06  
**Review HEAD:** 46ee5ff  

---

## Verdict: PASS

Phase A (build/preflight only) passes all validation checks.  
**Phase B launch/cutover is NOT approved.**

---

## Scope

```
A	.elis/pe/PE-OPS-CONTAINERS-02/HANDOFF.md
A	.elis/pe/PE-OPS-CONTAINERS-02/PE_TASK.md
A	.elis/pe/PE-OPS-CONTAINERS-02/implementation-plan.md
A	.elis/pe/PE-OPS-CONTAINERS-02/rollback-plan.md
A	.elis/pe/PE-OPS-CONTAINERS-02/runtime-inventory.md
A	.elis/pe/PE-OPS-CONTAINERS-02/validation-evidence.md
A	.elis/pe/PE-OPS-CONTAINERS-02/wrong-branch-recovery.md
A	ops/containers/elis-advisor/Dockerfile
A	ops/containers/elis-advisor/README.md
A	ops/containers/elis-advisor/docker-compose.yml
A	ops/containers/elis-advisor/entrypoint.sh
```

---

## Phase A Secret-Handling Review

### 1. Backup directory permissions (700)

```
$ stat -c '%a %n' /opt/elis/agent-worktrees/PE-OPS-CONTAINERS-02-infra-impl-a/backup
700 /opt/elis/agent-worktrees/PE-OPS-CONTAINERS-02-infra-impl-a/backup

$ stat -c '%a %n' /opt/elis/agent-worktrees/PE-OPS-CONTAINERS-02-infra-impl-a/backup/{config,data}
700 /opt/elis/agent-worktrees/PE-OPS-CONTAINERS-02-infra-impl-a/backup/config
700 /opt/elis/agent-worktrees/PE-OPS-CONTAINERS-02-infra-impl-a/backup/data
```

✅ PASS — All backup directories are 700.

### 2. Backup .env file permissions (600)

```
$ stat -c '%a %n' /home/samurai/.hermes/profiles/elis-advisor/.env
600 /home/samurai/.hermes/profiles/elis-advisor/.env

$ stat -c '%a %n' /home/samurai/backups/elis-rebuild/.openclaw.20260413T154555Z/.env
600 /home/samurai/backups/elis-rebuild/.openclaw.20260413T154555Z/.env
```

✅ PASS — All .env files are 600.

### 3. No .env contents or secret values in evidence/logs/commits

- Dockerfile has no COPY .env directive.
- entrypoint.sh intentionally does not print secret contents.
- No .env file exists in the Docker build context directory.
- Git log for the branch diff contains no .env file changes.
- Build output contains no secret values.

✅ PASS — No secret leakage detected.

### 4. Dockerfile does not COPY .env

```
$ grep -n "COPY.*\.env" ops/containers/elis-advisor/Dockerfile
(empty — exit code 1)
```

✅ PASS — No .env COPY in Dockerfile.

### 5. Image does not contain .env

```
$ docker run --rm --entrypoint="" elis-advisor:phasea-review find / -name ".env" -type f
(empty — exit code 1)
```

✅ PASS — No .env file in image.

---

## Phase A Build/Preflight Checks

### 6. compose config passes

```
$ cd ops/containers/elis-advisor && docker compose config
services:
  elis-advisor:
    build:
      context: …
    container_name: elis-advisor-container
    restart: "no"
    user: "1000:1000"
    volumes:
    - …/.hermes:/home/samurai/.hermes:ro
```

✅ PASS

### 7. Image build passes

```
$ docker build -t elis-advisor:phasea-review .
#8 DONE 2.0s — exit 0
```

✅ PASS

### 8. Image inspect passes

```
$ docker inspect elis-advisor:phasea-review --format '{{.Config.User}} {{.Config.Entrypoint}}'
elis-advisor [/bin/bash]
```

✅ PASS — Runs as non-root user `elis-advisor`, entrypoint is `/bin/bash`.

### 9. Mount plan matches approved scope

- `~/.hermes:/home/samurai/.hermes:ro` — scoped read-only mount, not broad `/home/samurai` ✅
- No `/opt/elis` mount ✅
- No Docker socket mount ✅
- No GitHub credential access ✅
- No OpenClaw production agent access ✅

✅ PASS

---

## Phase A No-Runtime-Launch Review

### 10. No container was started

```
$ docker ps -a --filter name=elis-advisor-container
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

✅ PASS — No elis-advisor-container exists.

### 11. elis-advisor-container.service was not started or enabled

```
$ systemctl --user list-unit-files | grep elis-advisor
elis-advisor-gateway.service   enabled   enabled
```

Only `elis-advisor-gateway.service` exists (pre-existing). No `elis-advisor-container.service`.

✅ PASS

### 12. Live elis-advisor-gateway.service remained unchanged and running

```
$ systemctl --user status elis-advisor-gateway.service
Active: active (running) since Mon 2026-05-11 09:36:26 BST; 3 days ago
```

✅ PASS — Service running, unchanged.

### 13. No production services affected

Running services confirmed unchanged:
- `openclaw-gateway.service` — active (running)
- `hermes-gateway.service` — active (running)
- `elis-advisor-gateway.service` — active (running)

✅ PASS

---

## Infra-Specific Checks (AGENTS.md §3.2)

### Shell script header compliance

```
$ grep -n "#!/usr/bin/env bash" ops/containers/elis-advisor/entrypoint.sh
1:#!/usr/bin/env bash
$ grep -n "set -euo pipefail" ops/containers/elis-advisor/entrypoint.sh
2:set -euo pipefail
```

✅ PASS

### Variable quoting

entrypoint.sh uses `"${SECRET_FILE:-}"` — properly quoted.

✅ PASS

### Port binding

No port mappings in compose file.

✅ PASS (N/A)

### Docker image tag policy

Dockerfile uses `ubuntu:22.04` (pinned). No `:latest` tags.

✅ PASS

### CI secret handling / Container isolation / CI naming / YAML lint

No workflow files or compose files with ELIS mounts in the PR diff. All YAML parses correctly.

✅ PASS

---

## Adversarial Test

Confirmed that a container run with a missing secret file exits cleanly (set -euo pipefail + conditional check in entrypoint). The entrypoint intentionally does not print secret contents even when the file exists.

---

## Phase B Status

**Phase B launch/cutover is NOT approved.** This review covers Phase A (build/preflight) only.

---

## Required Fixes

None (blocking findings: 0)
