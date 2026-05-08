# ELIS GitHub Agent Container Runbook

> Operational guide for the containerised ELIS GitHub Agent.
> **Path:** `ops/containers/github-agent/`
> **Wrapper:** `/opt/elis/repo/ops/containers/github-agent/elis-github-agent-container`
> **GitHub identity (inside container):** `elis-git-bot`

---

## Prerequisites

- Docker Engine 24+ and Docker Compose v2+
- The canonical repo cloned or available at `REPO_ROOT` (default `/opt/elis/repo`)
- GitHub token stored at `/opt/elis/secrets/github-agent.env` with `elis-git-bot` PAT
- Target workspace at `/opt/elis/agent-worktrees/github-agent`

---

## Quick start

### Build the image

```bash
cd /opt/elis/repo
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml build
```

Expected output: build completes without errors; image tagged `elis-github-agent:pe-ops-container-github-01`.

### Verify identity

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  --check-only
```

Expected output line:

```
[PASS] Authenticated as: elis-git-bot
```

### Verify workspace is writable

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  bash -c 'touch /workspace/.container-write-test && rm /workspace/.container-write-test && echo "PASS: workspace writable"'
```

Expected output: `PASS: workspace writable`

---

## Using the wrapper script

The wrapper at `ops/containers/github-agent/elis-github-agent-container` provides
a cleaner interface than raw docker compose commands.

### Check status

```bash
/opt/elis/repo/ops/containers/github-agent/elis-github-agent-container status
```

### Push a branch (approved verb)

```bash
/opt/elis/repo/ops/containers/github-agent/elis-github-agent-container push-branch
```

### Open a PR

```bash
/opt/elis/repo/ops/containers/github-agent/elis-github-agent-container open-pr /path/to/pr-body.md
```

### Check PR status

```bash
/opt/elis/repo/ops/containers/github-agent/elis-github-agent-container pr-checks 123
```

### Comment on a PR

```bash
/opt/elis/repo/ops/containers/github-agent/elis-github-agent-container pr-comment 123 /path/to/comment.md
```

### Merge a PR (PO approval required)

```bash
# This verb requires explicit PO approval before invocation
/opt/elis/repo/ops/containers/github-agent/elis-github-agent-container merge-pr 123
```

---

## One-shot commands (advanced)

For ad-hoc investigations or debugging, run one-shot commands directly:

```bash
# Check repository permission
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  --allow-pr-review -- gh repo view rochasamurai/ELIS-Multi-AI-Agent-Platform \
    --json nameWithOwner,viewerPermission

# List recent PRs
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  --allow-pr-review -- gh pr list --repo rochasamurai/ELIS-Multi-AI-Agent-Platform \
    --state all --limit 5

# Check workspace git status
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  bash -c 'git status --short --branch'
```

---

## Security boundary checks

### Confirm secret mount is read-only

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  bash -c 'touch /run/secrets/github-agent.env 2>&1 && echo "WARN: writable" || echo "PASS: read-only"'
```

Expected: `PASS: read-only` (or `touch: cannot touch '/run/secrets/github-agent.env': Read-only file system`).

### Confirm no ambient host gh credentials exposed

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  bash -c 'echo "gh config dir: $(ls /tmp/gh-config 2>/dev/null || echo empty)" && \
           echo "no host creds: $(gh auth status --show-status 2>&1 | head -1)"'
```

Expected: no reference to `rochasamurai` or any host account.

### Confirm no token leakage

The entrypoint script never prints `GH_TOKEN`. To verify:

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  --check-only 2>&1 | grep -oP 'ghp_\w+|github_pat_\w+' || echo "PASS: no token found in output"
```

Expected: `PASS: no token found in output`

---

## Rebuild and restart

```bash
cd /opt/elis/repo
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml build --no-cache
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent --check-only
```

---

## Troubleshooting

| Symptom | Likely cause | Check |
|---------|-------------|-------|
| `Secrets file not found` | Secret file not mounted or missing at `/run/secrets/github-agent.env` | Verify `/opt/elis/secrets/github-agent.env` exists and is readable by `elis-github` (GID 983) |
| `GH_TOKEN is empty` | The secret file exists but contains no `GH_TOKEN=` line | `cat /opt/elis/secrets/github-agent.env` (existence check only — do not print token) |
| `Cannot authenticate` | Token expired or revoked | PO must renew the PAT and update the secret file |
| `not a git repository` | Workspace volume is empty or not a git checkout | Verify `/opt/elis/agent-worktrees/github-agent/.git` exists and is valid |
| `Permission denied` on /workspace | Host UID/GID mismatch | Ensure workspace files are owned by `elis-github` (995:983) |
| Container exits immediately | Entrypoint syntax error | Run with `command: ["bash"]` in compose for interactive debugging |

---

## Evidence capture

Every GitHub action performed through the container should be recorded in the
PE evidence packet:

1. **Action timestamp**
2. **Verb used** (e.g. `push-branch`, `open-pr`)
3. **Command output** (redact any token-like strings)
4. **PR URL/number and SHA** (if applicable)
5. **Exit code** (0 = success)

### Safe evidence capture (no token leakage)

```bash
# Run the command
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent \
  --check-only 2>&1 | tee /opt/elis/agent-worktrees/github-agent/.elis/pe/PE-XXXXX/evidence-status.log

# Verify no token in log
grep -oP 'ghp_\w+|github_pat_\w+|ghu_\w+' /opt/elis/agent-worktrees/github-agent/.elis/pe/PE-XXXXX/evidence-status.log \
  && echo "WARN: token found in log!" || echo "PASS: no token in log"
```

---

## Rollback

### Stop and remove the container

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml down
```

### Rebuild from clean cache

```bash
docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml build --no-cache
```

### Restore workspace from backup

```bash
sudo rm -rf /opt/elis/agent-worktrees/github-agent
sudo tar -xzf /opt/elis/backups/github-agent-pre-container-<TIMESTAMP>.tgz -C /
```

### Fall back to host-based approach

If the container pilot fails and you need the previous host-user workflow:

```bash
# Restore the linked backup
sudo rm -rf /opt/elis/agent-worktrees/github-agent
sudo cp -a /opt/elis/agent-worktrees/github-agent.linked-backup.20260508T141916 /opt/elis/agent-worktrees/github-agent

# Restore the preserve directory
sudo cp -a /tmp/github-agent-preserve/* /opt/elis/agent-worktrees/github-agent/ 2>/dev/null || true

# Verify
sudo -u elis-github gh auth status
```

---

## Design principles

1. **Token is never printed** — `entrypoint.sh` loads via `grep` subshell; even error messages do not reveal the token value.
2. **Verb gating is enforced in the entrypoint** — the wrapper script only gates at the verb level; the entrypoint enforces actual command execution controls.
3. **No ambient host credentials** — `GH_CONFIG_DIR` is isolated to `/tmp/gh-config`; `GITHUB_TOKEN` and `GH_ENTERPRISE_TOKEN` are unset.
4. **Read-only secret mount** — the secret file is mounted `:ro`; the container cannot modify or delete it.
5. **Drop all capabilities** — the container runs with `no-new-privileges` and drops all Linux capabilities.