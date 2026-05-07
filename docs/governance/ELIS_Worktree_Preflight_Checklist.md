# ELIS Worktree Preflight Checklist

**Status:** Canonical — v1.1  
**Date:** 2026-05-06  
**Owner:** Carlos Rocha, Product Owner  
**Applies to:** All ELIS agents before starting any PE work  
**Authoritative sources:** ELIS_General_Guidance.md §5, AGENTS.md §2.2, LESSONS_LEARNED.md, ELIS_PE_Operating_Protocol.md §5 (Fixed Workspace Model)  
**Canonical record:** GitHub (this document)

---

## 1. Purpose

Every agent must verify the correct worktree before any PE work. This prevents cross-PE contamination, wrong-repo writes, and stale-branch work. The checks in this document are mandatory Step 0 actions before any file modifications, commits, or dispatches.

---

## 2. Mandatory Path Preflight (Step 0)

Run these commands before any PE work:

```bash
pwd
git rev-parse --show-toplevel
git status --short --branch
git branch --show-current
```

### Expected Results
- `pwd`: must match the agent's **fixed worktree path**, e.g. `/opt/elis/agent-worktrees/infra-impl-b` (NOT a per-PE path)
- `git rev-parse --show-toplevel`: must return the fixed worktree root, NOT `/opt/elis/repo`
- `git status --short --branch`: clean state or only expected files after reset
- `git branch --show-current`: must match the PE branch for the current assignment, e.g. `feature/pe-ops-fixed-workspaces-01-adopt-fixed-agent-workspace-and-github-write-boundary-model`

### Fixed Workspace Binding Certificate
Before any PE work begins, the agent must produce a **Fixed Workspace Binding Certificate** as defined in `docs/governance/ELIS_PE_Operating_Protocol.md §5.1b`. This certificate is mandatory evidence in the opening Status Packet.

Certificate fields:
| Field | Source |
|-------|--------|
| PE ID | CURRENT_PE.md |
| Agent ID | Agent's surface name (e.g. `infra-impl-b`) |
| Fixed workspace path | `pwd` |
| Git root | `git rev-parse --show-toplevel` |
| Branch | `git branch --show-current` |
| HEAD | `git rev-parse HEAD` |
| Base/expected commit | `git rev-parse origin/$BASE` (`$BASE` from CURRENT_PE.md) |
| Clean status | `git status --short --untracked-files=all` |
| Allowed file scope | From PE_TASK.md |
| Timestamp | ISO 8601 timestamp |
| Result | PASS (matches) or FAIL (mismatch) |

A FAIL result blocks all work until PM resolves the mismatch.

---

## 3. Worktree Isolation Checklist

### 3.1 General Isolation
- [ ] Worktree path follows fixed workspace convention: `/opt/elis/agent-worktrees/<role>-<slot>` (e.g. `infra-impl-b`, `infra-val-a`)
- [ ] The branch checked out in this fixed worktree matches the current PE branch from CURRENT_PE.md
- [ ] No other active agent writes to this same fixed worktree
- [ ] No shared mutable working directory between active agents
- [ ] OpenClaw workspace is NOT bound to `/opt/elis/repo`
- [ ] Read `.agentignore` — none of those files may be open or in context
- [ ] Wrong-worktree quarantine understood: if `pwd` or `git rev-parse --show-toplevel` does not match assigned path, stop all operations immediately
- [ ] No-copy rule understood: never copy or transfer files between worktrees

### 3.2 Repository Path Safety
- [ ] Canonical repo path: `/opt/elis/repo` — do not modify directly unless this PE is authorised
- [ ] Current worktree is distinct from canonical repo
- [ ] `git rev-parse --show-toplevel` does NOT return `/opt/elis/repo`
- [ ] No file writes go to canonical repo filesystem by accident (verify `pwd` matches worktree root)

### 3.3 OpenClaw File Tool vs Shell CWD Distinction
Agents must understand:
```
shell cwd != OpenClaw file-tool root
```
A command such as `cd /opt/elis/repo && git status` does not change where OpenClaw `read`, `write`, or `edit` tools resolve relative paths.

- [ ] Verify file-tool cwd matches assigned worktree
- [ ] Never rely on relative file-tool paths across worktrees

---

## 4. Branch and Base Checklist

### 4.1 Branch in Fixed Workspace
- [ ] Branch name matches CURRENT_PE.md registry for this PE
- [ ] Branch exists and is checked out in the fixed worktree
- [ ] If the PE branch does not exist yet in the fixed worktree, create it from the base: `git checkout -b feature/<pe-branch> origin/$BASE`
- [ ] No commits from unrelated PEs on this branch

