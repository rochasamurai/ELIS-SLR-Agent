# ELIS Multi-Agent Governance Architecture v2.0

**Status:** Proposed replacement for previous ELIS multi-agent governance / monitoring architecture documents  
**Date:** 2026-04-30  
**Owner:** Carlos Rocha, Product Owner  
**Scope:** ELIS-SLR-Agent / OpenClaw / Hermes operating model for reliable multi-PE execution

---

## 1. Executive Summary

The ELIS multi-agent system must stop relying on long-running conversational continuity as the primary mechanism for execution. The new architecture separates **platform health**, **PE governance**, **pre-dispatch readiness**, **runtime PE monitoring**, **implementation**, **validation**, and **PO advisory support**.

The central principle is:

> **OpenClaw should not be responsible for recovering OpenClaw.**

Therefore, the platform recovery layer remains outside OpenClaw, running on Hermes. OpenClaw remains the operational execution environment for PM coordination, PE gatekeeping, PE monitoring, implementers, and validators.

The new architecture introduces two explicit PE control roles inside OpenClaw:

1. **ELIS PE Gatekeeper** — pre-dispatch readiness gate.
2. **ELIS PE Watchdog** — runtime PE monitoring and stuck-execution detection.

It also formalises two external Hermes roles:

1. **ELIS Platform Monitor** — keeps Hermes/OpenClaw/server/auth/config/path services healthy.
2. **ELIS PO Advisor** — advises Carlos Rocha as PO, drafts decisions, and protects governance boundaries.

---

## 2. Design Rationale

Recent failures exposed the limits of the previous model:

- OpenClaw gateway failed because `OPENROUTER_API_KEY` was missing from the systemd user service environment.
- Agents attempted to read files from the wrong workspace path instead of `/opt/elis/repo`.
- PM dispatches sometimes created registry state without visible implementer artefacts.
- Validator and implementer sessions accumulated large context windows across multiple PEs.
- PR #389 was validated but blocked by a required `current-pe-check` failure unrelated to the PE’s original scope.
- Manual PO reasoning was required to distinguish governance, operational, validation, implementation, CI, branch-policy, and platform issues.

The new design responds by making agent execution **transactional, restartable, artefact-driven, and externally recoverable**.

---

## 3. Core Architectural Principles

### 3.1 Platform Recovery Must Be External to OpenClaw

The agent responsible for repairing OpenClaw must not depend on OpenClaw being healthy.

Therefore:

- **ELIS Platform Monitor runs on Hermes**, outside OpenClaw.
- It can restart OpenClaw, repair environment variables, diagnose systemd services, verify credentials, and check gateway health.
- It must not dispatch PE implementers or validators.

### 3.2 PM Dispatch Authority Is Exclusive

Only **ELIS PM** dispatches implementers and validators.

No other role should dispatch PE execution agents:

- not Platform Monitor;
- not PE Gatekeeper;
- not PE Watchdog;
- not PO Advisor;
- not validators;
- not implementers.

### 3.3 Preflight Is Mandatory Before Dispatch

PM must obtain a `READY` verdict from **ELIS PE Gatekeeper** before dispatching a new implementer run, except where Carlos explicitly grants a PO override.

### 3.4 Runtime Monitoring Is Separate from Preflight

**ELIS PE Gatekeeper** checks readiness before execution.  
**ELIS PE Watchdog** monitors progress after execution starts.

They must remain separate roles to avoid one overloaded monitoring agent.

### 3.5 Agents Are Disposable Workers

Agents must not be expected to remain productive across many PEs using long conversational history.

Each PE phase should use:

- a fresh session ID;
- a bounded task packet;
- explicit repo path;
- explicit branch;
- explicit artefact requirements;
- deterministic logs.

### 3.6 Repository Artefacts Are the Source of Truth

The project memory must live in artefacts, not chat history:

- `CURRENT_PE.md`
- `PE_TASK.md`
- `HANDOFF.md`
- `REVIEW.md`
- `STATUS_PACKET.md`
- CI logs
- PR comments
- Git commits
- diagnostic logs

### 3.7 No Silent Success

An agent run that produces no required artefacts is not a success.

Valid outcomes are:

- `PASS_WITH_ARTEFACTS`
- `BLOCKED_WITH_EVIDENCE`
- `FAIL_WITH_ERROR`

Invalid outcomes include:

- “OK” with no artefacts;
- `deliveryStatus=not_applicable`;
- “completed” with no commit/HANDOFF/REVIEW;
- silent timeout;
- non-visible agent run.

---

## 4. Layered Architecture

