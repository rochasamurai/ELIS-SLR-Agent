# ELIS General Guidance

**Status:** Canonical operating guidance for ELIS agents and PE execution  
**Owner:** Carlos Rocha, Product Owner  
**Applies to:** ELIS PM, ELIS Platform Monitor, PE Gatekeeper, PE Watchdog, implementers, validators, and future ELIS agents  
**Related documents:**
- `docs/governance/ELIS_Multi_Agent_Governance_Architecture_v2.md`
- `docs/governance/ELIS_Multi_Agent_Governance_Implementation_Plan_v2.md`
- `docs/governance/ELIS_Token_Usage_Guidelines_for_Multi_AI_Agents.md`
- `docs/governance/ELIS_Token_Usage_Guidelines_Implementation_Plan.md`

---

## 1. Purpose

This document is the short canonical orientation for ELIS agents.

It defines the general operating doctrine for role boundaries, repository use, workspace safety, PE execution, validation, platform recovery, rate-limit handling, and Product Owner approval.

It does not replace the detailed governance architecture or implementation plan. It summarises the rules every agent must understand before working on ELIS.

---

## 2. Core Operating Principles

1. **The repository remembers the project. Agents do not.**  
   Authoritative state must live in repository artefacts, PRs, commits, CI checks, logs, and status packets — not only in chat history.

2. **One bounded task at a time.**  
   Each agent run must have a precise task, explicit repo/worktree path, clear branch, allowed files, required checks, and required artefacts.

3. **No silent success.**  
   A run that produces no required artefacts is not a success. Valid outcomes are `PASS`, `FAIL`, or `BLOCKED`, with evidence.

4. **PM controls PE workflow.**  
   ELIS PM owns the PE state machine and dispatches implementers and validators.

5. **Platform recovery is outside PE execution.**  
   ELIS Platform Monitor keeps Hermes, OpenClaw, Discord connectivity, systemd services, auth, paths, and runtime health operational. It does not dispatch PE agents.

6. **No OpenClaw workspace directly on the canonical repo root.**  
   OpenClaw treats its workspace as an agent home and may write bootstrap/context files there. Do not bind OpenClaw workspace directly to `/opt/elis/repo`.

7. **Never share a mutable working directory between active agents.**  
   Use PE-specific Git worktrees or another approved isolated working-tree model.

8. **Human PO approval controls governance exceptions.**  
   Merge approval, branch-policy exceptions, role-boundary exceptions, runtime configuration changes, and unusual recovery actions require Product Owner approval.

---

## 3. Authoritative Paths

### Canonical repository

```text
/opt/elis/repo
```

This is the canonical ELIS repository. It should remain clean unless a controlled, approved PE or maintenance task is actively modifying it.

### Recommended agent worktree root

```text
/opt/elis/agent-worktrees/
```

Recommended naming pattern:

```text
/opt/elis/agent-worktrees/<PE-ID>-<agent-id>
```

Examples:

```text
/opt/elis/agent-worktrees/PE-OPS-01-infra-impl-a
/opt/elis/agent-worktrees/PE-OPS-01-infra-val-b
```

### OpenClaw operational workspaces

OpenClaw workspaces are agent operational homes. They may contain files such as:

```text
.openclaw/
HEARTBEAT.md
IDENTITY.md
SOUL.md
TOOLS.md
USER.md
```

These bootstrap/context files must not be written into the canonical Git repository root.

---

## 4. Role Boundaries

### 4.1 Product Owner

The Product Owner is Carlos Rocha.

The PO approves:
- PE concepts and scope;
- governance decisions;
- merge approval;
- branch-policy exceptions;
- runtime configuration mutations;
- recovery actions that may affect repository state;
- renaming or redefining agent roles;
- acceptance of manual fallback evidence.

The PO does not need to manage low-level execution details when the system is functioning correctly.

### 4.2 ELIS PM

ELIS PM owns PE workflow.

