# PE-GOV-01 — Consolidate ELIS PE Operating Protocol Templates

## Objective
Consolidate repeated ELIS PM / Discord operating instructions into canonical, versioned repo files in `docs/governance/`. These documents codify the operating rules that have been enforced through chat history, CLAUDE.md, AGENTS.md, ELIS_General_Guidance.md, and ad-hoc PM directives into standalone, versioned governance artefacts.

## Branch
`feature/pe-gov-01-operating-protocol-templates`

## Implementer
`infra-impl-b`

## Validator
`infra-val-a`

## Controlling Documents
- `CURRENT_PE.md` — release context and active PE registry
- `AGENTS.md` — agent workflow rules and role definitions
- `CLAUDE.md` — session-level agent rules
- `docs/governance/ELIS_General_Guidance.md` — short canonical operating guidance
- `docs/governance/ELIS_Multi_Agent_Governance_Architecture_v2.md`
- `docs/governance/ELIS_Multi_Agent_Governance_Implementation_Plan_v2.md`
- `docs/governance/ELIS_PE_Gatekeeper_Checklist.md`
- `LESSONS_LEARNED.md` — error patterns and recovery rules

## Allowed Files
- `docs/governance/ELIS_PE_Operating_Protocol.md` (create)
- `docs/governance/ELIS_PE_Dispatch_Checklist.md` (create)
- `docs/governance/ELIS_Worktree_Preflight_Checklist.md` (create)
- `docs/governance/ELIS_Provider_Preflight_Checklist.md` (create)
- `docs/governance/ELIS_No_Silent_Failure_Recovery.md` (create)
- `HANDOFF.md` (update)
- `.elis/pe/PE-GOV-01/PE_TASK.md` (create — this file)
- `docs/templates/PE_TASK.template.md` (update if needed)
- `docs/templates/HANDOFF.template.md` (create if needed)
- `docs/templates/REVIEW.template.md` (create if needed)

## Forbidden Files
- Do not touch `/opt/elis/repo`
- Do not push, open PR, merge, or dispatch validator
- Do not resume PE-AGT-01 or Increment 3
- Do not touch PR #390
- Do not modify files outside the allowed list above

## Required Artefacts
1. `docs/governance/ELIS_PE_Operating_Protocol.md`
2. `docs/governance/ELIS_PE_Dispatch_Checklist.md`
3. `docs/governance/ELIS_Worktree_Preflight_Checklist.md`
4. `docs/governance/ELIS_Provider_Preflight_Checklist.md`
5. `docs/governance/ELIS_No_Silent_Failure_Recovery.md`
6. `HANDOFF.md` — updated with PE-GOV-01 implementation status

## Acceptance Criteria
- AC-1: All five governance documents exist in `docs/governance/` with meaningful, versioned content.
- AC-2: Each document references its authoritative source (AGENTS.md, ELIS_General_Guidance.md, CLAUDE.md, LESSONS_LEARNED.md, or PM directives).
- AC-3: HANDOFF.md is updated to reflect PE-GOV-01 implementation state.
- AC-4: No files outside the allowed list are modified.
- AC-5: `python scripts/check_current_pe.py` passes.
- AC-6: Worktree is clean after final commit.
- AC-7: Implementation commit is present.

## Required Commands
- `python scripts/check_current_pe.py`

## Blocker Reporting Format
```text
BLOCKER: <description>
Evidence: <command output or file excerpt>
Suggested resolution: <what needs to happen>
```
