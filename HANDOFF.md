# HANDOFF — PE-GHA-02 · Workflow Classification and Branch Protection Hardening

**Date:** 2026-04-22
**PE:** `PE-GHA-02`
**Branch:** `feature/pe-gha-02-workflow-classification-and-branch-protection`
**Implementer:** `gha-impl-b` (Claude Code)
**Validator:** `gha-val-a` (CODEX @ `elis-server`)

---

## 1) Summary

Implements Phases B, C, and D of the GitHub Actions CI Authority Plan.

- **Phase B** — each key workflow file in `.github/workflows/` now carries a
  `# Classification:` header (CI / CI Advisory / Mixed / Orchestration) making
  the CI-vs-orchestration boundary self-documenting. ADR-012 records the rule.
- **Phase C** — branch protection hardening requires PM admin action (bot
  accounts lack branch protection write access). Exact steps are documented in
  `docs/_active/PE_GHA_02_PHASE_C_PM_ACTION.md`.
- **Phase D** — gate regression evidence is in §4: CI is already the sole
  blocking gate; no local agent claim can override a failing CI status.

---

## 2) Deliverables

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | Added `# Classification: CI` header |
| `.github/workflows/deep-review.yml` | Added `# Classification: CI / Advisory` header |
| `.github/workflows/autoformat.yml` | Added `# Classification: Mixed` header |
| `.github/workflows/implementer-runner.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/validator-runner.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/auto-merge-on-pass.yml` | Added `# Classification: Orchestration` header |
| `docs/decisions/ADR-012-workflow-classification.md` | New ADR recording CI vs Orchestration classification rule |
| `docs/decisions/README.md` | Added ADR-012 to index |
| `docs/_active/PE_GHA_02_PHASE_C_PM_ACTION.md` | PM action doc: exact steps to add 4 checks to branch protection |
| `HANDOFF.md` | This file |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | Every portable blocking gate runs in GitHub Actions | PASS (pre-existing; confirmed) |
| AC-2 | No agent token required for blocking CI path | PASS (pre-existing; confirmed) |
| AC-3 | Agent-token workflows limited to orchestration/mutation | PASS — classification headers make the boundary explicit |
| AC-4 | Repository guidance states CI is authoritative | PASS (PE-GHA-01) |
| AC-5 | `elis-server` documented as local preflight environment | PASS (PE-GHA-01) |
| AC-6 | Branch protection relies on GitHub Actions alone | PARTIAL — 3 of 7 portable-gate jobs required; Phase C PM action documents the 4 remaining additions |

---

## 4) Validation Commands

```bash
python scripts/check_agent_scope.py
python -m black --check --include "\.py$" elis/ tests/ scripts/
python -m ruff check .
python -m pytest tests/ --basetemp=.tmp/pe-gha-02 --tb=no
```

### Command output

```text
Agent scope clean — no secret-pattern files detected in worktree.

All done! ✨ 🍰 ✨
178 files would be left unchanged.

All checks passed!

2 failed, 1014 passed, 17 warnings in 12.89s
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_missing
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_lacks_oauth_key
(2 pre-existing failures unrelated to PE-GHA-02)
```

### Phase D — gate regression evidence

`auto-merge-on-pass.yml` Step 8 checks `mergeable_state == 'clean'` before
merging. That state requires all required CI checks to pass. A PR with local
agent claims but failing CI cannot reach `clean` and cannot auto-merge. CI is
already the sole blocking gate.

---

## 5) Scope Gate

```text
git diff --name-status origin/main..HEAD

M  .github/workflows/auto-merge-on-pass.yml
M  .github/workflows/autoformat.yml
M  .github/workflows/ci.yml
M  .github/workflows/deep-review.yml
M  .github/workflows/implementer-runner.yml
M  .github/workflows/validator-runner.yml
A  docs/_active/PE_GHA_02_PHASE_C_PM_ACTION.md
A  docs/decisions/ADR-012-workflow-classification.md
M  docs/decisions/README.md
M  HANDOFF.md
```

10 files. All within Phase B/C/D scope.

---

## 6) Notes for Validator

1. Confirm the 6 workflow files carry correct `# Classification:` headers.
2. Confirm ADR-012 exists and is indexed in `docs/decisions/README.md`.
3. Confirm `docs/_active/PE_GHA_02_PHASE_C_PM_ACTION.md` contains actionable
   branch protection steps for PM.
4. AC-1 through AC-5 satisfied; AC-6 partial — pending PM Phase C action.
5. Check CI green on this PR as Phase D gate regression evidence.
6. The 2 pytest failures are pre-existing (`test_verify_claude_auth.py`).