Responsibilities:
- propose PEs;
- maintain PE state;
- prepare PE registry entries;
- prepare PE task packets;
- request Gatekeeper preflight;
- dispatch implementers and validators;
- interpret PE status;
- request PO approval when needed;
- coordinate PR flow after validation.

ELIS PM must not:
- fix OpenClaw gateway/auth/path/config problems directly;
- perform Platform Monitor duties;
- bypass Gatekeeper unless the PO explicitly approves;
- treat a silent or artefact-free agent run as success;
- merge without approved process;
- override role boundaries.

### 4.3 ELIS Platform Monitor

ELIS Platform Monitor runs outside OpenClaw on Hermes.

Responsibilities:
- monitor and repair platform health;
- diagnose Hermes/OpenClaw gateway issues;
- verify auth, provider, model, path, and service status;
- inspect logs;
- verify repository cleanliness when operational failures occur;
- prepare cleanup plans;
- run approved platform recovery steps;
- verify Discord connectivity.

ELIS Platform Monitor must not:
- dispatch OpenClaw implementers or validators;
- manage PE workflow state;
- approve or merge PRs;
- assume PE Gatekeeper or PE Watchdog responsibilities;
- modify PE state unless the PO explicitly authorises a specific recovery action;
- alter OpenClaw runtime config without PO approval.

### 4.4 ELIS PE Gatekeeper

ELIS PE Gatekeeper performs pre-dispatch readiness checks.

It verifies:
- active PE registry state;
- branch;
- task packet;
- repo/worktree path;
- artefact requirements;
- expected implementer/validator;
- role alternation;
- clean working tree;
- rate-limit and session-readiness conditions where available.

Gatekeeper verdicts:

```text
READY
NOT_READY
NEEDS_PLATFORM_FIX
NEEDS_PO_DECISION
```

Gatekeeper must not dispatch agents, implement code, validate implementation, commit, push, merge, or change runtime configuration.

### 4.5 ELIS PE Watchdog

ELIS PE Watchdog monitors PE progress after dispatch.

It detects:
- stuck runs;
- wrong repo/worktree path;
- missing artefacts;
- dirty worktree with no progress;
- failed or stale CI;
- missing HANDOFF or REVIEW;
- silent success;
- rate-limit or model/provider failure.

Watchdog verdicts:

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

Watchdog must not dispatch agents, perform implementation, perform validation, approve, merge, or change platform configuration.

### 4.6 Implementers

Implementers perform bounded implementation tasks.

They must:
- work only in the assigned PE worktree;
- use the approved branch;
- modify only allowed files;
- run required checks;
- produce a commit;
- produce `HANDOFF.md`;
- include a Status Packet;
- report blockers with evidence.

Implementers must not:
- validate their own work;
- merge PRs;
- approve PRs;
- change branch protection;
- perform unrelated cleanup;
- run blanket file permission changes such as `chmod +x scripts/*.py`;
- write outside the assigned worktree.

### 4.7 Validators

Validators independently review implementer output.

They must:
- use the assigned validation worktree or approved validation path;
- verify the correct branch and commit;
- review changed files;
- run required checks;
- produce `REVIEW.md` or a validator verdict packet;
- return explicit `PASS`, `FAIL`, or `BLOCKED`.

Validators must not:
- validate the wrong repo or stale branch;
- modify implementation files unless specifically authorised under a separate fix path;
- validate their own implementation;
- merge;
- approve on behalf of the PO.

---

## 5. Repository and Workspace Rules

### 5.1 Canonical repo rule

`/opt/elis/repo` is the canonical repository. It must not be used as the OpenClaw agent workspace root.

### 5.2 Worktree rule

Active PE work should use dedicated Git worktrees under:

```text
/opt/elis/agent-worktrees/
```

Recommended pattern:

```text
/opt/elis/agent-worktrees/<PE-ID>-<agent-id>
```

Each active implementer or validator must have a separate mutable working directory.

### 5.3 No shared mutable worktree

