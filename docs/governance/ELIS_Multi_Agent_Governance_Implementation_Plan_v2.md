# ELIS Multi-Agent Governance Architecture v2.0 — Implementation Plan

**Status:** Proposed implementation plan replacing previous implementation documents for this purpose  
**Date:** 2026-04-30  
**Owner:** Carlos Rocha, Product Owner  
**Related architecture:** `ELIS_Multi_Agent_Governance_Architecture_v2.md`

---

## 1. Objective

Implement the ELIS multi-agent governance architecture v2.0 to make OpenClaw-based PE execution reliable across multiple PEs.

The plan creates a layered operating model:

```text
Hermes / outside OpenClaw:
- ELIS Platform Monitor
- ELIS PO Advisor

OpenClaw / PE execution:
- ELIS PM
- ELIS PE Gatekeeper
- ELIS PE Watchdog
- Implementers
- Validators
```

The implementation should reduce failures caused by stale sessions, wrong workspace paths, missing credentials, incomplete PE registry switches, silent implementer runs, missing HANDOFF/REVIEW evidence, ambiguous PM/Monitor role boundaries, and OpenClaw failures being diagnosed from inside OpenClaw.

---

## 2. Implementation Strategy

Do not build all changes at once.

Use phased implementation:

```text
Phase 0 — Freeze and document current state
Phase 1 — Rename and bound Hermes Platform Monitor
Phase 2 — Create ELIS PO Advisor on Hermes
Phase 3 — Define PE_TASK.md and artefact gates
Phase 4 — Create ELIS PE Gatekeeper
Phase 5 — Create fresh-session dispatch wrapper
Phase 6 — Create ELIS PE Watchdog
Phase 7 — Integrate PM state machine
Phase 8 — Pilot on one PE
Phase 9 — Roll out as default process
```

---

## 3. Phase 0 — Freeze and Document Current State

### Purpose

Establish the current baseline before changing architecture.

### Actions

1. Record current Hermes status.
2. Record current OpenClaw status.
3. Record current active agents.
4. Record current service state.
5. Record current OpenClaw model/provider state.
6. Record current PE state.
7. Save current configuration snapshots.

### Suggested commands

```bash
hermes status > /tmp/elis-architecture-v2-hermes-status.txt
openclaw status > /tmp/elis-architecture-v2-openclaw-status.txt
openclaw gateway status > /tmp/elis-architecture-v2-openclaw-gateway-status.txt
systemctl --user status hermes-gateway.service --no-pager > /tmp/elis-architecture-v2-hermes-gateway-service.txt
systemctl --user status openclaw-gateway.service --no-pager > /tmp/elis-architecture-v2-openclaw-gateway-service.txt
```

### Acceptance

- Baseline captured.
- No configuration change performed.

---

## 4. Phase 1 — Rename and Bound Hermes Platform Monitor

### Purpose

Preserve the existing Hermes-based monitor as the external recovery controller for OpenClaw.

### Decision

Rename current Hermes-based “ELIS Monitor” to:

```text
ELIS Platform Monitor
```

### Role boundary

ELIS Platform Monitor may diagnose and repair platform issues, verify gateway health, restart services, inspect logs, repair environment variables, verify OpenRouter/Codex auth, and check OpenClaw update status.

ELIS Platform Monitor must not dispatch agents, approve PRs, merge PRs, manage PE state, or perform product governance.

### Actions

1. Update Hermes identity / standing instruction.
2. Update Discord/bot display name if appropriate.
3. Update local documentation.
4. Confirm Platform Monitor can still run health and no-op checks.

### Standing instruction

```text
You are ELIS Platform Monitor, running outside OpenClaw on Hermes.

Your role is to keep elis-server, Hermes, OpenClaw, systemd user services, credentials, paths, workspace configuration, and updates healthy.

You may diagnose and repair operational platform issues when authorised.

You must not dispatch PE implementers or validators. ELIS PM dispatches agents.
You must not approve PRs, merge PRs, own PE state, change PE scope, or perform product governance.
```

### Acceptance

- Platform Monitor acknowledges boundaries.
- OpenClaw recovery remains possible when OpenClaw is broken.
- PM-only dispatch rule recorded.

---

## 5. Phase 2 — Create ELIS PO Advisor on Hermes

### Purpose