```text
Carlos Rocha — Product Owner
│
├── Hermes / Outside OpenClaw
│   │
│   ├── ELIS Platform Monitor
│   │   └── keeps Hermes/OpenClaw/server/auth/path/config healthy
│   │
│   └── ELIS PO Advisor
│       └── advises Carlos; drafts decisions; no execution authority
│
└── OpenClaw / PE Execution Layer
    │
    ├── ELIS PM
    │   └── owns PE state machine and dispatches agents
    │
    ├── ELIS PE Gatekeeper
    │   └── pre-dispatch readiness gate
    │
    ├── ELIS PE Watchdog
    │   └── runtime PE progress monitoring
    │
    ├── Implementers
    │   └── bounded implementation tasks
    │
    └── Validators
        └── independent validation tasks
```

---

## 5. Role Definitions

## 5.1 Carlos Rocha — Product Owner

Carlos Rocha is the final decision-maker for product, governance, approval, scope, and release decisions.

Carlos may approve PE proposals, authorise PM dispatch, approve PR governance gates, authorise merge paths, approve sensitive operational repairs, override PE gates when explicitly justified, and decide whether a failing check is in-scope or requires a new PE.

The PO should retain final control over PR approval, branch-policy exceptions, merge authorisation, major PE scope changes, sensitive configuration changes, and changes to governance rules.

---

## 5.2 ELIS Platform Monitor

### Runtime

**Hermes, outside OpenClaw.**

### Purpose

Keep the ELIS operational platform healthy.

### Responsibilities

- Monitor OpenClaw gateway health.
- Restart OpenClaw gateway when authorised.
- Diagnose systemd user service failures.
- Verify OpenRouter and Codex credentials.
- Repair missing environment variables.
- Diagnose wrong workspace/repo path issues.
- Verify OpenClaw no-op worker tests.
- Check OpenClaw updates and recommend timely upgrade.
- Check disk, memory, network, service state, and logs.
- Run operational diagnostics on `elis-server`.

### Allowed actions

- Inspect service status.
- Restart services.
- Check and repair environment variables.
- Back up and update service drop-ins.
- Run no-op health checks.
- Inspect operational logs.
- Apply authorised OpenClaw updates.
- Report platform readiness.

### Forbidden actions

- Dispatch implementers or validators.
- Approve PRs.
- Merge PRs.
- Own PE state.
- Modify PE scope.
- Change branch protection.
- Remove governance labels unless explicitly authorised.
- Modify implementation files.
- Perform product governance actions.

### Typical verdicts

- `PLATFORM_HEALTHY`
- `NEEDS_AUTH_FIX`
- `NEEDS_GATEWAY_FIX`
- `NEEDS_PATH_FIX`
- `NEEDS_UPDATE`
- `READY_FOR_GATEKEEPER`
- `BLOCKED`

---

## 5.3 ELIS PO Advisor

### Runtime

**Hermes, outside OpenClaw.**

### Purpose

Advise Carlos as Product Owner.

### Responsibilities

- Analyse reports from PM, Platform Monitor, Gatekeeper, Watchdog, implementers, validators, GitHub, CI, and PE registry.
- Classify issues into governance, operational, implementation, validation, CI, branch-policy, or PO decision categories.
- Draft safe messages for Carlos to send.
- Recommend next safest PO action.
- Protect role boundaries.
- Warn when an agent is exceeding its authority.

### Allowed actions

- Analyse evidence.
- Recommend approval or rejection.
- Draft messages.
- Identify risks.
- Request targeted diagnostics.
- Prepare decision packets.

### Forbidden actions

- Dispatch agents.
- Approve PRs.
- Merge PRs.
- Remove labels.
- Change branch protection.
- Edit files.
- Modify `CURRENT_PE.md`, `openclaw.json`, workflows, credentials, or services.
- Restart services.
- Perform operational fixes.

### Output format

The PO Advisor should normally answer with:

```text
Verdict:
Evidence:
Risk:
Next safest action:
Draft message:
```

### Typical verdicts

- `NEEDS_PM_ACTION`
- `NEEDS_PLATFORM_MONITOR_FIX`
- `NEEDS_GATEKEEPER_PREFLIGHT`
- `NEEDS_WATCHDOG_STATUS`
- `NEEDS_IMPLEMENTATION`
- `NEEDS_VALIDATION`
- `NEEDS_PO_DECISION`
- `READY_FOR_PO_APPROVAL`
- `BLOCKED`

---

## 5.4 ELIS PM

### Runtime

**OpenClaw.**

### Purpose

Own the PE state machine and dispatch implementers/validators.

### Responsibilities

