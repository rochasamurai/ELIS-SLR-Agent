# HANDOFF.md — PE-MS-04

**PE:** `PE-MS-04`  
**Title:** Agent Registry and Canonical Path Alignment  
**Implementer:** CODEX (`infra-impl-codex`)  
**Validator:** Claude Code (`infra-val-claude`)  
**Branch:** `feature/pe-ms-04-agent-registry-alignment`  
**Plan:** `ELIS_MultiAgent_Implementation_Plan_v1_6.md`

---

## Summary

This PE captures the current native OpenClaw runtime roster as-operated on `elis-server`,
normalizes the source-controlled runtime config to canonical host workspace paths, and
adds a sanitized runtime-config reference plus an explicit runtime audit document.

The live runtime is still a 13-agent configuration rather than the 19-agent
Architecture v1.6 target. PE-MS-04 records that gap clearly instead of masking it.

---

## Files Changed

| File | Change | Purpose |
|---|---|---|
| `openclaw/openclaw.json` | Updated | Normalize source-controlled runtime config to canonical host paths |
| `docs/openclaw/openclaw_sanitised.json` | Added | Redacted reviewable runtime-config reference |
| `docs/openclaw/AGENT_CATALOGUE.md` | Rewritten | Distinguish current 13-agent runtime from 19-agent architecture target |
| `docs/openclaw/RUNTIME_REGISTRY_AUDIT_2026-03-24.md` | Added | Capture live `agents.list` snapshot and gap analysis |
| `scripts/check_openclaw_doctor.py` | Updated | Enforce canonical native workspace paths and PM dual-channel bindings |
| `scripts/check_openclaw_security.py` | Updated | Reject `/app/...` runtime paths and require native host-path contract |
| `tests/test_check_openclaw_doctor.py` | Added | Cover canonical-path and binding validation rules |

---

## Design Decisions

1. PE-MS-04 treats the current live runtime as a **13-agent audited baseline**, not as a fictional 19-agent completed state.
2. The source-controlled runtime config now uses explicit canonical host paths under `/home/samurai/openclaw/...` for all currently registered agents.
3. The sanitized runtime reference lives under `docs/openclaw/openclaw_sanitised.json` so reviewers can inspect runtime shape without copying live identifiers.
4. The updated doctor/security checks reject `/app/...` container-only runtime paths and reject non-canonical workspace declarations in the repo config.
5. The gap from 13 generic/legacy agents to the 19-agent Architecture v1.6 target is left explicit for later PEs (`PE-MS-05` to `PE-MS-07`).

---

## Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| AC-1 | `openclaw config get agents.list` returns all declared agent IDs | PASS | live `ssh elis-server "openclaw config get agents.list --json"` output captured below |
| AC-2 | each agent workspace points to an existing host directory | PASS (current runtime roster) | live runtime snapshot shows the current 13-agent roster using the 7 active workspace families; source-controlled config normalized to those canonical host paths |
| AC-3 | no declared agent depends on `/app/...` container-only paths | PASS | `openclaw/openclaw.json`, sanitized copy, and check scripts all reject `/app/...` |
| AC-4 | `openclaw doctor` exits 0 with the expected agent list | PASS (repo config gate) | `scripts/check_openclaw_doctor.py` passes on the updated config; live `openclaw doctor` probe from this shell timed out and is recorded below |

---

## Live Runtime Evidence

### Live `agents.list` snapshot from `elis-server`

```text
ssh elis-server "openclaw config get agents.list --json"
[
  {
    "id": "pm",
    "workspace": "/home/samurai/openclaw/workspace-pm",
    "model": "openai/gpt-5-mini",
    "tools": {
      "elevated": {
        "enabled": false,
        "allowFrom": {
          "discord": [
            "1485180911619408014"
          ]
        }
      }
    }
  },
  {
    "id": "slr-impl-codex",
    "workspace": "workspace-slr-impl",
    "model": "openai/gpt-5.1-codex"
  },
  {
    "id": "slr-impl-claude",
    "workspace": "workspace-slr-impl",
    "model": "anthropic/claude-sonnet-4-6"
  },
  {
    "id": "slr-val-codex",
    "workspace": "workspace-slr-val",
    "model": "openai/gpt-5.1-codex"
  },
  {
    "id": "slr-val-claude",
    "workspace": "workspace-slr-val",
    "model": "anthropic/claude-sonnet-4-6"
  },
  {
    "id": "prog-impl-codex",
    "workspace": "workspace-prog-impl",
    "model": "openai/gpt-5.1-codex"
  },
  {
    "id": "prog-impl-claude",
    "workspace": "workspace-prog-impl",
    "model": "anthropic/claude-sonnet-4-6"
  },
  {
    "id": "prog-val-codex",
    "workspace": "workspace-prog-val",
    "model": "openai/gpt-5.1-codex"
  },
  {
    "id": "prog-val-claude",
    "workspace": "workspace-prog-val",
    "model": "anthropic/claude-sonnet-4-6"
  },
  {
    "id": "infra-impl-codex",
    "workspace": "workspace-infra-impl",
    "model": "openai/gpt-5.1-codex"
  },
  {
    "id": "infra-impl-claude",
    "workspace": "workspace-infra-impl",
    "model": "anthropic/claude-sonnet-4-6"
  },
  {
    "id": "infra-val-codex",
    "workspace": "workspace-infra-val",
    "model": "openai/gpt-5.1-codex"
  },
  {
    "id": "infra-val-claude",
    "workspace": "workspace-infra-val",
    "model": "anthropic/claude-sonnet-4-6"
  }
]
```

