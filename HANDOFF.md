# HANDOFF.md — PE-MS-06

**PE:** `PE-MS-06`  
**Title:** SLR Phase Workspace Provisioning  
**Implementer:** CODEX (`infra-impl-codex`)  
**Validator:** Claude Code (`infra-val-claude`)  
**Branch:** `feature/pe-ms-06-slr-phase-workspaces`  
**Plan:** `ELIS_MultiAgent_Implementation_Plan_v1_6.md`

---

## Summary

This PE replaces the generic SLR workspace/runtime topology with the Architecture v1.6
phase-specialized model. The source-controlled OpenClaw config now declares the full
19-agent roster, the 5 SLR phase workspaces are present in repo with specialized rules,
the generic `workspace-slr-impl` / `workspace-slr-val` trees are retired, and the
workspace/doctor checks now validate the phase-specific topology.

---

## Files Changed

| File | Change | Purpose |
|---|---|---|
| `openclaw/openclaw.json` | Modified | Replace generic SLR runtime entries with 10 phase-specialized agents |
| `docs/openclaw/openclaw_sanitised.json` | Modified | Redacted reviewable copy of the new 19-agent source-config |
| `openclaw/workspaces/workspace-slr-harvest/*` | Added | Harvest phase workspace rules and engine-specific instructions |
| `openclaw/workspaces/workspace-slr-screen/*` | Added | Screen phase workspace rules and engine-specific instructions |
| `openclaw/workspaces/workspace-slr-extract/*` | Added | Extraction phase workspace rules and engine-specific instructions |
| `openclaw/workspaces/workspace-slr-synth/*` | Added | Synthesis phase workspace rules and engine-specific instructions |
| `openclaw/workspaces/workspace-slr-prisma/*` | Added | PRISMA phase workspace rules and engine-specific instructions |
| `openclaw/workspaces/workspace-slr-impl/*` | Deleted | Retire generic SLR implementer workspace |
| `openclaw/workspaces/workspace-slr-val/*` | Deleted | Retire generic SLR validator workspace |
| `scripts/check_workspace_completeness.py` | Modified | Validate 19-agent / 10-workspace phase topology and file completeness |
| `scripts/check_openclaw_doctor.py` | Modified | Reject generic `slr-*` IDs and require the 10 phase-specialized SLR IDs |
| `scripts/deploy_openclaw_workspaces.sh` | Modified | Copy the full workspace tree even when `rsync` is unavailable |
| `tests/test_check_workspace_completeness.py` | Modified | Cover phase-shared workspaces, PM file set, and SLR cutover rules |
| `tests/test_check_openclaw_doctor.py` | Modified | Cover the 19-agent SLR phase roster and legacy-ID rejection |
| `tests/test_check_openclaw_config_sync.py` | Modified | Refresh fixture IDs to phase-specialized SLR agents |
| `docs/openclaw/AGENT_CATALOGUE.md` | Modified | Move the catalogue to the new 19-agent source-controlled target roster |
| `docs/openclaw/NATIVE_INSTALL.md` | Modified | Document the 5 SLR phase workspaces and deploy/restart requirement |
| `docs/openclaw/SLR_PHASE_WORKSPACE_PROVISIONING_2026-03-25.md` | Added | Provisioning note for the new SLR workspace layer |
| `docs/pm_agent/ASSIGNMENT_PROTOCOL.md` | Modified | Stop implying a single generic `slr-*` prefix for SLR assignments |
| `HANDOFF.md` | Updated | This file |

---

## Design Decisions

1. `PE-MS-06` provisions all 5 SLR phase workspaces in one cutover because the target architecture is a 19-agent topology, not a hybrid generic/phase mix.
2. SLR phase workspaces intentionally share one workspace per phase between the impl/val pair. The old `PE-MS-05` segmentation rule was narrowed so it still enforces separation for `infra` and `prog`, while accepting the phase-shared SLR model.
3. The generic `slr-impl-*` / `slr-val-*` source-controlled runtime entries are removed now to avoid maintaining two contradictory SLR topologies in repo.
4. The deploy script fallback was fixed in this PE because copying only `workspace-pm` when `rsync` is missing would silently fail to provision the new SLR phase workspaces.
5. `docs/openclaw/WORKSPACE_AUDIT_2026-03-25.md` is left untouched as historical evidence of the pre-cutover 7-workspace state from `PE-MS-05`.

---

## Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| AC-1 | The 5 SLR phase workspaces exist in repo and replace the generic SLR workspace pair | PASS | `workspace-slr-harvest`, `screen`, `extract`, `synth`, `prisma` added; generic `workspace-slr-impl` / `workspace-slr-val` deleted |
| AC-2 | `openclaw/openclaw.json` declares the Architecture v1.6 19-agent roster with phase-specialized SLR agents | PASS | `check_openclaw_doctor.py` exits 0; `openclaw_sanitised.json` shows 19-agent target |
| AC-3 | Workspace completeness check passes on the new topology | PASS | `check_workspace_completeness.py` exits 0 with `19 agents, 10 workspace(s)` |
| AC-4 | Generic SLR runtime/workspace declarations are no longer accepted by repo-side gates | PASS | `check_openclaw_doctor.py` and `check_workspace_completeness.py` both reject legacy `slr-*` IDs/workspaces |
| AC-5 | Native deployment guidance is aligned so the new workspaces can be deployed on `elis-server` | PASS | `deploy_openclaw_workspaces.sh` fallback fixed; `NATIVE_INSTALL.md` updated |

---

## Validation Commands

### Repo-side topology checks

```text
& 'C:\Program Files\LibreOffice\program\python.exe' scripts/check_workspace_completeness.py
OK: 19 agents, 10 workspace(s) — all present, all files complete, segmentation clean

& 'C:\Program Files\LibreOffice\program\python.exe' scripts/check_openclaw_doctor.py
OK: openclaw doctor configuration meets expected policies
```

### Quality gates

```text
python -m black --check .
All done! ✨ 🍰 ✨
121 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest tests/test_check_workspace_completeness.py tests/test_check_openclaw_doctor.py tests/test_check_openclaw_config_sync.py -q
............................                                             [100%]

python -m pytest -q --disable-warnings
........................................................................ [ 12%]
........................................................................ [ 24%]
........................................................................ [ 36%]
........................................................................ [ 49%]
........................................................................ [ 61%]
........................................................................ [ 73%]
........................................................................ [ 86%]
........................................................................ [ 98%]
........                                                                 [100%]
```

### Scope

```text
git diff --name-status origin/main...HEAD
M	docs/openclaw/AGENT_CATALOGUE.md
M	docs/openclaw/NATIVE_INSTALL.md
A	docs/openclaw/SLR_PHASE_WORKSPACE_PROVISIONING_2026-03-25.md
M	docs/openclaw/openclaw_sanitised.json
M	docs/pm_agent/ASSIGNMENT_PROTOCOL.md
M	openclaw/openclaw.json
A	openclaw/workspaces/workspace-slr-extract/AGENTS.md
A	openclaw/workspaces/workspace-slr-extract/CLAUDE.md
A	openclaw/workspaces/workspace-slr-extract/CODEX.md
A	openclaw/workspaces/workspace-slr-harvest/AGENTS.md
A	openclaw/workspaces/workspace-slr-harvest/CLAUDE.md
A	openclaw/workspaces/workspace-slr-harvest/CODEX.md
D	openclaw/workspaces/workspace-slr-impl/AGENTS.md
D	openclaw/workspaces/workspace-slr-impl/CLAUDE.md
D	openclaw/workspaces/workspace-slr-impl/CODEX.md
A	openclaw/workspaces/workspace-slr-prisma/AGENTS.md
A	openclaw/workspaces/workspace-slr-prisma/CLAUDE.md
A	openclaw/workspaces/workspace-slr-prisma/CODEX.md
A	openclaw/workspaces/workspace-slr-screen/AGENTS.md
A	openclaw/workspaces/workspace-slr-screen/CLAUDE.md
A	openclaw/workspaces/workspace-slr-screen/CODEX.md
A	openclaw/workspaces/workspace-slr-synth/AGENTS.md
A	openclaw/workspaces/workspace-slr-synth/CLAUDE.md
A	openclaw/workspaces/workspace-slr-synth/CODEX.md
D	openclaw/workspaces/workspace-slr-val/AGENTS.md
D	openclaw/workspaces/workspace-slr-val/CLAUDE.md
D	openclaw/workspaces/workspace-slr-val/CODEX.md
M	scripts/check_openclaw_doctor.py
M	scripts/check_workspace_completeness.py
M	scripts/deploy_openclaw_workspaces.sh
M	tests/test_check_openclaw_config_sync.py
M	tests/test_check_openclaw_doctor.py
M	tests/test_check_workspace_completeness.py
```

---

## Remaining Host Action

This PE updates the source-controlled runtime and workspace layer only. The live host still needs the standard native deployment step after merge:

```bash
bash scripts/deploy_openclaw_workspaces.sh
systemctl --user restart openclaw-gateway
openclaw doctor
```

That host sync is intentionally left for post-merge operational follow-up.

---

## Tooling Note

The default shell wrapper in this environment inconsistently resolves the `python` launcher for anything other than some pre-wired commands. To avoid fabricating results, repo-specific checks were run with an explicit interpreter where needed, and the final `black --check` / `pytest` evidence was captured from the elevated environment that uses the user's normal Python setup.

---

## Ready for Validator

Yes. The branch is limited to the SLR phase workspace cutover, supporting checks, and deployment/docs alignment needed to validate the 19-agent source-controlled topology.