- Propose PEs.
- Maintain PE workflow state.
- Prepare PE registry rows.
- Prepare PE task packets.
- Request Gatekeeper preflight.
- Dispatch implementers after Gatekeeper `READY`.
- Dispatch validators after implementer artefacts exist.
- Track PE status transitions.
- Ask PO for approvals.
- Close PEs after evidence.

### Allowed actions

- Create PE proposals.
- Update PE workflow state.
- Dispatch implementers and validators.
- Request Platform Monitor fixes.
- Request Gatekeeper readiness checks.
- Request Watchdog status reports.
- Prepare PM status packets.

### Forbidden actions

- Fix gateway/auth/path/systemd/platform problems.
- Dispatch without Gatekeeper `READY`, unless explicit PO override.
- Bypass validator independence.
- Approve PRs on behalf of PO.
- Merge without PO-approved process.
- Treat silent implementer completion as success.

### PE state machine

Recommended states:

```text
PLANNING
READY_FOR_PREFLIGHT
PREFLIGHT_PASS
IMPLEMENTING
IMPLEMENTER_BLOCKED
NEEDS_VALIDATION
VALIDATING
VALIDATOR_FAIL
VALIDATOR_PASS
READY_FOR_PO_APPROVAL
MERGE_PENDING
DONE
```

---

## 5.5 ELIS PE Gatekeeper

### Runtime

**OpenClaw.**

### Purpose

Run mandatory pre-dispatch readiness checks before PM dispatches an implementer or validator.

### Checks

#### PE registry

- Active PE header matches registry row.
- PE ID exists.
- Branch is populated.
- Implementer and validator are populated.
- Implementer/validator alternation is valid.
- Dependency status is clear.
- PE state is `ready-for-dispatch` or equivalent.

#### Repository

- `/opt/elis/repo` exists.
- Correct branch exists or can be created.
- Worktree is clean or expected dirty state is documented.
- Target files exist.
- Allowed and forbidden file scope is defined.

#### Task packet

- `PE_TASK.md` exists.
- Objective is precise.
- Allowed files listed.
- Forbidden files listed.
- Required commands listed.
- Expected artefacts listed.
- Blocker reporting format defined.

#### OpenClaw runtime

- Gateway reachable.
- Worker auth available.
- Intended implementer no-op passes or recently passed.
- Fresh session ID is planned.
- Token baseline is acceptable.

#### Governance

- PO approval present where required.
- PM dispatch authority confirmed.
- Monitor is not being asked to dispatch.
- Validator independence preserved.

### Allowed actions

- Inspect PE registry.
- Inspect task packet.
- Inspect branch status.
- Inspect runtime health status.
- Run read-only checks.
- Return readiness verdict.

### Forbidden actions

- Dispatch agents.
- Implement code.
- Validate code.
- Edit files.
- Restart services.
- Change credentials.
- Approve or merge PRs.

### Verdicts

```text
READY
NOT_READY
NEEDS_PLATFORM_FIX
NEEDS_PO_DECISION
```

### Output format

```text
PE Gatekeeper Verdict: READY / NOT_READY / NEEDS_PLATFORM_FIX / NEEDS_PO_DECISION

Evidence:
- Registry: PASS/FAIL
- Branch: PASS/FAIL
- Repo path: PASS/FAIL
- Task packet: PASS/FAIL
- Runtime: PASS/FAIL
- Auth: PASS/FAIL
- Fresh session plan: PASS/FAIL
- Artefact gates: PASS/FAIL

Blocking issues:
1. ...

Next owner:
PM / Platform Monitor / PO / Implementer / Validator

Next action:
...
```

---

## 5.6 ELIS PE Watchdog

### Runtime

**OpenClaw.**

### Purpose

Monitor active PE execution after dispatch and detect stuck or incomplete work.

### Responsibilities

- Watch active PEs.
- Check whether implementer actually started.
- Check whether expected artefacts exist.
- Detect no commit/no PR/no HANDOFF/no REVIEW.
- Detect stale sessions and excessive token growth.
- Detect gateway/auth/path/tool errors in logs.
- Report next responsible owner.
- Identify silent success.

### Allowed actions

- Inspect PE state.
- Inspect branches, PRs, CI, and artefacts.
- Inspect logs.
- Classify stuck conditions.
- Notify PM/PO/Platform Monitor.

### Forbidden actions

- Dispatch agents.
- Edit files.
- Approve PRs.
- Remove labels.
- Restart services.
- Change credentials.
- Merge PRs.

### Verdicts

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

---

## 5.7 Implementers

### Runtime

**OpenClaw.**

### Purpose

Execute bounded implementation tasks.

Each implementer run must use a fresh session ID, read the PE task packet, use `/opt/elis/repo` as the repository path, work only on the approved branch, modify only allowed files, run required tests, produce commit(s), produce `HANDOFF.md`, produce a Status Packet, and report blockers with evidence.

