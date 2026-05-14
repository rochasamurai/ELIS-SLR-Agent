# PE-OPS-PM-GUARDRAILS-01 — PE Task

## PE_ID
PE-OPS-PM-GUARDRAILS-01

## Objective
Make the PM coordination-only rule explicit, checkable, and durable before any future containerisation work.

## Base
`origin/main` @ `514bd9eeea9e59a181f87b62ca935df1f511844c`

## Branch
`feature/pe-ops-pm-guardrails-01-enforce-pm-coordination-only-behaviour`

## Staffing
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`

## Working copy
- Implementer fixed workspace: `/opt/elis/agent-worktrees/pm/.worktrees/pe-ops-pm-guardrails-01`
- Live PM workspace: `/home/samurai/openclaw/workspace-pm`

## Approved scope
- `docs/governance/ELIS_Agent_Roles_and_Boundaries.md`
- `.elis/pe/PE-OPS-PM-GUARDRAILS-01/PE_TASK.md`
- `.elis/pe/PE-OPS-PM-GUARDRAILS-01/HANDOFF.md`
- `.elis/pe/PE-OPS-PM-GUARDRAILS-01/REVIEW.md` (validator-owned; not authored by PM or implementer)
- `.elis/pe/PE-OPS-PM-GUARDRAILS-01/validation-evidence.md`
- `tests/test_pe_ops_pm_guardrails_01.py`
- live PM workspace files:
  - `/home/samurai/openclaw/workspace-pm/AGENTS.md`
  - `/home/samurai/openclaw/workspace-pm/SKILLS.md`
  - `/home/samurai/openclaw/workspace-pm/MEMORY.md` only if needed

## Required governance content
- PM coordinates only.
- PM must not edit files.
- PM must not implement.
- PM must not validate.
- PM must not author REVIEW.md / REVIEW_PE*.md.
- PM needs broad read-only visibility.
- PM must have narrow or no write authority.
- Future containerisation must enforce read-broadly/write-narrowly with filesystem permissions and mount design.

## Validator checklist language
- Confirm the PM did not author implementation artefacts.
- Confirm the PM did not author validation artefacts.
- Confirm the live PM workspace updates are limited to the approved files.
- Confirm no excluded OpenClaw runtime, auth, container, GitHub, A2A, Dash, CLAUDE.md, or CODEX.md files were changed.

## Hard boundaries
- no containerisation implementation
- no OpenClaw runtime/config changes
- no A2A
- no Dash
- no GitHub auth changes
- no model/provider changes
- no `CLAUDE.md` or `CODEX.md` changes
- no `docs/openclaw/*`
- no `openclaw/workspaces/*`
- no PM direct file edits outside the approved live workspace files

## Acceptance criteria
- PM coordination-only language is explicit in live PM workspace docs and repo governance.
- Read-only visibility and narrow/no-write authority are documented.
- Future containerisation requirement is recorded.
- Validator checklist language requires confirmation that PM did not author implementation or validation artefacts.
- `tests/test_pe_ops_pm_guardrails_01.py` checks the new governance language.
- live workspace edits are backed up first and evidenced.

## Evidence bundle
- `HANDOFF.md`
- `validation-evidence.md`
- backup paths for any live PM workspace files touched
- before/after hashes for live PM workspace files touched
