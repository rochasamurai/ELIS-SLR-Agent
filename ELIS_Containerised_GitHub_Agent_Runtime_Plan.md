# PE-OPS-CONTAINER-GITHUB-01 — Containerise ELIS GitHub Agent Runtime

## Context and correction

The previous host-level model, “one agent = one Linux user”, was directionally correct for security but incomplete for the current OpenClaw runtime.

It only works cleanly if OpenClaw can execute each agent process as that Linux user. In the current ELIS Server environment, the evidence showed that OpenClaw can route to `github-agent`, but the dispatched process still runs as the OpenClaw gateway user (`samurai`). This caused repeated failures around permissions, secrets, linked Git worktrees, ACLs, `safe.directory`, bootstrap files, and helper execution.

The corrected architecture is to move high-risk agent execution into containers while keeping OpenClaw as the orchestration layer.

## Architectural decision

Target model:

```text
OpenClaw continues to orchestrate agents, routing, sessions, prompts, tools, and governance workflow.

Each critical ELIS agent runs sensitive execution inside its own container.

The fixed worktree remains the only persistent writable state for the agent.

Secrets are mounted read-only into the container.

The container can be destroyed and recreated without losing the worktree or evidence.

GitHub Agent uses only elis-git-bot for GitHub operations.

PM does not execute GitHub write operations directly.
```

For the GitHub Agent pilot:

```text
Container: elis-github-agent
Persistent workspace: /opt/elis/agent-worktrees/github-agent
Secret file: /opt/elis/secrets/github-agent.env
GitHub identity: elis-git-bot
GitHub config directory: /workspace/.config/gh
```

## Proposed PE

```text
PE-OPS-CONTAINER-GITHUB-01 — Containerise ELIS GitHub Agent Runtime
```

Governance lane: **Strict PE**

## Objective

Replace the current host-user / ACL / helper approach for ELIS GitHub Agent with a containerised runtime that:

- preserves OpenClaw as the orchestration layer;
- isolates GitHub Agent execution;
- uses `elis-git-bot` only;
- mounts only the required workspace and secret;
- avoids ambient `rochasamurai` GitHub authentication;
- supports controlled GitHub actions such as branch push and PR creation;
- can be destroyed and recreated without losing persistent worktree state.

## Phase 0 — Freeze and preserve current state

Before any migration work:

1. Do not remove the current GitHub Agent worktree.
2. Do not delete `/opt/elis/secrets/github-agent.env`.
3. Do not remove the `elis-github` Linux user yet.
4. Do not push/open PR/merge using the unstable current execution path.
5. Preserve current evidence and rollback state.

Suggested backup command:

```bash
sudo mkdir -p /opt/elis/backups

sudo tar -czf /opt/elis/backups/github-agent-pre-container-$(date +%Y%m%dT%H%M%S).tgz \
  /opt/elis/agent-worktrees/github-agent \
  /opt/elis/secrets/github-agent.env \
  /home/samurai/.openclaw/openclaw.json
```

Expected outcome:

```text
A rollback archive exists before containerisation begins.
```

## Phase 1 — Define the container contract

### Required mounts

```text
/opt/elis/agent-worktrees/github-agent:/workspace:rw
/opt/elis/secrets/github-agent.env:/run/secrets/github-agent.env:ro
```

### Optional read-only mount

Only if the GitHub Agent needs to inspect the canonical repo:

```text
/opt/elis/repo:/repo:ro
```

### Do not mount

```text
/opt/elis/secrets as a directory
/opt/elis/repo as read-write
/opt/elis/agent-worktrees/pm as read-write
other agent worktrees as read-write
/home/samurai/.config/gh
/home/samurai/.openclaw secrets
ambient host GitHub credentials
```

### Container user

The container should run as a non-root user.

Preferred UID/GID alignment with the host:

```text
host user: elis-github
uid: 995
gid: 983
```

Inside the image:

```text
user: elis-github
uid: 995
gid: 983
```

This reduces host bind-mount permission friction.

### Environment

The container entrypoint must load:

```text
GH_TOKEN
GITHUB_TOKEN
GH_CONFIG_DIR=/workspace/.config/gh
```

from:

```text
/run/secrets/github-agent.env
```

The token value must never be printed.

## Phase 2 — Container image

Suggested repository path:

```text
ops/containers/github-agent/Dockerfile
ops/containers/github-agent/entrypoint.sh
```

### Dockerfile

```dockerfile
FROM ubuntu:24.04

ARG UID=995
ARG GID=983

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    jq \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
       | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
       | tee /etc/apt/sources.list.d/github-cli.list >/dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g ${GID} elis-github \
    && useradd -m -u ${UID} -g ${GID} -s /bin/bash elis-github

WORKDIR /workspace

COPY entrypoint.sh /usr/local/bin/elis-github-entrypoint
RUN chmod 755 /usr/local/bin/elis-github-entrypoint

USER elis-github

ENTRYPOINT ["/usr/local/bin/elis-github-entrypoint"]
```

