# ELIS GitHub Agent — Host Cleanup Checklist

> **Gate:** This checklist MUST NOT be executed until the containerised GitHub Agent pilot has passed
> all acceptance criteria (see `docs/architecture/ELIS_Containerised_GitHub_Agent_Runtime_Plan.md`).
>
> **Status:** DRAFT — gated behind successful pilot completion.

---

## Rollback prerequisites

Before making any change in this checklist, confirm:

- [ ] Container pilot has passed all ACs
- [ ] `elis-github-agent-container status` returns `[PASS] Authenticated as: elis-git-bot`
- [ ] Container can push branches and create PRs (tested with a sandbox branch)
- [ ] Rollback backup exists at `/opt/elis/backups/github-agent-pre-container-*.tgz`
- [ ] A fallback restore procedure is documented and tested
- [ ] PM has authorised cleanup

---

## Cleanup steps

### Step 1 — Archive the linked worktree backup

Once the container workspace is confirmed stable, the linked backup can be archived:

```bash
# Archive (compress) rather than delete
sudo tar -czf /opt/elis/backups/github-agent-linked-backup-$(date +%Y%m%dT%H%M%S).tgz \
  /opt/elis/agent-worktrees/github-agent.linked-backup.20260508T141916

# Only then remove
sudo rm -rf /opt/elis/agent-worktrees/github-agent.linked-backup.20260508T141916
```

**Rollback:** `sudo tar -xzf /opt/elis/backups/github-agent-linked-backup-*.tgz -C /`

### Step 2 — Remove the preserve directory

```bash
# Only remove if all files have been migrated into the persistent workspace
sudo rm -rf /tmp/github-agent-preserve
```

**Rollback:** recreate from archive if needed.

### Step 3 — Evaluate the `elis-github` Linux user

The `elis-github` user (UID 995, GID 983) is still useful as the volume owner for the
container workspace, ensuring permission alignment between host and container.

**Recommended:** Keep the user and group unless they conflict with other services.

**If removal is required** (only after all evidence is archived):

```bash
# First verify no running processes use this user
ps -u elis-github | head -5
pgrep -u elis-github && echo "WARN: processes still running" || echo "PASS: no active processes"

# Remove user (keeps group membership for container UID mapping)
sudo userdel elis-github
```

**Rollback:** `sudo useradd -u 995 -g 983 -m elis-github`

### Step 4 — Evaluate the `elis-github-secrets` group

The group is needed for access control to `/opt/elis/secrets/` even after containerisation:

```bash
# Check if any other group members exist
getent group elis-github-secrets
```

**Recommended:** Keep the group and directory permissions unchanged.
Secrets access is now mediated through the container mount, but the host ACL
provides a defence-in-depth layer.

**Rollback:** `sudo groupadd -g 982 elis-github-secrets && sudo usermod -a -G elis-github-secrets elis-github`

### Step 5 — Remove ACLs granting `samurai` read access to github-agent worktree

This step is only appropriate if the container is the sole GitHub Agent execution path:

```bash
# Check current ACLs
getfacl /opt/elis/agent-worktrees/github-agent

# Remove samurai ACL entry (only if PM/PO confirm no other agent needs read access)
sudo setfacl -x u:samurai /opt/elis/agent-worktrees/github-agent
```

**Rollback:** `sudo setfacl -m u:samurai:rx /opt/elis/agent-worktrees/github-agent`

### Step 6 — Final verification

After all cleanup steps:

```bash
# Container still works
docker compose -f /opt/elis/repo/ops/containers/github-agent/docker-compose.github-agent.yml \
  run --rm elis-github-agent --check-only

# Workspace integrity
ls /opt/elis/agent-worktrees/github-agent/.git

# Secrets still accessible (to container — not to samurai)
docker compose -f /opt/elis/repo/ops/containers/github-agent/docker-compose.github-agent.yml \
  run --rm elis-github-agent \
  bash -c 'test -r /run/secrets/github-agent.env && echo "PASS: secret accessible"'
```

---

## Items explicitly retained (with justification)

| Item | Justification |
|------|---------------|
| `/opt/elis/agent-worktrees/github-agent` | Persistent workspace volume for the container |
| `/opt/elis/secrets/github-agent.env` | Read-only secret source mounted into the container |
| `/opt/elis/secrets/` directory permissions | Defence-in-depth: host ACL restricts directory access even if mount config changes |
| `elis-github` Linux user (UID 995) | Volume owner alignment between host and container |
| `elis-github-secrets` group (GID 982) | Secrets directory group membership for the container user |
| Canonical repo at `/opt/elis/repo` | Container compose and wrapper scripts are served from here |

---

## Items removed with rollback

| Item | Rollback command |
|------|-----------------|
| `/opt/elis/agent-worktrees/github-agent.linked-backup.20260508T141916` | `sudo tar -xzf /opt/elis/backups/github-agent-linked-backup-*.tgz -C /` |
| `/tmp/github-agent-preserve` | Recreate from archive if needed |

---

## Evidence to record

For each cleanup step, record:

1. **Step number and name**
2. **Command run** (with any sensitive paths included; token values never appear)
3. **Exit code**
4. **Output** (redacted if necessary — run redact step before saving)
5. **Rollback command** (always available)

### Safe output capture

```bash
# Run step and capture exit code + output
STEP_LOG="/opt/elis/agent-worktrees/github-agent/.elis/pe/cleanup/step-1-archive.log"
mkdir -p "$(dirname "$STEP_LOG")"
sudo tar -czf /opt/elis/backups/github-agent-linked-backup-20260508T220000.tgz \
  /opt/elis/agent-worktrees/github-agent.linked-backup.20260508T141916 2>&1
echo "Exit code: $?" | tee -a "$STEP_LOG"
```

---

## Emergency rollback (full)

If the container pilot fails after cleanup has begun:

```bash
# 1. Restore workspace from backup
sudo rm -rf /opt/elis/agent-worktrees/github-agent
sudo tar -xzf /opt/elis/backups/github-agent-pre-container-*.tgz -C /

# 2. Restore linked backup
sudo tar -xzf /opt/elis/backups/github-agent-linked-backup-*.tgz -C /

# 3. Restore user if removed
sudo useradd -u 995 -g 983 -m elis-github 2>/dev/null || true

# 4. Restore group if removed
sudo groupadd -g 982 elis-github-secrets 2>/dev/null || true
sudo usermod -a -G elis-github-secrets elis-github 2>/dev/null || true

# 5. Restore ACLs
sudo setfacl -m u:samurai:rx /opt/elis/agent-worktrees/github-agent 2>/dev/null || true

# 6. Verify
sudo -u elis-github gh auth status
```