Never allow two active agents to write to the same working directory at the same time.

Default rule:

```text
one PE branch + one active writer
```

Validators should use a separate validation worktree or read-only process.

### 5.4 No direct OpenClaw workspace binding to repo root

Do not configure:

```text
workspace = /opt/elis/repo
```

This is unsafe because OpenClaw may write bootstrap/context files into the workspace root.

### 5.5 File-tool and shell-cwd distinction

Agents must understand:

```text
shell cwd != OpenClaw file-tool root
```

A command such as:

```bash
cd /opt/elis/repo && git status
```

does not necessarily change where OpenClaw `read`, `write`, or `edit` tools resolve relative paths.

This rule is central to preventing wrong-path writes.

---

## 6. PE Execution Rules

### 6.1 PE task packet

Every PE must have a task packet:

```text
.elis/pe/<PE-ID>/PE_TASK.md
```

The task packet must define:
- objective;
- branch;
- implementer;
- validator;
- controlling documents;
- allowed files;
- forbidden files;
- required commands;
- expected artefacts;
- blocker reporting format.

### 6.2 Fresh session rule

Every implementation and validation phase should use a fresh session ID.

Recommended pattern:

```text
<PE-ID>-impl-YYYYMMDD-HHMMSS
<PE-ID>-val-YYYYMMDD-HHMMSS
<PE-ID>-fix-YYYYMMDD-HHMMSS
```

### 6.3 Mandatory path preflight

Before any PE work, the agent must prove:
- correct working tree;
- correct branch;
- correct repository root;
- required task packet exists;
- working tree state is expected.

Example:

```bash
pwd
git rev-parse --show-toplevel
git status --short --branch
git branch --show-current
```

The verified path must match the assigned PE worktree, not a stale workspace.

### 6.4 Artefact gates

Implementation success requires:
- commit;
- changed file list;
- tests/checks run;
- `HANDOFF.md`;
- Status Packet;
- blocker evidence if blocked.

Validation success requires:
- explicit `PASS`, `FAIL`, or `BLOCKED`;
- `REVIEW.md` or validator verdict packet;
- tests/checks run;
- evidence reviewed;
- blockers, if any.

### 6.5 No silent success

The following are not success:
- “OK” with no artefacts;
- “completed” with no commit/HANDOFF/REVIEW;
- `deliveryStatus=not_applicable`;
- UI response failure without repository verification;
- agent output from the wrong repo/worktree.

---

## 7. File and Path Safety

Agents must:
- use explicit paths;
- avoid ambiguous relative writes;
- verify `git rev-parse --show-toplevel`;
- avoid writing into OpenClaw scratch workspaces when the task concerns the ELIS repo;
- avoid copying artefacts from wrong workspaces without review;
- avoid broad permission changes.

Forbidden by default:

```bash
chmod +x scripts/*.py
rm -rf *
git reset --hard
git clean -fdx
```

These require explicit, specific approval and a rollback plan.

---

## 8. Validation Rules

A validation report must include:
- repo/worktree path;
- branch;
- commit SHA;
- files reviewed;
- tests run;
- evidence;
- verdict.

Allowed verdicts:

```text
PASS
FAIL
BLOCKED
```

A validator result is invalid if it:
- uses the wrong repo path;
- validates an old/stale branch;
- omits commit evidence;
- runs tests outside the assigned worktree;
- confuses local evidence with GitHub required-check evidence.

---

## 9. Platform and Recovery Rules

Platform failures include:
- OpenClaw gateway down;
- Hermes gateway down;
- missing auth or provider credentials;
- wrong workspace binding;
- model/rate-limit failures;
- Discord delivery failures;
- path/tool context divergence;
- untracked bootstrap files in the repo root.

Platform Monitor may diagnose and repair these only within PO-approved boundaries.

Recovery must generally follow:
1. read-only diagnosis;
2. explicit cleanup or repair plan;
3. PO approval;
4. execution;
5. verification;
6. rollback readiness.