### entrypoint.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

SECRET_FILE="/run/secrets/github-agent.env"

if [ ! -r "$SECRET_FILE" ]; then
  echo "FAIL: missing GitHub Agent credential file: $SECRET_FILE" >&2
  exit 10
fi

set -a
source "$SECRET_FILE"
set +a

export GH_CONFIG_DIR="${GH_CONFIG_DIR:-/workspace/.config/gh}"
mkdir -p "$GH_CONFIG_DIR"

exec "$@"
```

## Phase 3 — Docker Compose definition

Suggested file:

```text
ops/containers/github-agent/docker-compose.github-agent.yml
```

Example:

```yaml
services:
  elis-github-agent:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        UID: "995"
        GID: "983"
    container_name: elis-github-agent
    working_dir: /workspace
    volumes:
      - /opt/elis/agent-worktrees/github-agent:/workspace:rw
      - /opt/elis/secrets/github-agent.env:/run/secrets/github-agent.env:ro
    environment:
      GH_CONFIG_DIR: /workspace/.config/gh
    user: "995:983"
    command: ["bash"]
    stdin_open: true
    tty: true
```

For governed operations, prefer one-shot executions:

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  gh api /user --jq .login
```

This avoids depending on long-lived container state.

## Phase 4 — Acceptance tests for the pilot

### Test 1 — GitHub identity

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  gh api /user --jq .login
```

Expected:

```text
elis-git-bot
```

### Test 2 — Repository permission

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  gh repo view rochasamurai/ELIS-Multi-AI-Agent-Platform --json nameWithOwner,viewerPermission
```

Expected:

```text
viewerPermission = WRITE
```

### Test 3 — Workspace write

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  bash -lc 'touch /workspace/.container-write-test && rm /workspace/.container-write-test && echo PASS'
```

Expected:

```text
PASS
```

### Test 4 — No access to host ambient credentials

Inside the container:

```bash
ls -ld /home/samurai/.config/gh || true
ls -ld /opt/elis/secrets || true
```

Expected:

```text
Host ambient gh credentials are not present.
The full /opt/elis/secrets directory is not mounted.
Only /run/secrets/github-agent.env is present.
```

### Test 5 — PR metadata read

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  gh pr list --repo rochasamurai/ELIS-Multi-AI-Agent-Platform --state all --limit 5
```

Expected:

```text
Command returns a PR list or an empty list without error.
```

### Test 6 — No token leakage

Search container output and evidence logs for token-like strings.

Expected:

```text
No token value printed.
```

## Phase 5 — OpenClaw-compatible integration

OpenClaw should remain the orchestration layer.

The containerised GitHub Agent execution should be exposed as a constrained operational tool, not as a replacement orchestration framework.

Suggested wrapper:

```text
/usr/local/bin/elis-github-agent-container
```

The wrapper should accept only approved verbs.

Initial verbs:

```text
status
push-current-branch
open-pr-evidence-closeout
pr-checks
```

Later, after a separate approval gate:

```text
merge-approved-pr
```

### Example wrapper

```bash
#!/usr/bin/env bash
set -euo pipefail

VERB="${1:-}"
COMPOSE_FILE="/opt/elis/repo/ops/containers/github-agent/docker-compose.github-agent.yml"

case "$VERB" in
  status)
    docker compose -f "$COMPOSE_FILE" run --rm elis-github-agent \
      bash -lc 'gh api /user --jq .login && git status --short --branch'
    ;;

  push-current-branch)
    docker compose -f "$COMPOSE_FILE" run --rm elis-github-agent \
      bash -lc 'git status --short --branch && git push -u origin HEAD'
    ;;

  open-pr-evidence-closeout)
    docker compose -f "$COMPOSE_FILE" run --rm elis-github-agent \
      gh pr create \
        --repo rochasamurai/ELIS-Multi-AI-Agent-Platform \
        --base main \
        --head chore/github-agent-evidence-closeout \
        --title "PE-OPS-GITHUB-02: record GitHub Agent evidence and isolation" \
        --body-file /workspace/.elis/pe/PE-OPS-GITHUB-02/PR_BODY_GITHUB_AGENT_EVIDENCE.md
    ;;

  pr-checks)
    docker compose -f "$COMPOSE_FILE" run --rm elis-github-agent \
      gh pr checks --repo rochasamurai/ELIS-Multi-AI-Agent-Platform
    ;;

  *)
    echo "FAIL: unsupported verb: $VERB" >&2
    exit 2
    ;;
esac
```

### Integration principle

```text
PM prepares and routes approved GitHub action packets.
OpenClaw dispatches ELIS GitHub.
ELIS GitHub invokes the constrained container wrapper.
The wrapper executes only approved verbs.
GitHub identity inside the container is elis-git-bot.
```

## Phase 6 — Retire the host-user workaround for GitHub operations

After the container pilot passes:

