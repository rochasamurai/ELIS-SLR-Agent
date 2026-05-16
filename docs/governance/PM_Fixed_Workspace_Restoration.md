# PM Fixed Workspace Restoration Procedure

**Status:** Canonical — v1.1
**Date:** 2026-05-16
**Owner:** Carlos Rocha, Product Owner
**Applies to:** PM agent

---

## 1. Purpose

Document the procedure and verification steps for restoring the PM fixed workspace
to align with the latest GitHub-committed files while preserving all runtime/context files
in the OpenClaw runtime workspace.

---

## 2. Key Distinction: Runtime Workspace vs Git Worktree

PM operates with two distinct environments:

| Environment | Path |
|-------------|------|
| OpenClaw runtime workspace | `/home/samurai/openclaw/workspace-pm` |
| Authorised Git worktree | `/opt/elis/agent-worktrees/pm` |

**Runtime workspace** holds persistent identity and context:
- `SOUL.md`, `AGENTS.md`, `MEMORY.md`, `SKILLS.md`, `IDENTITY.md`, `USER.md`
- Agent memory and session continuity files
- OpenClaw/Hermes bootstrap configuration

**Git worktree** holds repo state for the current task:
- `CURRENT_PE.md`, `.elis/pe/*/PE_TASK.md`, governance docs
- Source code, tests, plan files
- PE-specific artefacts

---

## 3. Restoration Procedure

### 3.1 Verify Runtime Workspace
- [ ] `/home/samurai/openclaw/workspace-pm` exists and is accessible
- [ ] `SOUL.md`, `AGENTS.md`, `MEMORY.md`, `SKILLS.md` are present
- [ ] Agent identity files (`IDENTITY.md`, `USER.md`) are present

### 3.2 Restore Git Worktree
- [ ] Worktree exists at `/opt/elis/agent-worktrees/pm`
- [ ] `CURRENT_PE.md` is restored from GitHub latest commit
- [ ] `AGENTS.md` is restored from GitHub latest commit (if tracked in repo)
- [ ] `.elis/pe/*/PE_TASK.md` files are restored as needed
- [ ] Ownership and permissions: `samurai:samurai`, mode 644
- [ ] Git worktree is clean (`git status --short` shows nothing unexpected)
- [ ] No persistent runtime files (`.openclaw/`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, `USER.md`) are present in the Git worktree

### 3.3 Verify Separation
- [ ] Runtime workspace and Git worktree are distinct paths
- [ ] Persistent runtime files reside only in the runtime workspace
- [ ] Only tracked governance files were restored to the Git worktree; runtime/context files untouched
- [ ] `git rev-parse --show-toplevel` returns the Git worktree root, not the runtime workspace

---

## 4. Verification Commands

```bash
# Verify runtime workspace
echo "Runtime workspace: /home/samurai/openclaw/workspace-pm"
ls /home/samurai/openclaw/workspace-pm/SOUL.md /home/samurai/openclaw/workspace-pm/AGENTS.md

# Verify Git worktree
echo "Git worktree: /opt/elis/agent-worktrees/pm"
cd /opt/elis/agent-worktrees/pm && pwd && git rev-parse --show-toplevel && git status --short

# Verify separation (no runtime files in Git worktree)
test ! -f /opt/elis/agent-worktrees/pm/SOUL.md || echo "FAIL: runtime file in Git worktree"
test ! -f /opt/elis/agent-worktrees/pm/HEARTBEAT.md || echo "FAIL: runtime file in Git worktree"

# Repo preflight
git -C /opt/elis/repo status --short
git -C /opt/elis/repo rev-parse --abbrev-ref HEAD
```

---

## 5. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2026-05-16 | PE-closeout | Document runtime workspace / Git worktree distinction. Add separation verification and exclusion check. Add restoration procedure for both environments. |
| 1.0 | 2026-05-03 | PM | Initial version.
