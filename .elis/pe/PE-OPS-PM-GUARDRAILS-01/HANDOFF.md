# HANDOFF — PE-OPS-PM-GUARDRAILS-01

## Summary
This PE defines the PM coordination-only boundary so the role stays read-broad / write-narrow and cannot drift into implementation or validation.

## Expected changes
- docs/governance/ELIS_Agent_Roles_and_Boundaries.md
- tests/test_pe_ops_pm_guardrails_01.py
- /home/samurai/openclaw/workspace-pm/AGENTS.md
- /home/samurai/openclaw/workspace-pm/SKILLS.md
- /home/samurai/openclaw/workspace-pm/MEMORY.md only if needed
- .elis/pe/PE-OPS-PM-GUARDRAILS-01/PE_TASK.md
- .elis/pe/PE-OPS-PM-GUARDRAILS-01/REVIEW.md (validator-owned; pending)
- .elis/pe/PE-OPS-PM-GUARDRAILS-01/validation-evidence.md

## Design decisions
- Keep the PM workspace lean: AGENTS.md remains the entry point and SKILLS.md carries the stronger coordination boundary language.
- Record the future containerisation requirement now, but do not implement the containerisation layer in this PE.
- Use a validator checklist that explicitly calls out PM authorship of implementation and validation artefacts.

## Backup / rollback plan
- Snapshot each live PM workspace file before editing.
- Keep the snapshot paths in the evidence file.
- Rollback is byte-for-byte restore from the snapshot, followed by hash re-checks.

## Status packet
- Base: `origin/main` @ `514bd9eeea9e59a181f87b62ca935df1f511844c`
- Branch: `feature/pe-ops-pm-guardrails-01-enforce-pm-coordination-only-behaviour`
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`
- PM role: coordination only