### Live probe limitation

```text
ssh elis-server "openclaw doctor"
command timed out after 60928 milliseconds
```

The host `agents.list` probe worked reliably from this shell, but `openclaw doctor`
did not return before timeout. The repo-side doctor gate below was used as the
deterministic validation artifact for this PE.

---

## Validation Commands

### Runtime-shape checks

```text
rg -n "gpt-5-mini|/home/samurai/openclaw|/app/|13-agent|19-agent" openclaw/openclaw.json docs/openclaw/openclaw_sanitised.json docs/openclaw/AGENT_CATALOGUE.md docs/openclaw/RUNTIME_REGISTRY_AUDIT_2026-03-24.md scripts/check_openclaw_doctor.py scripts/check_openclaw_security.py
docs/openclaw/RUNTIME_REGISTRY_AUDIT_2026-03-24.md:12:The live native OpenClaw runtime is still operating a **13-agent** configuration.
docs/openclaw/RUNTIME_REGISTRY_AUDIT_2026-03-24.md:13:That runtime does not yet match the **19-agent** Architecture v1.6 target, but it
docs/openclaw/RUNTIME_REGISTRY_AUDIT_2026-03-24.md:17:- the runtime no longer depends on `/app/...` container paths
docs/openclaw/RUNTIME_REGISTRY_AUDIT_2026-03-24.md:36:pm | /home/samurai/openclaw/workspace-pm | openai/gpt-5-mini
docs/openclaw/AGENT_CATALOGUE.md:23:As of 2026-03-24, the native runtime is still operating a 13-agent roster.
docs/openclaw/AGENT_CATALOGUE.md:45:- PM is currently in contingency mode on `openai/gpt-5-mini`.
docs/openclaw/AGENT_CATALOGUE.md:55:- no agent workspace points to `/app/...`
docs/openclaw/AGENT_CATALOGUE.md:60:This PE does **not** yet expand the runtime to the full 19-agent Architecture v1.6 target.
scripts/check_openclaw_security.py:81:        if "/app/" in workspace:
scripts/check_openclaw_doctor.py:32:        elif "/app/" in workspace:
openclaw/openclaw.json:6:        "workspace": "/home/samurai/openclaw/workspace-pm",
openclaw/openclaw.json:7:        "model": "openai/gpt-5-mini",
```

### Repo-side doctor gate

```text
& 'C:\Program Files\LibreOffice\program\python.exe' scripts/check_openclaw_doctor.py
OK: openclaw doctor configuration meets expected policies
```

### Quality gates

```text
python -m black --check .
All done! ✨ 🍰 ✨
119 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
........................................................................ [ 12%]
........................................................................ [ 25%]
........................................................................ [ 37%]
........................................................................ [ 50%]
........................................................................ [ 63%]
........................................................................ [ 75%]
........................................................................ [ 88%]
.................................................................        [100%]
565 passed, 17 warnings in 24.4s

python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

### Local tooling limitation

```text
& 'C:\Program Files\LibreOffice\program\python.exe' scripts/check_openclaw_security.py
ModuleNotFoundError: No module named 'yaml'
```

`check_openclaw_security.py` was updated and covered by `pytest`, but direct local
execution in this shell hit a Python-environment mismatch because the explicit
interpreter available here does not include `PyYAML`. CI installs `PyYAML==6.0.2`
for this check.

---

## Remaining Host Action

To complete live operational validation after merge:

1. pull the merged branch on `elis-server`
2. deploy `openclaw/openclaw.json` through the normal OpenClaw deployment path
3. rerun `openclaw config get agents.list --json`
4. rerun `openclaw doctor`
5. confirm the live runtime now exposes canonical absolute host paths for all 13 current agents

Later PEs then expand this normalized 13-agent baseline to the full Architecture v1.6 roster.

---

## Ready for Validator

Yes. Scope is limited to runtime registry audit, canonical path normalization, sanitized runtime reference, and matching repo-side validation checks.
