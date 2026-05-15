# PE-OPS-PM-GUARDRAILS-02 — PE Task

## PE_ID
PE-OPS-PM-GUARDRAILS-02

## Objective
Harden PM PE opening and dispatch recovery behaviour by adding deterministic context checks, failure-class taxonomy, and PM no-write enforcement guard scripts.

## Base
`origin/main` @ `93b62cf9565b2e5b4682b75212ef16527220058b`

## Branch
`feature/pe-ops-pm-guardrails-02-harden-pm-pe-opening-and-dispatch-recovery-behaviour`

## Staffing
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`

## Working copy
- Implementer fixed workspace: `/opt/elis/agent-worktrees/infra-impl-b`
- Live PM workspace: `/home/samurai/openclaw/workspace-pm`

## Approved scope
- `openclaw/workspaces/workspace-pm/AGENTS.md` — constitutional rules update
- `openclaw/workspaces/workspace-pm/SKILLS.md` — new workflow skills file
- `/home/samurai/openclaw/workspace-pm/AGENTS.md` — live PM AGENTS.md update
- `/home/samurai/openclaw/workspace-pm/SKILLS.md` — live PM SKILLS.md update
- `scripts/check_pe_opening_context.py` — new PE opening context check
- `scripts/check_dispatch_binding.py` — update with failure-class taxonomy
- `scripts/check_implementation_readiness.py` — rewrite to be PE-agnostic
- `scripts/check_review_artifact.py` — new REVIEW file path and authorship check
- `scripts/check_pm_no_write.py` — new PM no-write enforcement check
- `scripts/check_review.py` — compatibility update (standard REVIEW.md path)
- `tests/test_check_pe_opening_context.py` — new tests
- `tests/test_check_dispatch_binding.py` — updated tests
- `tests/test_check_implementation_readiness.py` — new tests
- `tests/test_check_review_artifact.py` — new tests
- `tests/test_check_pm_no_write.py` — new tests
- `tests/test_check_review.py` — updated tests
- `tests/test_pm_agent_rules.py` — updated tests
- `.elis/pe/PE-OPS-PM-GUARDRAILS-02/HANDOFF.md`
- `.elis/pe/PE-OPS-PM-GUARDRAILS-02/PE_TASK.md`
- `.elis/pe/PE-OPS-PM-GUARDRAILS-02/validation-evidence.md`

## Required governance content
- PM AGENTS.md constitutional rules: PE opening context guard, dispatch failure classes, PM no-write enforcement, dispatch binding guard.
- PM SKILLS.md workflow skills: PE opening context workflow, dispatch binding workflow, failure-class taxonomy, PM no-write verification, implementation readiness check.
- Failure-class taxonomy covering all dispatch blocking scenarios.
- Deterministic check scripts for PE opening context, dispatch binding, implementation readiness, REVIEW file integrity, and PM no-write enforcement.
- Tests for all new and updated scripts.
- PE evidence bundle with file backup hashes.

## Hard boundaries
- no containerisation implementation
- no OpenClaw runtime/config changes
- no A2A
- no Dash
- no GitHub auth changes
- no model/provider changes
- no config/secret/token changes
- no PM direct file edits outside the approved live workspace files
- no dispatch of validator

## Acceptance criteria
- `check_pe_opening_context.py` exits cleanly with correct arguments and reports classification codes on failure.
- `check_dispatch_binding.py` supports `--classify` flag with failure-class taxonomy.
- `check_implementation_readiness.py` is PE-agnostic (does not hardcode PE-OPS-SKILLS-01).
- `check_review_artifact.py` validates REVIEW.md path and authorship.
- `check_pm_no_write.py` detects PM-authored files.
- `check_review.py` finds `REVIEW.md` files at `.elis/pe/*/REVIEW.md` standard paths.
- All tests pass (`pytest tests/test_check_pe_opening_context.py tests/test_check_dispatch_binding.py tests/test_check_implementation_readiness.py tests/test_check_review_artifact.py tests/test_check_pm_no_write.py tests/test_check_review.py tests/test_pm_agent_rules.py`).
- Live PM workspace files backed up with before/after hashes recorded.
- Repo-tracked `openclaw/workspaces/workspace-pm/SKILLS.md` created.

## Evidence bundle
- `HANDOFF.md`
- `validation-evidence.md`
- backup paths for live PM workspace files touched
- before/after hashes for live PM workspace files touched
