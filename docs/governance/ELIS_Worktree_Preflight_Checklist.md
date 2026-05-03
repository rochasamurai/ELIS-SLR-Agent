# ELIS Worktree Preflight Checklist

**Status:** Canonical — v1.0  
**Date:** 2026-05-03  
**Owner:** Carlos Rocha, Product Owner  
**Applies to:** All ELIS agents before starting any PE work  
**Authoritative sources:** ELIS_General_Guidance.md §5, AGENTS.md §2.2, LESSONS_LEARNED.md  
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
- `pwd`: must match the assigned PE worktree, e.g. `/opt/elis/agent-worktrees/PE-GOV-01-infra-impl-b`
- `git rev-parse --show-toplevel`: must return the worktree root, NOT `/opt/elis/repo`
- `git status --short --branch`: clean state or only expected files
- `git branch --show-current`: must match the PE branch, e.g. `feature/pe-gov-01-operating-protocol-templates`

---

## 3. Worktree Isolation Checklist

### 3.1 General Isolation
- [ ] Worktree path follows convention: `/opt/elis/agent-worktrees/<PE-ID>-<agent-id>`
- [ ] No other active agent writes to this same worktree
- [ ] No shared mutable working directory between active agents
- [ ] OpenClaw workspace is NOT bound to `/opt/elis/repo`
- [ ] Read `.agentignore` — none of those files may be open or in context

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

### 4.1 Branch
- [ ] Branch name matches CURRENT_PE.md registry for this PE
- [ ] Branch is created from the base branch declared in CURRENT_PE.md
- [ ] No commits from unrelated PEs on this branch

### 4.2 Base
- [ ] Base branch is up to date (`git fetch origin && git merge-base origin/$BASE HEAD` returns the tip of `origin/$BASE`)
- [ ] If another PE merged since branch creation, rebase: `git rebase origin/$BASE`
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
- [ ] No uncommitted files from a previous session (stashing across sessions is prohibited)

### 6.2 When Starting from a Fresh Worktree
- [ ] Worktree is checked out from the base branch
- [ ] No lingering files from unrelated work
- [ ] Branch exists and is checked out

### 6.3 When Resuming Work
- [ ] Previous commit is on the correct branch
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
| 1.0     | 2026-05-03 | PM     | Initial canonical consolidation from ELIS_General_Guidance.md §5, AGENTS.md, LESSONS_LEARNED.md. |