Implementers must not validate their own work, merge, approve PRs, change branch protection, change scope, or modify forbidden files.

---

## 5.8 Validators

### Runtime

**OpenClaw.**

### Purpose

Independently validate implementer output.

Each validator run must use a fresh session ID, review `HANDOFF.md`, inspect changed files, run or verify required tests, inspect CI evidence, produce `REVIEW.md` or validator verdict packet, and issue explicit `PASS`, `FAIL`, or `BLOCKED`.

Validators must not implement fixes unless explicitly authorised under a separate PE, validate their own implementation, merge, approve on behalf of PO, or dispatch agents.

---

## 6. PE Execution Flow

```text
1. PO approves PE concept.
2. PM creates PE proposal.
3. PM creates/updates PE registry row.
4. PM creates PE_TASK.md.
5. PM requests Gatekeeper preflight.
6. Gatekeeper returns READY.
7. PM dispatches implementer with fresh session ID.
8. Implementer produces commit + HANDOFF.md + Status Packet.
9. Watchdog confirms artefacts exist.
10. PM dispatches validator with fresh session ID.
11. Validator produces REVIEW/verdict.
12. Watchdog confirms validation evidence.
13. PM requests PO approval if needed.
14. PR merge path proceeds through normal branch protection.
15. PM closes PE.
```

If Gatekeeper returns `NEEDS_PLATFORM_FIX`:

```text
Gatekeeper → PM → Platform Monitor → fix → Gatekeeper rerun
```

If Watchdog returns `STUCK`:

```text
Watchdog → PM → determine owner → Platform Monitor / Implementer / Validator / PO
```

---

## 7. PE Task Packet

Every PE should have a canonical task packet:

```text
.elis/pe/<PE-ID>/PE_TASK.md
```

Required sections:

```text
Objective
Repository
Implementer
Validator
Allowed files
Forbidden changes
Required commands
Acceptance criteria
Required artefacts
Blocker reporting format
```

The PE task packet prevents agents from relying on chat history and eliminates ambiguity around path, branch, scope, and acceptance criteria.

---

## 8. Artefact Gates

### Implementer success requires

```text
- implementation commit
- HANDOFF.md
- Status Packet
- tests run
- changed file list
- blocker evidence if blocked
```

### Validator success requires

```text
- REVIEW.md or validator verdict packet
- explicit PASS / FAIL / BLOCKED
- evidence
- CI interpretation
- required fixes if FAIL
```

### PM closure requires

```text
- implementer evidence
- validator evidence
- PR status
- CI status
- PO decision if required
```

---

## 9. Fresh Session Policy

Every implementer and validator run should use a fresh session ID:

```text
<pe-id>-impl-YYYYMMDD-HHMMSS
<pe-id>-val-YYYYMMDD-HHMMSS
<pe-id>-fix-YYYYMMDD-HHMMSS
```

Long-lived sessions should not be reused for new PE phases.

---

## 10. Platform vs PE Responsibilities

| Problem | Owner |
|---|---|
| OpenClaw gateway not listening | Platform Monitor |
| Missing `OPENROUTER_API_KEY` | Platform Monitor |
| Codex OAuth broken | Platform Monitor |
| Wrong workspace/repo path | Platform Monitor |
| Partial PE registry setup | PM, checked by Gatekeeper |
| Missing PE task packet | PM, checked by Gatekeeper |
| Implementer did not start | Watchdog → PM |
| Implementer no artefacts | Watchdog → PM |
| Validator no verdict | Watchdog → PM |
| PR approval decision | PO |
| Merge blocker from required check | PM + PO decision |
| Implementation code fix | Implementer |
| Independent validation | Validator |

---

## 11. Naming Standard

Use these names consistently:

```text
ELIS Platform Monitor
ELIS PO Advisor
ELIS PM
ELIS PE Gatekeeper
ELIS PE Watchdog
```

Avoid creating another “ELIS Monitor” inside OpenClaw.

---

## 12. Replacement Notice

This architecture replaces previous informal descriptions of:

- ELIS Monitor as a broad operational and PE monitor;
- PO Advisor as the main proposed solution to multi-PE reliability;
- PM dispatch without mandatory preflight;
- long-running agent continuity as the main execution mechanism.

The new design is a layered, restartable, artefact-driven PE execution architecture.

---

## 13. Final Operating Principle

> **Agents do not remember the project. The repository remembers the project. Agents execute one bounded job at a time. PM controls state. Platform Monitor controls operational health. Gatekeeper controls readiness. Watchdog controls progress visibility. PO controls approval.**
