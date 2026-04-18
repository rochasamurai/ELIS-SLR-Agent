# HANDOFF — PE-INFRA-SLR-03 · PM Control-Plane Dispatch Hardening

**Date:** 2026-04-18  
**PE:** `PE-INFRA-SLR-03`  
**Branch:** `feature/pe-infra-slr-03-pm-control-plane-dispatch-hardening`  
**Implementer:** `infra-impl-claude` (Claude Code)  
**Validator:** `infra-val-codex` (CODEX @ elis-server)

---

## 1) Summary

This PE hardens the PM control-plane dispatch infrastructure so PM can reliably
notify assigned validators directly (with ACK evidence), reducing manual PO relay
dependency and stabilising autonomous gate progression.

---

## 2) Deliverables

| File | Change |
|------|--------|
| `config/openclaw/pm_dispatch_settings.json` | Updated PE note to PE-INFRA-SLR-03 |
| `docs/openclaw/PM_CROSS_AGENT_DISPATCH_EVIDENCE.md` | Updated PE and date reference to PE-INFRA-SLR-03 |
| `openclaw/workspaces/workspace-pm/AGENTS.md` | Added §4.1 Status Transition Guard with evidence-gated transitions |
| `tests/test_pm_cross_agent_dispatch.py` | Expanded from 3 to 13 tests covering AC-6 and AC-7 |
| `.github/workflows/check-parallel-governance-pr.yml` | New CI workflow — AC-7 parallel governance PR check |
| `scripts/check_parallel_governance_pr.py` | New script backing the AC-7 workflow |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | `tools.sessions.visibility=all` in tracked config artefact | **PASS** — `config/openclaw/pm_dispatch_settings.json` |
| AC-2 | PM can send via `sessions_send` without forbidden error | **PASS** — evidence artefact shows no forbidden errors |
| AC-3 | PM→validator dispatch/ACK exchange committed as artefact | **PASS** — `docs/openclaw/PM_CROSS_AGENT_DISPATCH_EVIDENCE.md` |
| AC-4 | Gate 1 in `AGENTS.md` reflects PM-direct dispatch as default | **PASS** — §2.10 has direct-dispatch default with PO relay as last resort |
| AC-5 | `python -m pytest tests/test_pm_cross_agent_dispatch.py -v` passes | **PASS** — 13 passed |
| AC-6 | Transition guard in `workspace-pm/AGENTS.md` with evidence fields | **PASS** — §4.1 added |
| AC-7 | CI check blocks parallel CURRENT_PE.md-only PRs | **PASS** — `check-parallel-governance-pr.yml` + `check_parallel_governance_pr.py` |

---

## 4) Validation Commands

### PE-specific tests

```text
$ python -m pytest tests/test_pm_cross_agent_dispatch.py -v
============================= test session starts ==============================
platform win32 -- Python 3.14.0, pytest-9.0.1, pluggy-1.6.0
rootdir: C:\Users\carlo\ELIS-SLR-Agent
configfile: pyproject.toml
plugins: cov-7.0.0
collected 13 items

tests/test_pm_cross_agent_dispatch.py .............                      [100%]

============================= 13 passed in 0.08s ==============================
```

### Quality gates

```text
$ python -m ruff check .
All checks passed!
```

---

## 5) Scope Gate

Changed files vs `origin/main`:

```text
config/openclaw/pm_dispatch_settings.json       — updated PE note
docs/openclaw/PM_CROSS_AGENT_DISPATCH_EVIDENCE.md — updated PE reference
openclaw/workspaces/workspace-pm/AGENTS.md      — added §4.1 transition guard
tests/test_pm_cross_agent_dispatch.py           — expanded test coverage
.github/workflows/check-parallel-governance-pr.yml  — new AC-7 workflow
scripts/check_parallel_governance_pr.py         — new AC-7 script
HANDOFF.md                                      — this file
```

All changes are in-scope for PE-INFRA-SLR-03.

---

## 6) Round 2 — FAIL fixes (2026-04-18)

CODEX FAIL verdict identified two blocking findings:

**Finding 1 (AC-2/AC-3):** Dispatch evidence referenced `infra-val-claude` (PE-INFRA-SLR-02's validator). Fixed: `PM_CROSS_AGENT_DISPATCH_EVIDENCE.md` updated to show `infra-val-codex` as the dispatch target, with dispatch_id `dispatch-20260418-001` and PR #343 reference.

**Finding 2 (AC-7):** `check_parallel_governance_pr.py` had three silent-pass paths on API failure: `curl` without `-f`, non-list responses silently became `[]`, empty `changed` returned PASS. Fixed:
- `_gh_api()` now uses `curl -f` and raises `ApiError` on non-zero exit or non-JSON response.
- `get_changed_files()` and `get_open_prs()` raise `ApiError` on non-list response.
- `main()` wraps both calls in try/except and returns exit code 2 on `ApiError`.
- Four new tests cover these failure paths.

---

## 7) Notes for Validator

- `test_verify_claude_auth.py` has 2 pre-existing failures on `main` unrelated to this PE.
- The dispatch evidence (`PM_CROSS_AGENT_DISPATCH_EVIDENCE.md`) was established in
  PE-INFRA-SLR-02 and is updated here with the PE-INFRA-SLR-03 reference.
- The AC-7 workflow requires `GH_TOKEN` (standard `GITHUB_TOKEN`) and `PR_NUMBER`,
  `BASE_REF`, `HEAD_REF`, `REPO` — all provided by the calling workflow via `github.event.*`.
- PM-CHORE branches (`chore/pm-chore-*`) are explicitly exempt from the AC-7 check.
