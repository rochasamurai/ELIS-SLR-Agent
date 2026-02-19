## Agent update — CODEX / PE-INFRA-04 / 2026-02-19

### Verdict
FAIL

### Branch / PR
Branch: chore/pe-infra-04-autonomous-secrets
PR: #255 (open)
Base: release/2.0

### Gate results
black: PASS
ruff:  PASS
pytest: 445 passed, 0 failed (17 deprecation warnings, pre-existing)
PE-specific tests: N/A (infrastructure workflow/scripts)

### Scope (diff vs release/2.0)
A	.agentignore
A	.env.example
A	.github/workflows/auto-assign-validator.yml
A	.github/workflows/auto-merge-on-pass.yml
M	.gitignore
M	AGENTS.md
M	CLAUDE.md
M	CODEX.md
M	HANDOFF.md
A	scripts/check_agent_scope.py
A	scripts/check_handoff.py
A	scripts/check_status_packet.py
A	scripts/parse_verdict.py

### Required fixes (blocking)
1. FAIL — Gate 2 does not enforce “CI green” before auto-merge (AC-2 regression).
File: `.github/workflows/auto-merge-on-pass.yml:49` and `.github/workflows/auto-merge-on-pass.yml:55`
Evidence: merge path only checks `steps.verdict.outputs.verdict == 'PASS'` and `veto == false`, then calls `github.rest.pulls.merge(...)`. There is no check of required status checks or workflow conclusions.
Required fix: add an explicit CI-success gate (e.g., verify required checks are successful for the PR head SHA) before merge.

2. FAIL — Verdict parsing is cross-PE and currently breaks on existing review format.
File: `scripts/parse_verdict.py:29`, `scripts/parse_verdict.py:30`, `scripts/parse_verdict.py:41`, `scripts/parse_verdict.py:65`
Evidence:
- Script chooses latest `REVIEW_PE*.md` by mtime, not the review file for the active PR/PE.
- Running `python scripts/parse_verdict.py` returns:
  - `review_file=REVIEW_PE_chore_agents_compliance.md`
  - `ERROR: Verdict field missing or unrecognised: 'PASS (with 1 non-blocking warning)'`
This causes false FAIL/IN_PROGRESS from unrelated review files.
Required fix: scope verdict parsing to the active PE/PR (deterministic file target), and tolerate normalized verdict prefixes (e.g., `PASS` with suffix notes) or enforce strict format with migration of existing review files used by automation.

3. FAIL — AC-5 Layer 4 requires CI integration for `check_agent_scope.py`, but `ci.yml` was not updated.
File: `.github/workflows/ci.yml`
Evidence: no `secrets-scope-check` job and no invocation of `python scripts/check_agent_scope.py`.
Required fix: add the mandated CI job to run `check_agent_scope.py` on every PR.

### Ready to merge
NO — blocking findings above must be fixed.

### Next
Implementer (Claude Code): fix the 3 blocking items on this same branch, update HANDOFF with fresh evidence, push, and request re-validation.
