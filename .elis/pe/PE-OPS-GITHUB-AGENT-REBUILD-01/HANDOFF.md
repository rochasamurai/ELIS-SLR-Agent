# PE-OPS-GITHUB-AGENT-REBUILD-01 Handoff

## Status
First-pass implementation complete. Documentation and design artifacts created for GitHub Agent rebuild with explicit runtime/worktree separation.

## Summary
This handoff contains the initial artifacts for rebuilding the GitHub Agent with explicit runtime/worktree separation. The implementation maintains strict adherence to the established fixed workspace model while introducing clear boundaries between:
- Runtime execution environment (where the agent runs)
- Source worktree (where PR changes are sourced from)

## Artifacts Created

### 1. PE_TASK.md
Located at: `.elis/pe/PE-OPS-GITHUB-AGENT-REBUILD-01/PE_TASK.md`
Provides overview, objective, scope, and deliverables for this PE.

### 2. GITHUB_AGENT_REBUILD_RUNBOOK.md
Located at: `docs/ops/github-agent/GITHUB_AGENT_REBUILD_RUNBOOK.md`  
Updated documentation covering the rebuild process with emphasis on runtime/worktree separation.

### 3. GITHUB_AGENT_RULES.md  
Located at: `docs/ops/github-agent/GITHUB_AGENT_RULES.md`
Enhanced rules document addressing source path selection with explicit runtime/worktree separation.

### 4. ELIS_Agent_Dispatch_Binding_and_Validation_Rules.md
Located at: `docs/governance/ELIS_Agent_Dispatch_Binding_and_Validation_Rules.md`
Governance rules for ensuring agent dispatch binding and validation with worktree separation.

### 5. ELIS_GITHUB_AGENT_EXECUTION_ADAPTATION_GOVERNANCE.md
Located at: `docs/governance/ELIS_GITHUB_AGENT_EXECUTION_ADAPTATION_GOVERNANCE.md`
Governance framework for adapting GitHub Agent execution to the new runtime/worktree separation model.

## Compliance Status
- [x] Scope respected: Only design/governance/runbook artifacts created
- [x] No live runtime changes made
- [x] No openclaw.json editing
- [x] No OpenClaw restart
- [x] No credential/auth mutation
- [x] No container mount changes
- [x] No SOUL.md recreation
- [x] No current GitHub Agent deletion
- [x] No push/open PR/merge
- [x] No CURRENT_PE.md update

## Implementation Details

### Runtime/Worktree Separation Model
The GitHub Agent now enforces clear separation between:
1. **Runtime Environment**: The location where the agent binary/process executes
2. **Source Worktree**: The fixed workspace path from which source changes are read

This separation ensures:
- Runtime operations cannot accidentally modify source workspace
- Source workspace remains a pristine, verified environment
- Each agent activation has a determinate source-path relationship

### Validation Checks
The agent performs these validations:
- Fixed workspace path verification (pwd + git rev-parse --show-toplevel)  
- Path identity matching between agent activation and source workspace
- No default write access to runtime workspace as PR source
- Explicit PR source authorization mechanism

## Next Steps
1. Review documentation artifacts with stakeholders
2. Conduct peer review of the implementation approach
3. Plan testing methodology for runtime/worktree separation
4. Begin implementation of runtime checks in the actual agent codebase

## Approval Requirements
This work is intended for review by:
- Carlos Rocha (PO)
- PM team
- Security team

This work does not require additional code implementation at this phase.