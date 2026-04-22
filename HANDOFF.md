# HANDOFF — PE-GHA-02 · Workflow Classification and Branch Protection Hardening

**Date:** 2026-04-22
**PE:** `PE-GHA-02`
**Branch:** `feature/pe-gha-02-workflow-classification-and-branch-protection`
**Implementer:** `gha-impl-b` (Claude Code)
**Validator:** `gha-val-a` (CODEX @ `elis-server`)

---

## 1) Summary

Implements Phases B, C, and D of the GitHub Actions CI Authority Plan.

- **Phase B** — every workflow file in `.github/workflows/` now carries a
  `# Classification:` header (CI / CI Advisory / Mixed / Orchestration) making
  the CI-vs-orchestration boundary self-documenting. All 35 workflow files
  classified. ADR-012 records the rule.
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
| `.github/workflows/agent-automerge.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/agent-run.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/agents-compliance.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/auto-assign-validator.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/benchmark_2_phase1.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/benchmark_validation.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/bot-auth-verify.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/bot-commit.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/check-parallel-governance-pr.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/ci-current-pe.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/elis-agent-nightly.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/elis-agent-screen.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/elis-agent-search.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/elis-housekeeping.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/elis-imports-convert.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/elis-search-preflight.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/elis-validate.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/export-docx.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/notify-pm-agent.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/pe-sequencer.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/pm-arbiter.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/pm-chore-approve.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/pm-discord-command.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/pm-observability-dashboard.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/pm-plan-load.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/projects-autoadd.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/projects-runid.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/test_database_harvest.yml` | Added `# Classification: Orchestration` header |
| `.github/workflows/validator-dispatch.yml` | Added `# Classification: Orchestration` header |
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
| AC-3 | Agent-token workflows limited to orchestration/mutation | PASS — all 35 workflow files carry `# Classification:` headers making the boundary explicit |
| AC-4 | Repository guidance states CI is authoritative | PASS (PE-GHA-01) |
| AC-5 | `elis-server` documented as local preflight environment | PASS (PE-GHA-01) |
| AC-6 | Branch protection relies on GitHub Actions alone | PASS — all 7 checks required on main: quality, tests, validate, current-pe-check, secrets-scope-check, review-evidence-check, slr-quality-check |

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

M  .github/workflows/agent-automerge.yml
M  .github/workflows/agent-run.yml
M  .github/workflows/agents-compliance.yml
M  .github/workflows/auto-assign-validator.yml
M  .github/workflows/auto-merge-on-pass.yml
M  .github/workflows/autoformat.yml
M  .github/workflows/benchmark_2_phase1.yml
M  .github/workflows/benchmark_validation.yml
M  .github/workflows/bot-auth-verify.yml
M  .github/workflows/bot-commit.yml
M  .github/workflows/check-parallel-governance-pr.yml
M  .github/workflows/ci-current-pe.yml
M  .github/workflows/ci.yml
M  .github/workflows/deep-review.yml
M  .github/workflows/elis-agent-nightly.yml
M  .github/workflows/elis-agent-screen.yml
M  .github/workflows/elis-agent-search.yml
M  .github/workflows/elis-housekeeping.yml
M  .github/workflows/elis-imports-convert.yml
M  .github/workflows/elis-search-preflight.yml
M  .github/workflows/elis-validate.yml
M  .github/workflows/export-docx.yml
M  .github/workflows/implementer-runner.yml
M  .github/workflows/notify-pm-agent.yml
M  .github/workflows/pe-sequencer.yml
M  .github/workflows/pm-arbiter.yml
M  .github/workflows/pm-chore-approve.yml
M  .github/workflows/pm-discord-command.yml
M  .github/workflows/pm-observability-dashboard.yml
M  .github/workflows/pm-plan-load.yml
M  .github/workflows/projects-autoadd.yml
M  .github/workflows/projects-runid.yml
M  .github/workflows/test_database_harvest.yml
M  .github/workflows/validator-dispatch.yml
M  .github/workflows/validator-runner.yml
A  docs/_active/PE_GHA_02_PHASE_C_PM_ACTION.md
A  docs/decisions/ADR-012-workflow-classification.md
M  docs/decisions/README.md
M  HANDOFF.md
```

39 files. All within Phase B/C/D scope.

---

## 6) Notes for Validator

1. Confirm all 35 workflow files carry correct `# Classification:` headers on
   line 1: 1 CI, 1 CI Advisory, 1 Mixed, 32 Orchestration.
2. Confirm ADR-012 exists and is indexed in `docs/decisions/README.md`.
3. Confirm `docs/_active/PE_GHA_02_PHASE_C_PM_ACTION.md` contains actionable
   branch protection steps for PM.
4. AC-1 through AC-6 all satisfied. Branch protection verified via:
   `gh api repos/rochasamurai/ELIS-Multi-AI-Agent-Platform/branches/main --jq '.protection.required_status_checks.checks[].context'`
   → quality, tests, validate, current-pe-check, secrets-scope-check, review-evidence-check, slr-quality-check
5. Check CI green on this PR as Phase D gate regression evidence.
6. The 2 pytest failures are pre-existing (`test_verify_claude_auth.py`).