Create an external advisory agent for Carlos as PO.

### Runtime

Hermes, outside OpenClaw.

### Role

Advisory only. No execution authority.

### Standing instruction

```text
You are ELIS PO Advisor, an advisory agent running outside OpenClaw on Hermes.

Carlos Rocha is the Product Owner and final decision-maker.

You analyse reports from ELIS PM, ELIS Platform Monitor, ELIS PE Gatekeeper, ELIS PE Watchdog, implementers, validators, GitHub, CI, and PE registry state.

You advise, classify, and draft. You do not execute.

You must not dispatch agents, approve PRs, merge PRs, remove labels, change branch protection, edit files, modify CURRENT_PE.md, modify openclaw.json, modify workflows, change credentials, restart services, or perform operational fixes.

Always respond with:
1. Verdict
2. Evidence
3. Risk
4. Next safest action
5. Draft message, when useful
```

### Acceptance

- PO Advisor confirms advisory-only role.
- It can draft messages to PM/Platform Monitor.
- It does not mutate anything.

---

## 6. Phase 3 — Define PE_TASK.md and Artefact Gates

### Purpose

Make each PE self-contained, restartable, and independent of chat history.

### Directory convention

```text
.elis/pe/<PE-ID>/PE_TASK.md
.elis/runs/<PE-ID>/
```

### PE_TASK.md template

Create:

```text
docs/templates/PE_TASK.template.md
```

Suggested content:

```md
# <PE-ID> — <Title>

## Objective
<one clear objective>

## Repository
Repo path: `/opt/elis/repo`
Branch: `<branch>`

## Implementer
<agent id>

## Validator
<agent id>

## Allowed files
- ...

## Forbidden changes
- ...

## Required commands
- cd /opt/elis/repo
- ...

## Acceptance criteria
1. ...
2. ...

## Required artefacts
- commit
- HANDOFF.md
- Status Packet
- test output
- PR link, if required

## Blocker reporting format
If blocked, report:
- blocker class
- exact command
- exact error
- file/path involved
- smallest safe fix
```

### Artefact gates

Document:

```text
docs/governance/PE_ARTEFACT_GATES.md
```

Required implementer artefacts:

```text
- commit
- HANDOFF.md
- Status Packet
- tests run
- changed file list
- blocker evidence if blocked
```

Required validator artefacts:

```text
- REVIEW.md or validator verdict packet
- explicit PASS / FAIL / BLOCKED
- evidence
- CI interpretation
- required fixes if FAIL
```

### Acceptance

- Template exists.
- Artefact gate document exists.
- PM instructed not to dispatch without PE_TASK.md.

---

## 7. Phase 4 — Create ELIS PE Gatekeeper

### Purpose

Create a pre-dispatch readiness gate inside OpenClaw.

### Role

Read-only by default. No dispatch.

### Gatekeeper verdicts

```text
READY
NOT_READY
NEEDS_PLATFORM_FIX
NEEDS_PO_DECISION
```

### Gatekeeper checklist

Create:

```text
docs/governance/PE_GATEKEEPER_CHECKLIST.md
```

Checklist sections:

```text
1. PE registry
2. Repository
3. Task packet
4. Runtime
5. Auth
6. Fresh session plan
7. Artefact gates
8. Governance
```

### Gatekeeper command pattern

PM asks:

```text
@ELIS PE Gatekeeper Run preflight for <PE-ID>. Do not modify files. Return READY / NOT_READY / NEEDS_PLATFORM_FIX / NEEDS_PO_DECISION.
```

### Gatekeeper output

```text
PE Gatekeeper Verdict:

Evidence:
- Registry:
- Branch:
- Repo path:
- Task packet:
- Runtime:
- Auth:
- Fresh session plan:
- Artefact gates:

Blocking issues:

Next owner:

Next action:
```

### Recommended first step

Start as documented protocol plus scriptable checklist, then promote to agent after one PE pilot.

### Acceptance

- Gatekeeper role exists.
- Gatekeeper returns deterministic readiness verdict.
- PM does not dispatch unless Gatekeeper returns `READY`, except explicit PO override.

---

## 8. Phase 5 — Create Fresh-Session Dispatch Wrapper

### Purpose

Prevent stale sessions and enforce explicit repo path, branch, task packet, logs, and artefacts.

