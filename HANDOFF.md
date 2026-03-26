# HANDOFF.md — PE-PLAN-01

**PE:** PE-PLAN-01 — Architecture Decision Records: Infrastructure and First Batch
**Branch:** `feature/pe-plan-01-adr-infrastructure`
**Implementer:** Claude Code (`infra-impl-claude`)
**Date:** 2026-03-26

---

## Summary

Introduced the ADR system for the ELIS project. Created the `docs/decisions/`
directory with a README guide and 6 retroactive ADRs documenting the key
architectural decisions made during the ELIS development history. Extended
`AGENTS.md` with §2.12 defining when to create an ADR.

---

## Files changed

```
A  docs/decisions/README.md
A  docs/decisions/ADR-001-two-agent-alternation-model.md
A  docs/decisions/ADR-002-git-worktrees-pe-isolation.md
A  docs/decisions/ADR-003-parallel-track-model.md
A  docs/decisions/ADR-004-handoff-copy-not-symlink.md
A  docs/decisions/ADR-005-agent-browser-rejected-for-auth.md
A  docs/decisions/ADR-006-openclaw-as-native-runtime.md
M  AGENTS.md
M  HANDOFF.md
```

---

## Acceptance criteria checklist

| # | Criterion | Status |
|---|---|---|
| AC-1 | `docs/decisions/README.md` present with template, lifecycle, and creation rules | ✓ |
| AC-2 | 6 ADRs present with status `Accepted` and all fields completed | ✓ |
| AC-3 | Each ADR has at least one discarded alternative documented | ✓ |
| AC-4 | `AGENTS.md` updated with rule for when to create an ADR (§2.12) | ✓ |
| AC-5 | ADR-003 references empirical case PE-MS-07 ∥ PR #299 | ✓ |
| AC-6 | ADR-004 references finding F4 from PR #299 | ✓ |

---

## ADR content notes

**ADR-001** (two-agent alternation): covers the alternation rule governing Implementer/Validator
rotation across PEs. References the PE-MS series (PE-MS-01 to PE-MS-08) as historical evidence.

**ADR-002** (git worktrees): covers mandatory worktree-per-PE isolation. References `AGENTS.md §3`
and `CLAUDE.md` do-not list. Worktree pattern observed across all 8 MiniServer PEs.

**ADR-003** (parallel tracks): covers the parallel-track model. Cites PE-MS-07 ∥ PR #299 as the
empirical case. Notes PE-AUTH-01 ∥ PE-AUTH-02 as structurally eligible but not yet empirically
verified (per AC-5).

**ADR-004** (HANDOFF copy not symlink): covers the decision to use a generated copy. References
PR #299 Finding 4 (Medium — HANDOFF symlink fragility across Windows/Linux) as the direct
evidence that motivated the decision (per AC-6).

**ADR-005** (agent browser rejected for auth): covers the decision not to use browser-based login
for credential harvesting. Agent browser remains available for content retrieval only.

**ADR-006** (OpenClaw as native runtime): covers the transition from Docker Compose to native
OpenClaw + systemd --user. References PE-MS-08 (PR #302) end-to-end validation as confirmation.

**AGENTS.md §2.12**: added after §2.11 (language standard). Defines mandatory ADR triggers,
non-required cases, and a judgement heuristic. Points to `docs/decisions/README.md` for format.

---

## Quality gates (verbatim output)

Run from worktree `.worktrees/pe-plan-01` on 2026-03-26:

```text
python -m black --check .
All done! ✨ 🍰 ✨
125 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest
602 passed, 17 warnings in 18.17s

python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

## Validator notes

- All ADR files are in `docs/decisions/` — no test files were modified.
- `AGENTS.md` change is limited to adding §2.12 after §2.11; no other sections were touched.
- Scope is clean: 7 new files + 2 modified files (AGENTS.md, HANDOFF.md), all PE-PLAN-01 scope.

---

*ELIS SLR Agent · HANDOFF.md · infra-impl-claude · 2026-03-26*
