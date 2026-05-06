# PE-OPS-PO-ADVISOR-01 — Deploy ELIS PO Advisor on Hermes

## PE_ID
PE-OPS-PO-ADVISOR-01

## Title
Deploy ELIS PO Advisor on Hermes

## Objective
Define and prepare a Hermes-based ELIS PO Advisor agent to support Carlos/PO with governance advice, routing decisions, evidence review, and safe message drafting across PM, Supervisor, GitHub Agent, Implementer, Validator, GitHub, and Discord.

## Background
ELIS needs an advisory-only PO-facing helper that improves governance clarity and message quality without gaining execution authority. The PO Advisor must support decision-making and drafting while preserving Carlos/PO as the final approval authority.

## Allowed file scope
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-PO-ADVISOR-01/PE_TASK.md`

Optional only if later authorised by the PE task:
- `docs/governance/ELIS_PO_Advisor_Operating_Model.md`

## Out of scope
- Hermes/OpenClaw config changes
- implementation or validation work
- dispatching agents
- PR / merge actions
- GitHub write actions without later explicit PO approval
- any bypass of Carlos/PO approval
- Discord channel creation
- Discord permission changes
- message relay on behalf of Carlos/PO
- unrelated cleanup or refactoring

## Role-boundary rules
- **PM:** coordinates PE flow, routes approved actions, and records evidence
- **Supervisor:** platform/runtime diagnosis, OpenClaw/Hermes/Discord/GitHub operational safety, worktree certification, config diagnosis/change only after explicit PO approval, and read-only evidence collection unless explicitly authorised
- **PO Advisor:** advise Carlos/PO; it does not own PE coordination
- **GitHub Agent:** remains separate; no role bleed
- **Implementer:** implementation only
- **Validator:** validation only
- **Carlos/PO:** final approval authority

The PO Advisor is advisory-only:
- no dispatch authority
- no implementation authority
- no official validation authority
- no config authority
- no GitHub write authority
- no merge authority

## Discord operating model
- Define only the operating model, not channel creation or permission changes.
- Recommend whether the PO Advisor should operate in:
  - parent channel,
  - PE threads,
  - or a dedicated advisory channel.
- Define message-drafting workflow for Carlos/PO approval.
- Define future deployment requirements for Discord routing.

Explicit rule:
- PO Advisor may draft messages to PM, Supervisor, GitHub Agent, Implementer, Validator, or GitHub for Carlos/PO review.
- PO Advisor must not send or relay those messages on behalf of Carlos/PO unless a later PO-approved deployment PE creates a controlled relay mechanism with explicit permissions, logging, and rollback.

## Implementation deliverables
- PE task artefact for `PE-OPS-PO-ADVISOR-01`
- PO Advisor operating model suitable for later Hermes deployment
- role definition for the PO Advisor
- authority and prohibition rules
- advisory workflow for:
  - verdicts
  - evidence review
  - risk classification
  - next safest action
  - draft messages
- Discord operating model covering:
  - parent channel usage
  - PE thread usage
  - advisory-channel recommendations
  - audit trail handling
  - message drafting workflow
- interaction rules with PM, Supervisor, GitHub Agent, Implementer, Validator, GitHub, and Carlos/PO
- explicit no-authority rules:
  - no dispatch
  - no implementation
  - no official validation
  - no config changes
  - no GitHub write
  - no merge
  - no message relay on behalf of Carlos/PO

## Validation deliverables
- explicit acceptance criteria
- evidence requirements for advisory actions
- confirmation that the PO Advisor remains advisory-only
- confirmation that no dispatch/config/merge authority is introduced
- confirmation that Carlos/PO approval remains final

## Acceptance criteria
- PO Advisor role is clearly defined
- advisory boundaries are explicit and enforced
- Discord routing and audit behavior are defined
- no dispatch, implementation, validation, config, GitHub write, merge, channel creation, or permission-change authority is granted
- Carlos/PO retains final approval authority
- opening scope remains limited to the approved files only

## Opening-step restrictions
- opening edits are limited to `CURRENT_PE.md` and `.elis/pe/PE-OPS-PO-ADVISOR-01/PE_TASK.md`
- do not dispatch implementer yet
- do not modify Hermes/OpenClaw config
- do not push/open PR/merge

## Staffing
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`

## Branch
- `feature/pe-ops-po-advisor-01-deploy-elis-po-advisor-on-hermes`