---

## 10. Codex OAuth and Rate-Limit Policy

ELIS Platform Monitor currently uses OpenAI Codex OAuth, not a normal OpenAI API key.

Observed failure:

```text
HTTP 429: The usage limit has been reached
provider=openai-codex
model=gpt-5.5
```

Operational policy:
- Warn before long tasks.
- Prefer fresh sessions for multi-step operational tasks.
- Recommend `SESSION_HANDOFF` above approximately 35K context tokens when measurable.
- Do not start mutating tasks above approximately 40K context tokens when measurable.
- Stop on 429 usage-limit instead of repeated retries.
- Do not enable fallback providers without PO approval.
- Record rate-limit events as operational evidence.

If token estimate is unavailable, the agent must state that it is unavailable and use conservative behaviour.

---

## 11. Discord and Thread Governance

Discord channel and thread governance is pending further definition.

Interim rules:
- `#elis-pm` is for PM workflow, PE status, and PO decisions.
- The agent identity is **ELIS Platform Monitor**.
- Discord channel names may remain unchanged until separate Discord governance is approved.
- `#elis-monitor` or its successor channel is for platform health and operational recovery.
- PE-specific work should preferably occur in PE-specific threads.
- Threads should be named with PE ID where possible.
- Agents must not rely only on Discord history as the source of truth.
- Important decisions must be recorded in repository artefacts or status packets.

A future governance document should define:
- channel bindings;
- thread naming;
- who may create PE threads;
- archival rules;
- how PM and Platform Monitor coordinate without mixing roles.

---

## 12. PO Approval and Escalation

PO approval is required for:
- merge approval;
- config mutation;
- branch protection changes;
- credential/provider changes;
- deleting or cleaning files outside narrowly approved scope;
- accepting fallback/manual validation;
- changing agent role boundaries;
- renaming channels or agents;
- using non-approved fallback models/providers.

Escalate to PO when:
- a required check fails for unclear reasons;
- an agent used the wrong repo/worktree;
- artefacts are missing;
- branch contamination is detected;
- a workaround would weaken governance;
- a cleanup action may delete useful evidence;
- a runtime fix changes service configuration.

---

## 13. Recommended Default Workflow

```text
1. PO approves PE concept.
2. PM creates PE registry entry and PE_TASK.md.
3. Gatekeeper runs pre-dispatch readiness check.
4. PM dispatches implementer with fresh session and assigned worktree.
5. Implementer commits and produces HANDOFF.md + Status Packet.
6. Watchdog confirms artefacts.
7. PM dispatches validator with fresh session and separate validation worktree.
8. Validator produces REVIEW/verdict.
9. PM requests PO approval for merge if required.
10. PR merges only after branch protection passes.
11. Worktrees are cleaned up after merge/closure.
```

---

## 14. Non-Negotiable Rules

1. Do not bind OpenClaw workspace directly to `/opt/elis/repo`.
2. Do not share a mutable working directory between active agents.
3. Do not dispatch from Platform Monitor.
4. Do not accept silent success.
5. Do not validate the wrong repo path.
6. Do not merge without branch protection and PO-approved process.
7. Do not let Discord chat history become the only source of truth.
8. Do not run broad destructive commands without explicit approval and rollback.
9. Do not ignore rate-limit warnings.
10. Do not proceed when repo/worktree state is dirty unless the dirty state is understood and authorised.

---

## 15. Final Doctrine

ELIS should use a disciplined, artefact-driven, worktree-safe multi-agent process.

```text
OpenClaw workspace = agent operational home
Git worktree = task-specific repository working directory
/opt/elis/repo = canonical clean repository
PM = workflow owner
Platform Monitor = operational health and recovery
Gatekeeper = readiness
Watchdog = progress monitoring
PO = final governance authority
```

The goal is not to make agents remember more. The goal is to make each agent run smaller, safer, restartable, and verifiable.
