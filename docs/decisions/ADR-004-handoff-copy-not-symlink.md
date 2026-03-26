# ADR-004: HANDOFF as Generated Copy, Not Symlink

**Status:** Accepted
**Date:** 2026-03-26
**Deciders:** PM (Carlo Rocha), CODEX, Claude Code

## Context

`HANDOFF.md` at the repository root is the Implementer's technical handoff
document for the active PE. Early versions of the 2-Agent Automation Plan
proposed making this a symlink to a namespaced file in a `handoffs/` directory
(e.g., `HANDOFF.md → handoffs/HANDOFF_PE-MS-07.md`), so that individual PE
handoffs could be archived and referenced independently after merging.

The symlink strategy was reviewed and found to be fragile in practice. The
project operates across both Windows worktrees (Claude Code) and a Linux
runtime environment (elis-server). Symlinks behave differently across these
platforms: Windows requires elevated privileges or Developer Mode for
filesystem symlinks, and Git handles symlinks differently on checkout depending
on the platform configuration (`core.symlinks`).

## Decision

`HANDOFF.md` at the repository root is a **generated copy** — not a symlink.
The Implementer writes it directly as a regular file on the PE branch. It is
not linked to any external path. After merge, it persists as the last
Implementer's handoff, and is overwritten by the next Implementer at the start
of the next PE.

If per-PE handoff archives are needed in future, they should be implemented as
`HANDOFF.md` being committed to `docs/_archive/` or a similar directory as a
copy, not as symlinks.

## Consequences

### Positive
- Works identically on Windows and Linux without platform-specific Git or
  filesystem configuration.
- No dependency on `core.symlinks` or elevated OS permissions.
- Simple: one file, one location, always a regular file.

### Negative / trade-offs
- There is no automatic per-PE archive of HANDOFF content; the file is
  overwritten on each PE.
- If historical handoffs need to be retrieved, they must be accessed via
  git history (`git show <sha>:HANDOFF.md`).

## Alternatives considered

### Alternative A — Symlink `HANDOFF.md → handoffs/HANDOFF_{PE}.md`

Root `HANDOFF.md` is a symlink pointing to a PE-specific file in a subdirectory.

Discarded because symlinks are fragile across Windows and Linux in this project's
setup. On Windows, creating symlinks requires Developer Mode or elevated
privileges. Git's handling of symlinks on checkout is platform-dependent
(`core.symlinks=false` on many Windows installs, which materialises symlinks as
text files containing the target path rather than actual symlinks). This caused
workflow failures in the cross-platform 2-agent setup.

**Reference:** REVIEW_ELIS_2Agent_Automation_Plan_v2_0.md — Finding 4 (Medium):
"HANDOFF.md symlink strategy is fragile across Windows and Linux workflows"
(PR #299). This finding directly motivated the adoption of the generated-copy
approach.

### Alternative B — Versioned archive in a dedicated directory

Keep every PE's `HANDOFF.md` as a separate committed file in `handoffs/`.

Discarded at this stage because it adds directory proliferation without a
demonstrated need. Git history provides access to all prior handoffs without
a separate archive directory. This alternative can be revisited if per-PE
handoff retrieval becomes a common operational need.

## Evidence / references

- `REVIEW_ELIS_2Agent_Automation_Plan_v2_0.md` — Finding 4 (Medium): HANDOFF
  symlink strategy flagged as fragile in PR #299
- `ELIS_2Agent_Automation_Plan_v2_0.md` — plan updated to reflect generated-copy
  approach after the PR #299 review
- `AGENTS.md` §2.7 — HANDOFF.md committed before PR is opened (regular file)
