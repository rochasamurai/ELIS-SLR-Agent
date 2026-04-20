# HANDOFF — PE-INFRA-SLR-04 · Model-Agnostic Agent Naming Governance

**Date:** 2026-04-20  
**PE:** `PE-INFRA-SLR-04`  
**Branch:** `feature/pe-infra-slr-04-model-agnostic-agent-naming-governance`  
**Implementer:** `infra-impl-a` (CODEX @ `elis-server`)  
**Validator:** `infra-val-b` (Claude Code)

---

## 1) Summary

This PE replaces active model-coupled workflow agent identifiers with
model-agnostic slot-based identifiers using the canonical rule
`<domain>-<role>-<slot>`. The change keeps engine resolution and alternation
logic working through an explicit committed migration map, updates active
governance/runtime artefacts to the new IDs, and adds a policy gate preventing
new model-coupled IDs from re-entering active workflow surfaces.

---

## 2) Deliverables

| File | Change |
|------|--------|
| `config/agent_id_migration_map.json` | New normative migration map from legacy IDs to canonical slot-based IDs |
| `elis/agent_id.py` | New shared helper for canonical IDs, engine resolution, and compatibility mapping |
| `elis/role_surface.py` | Switched canonical surfaces from engine suffixes to slot suffixes |
| `scripts/check_current_pe.py` | Engine resolution now uses the committed slot registry |
| `scripts/check_parallel_eligibility.py` | Parallel-engine checks accept canonical slot-based IDs |
| `scripts/check_role_registration.py` | Registry validation accepts canonical IDs and explicit legacy compatibility |
| `scripts/plan_loader.py` | Plan ingestion resolves engines through the shared agent-ID helper |
| `scripts/pm_assign_pe.py` | New PE assignment emits canonical slot-based IDs |
| `scripts/pm_status_reporter.py` | PO-facing engine display resolves from canonical IDs |
| `scripts/check_openclaw_doctor.py` | OpenClaw doctor expects slot-based SLR/runtime IDs |
| `scripts/check_agent_id_naming_policy.py` | New policy gate for active agent-ID surfaces |
| `tests/test_agent_id_naming_policy.py` | New PE-specific acceptance coverage |
| `tests/test_pe_infra_slr_01.py` | Updated role-surface normalisation tests for slot-based naming |
| `tests/test_pm_assign_pe.py` | Updated PM-assignment expectations to canonical IDs |
| `AGENTS.md` | Added normative slot registry and updated §14 governance language |
| `CURRENT_PE.md` | Active PE rows now use canonical IDs for PE-INFRA-SLR-04/05 |
| `ELIS_MultiAgent_Implementation_Plan_v1_8_3.md` | Active plan references updated to canonical IDs |
| `docs/openclaw/openclaw_sanitised.json` | Active OpenClaw runtime IDs updated to canonical slot-based IDs |
| `docs/decisions/ADR-009-model-agnostic-agent-id-slots.md` | New ADR recording the slot-based naming decision |
| `docs/decisions/README.md` | ADR index updated |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | A normative naming rule is committed and referenced by PM workflow docs for all active agent IDs (`<domain>-<role>-<slot>` or explicit equivalent) | **PASS** — `AGENTS.md` §14 and `config/agent_id_migration_map.json` define the canonical rule and slot registry |
| AC-2 | A committed migration map exists (old ID → new ID) for all active infra/prog/slr agent IDs used by PM, implementer, and validator workflows | **PASS** — `config/agent_id_migration_map.json` covers active infra/prog/slr and phase-specialised SLR IDs |
| AC-3 | `CURRENT_PE.md`, active plan references, and OpenClaw runtime config are updated to use the new model-agnostic IDs | **PASS** — `CURRENT_PE.md`, `ELIS_MultiAgent_Implementation_Plan_v1_8_3.md`, and `docs/openclaw/openclaw_sanitised.json` use canonical slot-based IDs for active surfaces |
| AC-4 | Dispatch and validation scripts that resolve agent IDs are updated to accept the new IDs; legacy IDs are allowed only as an explicit temporary compatibility path | **PASS** — `elis/agent_id.py` centralises canonical/legacy resolution and the affected scripts now call it |
| AC-5 | A CI/policy check fails if new model-coupled naming is introduced into active agent-ID surfaces | **PASS** — `scripts/check_agent_id_naming_policy.py` and `tests/test_agent_id_naming_policy.py` enforce the active-surface guard |
| AC-6 | `python -m pytest tests/test_agent_id_naming_policy.py -v` passes | **PASS** — 11 tests passed under the repaired local Python environment |

