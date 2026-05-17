# ELIS Agent Dispatch Binding and Validation Rules for Runtime/Worktree Separation

## Overview
This document outlines the governance rules and validation procedures for agent dispatch binding and worktree separation in the ELIS system. These rules ensure that agents are properly dispatched to their designated fixed workspaces and that runtime/worktree separation is maintained during GitHub operations.

## Purpose
To establish clear binding requirements and validation procedures for all agents that operate within the ELIS environment, particularly those performing GitHub operations. This includes maintaining strict separation between runtime environments and source worktrees to prevent operational and security risks.

## Scope
These rules apply to all ELIS agents that:
- Perform GitHub operations (PR creation, commits, etc.)
- Operate within fixed workspaces
- Require source path identification for security and compliance
- Must maintain explicit separation between runtime and source contexts

## Core Principles

### 1. Fixed Workspace Binding
Each agent must bind to exactly one fixed workspace as its primary operational context.

### 2. Runtime/Worktree Separation
Agents must enforce separation between:
- Runtime execution environment (where the agent executes)
- Source worktree (where PR changes come from)
- These contexts must always differ to maintain security boundaries

### 3. Identity Verification
Agent identity must be verified against the workspace binding and validated through multiple mechanisms.

### 4. Authorization Chain
All agent operations must traverse proper authorization chains through PM/PO for any GitHub write operations.

## Binding Validation Process

### Pre-Dispatch Validation
Before any agent activation:
1. Verify the target fixed workspace path is valid
2. Confirm proper workspace binding for the agent role
3. Ensure the workspace matches the agent's expected identity
4. Validate that the workspace has appropriate permissions

### Runtime/Worktree Verification Flow
For every agent operation involving GitHub:
1. **Identity Check**: `pwd` vs `git rev-parse --show-toplevel` comparison
2. **Separation Validation**: Ensure runtime ≠ source worktree paths
3. **Repository Check**: Validate both paths are git repositories
4. **Permission Verification**: Verify required accesses are available

### Validation Components

#### 1. Path Identity Validation
```
# Validate that runtime is properly separated from source
RUNTIME_PATH=$(pwd)
SOURCE_PATH=$(git rev-parse --show-toplevel)

if [ "$RUNTIME_PATH" = "$SOURCE_PATH" ]; then
    echo "ERROR: Runtime and source worktrees must be different"
    exit 1
fi
```

#### 2. Workspace Validity Check
```
# Verify both workspaces are valid fixed workspaces
if [[ ! -d "$RUNTIME_PATH" ]] || [[ ! -d "$SOURCE_PATH" ]]; then
    echo "ERROR: Invalid workspace path detected"
    exit 1
fi

if ! git -C "$RUNTIME_PATH" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: Runtime workspace is not a git repository"
    exit 1
fi

if ! git -C "$SOURCE_PATH" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: Source workspace is not a git repository"
    exit 1
fi
```

#### 3. Fixed Workspace Verification
Agents must validate that:
- The workspace path is within the fixed workspace hierarchy
- Workspace identity matches agent configuration
- The workspace corresponds to the PE being operated on  
- The workspace has not been quarantined or deactivated

## Agent Assignment and Dispatch Rules

### Role-Based Assignment
- Implementer agents must bind to their designated implementer workspace
- Validator agents must bind to their designated validator workspace
- GitHub Agent must bind to its designated GitHub workspace
- All assignments follow the fixed workspace model

### Dispatch Boundaries
1. **Fixed Path Validation**: No runtime path may resolve to a different workspace than assigned
2. **Workspace Integrity**: No changes to fixed workspace layout outside of defined processes
3. **Access Restrictions**: Runtime workspace cannot be used as source workspace
4. **Authorization Dependencies**: All operations require proper PM/PO authorization for GitHub writes

## SELF_CONTAINED_STATE_CHANGING_DISPATCH_RULE

Agents that perform state-changing operations (e.g., GitHub write operations) must operate within a self-contained dispatch model that:
1. Ensures all inputs and outputs are explicitly defined
2. Requires validation of all external state dependencies 
3. Maintains deterministic and reproducible behavior
4. Provides clear auditing of all operations
5. Enforces authorization chain through PM/PO before any write operation

## STATE_CHANGING_DISPATCH_PRE_RESET_RULE

State-changing dispatch operations must be preceded by a complete reset of the agent's working state to ensure clean, deterministic execution and prevent contamination from previous operations.

## COMPLETE_COMMIT_EVIDENCE_BEFORE_REVALIDATION_RULE

All revalidation activities require complete commit evidence before proceeding. This ensures that validation is performed against committed code and not on temporary or uncommitted changes. The commit evidence includes:
1. Fully committed and integrated changes
2. Explicit commit SHA of the validated state
3. Verification that the commit is reachable from the target branch
4. Evidence that the validation was performed on committed code state

