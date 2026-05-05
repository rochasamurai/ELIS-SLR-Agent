# ELIS OpenClaw-Native Operating Model

**Status:** Draft operating model for PE-OPS-OPENCLAW-ARCH-01. This document does not by itself authorise OpenClaw config changes, agent dispatch, worktree cleanup, or PR/merge.
**Owner:** Carlos Rocha, Product Owner
**Scope:** ELIS OpenClaw runtime, session, workspace, and dispatch boundaries

## 1. Purpose

This document defines the OpenClaw-native operating model for ELIS. It makes the boundary between OpenClaw runtime state and ELIS Git worktree state explicit so ELIS can preserve auditability, attribution, reproducibility, and safety.

## 2. Scope and Authority

### 2.1 Scope

This document governs:
- OpenClaw workspace and runtime behavior
- ELIS Git worktree usage for PE execution
- agent/session binding and dispatch rules
- bootstrap/context file handling
- recovery and archival expectations

### 2.2 Authority

- Carlos Rocha is final approval authority.
- GitHub remains the canonical record for ELIS artefacts and evidence.
- OpenClaw executes and coordinates; it does not replace GitHub as the audit record.
- This document is subordinate to the governing decisions in ADR-006 and ADR-002.

## 3. Definitions

### 3.1 OpenClaw workspace

The host-side runtime/context boundary used by OpenClaw for agent execution, prompt inputs, session state, and operational files. It is not, by default, the same thing as an ELIS Git worktree.

### 3.2 ELIS Git worktree

The isolated Git working directory used for ELIS code, governance, or documentation change work. It is the code/change/audit boundary for PE execution.

### 3.3 Runtime state

OpenClaw-managed live state, including session metadata, channel bindings, logs, and other runtime-managed metadata. Runtime state belongs under `~/.openclaw`.

### 3.4 Audit state

Versioned ELIS evidence and governance state recorded in GitHub or repository artefacts, including commits, PRs, docs, handoffs, reviews, and CI evidence.

### 3.5 agentDir

The OpenClaw-managed directory associated with a configured agent’s runtime identity, local agent state, auth/profile material, and related execution metadata.

### 3.6 Session store

The OpenClaw-managed store of active or archived agent sessions and their routing/state metadata.

### 3.7 Configured agent

A stable OpenClaw-native agent definition with a persistent identity, workspace binding, and runtime configuration.

### 3.8 Detached subagent

A short-lived, ephemeral run that is not the primary continuity vehicle for a PE and must not be used as an unsafe fallback for PE continuity.

### 3.9 Thread-bound session

A session explicitly tied to a canonical Discord thread or equivalent continuity anchor for a specific PE.

### 3.10 Bootstrap/context files

Intentional OpenClaw prompt inputs and runtime context files. They are part of the runtime boundary and are not automatically contamination.

### 3.11 Prompt-level cwd override

A runtime/file-tool or prompt-scope working-directory override. It may affect execution context, but it is not valid evidence of ELIS Git worktree attribution.

## 4. Boundary Model

### 4.1 OpenClaw workspace vs ELIS Git worktree

OpenClaw workspace and ELIS Git worktree are distinct boundaries by default. They may share a path only by explicit Carlos/PO decision, documented PE scope, and Supervisor-certified preflight.

- OpenClaw workspace: runtime/context boundary
- ELIS Git worktree: code/change/audit boundary

They may interact, but they must not be treated as identical unless a PE explicitly and intentionally designates a runtime-owned worktree model.

### 4.2 Runtime state vs audit state

Runtime state may support execution and recovery, but audit state is what proves what happened.

- Runtime state must not substitute for commit provenance.
- Audit state must not be inferred from runtime cwd or session placement.
- A command being run from a path is not sufficient proof of provenance.

### 4.3 Worktree ownership

A PE worktree must be explicitly assigned and verified before any write-capable dispatch.

- The worktree is the source of change authority.
- The configured workspace is the source of runtime context.
- Attribution must be proven from the authorised worktree, not merely from the session environment.

## 5. Runtime Primitives

### 5.1 `~/.openclaw`

This directory holds live OpenClaw runtime state, including configuration, sessions, logs, and other runtime-managed metadata.

### 5.2 `agentDir`, workspace, and session store

These are distinct runtime concepts:
- `agentDir` identifies the configured agent context
- workspace identifies the runtime/context boundary
- session store tracks active and archived sessions

They must not be conflated with ELIS repository state.

### 5.3 Bootstrap/context files

Bootstrap and context files are valid runtime inputs when intentionally present. They are not contamination by default.

Unexpected auto-generated bootstrap/context files in an ELIS Git worktree are not acceptable dispatch-clean state. They must be governed, tracked intentionally, redirected, or prevented through proper OpenClaw-compatible settings.

However:
- they must be intentional
- they must be scoped
- they must not be mistaken for ELIS code provenance

## 6. Agent Model

### 6.1 Stable configured agents

ELIS should prefer stable configured agents for normal runtime operation.

These agents:
- are OpenClaw-native
- have known workspace bindings
- have known session and attribution behavior
- can be audited through their configured identity and runtime context

### 6.2 Detached subagents

