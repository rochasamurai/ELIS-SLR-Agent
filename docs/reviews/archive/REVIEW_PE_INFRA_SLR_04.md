# REVIEW — PE-INFRA-SLR-04 · Model-Agnostic Agent Naming Governance

**Validator:** `infra-val-b` (Claude Code)  
**Date:** 2026-04-20  
**PR:** #345  
**Branch:** `feature/pe-infra-slr-04-model-agnostic-agent-naming-governance`

---

### Verdict

PASS

---

### Gate results

```
black:  PASS — implementer reported scoped black --check clean on all changed Python files
ruff:   PASS — implementer reported scoped ruff check clean on all changed Python files
pytest: PASS — 74/74 passed locally (infra-val-b session);
               122/122 passed in implementer CI run
```

---

### Scope

```
M  AGENTS.md
M  CURRENT_PE.md
M  ELIS_MultiAgent_Implementation_Plan_v1_8_3.md
A  config/agent_id_migration_map.json
A  docs/decisions/ADR-009-model-agnostic-agent-id-slots.md
M  docs/decisions/README.md
M  docs/openclaw/openclaw_sanitised.json
A  elis/agent_id.py
M  elis/role_surface.py
M  openclaw/openclaw.json
M  scripts/check_agent_id_naming_policy.py
M  scripts/check_current_pe.py
M  scripts/check_openclaw_doctor.py
M  scripts/check_parallel_eligibility.py
M  scripts/check_role_registration.py
M  scripts/plan_loader.py
M  scripts/pm_assign_pe.py
M  scripts/pm_status_reporter.py
A  tests/test_agent_id_naming_policy.py
M  tests/test_check_openclaw_doctor.py
M  tests/test_pe_infra_slr_01.py
M  tests/test_pm_assign_pe.py
M  HANDOFF.md
```

All changes are in-scope for PE-INFRA-SLR-04. No unrelated files modified.

---

### AC Assessment

| AC | Criterion | Verdict | Evidence |
|----|-----------|---------|----------|
| AC-1 | Normative naming rule committed and referenced by PM workflow docs | **PASS** | `AGENTS.md` §14 + `docs/decisions/ADR-009-model-agnostic-agent-id-slots.md` — rule `<domain>-<role>-<slot>` |
| AC-2 | Migration map covers all active infra/prog/slr IDs | **PASS** | `config/agent_id_migration_map.json` — 22 legacy→canonical mappings across all active domains |
| AC-3 | `CURRENT_PE.md`, plan references, and OpenClaw runtime config updated | **PASS** | CURRENT_PE.md active rows use `infra-impl-a`/`infra-val-b`; `openclaw/openclaw.json` all slot-based; plan PE-INFRA-SLR-04/05 sections show canonical IDs |
| AC-4 | Scripts accept new IDs; legacy only via explicit compatibility path | **PASS** | `elis/agent_id.py` centralises resolution; all affected scripts delegate to it; `legacy_to_canonical_map()` is the single compat path |
| AC-5 | CI/policy check fails on model-coupled naming in active surfaces | **PASS** | `scripts/check_agent_id_naming_policy.py` guards CURRENT_PE.md, plan, `openclaw_sanitised.json`, and `AGENTS.md` §14 |
| AC-6 | `pytest tests/test_agent_id_naming_policy.py -v` passes | **PASS** | 11 passed locally; 122 passed in CI including regression tests |

---

### Required fixes

None.

---

### Evidence

```
$ python -m pytest tests/test_agent_id_naming_policy.py tests/test_pe_infra_slr_01.py tests/test_pm_assign_pe.py -v
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.1, pluggy-1.6.0
collected 74 items

tests/test_agent_id_naming_policy.py ...........                         [ 14%]
tests/test_pe_infra_slr_01.py .....................................      [ 64%]
tests/test_pm_assign_pe.py ..........................                    [100%]

74 passed in 0.69s
```

Migration map (22 entries, all canonical IDs are slot-based, no provider tokens):

```json
{
  "naming_rule": "<domain>-<role>-<slot>",
  "slots": {"a": "codex", "b": "claude", "c": "gemini"},
  "legacy_to_canonical": {
    "infra-impl-codex": "infra-impl-a",  "infra-impl-claude": "infra-impl-b",
    "infra-val-codex":  "infra-val-a",   "infra-val-claude":  "infra-val-b",
    ...22 total...
  }
}
```

`openclaw/openclaw.json` agent IDs (all slot-based, confirmed):
`pm, harvest-impl-a, harvest-val-b, screen-impl-b, screen-val-a, extract-impl-a,
extract-val-b, synth-impl-b, synth-val-a, prisma-impl-b, prisma-val-a,
prog-impl-a, prog-impl-b, prog-val-a, prog-val-b,
infra-impl-a, infra-impl-b, infra-val-a, infra-val-b`

---

### Observations (non-blocking)

1. **HANDOFF self-applies the new naming.** The HANDOFF identifies `infra-impl-a` as Implementer and `infra-val-b` as Validator — the PE eats its own dog food. Correct.
2. **`pm` agent retains its singleton ID.** The `pm` agent is not subject to the slot rule and is correctly excluded from the migration map and policy checks.
3. **Historical registry rows preserve legacy IDs.** The policy check is intentionally narrow to active surfaces; archival history is untouched. This is the correct design.