## TWO_INSPECTION_ONLY_FAILURE_ESCALATION_RULE

Any failure during operation validation must trigger a two-inspection escalation process:
1. Initial failure inspection to identify root cause
2. Second validation attempt with enhanced diagnostics
3. Escalation to supervisor role if failure persists after second inspection

## VALIDATOR_BRANCH_OWNERSHIP_RULE

Validator agents must only operate on branches they exclusively own, preventing cross-contamination of validation results and ensuring clear ownership of validation artifacts.

## IMPLEMENTER_BRANCH_RELEASE_AFTER_IMPLEMENTATION_RULE

Implementer agents must release their working branches and clean up any temporary artifacts after successful implementation, ensuring no lingering state affects future operations.

## GITIGNORE_POLICY_CHANGE_INTEGRATION_RULE

When gitignore policy changes are introduced, they must be integrated systematically with existing workspace governance to maintain consistent exclusion patterns across all agent workspaces.

## VALIDATION_AFTER_PASS_WITH_NOTES_RULE

Operations that pass validation but include notes or warnings must be documented and reviewed by the appropriate oversight role for potential action items.

## CHILD_SESSION_NO_IMPLIED_CONTEXT_RULE

Child sessions spawned from parent dispatches must not carry implied context from their parents. Each child session must establish its own explicit context and validate all assumptions independently.

## PM_STATE_CHANGING_DISPATCH_SKILL

The PM (Product Manager) role must possess the skill to issue state-changing dispatch commands that can only be executed after proper authorization chain validation from PM/PO for any write operations on GitHub.

## DISPATCH_CONTRACT_MACHINE_CHECK_RULE

All dispatch contracts must include machine-checkable validation routines to verify the compatibility of dispatch parameters with agent capabilities and workspace expectations before operation initiation.

## DOCS_ONLY_CORRECTION_DISPATCH_RULE

Documentation-only corrections must be submitted within the correct documentation governance framework, following the same validation processes as operational changes, including proper branch tagging and review cycles.

## OPENCLAW_CONFIG_EMERGENCY_CORRECTION_RECORD_RULE

All emergency configuration corrections applied to OpenClaw runtime must be recorded in a dedicated correction log that includes timestamp, operator identity, change impact assessment, and rollback procedure documentation.

## Enforcement Mechanisms

### Automated Enforcement
1. **Startup Validation**: Agent initialization checks binding validity
2. **Operation Validation**: Each GitHub operation validates separation  
3. **Continuous Monitoring**: Runtime checks for workspace integrity
4. **Error Reporting**: Clear messaging on validation failures

### Policy Violations
When violations are detected:
1. Immediate termination of the operation
2. Detailed error logging with validation details
3. Alert generation to supervision systems
4. Automatic isolation of problematic agent instance

### Audit Requirements
All binding and validation activities must be:
- Logged with timestamps
- Include agent identity and workspace details
- Capture validation parameters and results
- Store in a centralized audit trail for compliance

## Integration with Existing Protocols

### Alignment with PE Operating Protocol
These binding rules integrate with the PE Operating Protocol by:
- Reinforcing fixed workspace constraints
- Maintaining agent identity verification requirements
- Supporting the worktree preflight checklist
- Enabling Supervisor role monitoring of bindings

### Relationship to GitHub Agent Operating Model
The dispatch binding rules support and enhance:
- GitHub write boundary enforcement
- Source path governance
- Fixed workspace compliance
- Risk mitigation for unauthorized operations

## Compliance Framework

### Audit Checklist
For runtime/worktree separation compliance:
- [ ] Runtime workspace path != Source workspace path
- [ ] Both workspaces are valid git repositories
- [ ] Workspace identities match agent configurations
- [ ] Agent binding certificate is valid
- [ ] No unauthorized access to runtime workspace as source

### Incident Response
When binding failures occur:
1. Identify violation type (path, identity, authorization)
2. Escalate to Supervisor role for assessment
3. Isolate affected agent instance
4. Document for post-mortem analysis
5. Implement preventive measures for recurrence

## Version History

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.3     | 2026-05-17 | PM     | Restored core dispatch rules and expanded state change validation |
| 1.0     | 2026-05-17 | PM     | Initial draft incorporating runtime/worktree separation requirements |

## References
- `docs/governance/ELIS_PE_Operating_Protocol.md`
- `docs/governance/ELIS_GitHub_Agent_Operating_Model.md`
- `docs/governance/ELIS_Worktree_Preflight_Checklist.md`
- `docs/ops/github-agent/GITHUB_AGENT_RULES.md`