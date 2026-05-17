# PE-OPS-GITHUB-AGENT-REBUILD-01: GitHub Agent Rebuild with Explicit Runtime/Worktree Separation

## Overview
This PE focuses on rebuilding the GitHub Agent with explicit runtime/worktree separation to ensure that the agent operates within its designated fixed workspace while maintaining clear separation between runtime environment and source worktree contexts.

## Objective
- Establish explicit runtime/worktree separation for GitHub Agent execution
- Maintain strict adherence to the fixed workspace binding model 
- Ensure GitHub operations can only originate from properly verified fixed workspaces
- Implement source path enforcement with clear boundaries between execution context and source workspace

## Scope
This PE covers:
- Design and documentation of explicit runtime/worktree separation for GitHub Agent
- Governance rules for source path selection and validation
- Runbook updates for agent rebuild and deployment
- Implementation of enforcement mechanisms for source path isolation
- Verification testing for runtime/worktree separation

## Deliverables
1. Updated PE_TASK.md (this file)
2. Updated HANDOFF.md  
3. GitHub Agent Runbook update (GITHUB_AGENT_REBUILD_RUNBOOK.md)
4. Updated GitHub Agent Rules documentation (GITHUB_AGENT_RULES.md)
5. Governance documentation for agent dispatch binding and validation (ELIS_Agent_Dispatch_Binding_and_Validation_Rules.md)
6. Governance documentation for GitHub agent execution adaptation (ELIS_GITHUB_AGENT_EXECUTION_ADAPTATION_GOVERNANCE.md)

## Stakeholders
- Carlos Rocha (PO)
- PM (Product Management)
- Infrastructure Team
- Security/Compliance Team
- GitHub Agent Developers
- Supervisor Role Operators

## Timeline
- Start: 2026-05-17
- Expected Completion: 2026-05-24
- Review Window: 2026-05-25 - 2026-05-27

## Dependencies
- Current ELIS PE Operating Protocol implementation
- Fixed workspace model compliance
- GitHub write boundary enforcement mechanisms
- Existing GitHub Agent operating model compatibility