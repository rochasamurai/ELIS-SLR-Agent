# HANDOFF.md — PE-MS-03

**PE:** `PE-MS-03`
**Title:** PM Discord Reporting Hardening
**Implementer:** Claude Code (`infra-impl-claude`)
**Validator:** CODEX (`infra-val-codex`)
**Branch:** `feature/pe-ms-03-pm-discord-reporting`
**Plan:** `ELIS_MultiAgent_Implementation_Plan_v1_6.md`

---

## Summary

This PE hardens the PM Agent's Discord reporting behavior by adding concrete formatting constraints, a Discord-safe PE status summary format, a full-registry compact format, and an explicit worktree-vs-registry distinction rule. All changes are in the PM prompt stack (deploy source + docs mirror) and the PM rules reference doc.

---

## Files Changed

| File | Change | Purpose |
|---|---|---|
| `openclaw/workspaces/workspace-pm/AGENTS.md` | Updated | §5.1–5.3 Discord-safe formats; §8 concrete table size rules |
| `openclaw/workspaces/workspace-pm/MEMORY.md` | Updated | Two new invariants: full-table prohibition and worktree≠branch |
| `docs/openclaw/workspace-pm/AGENTS.md` | Updated | Mirror of deploy source |
| `docs/openclaw/workspace-pm/MEMORY.md` | Updated | Mirror of deploy source |
| `docs/openclaw/PM_AGENT_RULES.md` | Updated | Discord Reporting Rules section added |

---

## Design Decisions

1. §5.1 defines the default PE status format as a bullet list of non-merged PEs grouped by status — fits within Discord's 2000-char limit regardless of registry size.
2. §5.2 defines the compact single-line-per-PE format for full registry requests — avoids the 7-column table while preserving all information.
3. §5.3 makes the worktree vs registry distinction operational: always run `git worktree list`, never assert worktree existence from registry data alone.
4. §8 Discord Formatting Rules table makes constraints concrete — "any table > 5 rows → bullet list" is a clear trigger.
5. MEMORY.md invariants ensure rules survive session drift via "never reintroduce" pattern.

---

## Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| AC-1 | PM Agent distinguishes registry entries from actual worktrees | PASS | §5.3 + MEMORY invariant: "Registry branch names do not prove worktrees exist — always verify with git worktree list" |
| AC-2 | PM Agent does not produce malformed large-table output in Discord | PASS | §8: "any table > 5 rows → bullet list"; "full 7-column registry table → never"; §5.1/5.2 provide concrete safe formats |
| AC-3 | PM Agent uses the correct source per question type | PASS | §5 source table retained; §5.1–5.3 add output format for each source type |
| AC-4 | Validation captures at least one Discord-safe full-registry response | PENDING (host) | Live Discord test required post-deploy — deferred to host step after merge |

---

## Validation Commands

### Mirror alignment

```text
git diff --no-index -- openclaw/workspaces/workspace-pm/AGENTS.md docs/openclaw/workspace-pm/AGENTS.md
git diff --no-index -- openclaw/workspaces/workspace-pm/MEMORY.md docs/openclaw/workspace-pm/MEMORY.md
```

Expected: no diff output.

### Prompt-stack rule presence

```text
rg -n "7-column\|worktree list\|compact\|bullet" openclaw/workspaces/workspace-pm docs/openclaw/workspace-pm docs/openclaw/PM_AGENT_RULES.md
```

Expected: Discord formatting constraints and worktree distinction present in all three locations.

### Quality gates

```text
python -m black --check .
All done! ✨ 🍰 ✨
118 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest
565 passed, 17 warnings in 9.23s
```

---

## Remaining Host Action (post-merge)

1. Run `bash scripts/deploy_openclaw_workspaces.sh` on `elis-server`
2. Run `systemctl --user restart openclaw-gateway`
3. Use `docs/openclaw/PM_SESSION_RESET.md` to start a fresh PM session
4. Send `What are the current PEs?` — verify bullet-list format, not a table
5. Send `List all PEs including history` — verify compact single-line format
6. Send `What worktrees are active?` — verify PM runs `git worktree list`, not registry inference

Steps 4–6 satisfy AC-4.

---

## Ready for Validator

Yes. Scope is limited to PM Discord reporting constraints in the prompt stack and reference doc.