---

## 4) Validation Commands

### Formatting

```text
$ & '.\.venv312\Scripts\python.exe' -m black --check elis\agent_id.py elis\role_surface.py scripts\check_current_pe.py scripts\check_openclaw_doctor.py scripts\check_parallel_eligibility.py scripts\check_role_registration.py scripts\check_agent_id_naming_policy.py scripts\plan_loader.py scripts\pm_assign_pe.py scripts\pm_status_reporter.py tests\test_pe_infra_slr_01.py tests\test_pm_assign_pe.py tests\test_agent_id_naming_policy.py
All done! ✨ 🍰 ✨
13 files would be left unchanged.
```

### Lint

```text
$ & '.\.venv312\Scripts\python.exe' -m ruff check elis\agent_id.py elis\role_surface.py scripts\check_current_pe.py scripts\check_openclaw_doctor.py scripts\check_parallel_eligibility.py scripts\check_role_registration.py scripts\check_agent_id_naming_policy.py scripts\plan_loader.py scripts\pm_assign_pe.py scripts\pm_status_reporter.py tests\test_pe_infra_slr_01.py tests\test_pm_assign_pe.py tests\test_agent_id_naming_policy.py
All checks passed!
```

### PE-specific and regression tests

```text
$ & '.\.venv312\Scripts\python.exe' -m pytest tests\test_agent_id_naming_policy.py tests\test_pe_infra_slr_01.py tests\test_pm_assign_pe.py tests\test_check_current_pe.py tests\test_plan_loader.py -v --basetemp=.tmp_case4 -p no:cacheprovider
============================= test session starts =============================
platform win32 -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-infra-slr-04
configfile: pyproject.toml
collected 122 items

tests\test_agent_id_naming_policy.py ...........                         [  9%]
tests\test_pe_infra_slr_01.py .....................................      [ 39%]
tests\test_pm_assign_pe.py ..........................                    [ 60%]
tests\test_check_current_pe.py ............                              [ 70%]
tests\test_plan_loader.py ....................................           [100%]

============================= 122 passed in 2.91s =============================
```

---

## 5) Scope Gate

Changed files vs `origin/main`:

```text
M  AGENTS.md
M  CURRENT_PE.md
M  ELIS_MultiAgent_Implementation_Plan_v1_8_3.md
M  docs/decisions/README.md
M  docs/openclaw/openclaw_sanitised.json
M  elis/role_surface.py
M  scripts/check_current_pe.py
M  scripts/check_openclaw_doctor.py
M  scripts/check_parallel_eligibility.py
M  scripts/check_role_registration.py
M  scripts/plan_loader.py
M  scripts/pm_assign_pe.py
M  scripts/pm_status_reporter.py
M  tests/test_pe_infra_slr_01.py
M  tests/test_pm_assign_pe.py
?? config/agent_id_migration_map.json
?? docs/decisions/ADR-009-model-agnostic-agent-id-slots.md
?? elis/agent_id.py
?? scripts/check_agent_id_naming_policy.py
?? tests/test_agent_id_naming_policy.py
?? HANDOFF.md
```

All tracked changes are in-scope for PE-INFRA-SLR-04.

---

## 6) Design Notes

1. **Canonical IDs are slot-based, not engine-derived.**
   The active naming rule is now `<domain>-<role>-<slot>`, with slot-to-engine
   mapping committed in `config/agent_id_migration_map.json`.

2. **Legacy IDs remain explicit compatibility input only.**
   The code still accepts legacy names such as `infra-impl-codex`, but only via
   the committed migration map. New active artefacts must emit canonical IDs.

3. **Shared resolution replaced repeated substring parsing.**
   `elis/agent_id.py` is now the single place for canonicalisation and engine
   lookup, reducing drift across PM and validator tooling.

4. **The policy check is intentionally narrow to active surfaces.**
   Historical audit text is preserved. The guard blocks model-coupled naming in
   active workflow artefacts instead of rewriting archival history.

---

## 7) Notes for Validator

- The local runtime was repaired during implementation using `uv` and a fresh
  `.venv312`; the original `.venv` created via Python Manager was not used for
  validation because it pointed at an inaccessible interpreter path.
- `pytest` needed `--basetemp` inside the worktree and `-p no:cacheprovider`
  under this Windows environment to avoid sandbox/temp-directory ACL noise.
- `gh pr list` returned `HTTP 401` in this session, so PR discovery/opening could
  not be completed from this shell. The branch and `HANDOFF.md` are ready for the
  next authenticated `git push` / `gh pr create` step.