Detached subagents are ephemeral and should be treated as bounded runs only.

They must not be treated as an unsafe fallback for PE continuity.
They must not replace a thread-bound PE session when continuity matters.
A detached subagent run may produce candidate evidence only. It is not valid implementation output for a continuity-sensitive PE unless explicitly authorised by Carlos/PO after Supervisor diagnosis.

### 6.3 Thread-bound sessions

Where PE continuity matters, the session must be bound to the canonical PE thread.

This provides:
- visible audit trail continuity
- explicit ownership
- controlled handoff and archival

## 7. Dispatch Model

### 7.1 Thread-bound vs detached dispatch

- Thread-bound dispatch is the default for continuity-sensitive PE work.
- Detached dispatch is not a continuity fallback.
- Unsafe fallback paths must be impossible, not merely discouraged.

### 7.2 Allowlists and fallback blocking

Dispatch must remain governed by allowlists and explicit policy gates.

- permitted operations are explicit
- disallowed fallback paths are blocked
- “try something else” runtime behavior is not acceptable for attribution-sensitive PE work
- No broad `.gitignore` suppression is approved for OpenClaw bootstrap/runtime files. Unexpected OpenClaw runtime/bootstrap files must be handled through governed OpenClaw-compatible workspace configuration, tracked minimal context where approved, or runtime/workspace separation — not by hiding them.

### 7.3 Attribution rules

Attribution must be based on:
- authorised PE worktree
- authorised branch
- committed artefacts
- session/thread binding where required

Prompt-level cwd override is not evidence of legitimate attribution.

## 8. Recovery and Resilience

### 8.1 Config recovery / last-good

OpenClaw config recovery should preserve operational resilience without redefining ELIS audit state.
`openclaw.json.last-good` and clobbered config snapshots are OpenClaw recovery artefacts. They must not silently override Supervisor-approved ELIS configuration without detection, validation, and audit.

### 8.2 Heartbeats

Heartbeats are scheduled agent turns used for monitoring or proactive handling. They are not evidence of PE completion.

### 8.3 Token/context loading

Token and context loading must be explicit, intentional, and auditable. Loaded context must not silently change PE attribution or session ownership.

## 9. PE Lifecycle Implications

### 9.1 Current PE source of truth

The active PE registry remains governed by ELIS repo artefacts and PE governance docs.

### 9.2 Handoff and review

Root handoff artefacts are transitional. PE-local handoff/review artefacts should be preferred as the long-term operational pattern.

### 9.3 Archival

After PE close, merge, or formal termination, the session is inactive forever. It may be preserved and searched for audit, but must not be resumed, rebound, reused, or treated as live continuity for a later PE.

## 10. Operational Consequences

This model implies:
- runtime and worktree boundaries must always be checked explicitly
- bootstrap/context files are deliberate runtime inputs
- detached fallback is blocked
- provenance must be proven, not inferred
- PE continuity may require thread-bound sessions
- archival is permanent, not optional
- Broad `.gitignore` suppression is not an approved solution for OpenClaw bootstrap/runtime files.

## 11. PO Decisions / Unresolved Questions

- May OpenClaw runtime state ever seed an ELIS Git worktree intentionally?
- Should some PE classes use a worktree-backed workspace model?
- What is the exact treatment of minimal tracked bootstrap/context files?
- Are thread-bound sessions mandatory for all PEs or only continuity-sensitive PEs?
- Is a config-change runbook required for this PE?

## 12. Non-goals

- This document does not modify OpenClaw config.
- This document does not decide every open PO question.
- This document does not replace ADR-006 or ADR-002.
- This document does not authorise detached fallback dispatch.
- This document does not authorise `.gitignore` suppression.

## 13. Validation Criteria

- No contradiction with ADR-006 or ADR-002.
- Clear separation of workspace/runtime/worktree/session boundaries.
- Explicit handling of bootstrap/context files.
- Explicit distinction between configured agents and detached subagents.
- Explicit thread-bound vs detached dispatch rules.
- Explicit allowlist and fallback-blocking doctrine.
- Explicit config recovery / last-good, heartbeat, token/context, and archival rules.
- No stale assumptions remain about attribution or session reuse.

## 14. Cross-References

- `docs/decisions/ADR-006-openclaw-as-native-runtime.md`
- `docs/decisions/ADR-002-git-worktrees-pe-isolation.md`
- `docs/openclaw/TARGET_LAYOUT.md`
- `docs/openclaw/DEPLOYMENT.md`
- `docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md`
- `docs/openclaw/PM_SESSION_RESET.md`
- `docs/openclaw/PM_AGENT_ORCHESTRATION_IMPLEMENTATION_PLAN.md`
- `docs/openclaw/EXEC_POLICY.md`
- `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md`
- `docs/governance/ELIS_PE_Operating_Protocol.md`
- `docs/governance/ELIS_PE_Dispatch_Checklist.md`
- `docs/governance/ELIS_Worktree_Preflight_Checklist.md`
- `docs/governance/ELIS_No_Silent_Failure_Recovery.md`
- `docs/governance/ELIS_Discord_PO_PM_Checkpoint_Governance.md`
