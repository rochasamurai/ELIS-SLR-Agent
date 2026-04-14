# PM Agent Orchestration Contract

> Status: proposed standard for ELIS OpenClaw orchestration
> Date: 2026-04-14
> Scope: PM control of Implementer and Validator agents with auditable execution

---

## 1. Purpose

This contract defines how the PM controls agents in OpenClaw while preserving
reliability, traceability, and branch-protection compliance.

It separates:

- control plane: PM to agent orchestration and status visibility
- execution plane: deterministic worker execution (direct session or runner)

Both planes are mandatory. Neither replaces the other.

---

## 2. Normative Rules

### 2.1 PM Control

1. PM must be able to address any assigned agent by role ID.
2. A PM command must return an acknowledgement within 15 seconds.
3. Every command must have a unique `command_id`.

### 2.2 Execution Backends

1. Primary backend is direct OpenClaw agent session.
2. Fallback backend is GitHub runner dispatch.
3. Fallback is allowed only in explicit degraded mode and must be reported to PO.

### 2.3 Evidence and Audit

1. Every command must produce a durable execution record.
2. Execution record must include:
   - `command_id`
   - `pe_id`
   - `agent_id`
   - backend used
   - start and finish timestamps
   - outcome (`pass`, `fail`, `blocked`, `cancelled`)
   - run URL or session reference
3. No PE state may be reported as `implementing` without remote branch or PR evidence.

### 2.4 PE Status Semantics

Use these operator-facing rules:

- `planning`: PE assigned, but no remote branch/PR/commit evidence
- `implementing`: active branch exists and implementation evidence exists
- `validating`: validator evidence exists (review file and/or review action)
- `merged`: merged to base branch

### 2.5 Authoritative State Read

1. PM reads `CURRENT_PE.md` through workspace entrypoints when host repo is clean.
2. If host repo is dirty, PM must read `origin/main:CURRENT_PE.md` for status answers.
3. PM must not answer PE status from stale local copies.

---

## 3. Control API Contract

### 3.1 Command Envelope (PM -> Router/Agent)

```json
{
  "command_id": "cmd-20260414-001",
  "operation": "start_pe",
  "pe_id": "PE-INFRA-SLR-01",
  "agent_id": "infra-impl-claude",
  "branch": "feature/pe-infra-slr-01-role-based-agent-surface-normalisation",
  "base_branch": "main",
  "plan_file": "ELIS_MultiAgent_Implementation_Plan_v1_8_2.md",
  "requested_by": "pm",
  "issued_at": "2026-04-14T09:00:00Z"
}
```

### 3.2 Acknowledgement Envelope (Router/Agent -> PM)

```json
{
  "command_id": "cmd-20260414-001",
  "ack": "accepted",
  "backend": "github_runner",
  "state": "running",
  "execution_ref": "gh://actions/runs/123456789",
  "ack_at": "2026-04-14T09:00:07Z"
}
```

---

## 4. Degraded Mode Policy

Degraded mode is active when direct worker session reachability fails.

Required behaviour:

1. PM reports degraded mode to PO before fallback dispatch.
2. PM still starts work using runner dispatch.
3. PM provides recovery status for direct session routing.
4. PM exits degraded mode only after reachability checks pass.

---

## 5. Security and Permissions

1. Bot identities must be distinct for protected-branch review actions.
2. PM tokens must use least privilege for orchestration commands.
3. Secret values must never appear in PM messages, logs, or status packets.
4. Execution records must avoid secret payload material.

---

## 6. Compliance Checks

This contract is satisfied only if all checks pass:

1. PM can start assigned Implementer with `command_id` and acknowledgement.
2. PM can query live state for each assigned agent.
3. Fallback dispatch produces auditable run reference.
4. Status reporting obeys evidence-based semantics.
5. `CURRENT_PE.md` source selection obeys dirty-tree guard rule.

---

## 7. Related Artifacts

- `openclaw/workspaces/workspace-pm/AGENTS.md`
- `openclaw/workspaces/workspace-pm/MEMORY.md`
- `.github/workflows/ci-current-pe.yml`
- `.github/workflows/implementer-runner.yml`
- `.github/workflows/validator-runner.yml`
- `scripts/dispatch_implementer_runner.py`
- `scripts/dispatch_validator_runner.py`