### Proposed script

```text
scripts/elis_dispatch_agent.sh
```

### Interface

```bash
scripts/elis_dispatch_agent.sh \
  --pe PE-INFRA-AGENT-02 \
  --role implementer \
  --agent infra-impl-b \
  --task .elis/pe/PE-INFRA-AGENT-02/PE_TASK.md
```

### Enforced behaviours

- Generates fresh session ID.
- Injects `/opt/elis/repo`.
- Injects branch.
- Injects PE task packet.
- Requires artefacts.
- Saves raw output under `.elis/runs/<PE-ID>/`.
- Returns concise status.
- Does not treat `OK` as success unless artefacts exist.

### Session ID format

```text
<PE-ID>-impl-YYYYMMDD-HHMMSS
<PE-ID>-val-YYYYMMDD-HHMMSS
<PE-ID>-fix-YYYYMMDD-HHMMSS
```

### Acceptance

- Wrapper can dispatch a no-op worker run with fresh session ID.
- Wrapper writes raw logs.
- Wrapper reports provider/model/session ID.
- Wrapper refuses missing PE_TASK.md.
- Wrapper refuses missing repo path.

---

## 9. Phase 6 — Create ELIS PE Watchdog

### Purpose

Detect stuck or incomplete PE execution after dispatch.

### Runtime

OpenClaw.

### Role

Read-only by default. No dispatch.

### Watchdog checks

For each active PE:

```text
1. Active PE state
2. Branch exists
3. Implementer started
4. Commit appeared
5. HANDOFF.md exists
6. Status Packet exists
7. PR exists if required
8. CI running/passed/failed
9. Validator started
10. REVIEW/verdict exists
11. Sessions not stale/excessively large
12. Logs show no auth/path/tool/gateway errors
```

### Watchdog verdicts

```text
RUNNING
STUCK
MISSING_ARTEFACTS
IMPLEMENTER_BLOCKED
VALIDATOR_BLOCKED
NEEDS_PLATFORM_FIX
NEEDS_PM_ACTION
NEEDS_PO_DECISION
DONE
```

### Output format

```text
PE Watchdog Status: <verdict>

PE:
Branch:
Current state:
Last activity:
Expected artefacts:
Found artefacts:
Missing artefacts:
Errors:
Next owner:
Next action:
```

### Acceptance

- Watchdog can inspect one active PE.
- Watchdog can detect missing HANDOFF/REVIEW.
- Watchdog can classify wrong repo path as `NEEDS_PLATFORM_FIX`.
- Watchdog does not dispatch agents.

---

## 10. Phase 7 — Integrate PM State Machine

### Purpose

Make ELIS PM operate as workflow controller instead of long-running reasoning agent.

### Required PM state transitions

```text
PLANNING → READY_FOR_PREFLIGHT
requires PE registry row + PE_TASK.md

READY_FOR_PREFLIGHT → PREFLIGHT_PASS
requires Gatekeeper READY

PREFLIGHT_PASS → IMPLEMENTING
requires PM dispatch record

IMPLEMENTING → NEEDS_VALIDATION
requires commit + HANDOFF.md + Status Packet

NEEDS_VALIDATION → VALIDATING
requires validator dispatch

VALIDATING → VALIDATOR_PASS
requires REVIEW/verdict PASS

VALIDATOR_PASS → READY_FOR_PO_APPROVAL
requires CI status and PR status

READY_FOR_PO_APPROVAL → MERGE_PENDING
requires PO approval if needed

MERGE_PENDING → DONE
requires merge/closure evidence
```

### PM hard rules

- PM dispatches agents.
- PM does not fix platform issues.
- PM does not dispatch without Gatekeeper `READY`.
- PM does not accept silent success.
- PM does not validate implementation itself.
- PM requests Platform Monitor for operational fixes.
- PM requests Watchdog for runtime state.

### Acceptance

- PM role prompt updated.
- PM acknowledges Gatekeeper and Watchdog roles.
- PM produces state transition evidence.

---

## 11. Phase 8 — Pilot on One PE

### Recommended pilot

Use a small operational PE, not a major feature PE.

Suggested:

```text
PE-OPS-01 — ELIS PE Execution Pipeline Hardening
```

### Pilot flow

