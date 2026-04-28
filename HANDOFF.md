## Summary
Removed 11 obsolete engine-specific agent documentation/config files so the repo no longer treats them as active guidance. Verified the remaining agent documentation/config source-of-truth surfaces are `openclaw/openclaw.json` and `docs/openclaw/AGENT_CATALOGUE.md`; the deleted files are absent and no longer available as competing references.

## Files Changed
| Path | Type |
|---|---|
| `config/reviewer_identity_map.json` | deleted |
| `docs/openclaw/CLAUDE_AUTH_SETUP.md` | deleted |
| `docs/openclaw/CODEX_AGENT_SETUP.md` | deleted |
| `docs/openclaw/CODEX_AUTH_SETUP.md` | deleted |
| `docs/openclaw/INFRA_AGENT_SETUP.md` | deleted |
| `docs/openclaw/PARALLEL_TRACK_GUIDE.md` | deleted |
| `docs/openclaw/PM_AGENT_ORCHESTRATION_CONTRACT.md` | deleted |
| `docs/openclaw/PM_AGENT_RULES.md` | deleted |
| `docs/openclaw/PM_CROSS_AGENT_DISPATCH_EVIDENCE.md` | deleted |
| `docs/pm_agent/ASSIGNMENT_PROTOCOL.md` | deleted |
| `docs/pm_agent/ESCALATION_PROTOCOL.md` | deleted |
| `HANDOFF.md` | modified |

## Design Decisions
- Kept the change set strictly to the 11 requested deletions plus this handoff update.
- Interpreted the legacy-name verification requirement narrowly: confirm the deleted agent-doc/config surfaces are removed and that the intended surviving source-of-truth files still exist. A repo-wide non-archive search still returns many historical/planning/runtime references to `CODEX`, `codex`, and `Claude Code`, so broader normalization is out of scope for this PE.
- Recorded the environment gate outcome exactly as observed: `black` and `ruff` passed; `pytest` is unavailable in this session (`No module named pytest`).

## Acceptance Criteria
- [x] Delete `docs/openclaw/CODEX_AGENT_SETUP.md`
- [x] Delete `docs/openclaw/CODEX_AUTH_SETUP.md`
- [x] Delete `docs/openclaw/CLAUDE_AUTH_SETUP.md`
- [x] Delete `docs/openclaw/INFRA_AGENT_SETUP.md`
- [x] Delete `docs/openclaw/PM_AGENT_ORCHESTRATION_CONTRACT.md`
- [x] Delete `docs/openclaw/PM_CROSS_AGENT_DISPATCH_EVIDENCE.md`
- [x] Delete `docs/openclaw/PARALLEL_TRACK_GUIDE.md`
- [x] Delete `docs/openclaw/PM_AGENT_RULES.md`
- [x] Delete `config/reviewer_identity_map.json`
- [x] Delete `docs/pm_agent/ASSIGNMENT_PROTOCOL.md`
- [x] Delete `docs/pm_agent/ESCALATION_PROTOCOL.md`
- [x] Verify `openclaw/openclaw.json` still exists as a source of truth
- [x] Verify `docs/openclaw/AGENT_CATALOGUE.md` still exists as a source of truth
- [x] Verify deleted files are absent from the working tree
- [x] Verify no additional active source-of-truth file was retained from the deleted set
- [ ] Verify no remaining files reference legacy engine names beyond archived documents [blocked: repo-wide non-archive search still returns many matches in active historical/planning/runtime files outside this PE scope]

## Validation Commands
- `python -m black --check .`
  - `210 files would be left unchanged.`
- `python -m ruff check .`
  - `All checks passed!`
- `python -m pytest -q`
  - `/usr/bin/python: No module named pytest`
- `rg -n --hidden --glob '!docs/_archive/**' --glob '!**/.git/**' '\b(CODEX|codex|Claude Code)\b' .`
  - Returned many matches in active non-archive files (for example `CURRENT_PE.md`, plan files, scripts, workflow files, handoffs, and runbooks); therefore a repo-wide “no remaining references” claim cannot be made within this PE’s delete-only scope.
- `ls -1 openclaw/openclaw.json docs/openclaw/AGENT_CATALOGUE.md`
  - Confirmed both files exist.
- Python existence check for all 11 deletion targets
  - Confirmed all 11 paths are missing after `git rm`.

## Status Packet
### §6.1 Working-tree state
```text
## feature/pe-infra-agent-01-doc-consolidation
D  config/reviewer_identity_map.json
D  docs/openclaw/CLAUDE_AUTH_SETUP.md
D  docs/openclaw/CODEX_AGENT_SETUP.md
D  docs/openclaw/CODEX_AUTH_SETUP.md
D  docs/openclaw/INFRA_AGENT_SETUP.md
D  docs/openclaw/PARALLEL_TRACK_GUIDE.md
D  docs/openclaw/PM_AGENT_ORCHESTRATION_CONTRACT.md
D  docs/openclaw/PM_AGENT_RULES.md
D  docs/openclaw/PM_CROSS_AGENT_DISPATCH_EVIDENCE.md
D  docs/pm_agent/ASSIGNMENT_PROTOCOL.md
D  docs/pm_agent/ESCALATION_PROTOCOL.md
M  HANDOFF.md
```

### §6.2 Repository state
```text
feature/pe-infra-agent-01-doc-consolidation
```

### §6.3 Quality gates
- `black --check`: PASS
- `ruff check`: PASS
- `pytest -q`: [blocked] unavailable in current environment (`No module named pytest`)
- Legacy-name verification search: [blocked] repo still contains many non-archive references outside this PE scope

### §6.4 Ready to merge
```text
NO — outstanding blocked validation: pytest unavailable in this session, and repo-wide legacy-name references remain outside delete-only PE scope.
```