### 4.2 Base
- [ ] Base branch is up to date (`git fetch origin && git merge-base origin/$BASE HEAD` returns the tip of `origin/$BASE`)
- [ ] If another PE merged since the branch was created or last rebased, rebase: `git rebase origin/$BASE`
- [ ] Drift check: `git merge-base origin/$BASE HEAD` should equal the tip of `origin/$BASE`

---

## 5. Task Packet Checklist

- [ ] `.elis/pe/<PE-ID>/PE_TASK.md` exists
- [ ] Objective, allowed files, and required artefacts match the current PE
- [ ] Acceptance criteria are understood
- [ ] Required commands are ready to run
- [ ] Forbidden files are known and excluded from any writes

---

## 6. Working Tree State Checklist

### 6.1 Clean State
- [ ] `git status -sb` shows clean or expected state
- [ ] If dirty: the state is expected and authorised for this phase
- [ ] No uncommitted files from a previous (now-completed) PE session (stashing across sessions is prohibited)
- [ ] All outstanding changes from a prior PE are committed, stashed-and-cleared, or resolved

### 6.2 Fixed Workspace Reset (Start of Each New PE)
- [ ] Worktree is reset: stale branch state is cleaned (stash/discard disposable state)
- [ ] Base is fetched: `git fetch origin`
- [ ] Branch is checked out or created for the current PE
- [ ] No lingering files from the prior PE's branch
- [ ] Rebase if needed: `git rebase origin/$BASE`

### 6.3 Separate Persistent Runtime Files from Disposable Repo State
- [ ] Persistent agent runtime/context files (AGENTS.md, SKILLS.md, SOUL.md, tool manifests, OpenClaw/Hermes bootstrap files) reside outside the fixed worktree
- [ ] Disposable repo/task state (source code, HANDOFF, REVIEW, `.elis/` PE workspace) is cleaned during reset
- [ ] No persistent runtime files are written into the fixed worktree
- [ ] If any persistent file accidental lands in the worktree, it is moved out before the worktree is reset for the next PE

### 6.4 When Resuming Work (Same PE, Same Branch)
- [ ] Previous commit is on the correct PE branch
- [ ] `git log -1 --oneline` shows the expected previous work
- [ ] No merge conflicts in progress

---

## 7. Artefact Pre-Check

- [ ] Previous phase artefacts exist if this is a continuation:
  - [ ] Implementer: HANDOFF.md exists (if resuming)
  - [ ] Validator: REVIEW exists or is in progress
- [ ] Required check scripts exist (e.g. `scripts/check_current_pe.py`)
- [ ] Black, ruff, pytest are available

---

## 8. Common Pitfalls (from LESSONS_LEARNED.md)

| Pitfall | Prevention |
|---------|------------|
| Running `chmod +x scripts/*.py` | Forbidden by default; requires PO approval |
| Running `rm -rf *`, `git reset --hard`, `git clean -fdx` | Forbidden by default; requires PO approval and rollback plan |
| Writing to `/opt/elis/repo` instead of worktree | Always verify `git rev-parse --show-toplevel` before writing |
| Switching branches with a dirty tree | Run `git status -sb` first; commit or stash before switching |
| Relative path confusion (OpenClaw file-tool root ≠ shell cwd) | Use explicit absolute paths; verify cwd matches worktree |
| Using stale branch | Run `git fetch origin && git rebase origin/$BASE` before starting |

---

## 9. Verification Commands

```bash
# Verify worktree identity
echo "Worktree root: $(pwd)"
echo "Git root: $(git rev-parse --show-toplevel)"
echo "Branch: $(git branch --show-current)"
echo "Clean state: $(git status --short --branch)"
echo "Last commit: $(git log -1 --oneline)"

# Verify branch is current vs base
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
echo "Base branch: $BASE"
git fetch origin 2>/dev/null
git merge-base origin/$BASE HEAD
git rev-parse origin/$BASE

# Verify task packet
echo "Task packet: $(ls .elis/pe/*/PE_TASK.md 2>/dev/null || echo NOT FOUND)"
```

---

## 10. Version History

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.1     | 2026-05-06 | PM     | Adopt fixed workspace paths (role+slot, not PE-ID). Add fixed workspace reset checklist. Update expected path patterns and branch instructions. |
| 1.0     | 2026-05-03 | PM     | Initial canonical consolidation from ELIS_General_Guidance.md §5, AGENTS.md, LESSONS_LEARNED.md. |
