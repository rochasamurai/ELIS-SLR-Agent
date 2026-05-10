# ELIS Advisor — Request/Response Templates

**Version:** 1.0  
**Date:** 2026-05-10  
**Status:** Operational  

---

## 1. Default response format

```
1. Verdict
2. Correct recipient
3. Evidence
4. Risk
5. Next safest action
6. Draft message
```

## 2. Template: PM validation/status packet response

When PM sends a structured validation/status packet, respond using this template.

### 2.1 Sample packet from PM

```
VALIDATION PACKET — PE-OPS-XXXX-XX

PE: PE-OPS-XXXX-XX
Commit: abc1234def5678
Agent: infra-impl-b
Verdict: PASS
Review artefact: .elis/pe/PE-OPS-XXXX-XX/REVIEW.md
Checks: check_fixed_worktrees.py: PASS, pytest: PASS
Findings: None
Ready for PR: yes
```

### 2.2 Advisor response to a PASS packet

```
Verdict
Packet acknowledged. Validation is PASS.

Correct recipient
Carlos / PO.

Evidence
PE-OPS-XXXX-XX validation packet reports PASS verdict.
Commit abc1234 has been reviewed by [agent].
Checks: all passing.
Review artefact: .elis/pe/PE-OPS-XXXX-XX/REVIEW.md.

Risk
Low — all checks pass, no blocking findings.

Next safest action
1. Confirm PO is satisfied with the validation evidence.
2. If yes, proceed to PR step (PM opens PR or authorises PO to open).
3. Ensure HANDOFF.md and REVIEW.md are in the PR body.

Draft message
PM, the PE-OPS-XXXX-XX validation is complete with a PASS verdict.
Please proceed to the PR step if PO approves.
```

### 2.3 Advisor response to a FAIL packet

```
Verdict
Packet acknowledged. Validation is FAIL.

Correct recipient
[Implementer agent] — the correct agent to fix the findings.

Evidence
PE-OPS-XXXX-XX validation packet reports FAIL verdict.
[Specific blocking findings from packet]
Checks: [which checks failed].

Risk
Moderate — blocking findings must be resolved before PR.

Next safest action
1. [Implementer] should review the failing checks.
2. Fix findings and commit.
3. Request re-validation by [Validator].
4. Do not proceed to PR until re-validation passes.

Draft message
[Implementer], validation of PE-OPS-XXXX-XX reported FAIL.
Please review and fix: [list findings].
After fixing, request re-validation from [Validator].
```

### 2.4 Advisor response to an incomplete packet

```
Verdict
Packet received but incomplete. Cannot assess.

Correct recipient
PM.

Evidence
The validation packet is missing one or more required fields:
- [missing field 1]
- [missing field 2]

Risk
Moderate — without complete evidence, PO cannot make an informed decision.

Next safest action
Ask PM to provide the missing fields before proceeding.

Draft message
PM, the validation packet for PE-OPS-XXXX-XX is missing required fields.
Please provide: [list missing fields].
```

## 3. Template: PO/PM governance question

When PO or PM asks a governance question, respond using this template.

```
Verdict
[Brief answer to the question]

Correct recipient
[Who should act on this]

Evidence
[Citations from CURRENT_PE.md, governance docs, handoff evidence, etc.]

Risk
[Risk level + brief justification]

Next safest action
[Step-by-step recommendation]

Draft message
[If applicable, a ready-to-use message for the correct recipient]
```

## 4. Template: PE state inquiry

When asked about PE state, respond with this structured summary.

```
PE Status Summary — [PE ID]

Status: [planning/implementing/validating/gate-1-pending/gate-2-pending/merged/blocked/superseded]
Branch: feature/[branch-name]
Implementer: [agent-id]
Validator: [agent-id]
Last evidence: [HANDOFF.md / REVIEW.md if available]

Current phase:
- [brief description of where the PE is now]

Known risks:
- [risk 1]
- [risk 2]

Next expected step:
- [what should happen next]
```

## 5. Template: Boundary/caveat warning

When asked to cross a boundary or when a risk is detected.

```
Advisory Warning — [Issue]

Summary
[One-line description of the boundary issue]

Relevant boundary
[Citing the relevant section from ELIS_Advisor_Role_Boundaries.md]

Risk
[Risk level]

Recommendation
[What should happen instead]

Draft message
[Draft for PO or PM to send to the correct party]
```

## 6. Template: Boot confirmation

When ELIS Advisor starts up and confirms operational status.

```
ADVISOR_SERVICE_OK — ELIS Advisor.

Boot reference:
- Bootstrap: docs/ops/elis-advisor/ELIS_Advisor_Bootstrap_Operating_Mode.md
- Handoff: .elis/pe/PE-OPS-ADVISOR-HANDOFF-01/evidence/ELIS_ADVISOR_HANDOFF_elis-server_2026-05-09.md
- PE: [current PE from CURRENT_PE.md]
- Branch: [current branch]

Waiting in #elis-advisor for PM/PO messages.
```

## 7. Template: A2A envelope (structured message to PM/Supervisor)

```
A2A Envelope
Source: advisor
Target: pm|supervisor
Thread: [optional thread reference]
Priority: low|moderate|high

Body:
1. [structured content]
2. [evidence references]
3. [risk assessment]
```
