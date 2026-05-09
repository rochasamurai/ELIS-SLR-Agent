# PE-OPS-ADVISOR-01 — Implement ELIS Advisor on Hermes

## PE_ID
PE-OPS-ADVISOR-01

## Title
Implement ELIS Advisor on Hermes

## Objective
Define and prepare an advisory-only ELIS Advisor on Hermes so it can help with PE opening, evidence review, risk classification, and safe draft guidance without gaining dispatch, implementation, validation, or merge authority.

## Background
ELIS needs a Hermes-hosted advisor that can support PM and Supervisor with opening packets, boundary checks, and evidence-oriented drafting while keeping all final decisions and execution with the approved human and agent roles.

## Allowed file scope
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-ADVISOR-01/PE_TASK.md`

## Implementation file scope to be proposed and pinned before dispatch
- Hermes/config binding documentation required to safely define the advisor deployment
- advisory role and boundary notes required by this PE
- any additional file scope must be explicitly pinned before dispatch

## Out of scope
- Hermes/OpenClaw config changes during opening
- secrets, tokens, GitHub settings, Docker, or host permissions changes during opening
- implementation or validation work during opening
- dispatching agents during opening
- PR / merge actions during opening
- unrelated cleanup or refactoring

## Role-boundary rules
- **PM:** coordinates PE flow and records evidence
- **Supervisor:** performs read-only platform/runtime diagnosis, including Hermes/OpenClaw binding checks, and collects evidence unless explicitly authorised otherwise
- **ELIS Advisor:** advisory-only support for PE opening, evidence review, risk classification, next safest action, and draft messages
- **Implementer:** implementation only
- **Validator:** validation only
- **Carlos/PO:** final approval authority where applicable

The ELIS Advisor is advisory-only:
- no dispatch authority
- no implementation authority
- no official validation authority
- no config authority
- no GitHub write authority
- no merge authority

## Advisory workflow
- review opening packets
- identify missing evidence or unsafe assumptions
- draft concise next-step guidance
- classify risk and boundary concerns
- suggest the safest allowed action
- keep all decisions with PM, Supervisor, and Carlos/PO as applicable

## Hermes operating model
- define the advisor as a Hermes-bound advisory surface only
- preserve read-only inspection requirements before any dispatch
- do not assume config or binding changes are needed until verified
- keep deployment prerequisites explicit and auditable

## Deliverables
- PE task artefact for `PE-OPS-ADVISOR-01`
- ELIS Advisor operating model suitable for later Hermes deployment
- role definition for the ELIS Advisor
- authority and prohibition rules
- advisory workflow for:
  - opening packets
  - evidence review
  - risk classification
  - next safest action
  - draft messages
- Hermes binding / diagnosis notes for later deployment planning
- explicit no-authority rules:
  - no dispatch
  - no implementation
  - no official validation
  - no config changes
  - no GitHub write
  - no merge

## Validation deliverables
- explicit acceptance criteria
- evidence requirements for advisory actions
- confirmation that the ELIS Advisor remains advisory-only
- confirmation that no dispatch/config/merge authority is introduced
- confirmation that read-only Hermes inspection happens before any deployment change

## Acceptance criteria
- advisor role is clearly defined
- advisory boundaries are explicit and enforced
- Hermes binding questions are identified before dispatch
- no dispatch, implementation, validation, config, GitHub write, or merge authority is granted
- opening scope remains limited to the approved files only

## Opening-step restrictions
- opening edits are limited to `CURRENT_PE.md` and `.elis/pe/PE-OPS-ADVISOR-01/PE_TASK.md`
- do not dispatch implementer yet
- do not modify Hermes/OpenClaw config
- do not push/open PR/merge

## Staffing
- Implementer: `infra-impl-a`
- Validator: `infra-val-b`

## Branch
- `feature/pe-ops-advisor-01-implement-elis-advisor-on-hermes`
