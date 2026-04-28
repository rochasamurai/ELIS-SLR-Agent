## Summary
Removed 11 obsolete engine-specific agent documentation/config files so the repo no longer treats them as active guidance. Verified the remaining agent documentation/config source-of-truth surfaces are `openclaw/openclaw.json` and `docs/openclaw/AGENT_CATALOGUE.md`; the deleted files are absent and no longer available as competing references. Added follow-up fixes for PR #388 so `scripts/check_current_pe.py` accepts both legacy agent labels and ADR-009 slot-based labels in the Agent roles table, reviewer/bot identity mapping now loads from `openclaw/openclaw.json` (`agents.reviewerIdentities`) instead of the intentionally deleted standalone map file, and `tests/test_gate2_auto_merge.py` now exercises slot-based validator-role fixtures while no longer expecting the intentionally deleted `docs/openclaw/PARALLEL_TRACK_GUIDE.md`.

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
| `elis/reviewer_identity.py` | modified |
| `openclaw/openclaw.json` | modified |
| `scripts/check_current_pe.py` | modified |
| `scripts/check_reviewer_identity.py` | modified |
| `scripts/gh_bot.py` | modified |
| `tests/test_check_current_pe.py` | modified |
| `tests/test_gate2_auto_merge.py` | modified |
| `tests/test_validator_identity_mapping.py` | modified |

## Design Decisions
- Kept the original PE change set focused on the 11 requested deletions, then applied only the minimal follow-up code fixes needed to unblock PR #388 CI.
- Updated `scripts/check_current_pe.py` to treat role labels as compatibility aliases per engine: `codex` matches either `CODEX` or `slot-a`, `claude` matches either `Claude Code` or `slot-b`, and `gemini` still matches `Gemini CLI`.
- Restored reviewer identity loading through the canonical runtime config instead of recreating the deleted standalone map file, so runtime helpers and CI tests share one source of truth.
- Kept `scripts/check_reviewer_identity.py` black-formatted and aligned the gate-2 acceptance fixtures with the slot-based Agent roles table now used in `CURRENT_PE.md`.
- Removed the `PARALLEL_TRACK_GUIDE.md` expectation from gate-2 acceptance coverage because that file deletion is intentional PE scope, not a regression.
- Added a defensive `sys.path` bootstrap to `scripts/gh_bot.py` so direct script execution still resolves the in-repo `elis` package on hosts where `scripts/` becomes `sys.path[0]`.
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
- `python -m black scripts/check_reviewer_identity.py`
  - `1 file left unchanged.`
- `python -m black --check scripts/check_current_pe.py scripts/check_reviewer_identity.py tests/test_check_current_pe.py tests/test_gate2_auto_merge.py`
  - `4 files would be left unchanged.`
- `python -m ruff check scripts/check_current_pe.py scripts/check_reviewer_identity.py tests/test_check_current_pe.py tests/test_gate2_auto_merge.py`
  - `All checks passed!`
- `python -m pytest -q tests/test_check_current_pe.py tests/test_gate2_auto_merge.py`
  - `/usr/bin/python: No module named pytest`
- `python scripts/check_current_pe.py`
  - `CURRENT_PE.md OK — release context, roles, registry, and alternation valid.`
- `python - <<'PY' ... runpy.run_path('scripts/gh_bot.py', run_name='__main__') ... PY`
  - Reached CLI argument parsing successfully, confirming the updated direct-script import path no longer fails before startup.
- `python scripts/gh_bot.py codex --check-only`
  - Fails later at runtime on this host because bot-token environment is not configured here, but no longer fails due to missing `config/reviewer_identity_map.json`.
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
M  elis/reviewer_identity.py
M  openclaw/openclaw.json
M  scripts/check_reviewer_identity.py
M  scripts/gh_bot.py
M  tests/test_gate2_auto_merge.py
M  tests/test_validator_identity_mapping.py
```

### §6.2 Repository state
```text
feature/pe-infra-agent-01-doc-consolidation
```

### §6.3 Quality gates
- `black --check` (targeted checker + tests): PASS
- `ruff check` (targeted checker + tests): PASS
- `pytest -q tests/test_check_current_pe.py tests/test_gate2_auto_merge.py`: [blocked] unavailable in current environment (`No module named pytest`)
- `python scripts/check_current_pe.py`: PASS
- `gh_bot.py` import/startup smoke check: PASS
- `pytest -q` for identity tests: [blocked] unavailable in current environment (`No module named pytest`)
- Legacy-name verification search: [blocked] repo still contains many non-archive references outside this PE scope

### §6.4 Ready to merge
```text
NO — outstanding blocked validation: pytest unavailable in this session, and repo-wide legacy-name references remain outside delete-only PE scope. Fixes #3 and #4 are implemented but not fully test-executed locally on this host.
```