1. Keep `/opt/elis/agent-worktrees/github-agent` as the persistent workspace volume.
2. Keep `/opt/elis/secrets/github-agent.env` as the secret source mounted read-only.
3. Stop using `sudo -u elis-github` for GitHub operations.
4. Do not immediately remove the host `elis-github` user; it may still be useful for volume ownership.
5. Stop extending ACL/helper fixes as the primary model.
6. Record the container wrapper as the canonical GitHub Agent execution path.

## Phase 7 — Rollback

Rollback commands:

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml down
```

If workspace restoration is needed:

```bash
sudo rm -rf /opt/elis/agent-worktrees/github-agent
sudo tar -xzf /opt/elis/backups/github-agent-pre-container-<timestamp>.tgz -C /
```

Rollback rules:

```text
Do not delete github-agent.env.
Do not delete the rollback archive.
Do not remove the host elis-github user until container pilot has passed and rollback is no longer needed.
```

## Acceptance criteria

The PE passes only when:

1. GitHub Agent runs in a container as non-root.
2. `/opt/elis/agent-worktrees/github-agent` is mounted read-write as `/workspace`.
3. `/opt/elis/secrets/github-agent.env` is mounted read-only as `/run/secrets/github-agent.env`.
4. GitHub identity inside the container is `elis-git-bot`.
5. Repository permission is `WRITE`.
6. Container can perform read-only GitHub checks.
7. Container can write only to its mounted workspace.
8. Container cannot access ambient `rochasamurai` GitHub credentials.
9. PM cannot read the GitHub token.
10. PM does not execute GitHub write actions directly.
11. The constrained wrapper rejects unsupported verbs.
12. Branch push and PR creation work only after PO approval.
13. Merge remains blocked until explicit PO approval.
14. Evidence is recorded in the PE evidence packet.
15. Container can be destroyed and recreated without losing worktree state.

## How this resolves previous failures

| Previous problem | Containerised model resolution |
|---|---|
| OpenClaw dispatch runs as `samurai` | Sensitive operation runs in container |
| PM cannot read token | Token mounted only inside container as read-only secret |
| Need for `sudo -u elis-github` | Replaced by container wrapper |
| Linked worktree metadata ownership conflict | Use independent clone/workspace volume |
| Runtime files lost during rebuild | Persistent volume plus explicit bootstrap |
| Increasing ACL complexity | Replace with bind mounts: `rw`, `ro`, or absent |
| Ambient `rochasamurai` auth leakage | Container uses its own `GH_CONFIG_DIR` |
| Hard to clean corrupted agent environment | Destroy/recreate container |
| Worktree must persist | Worktree is mounted as persistent volume |

## Proposed PM opening message

```text
PM ACTION — PROPOSE PE-OPS-CONTAINER-GITHUB-01

We need to replace the current host-user/ACL/helper approach for ELIS GitHub Agent with a containerised GitHub Agent runtime.

Reason:
The Linux-user model proved useful for understanding the boundary, but OpenClaw currently dispatches subagents as the gateway user rather than as per-agent Linux users. This caused repeated permission, secret visibility, and bootstrap failures.

Goal:
Create a containerised GitHub Agent pilot that preserves OpenClaw orchestration while moving GitHub-sensitive execution into a dedicated container.

Proposed PE:
PE-OPS-CONTAINER-GITHUB-01 — Containerise ELIS GitHub Agent Runtime

Governance lane:
Strict PE

Objectives:
- Containerise GitHub Agent execution.
- Mount /opt/elis/agent-worktrees/github-agent as rw.
- Mount /opt/elis/secrets/github-agent.env as read-only.
- Ensure GitHub identity is elis-git-bot.
- Ensure no ambient rochasamurai gh auth is used.
- Provide a constrained wrapper for approved GitHub actions.
- Validate push/open PR only after PO approval.
- Keep OpenClaw as orchestration layer.

Opening scope:
- CURRENT_PE.md
- .elis/pe/PE-OPS-CONTAINER-GITHUB-01/PE_TASK.md

Implementation scope to propose:
- ops/containers/github-agent/Dockerfile
- ops/containers/github-agent/entrypoint.sh
- ops/containers/github-agent/docker-compose.github-agent.yml
- docs/governance/ELIS_Containerised_Agent_Runtime_Runbook.md
- docs/governance/ELIS_GitHub_Agent_Operating_Model.md if needed
- docs/governance/ELIS_PE_Operating_Protocol.md if needed

Out of scope:
- migrating all agents at once
- deleting existing host users
- deleting existing secrets
- removing rochasamurai auth globally
- replacing OpenClaw
- changing Discord routing
- merging without PO approval

Do not edit yet.
Do not dispatch yet.

First report:
- current PE state
- whether PE-OPS-GITHUB-02 needs to be closed/blocked before opening this PE
- proposed branch
- proposed implementer/validator
- exact opening file scope
```

## Final decision statement

```text
Abandon host Linux-user-per-agent as the primary execution model.
Adopt container-per-agent as the target runtime isolation model.
Pilot first with ELIS GitHub Agent.
Keep OpenClaw as the orchestration layer.
Use containers as the secure execution boundary.
```
