# ADR-002: Git Worktrees for PE Isolation

**Status:** Accepted
**Date:** 2026-03-26
**Deciders:** PM (Carlo Rocha), CODEX, Claude Code

## Context

Each PE is implemented on its own feature branch. Early in the project, agents
would check out branches in the main working directory, which caused several
recurring problems:

- checkout failures when local edits existed on unrelated files
- accidental cross-PE contamination (PE-N edits leaking into PE-N+1)
- VS Code Source Control accumulating stale GitHub connections
- parallel PE work being impossible without constant stashing or branch switching

A mechanism was needed to allow each active PE branch to have its own working
directory, fully isolated from other branches and from the main repo folder.

## Decision

Every PE is developed in a dedicated Git worktree. The main repo folder always
stays on `main`. Each PE branch lives in its own worktree under
`.worktrees/<pe-id>/` (relative to the repo root).

Worktree lifecycle:

1. **Create** at the start of the PE, from the base branch.
2. **Work** exclusively in that worktree for the PE's duration.
3. **Remove** immediately after the PR merges.

## Consequences

### Positive
- Complete file-system isolation: no checkout failures, no cross-PE leakage.
- Multiple PEs can run simultaneously without branch switching.
- The main repo folder remains on `main` at all times, giving agents a stable
  reference point.
- Scope gate (`git diff --name-status origin/main..HEAD`) works correctly from
  within the worktree without contamination from other work.

### Negative / trade-offs
- Disk overhead: each worktree is a full copy of the working tree.
- Stale worktrees must be pruned manually after merges; neglecting this
  accumulates dead directories.
- Windows path lengths can cause issues with deeply nested worktrees.

## Alternatives considered

### Alternative A — Branch switching with stash

Switch branches in the main repo directory and use `git stash` to park
in-progress work.

Discarded because stash state is not committed, survives reboots poorly,
and creates ambiguity when multiple unrelated changes need to be parked
simultaneously. It also makes parallel PE work impractical.

### Alternative B — Separate repository clones per PE

Maintain a separate local clone of the repo for each active PE.

Discarded because it duplicates the full git history for each clone, complicates
pushing and pulling (each clone has its own origin state), and adds significant
disk overhead with no advantage over worktrees for this use case.

## Evidence / references

- `AGENTS.md` §3 — Worktree lifecycle, mandatory for every PE
- `CLAUDE.md` — do-not list: "Do not switch branches with local edits (use worktrees)"
- PE-MS series: `.worktrees/pe-ms-01` through `.worktrees/pe-ms-08` — consistent
  application of this pattern across all 8 MiniServer PEs
