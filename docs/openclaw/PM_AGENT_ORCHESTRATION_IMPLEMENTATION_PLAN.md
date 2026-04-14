# PM Agent Orchestration Implementation Plan

> Status: implementation plan for PM to agent orchestration hardening
> Date: 2026-04-14
> Depends on: `docs/openclaw/PM_AGENT_ORCHESTRATION_CONTRACT.md`

---

## 1. Objective

Implement a reliable PM orchestration model where:

- PM can control any assigned agent by role ID
- direct OpenClaw session control is primary
- runner dispatch is safe fallback
- all actions are auditable and evidence-backed

---

## 2. Scope

In scope:

- PM workspace orchestration rules
- command routing and fallback behaviour
- execution evidence and status semantics
- CI workflow linkage for implementer and validator runs
- tests for routing and status correctness

Out of scope:

- replacing OpenClaw runtime internals
- changing branch protection policy content
- model-provider specific tuning

---

## 3. Work Packages

### WP-1: PM Rule Hardening

Deliverables:

- update PM workspace rules with authoritative-state guard
- add explicit PE start procedure with runner fallback
- persist rules in PM `MEMORY.md`

Status target:

- merged and deployed to `elis-server`

Acceptance:

- PM no longer reports PE status from stale local file when repo is dirty
- PM can start PE without requiring direct live worker chat

### WP-2: Command Routing Layer

Deliverables:

- add `scripts/pm_orchestrator.py`
- add `scripts/check_agent_reachability.py`
- define command envelopes (`command_id`, `operation`, `agent_id`, `pe_id`)

Acceptance:

- PM command returns ACK within SLA
- backend choice (`direct_session` or `github_runner`) is explicit

### WP-3: Execution Ledger

Deliverables:

- add `reports/ops/agent_runs/` JSON records
- include start, backend, reference, outcome, timestamps

Acceptance:

- every PM start command has a durable execution record
- records can be traced from PM command to runner/session result

### WP-4: Workflow Integration

Deliverables:

- add `.github/workflows/pm-agent-dispatch.yml`
- pass `command_id` through implementer/validator runners
- post run links in PM evidence path

Acceptance:

- dispatch job can start implementer/validator deterministically
- PM can report run URL and completion outcome

### WP-5: Validation and Tests

Deliverables:

- `tests/test_pm_orchestrator.py`
- `tests/test_check_agent_reachability.py`
- status semantics tests for planning/implementing/validating/merged

Acceptance:

- test suite covers routing, fallback, and status evidence rules
- CI fails on regression

### WP-6: Operational Rollout

Deliverables:

- deploy updated workspaces with `scripts/deploy_openclaw_workspaces.sh`
- restart gateway and reset PM session
- run PM E2E validation runbook

Acceptance:

- PM responds with authoritative status source
- PM can start PE and provide evidence in one cycle

---

## 4. Sequence

1. Complete WP-1 (rules and memory hardening)
2. Implement WP-2 and WP-3 in same branch
3. Implement WP-4 workflow wiring
4. Add WP-5 tests and CI checks
5. Execute WP-6 deployment and E2E validation

---

## 5. Risks and Mitigations

Risk: silent fallback hides degraded direct-session routing  
Mitigation: mandatory degraded-mode disclosure in PM response template

Risk: stale local checkout causes wrong PE status  
Mitigation: hard rule to read `origin/main:CURRENT_PE.md` when dirty

Risk: status overstatement (`implementing` without evidence)  
Mitigation: enforce evidence-based status semantics in PM logic and tests

Risk: bot identity mismatch for review actions  
Mitigation: keep validator identity mapping and protected-branch review checks aligned

---

## 6. Completion Criteria

The plan is complete when all are true:

1. PM can start Implementer/Validator by role ID with command acknowledgement.
2. PM can report backend used and run reference for each command.
3. Direct session unavailability no longer blocks PE start.
4. PE status reporting is evidence-based and reproducible.
5. PM E2E validation passes after deployment on `elis-server`.

---

## 7. Operational Commands

Deployment and activation:

```bash
cd /opt/elis/repo
git pull
bash scripts/deploy_openclaw_workspaces.sh
systemctl --user restart openclaw-gateway
```

Health checks:

```bash
openclaw doctor
openclaw channels status --probe
openclaw approvals get --gateway
```

---

## 8. Related Artifacts

- `docs/openclaw/PM_AGENT_ORCHESTRATION_CONTRACT.md`
- `docs/openclaw/DEPLOYMENT.md`
- `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md`
- `docs/openclaw/PM_SESSION_RESET.md`
- `openclaw/workspaces/workspace-pm/AGENTS.md`
- `openclaw/workspaces/workspace-pm/MEMORY.md`