1. PO approves PE-OPS-01.
2. PM creates PE registry row.
3. PM creates PE_TASK.md.
4. Gatekeeper runs preflight.
5. PM dispatches implementer using wrapper.
6. Implementer produces artefacts.
7. Watchdog confirms artefacts.
8. PM dispatches validator.
9. Validator produces REVIEW.
10. PO reviews final status.

### Acceptance

- One PE completes using the new workflow.
- No agent relies on old session history.
- Artefacts are complete.
- Roles remain separated.

---

## 12. Phase 9 — Rollout as Default Process

### Purpose

Make the architecture the default process for all future PEs.

### Actions

1. Add documentation references to main repo docs.
2. Update PM prompt/profile.
3. Update Platform Monitor prompt/profile.
4. Add Gatekeeper role.
5. Add Watchdog role.
6. Add PO Advisor role.
7. Train workflow on two additional PEs.
8. Archive replaced documents.

### Acceptance

- New PE process is documented.
- PM follows Gatekeeper-before-dispatch.
- Watchdog reports active PE status.
- Platform Monitor remains outside OpenClaw.
- PO Advisor remains advisory only.

---

## 13. Suggested Repository Files

Create or update:

```text
docs/governance/ELIS_Multi_Agent_Governance_Architecture_v2.md
docs/governance/ELIS_Multi_Agent_Governance_Implementation_Plan_v2.md
docs/governance/PE_GATEKEEPER_CHECKLIST.md
docs/governance/PE_ARTEFACT_GATES.md
docs/templates/PE_TASK.template.md
docs/governance/ROLE_BOUNDARIES.md
scripts/elis_dispatch_agent.sh
```

Optional later:

```text
scripts/elis_pe_preflight.py
scripts/elis_pe_watchdog.py
.elis/pe/<PE-ID>/PE_TASK.md
.elis/runs/<PE-ID>/
```

---

## 14. Replacement Plan for Previous Documents

This plan should replace previous documents whose purpose was to define:

- broad ELIS Monitor responsibilities;
- PM/Monitor role overlap;
- PO Advisor as the primary fix for multi-PE reliability;
- ad hoc token/context handling as the main reliability strategy;
- PM dispatch without mandatory readiness gate;
- long-running agent continuity as execution design.

Archive older documents under:

```text
docs/_archive/<date>/
```

Add a note:

```text
Replaced by ELIS Multi-Agent Governance Architecture v2.0 and Implementation Plan v2.0.
```

---

## 15. Risk Register

| Risk | Impact | Mitigation |
|---|---:|---|
| Too many new roles create confusion | High | Clear naming and role boundaries |
| PM bypasses Gatekeeper | High | PM hard rule and PO policy |
| Gatekeeper becomes another executor | Medium | Read-only by default |
| Watchdog mutates state | Medium | Read-only by default |
| Platform Monitor dispatches agents | High | Explicit prohibition |
| PE_TASK.md becomes stale | Medium | Gatekeeper checks consistency |
| Wrapper script becomes too complex | Medium | Start minimal |
| Agents still use wrong repo path | High | Wrapper injects `/opt/elis/repo`; Gatekeeper checks |
| Token bloat remains high | Medium | Fresh sessions and PE packets |
| Old sessions contaminate new PEs | High | Fresh session IDs mandatory |

---

## 16. Immediate Next Actions

1. Approve architecture v2.0.
2. Rename current Hermes Monitor to `ELIS Platform Monitor`.
3. Create Hermes PO Advisor standing instruction.
4. Create `PE_TASK.md` template and artefact gates.
5. Create Gatekeeper checklist.
6. Pilot with `PE-OPS-01 — ELIS PE Execution Pipeline Hardening`.

---

## 17. PO Approval Checkpoint

Before implementation starts, Carlos should approve:

```text
1. Final role names.
2. Hermes vs OpenClaw placement.
3. PM-only dispatch rule.
4. Platform Monitor external recovery role.
5. Gatekeeper mandatory pre-dispatch rule.
6. Watchdog runtime monitoring role.
7. PO Advisor advisory-only role.
8. PE-OPS-01 pilot.
```

---

## 18. Final Implementation Principle

> **Do not make agents smarter by giving them longer memory. Make the system more reliable by giving each agent a smaller, clearer, restartable job with explicit artefacts and independent gates.**
