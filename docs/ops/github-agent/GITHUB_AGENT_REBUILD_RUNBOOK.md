# GitHub Agent Rebuild Runbook with Explicit Runtime/Worktree Separation

## Overview
This runbook provides guidelines for rebuilding the GitHub Agent with explicit runtime/worktree separation to maintain architectural integrity and security boundaries.

## Prerequisites
- Current ELIS PE Operating Protocol implementation
- Fixed workspace model compliance
- GitHub write boundary enforcement mechanisms
- Understanding of the existing GitHub Agent operating model

## Runtime/Worktree Separation Model

### Key Concepts

#### Runtime Environment
- The execution location of the GitHub Agent binary/process
- Should be isolated from source worktree to prevent accidental source modifications
- Typically located in a temporary/runtime directory during execution
- Can be different from the source worktree path

#### Source Worktree
- The fixed workspace path from which PR changes are sourced
- Must be a verified, authenticated fixed worktree
- Must match the agent activation identity 
- Should not be the same as runtime environment

### Separation Enforcement

#### 1. Path Verification
```
# Runtime Environment Check
RUNTIME_WORKTREE=$(pwd)
RUNTIME_COMMIT=$(git rev-parse HEAD)

# Source Worktree Verification  
SOURCE_WORKTREE=$(git rev-parse --show-toplevel) 
SOURCE_COMMIT=$(cd $SOURCE_WORKTREE && git rev-parse HEAD)

# Identity Validation
if [ "$RUNTIME_WORKTREE" = "$SOURCE_WORKTREE" ]; then
    echo "ERROR: Runtime and source worktrees cannot be identical"
    exit 1
fi
```

#### 2. Fixed Workspace Binding
All GitHub Agent operations must occur from verified fixed workspaces:
- `/opt/elis/agent-worktrees/<role>-<slot>` 
- Identity must be validated through path verification and commit checks

#### 3. Source Path Authorization
- Only explicitly authorized source paths allowed
- Single source path enforcement to avoid ambiguity
- Source paths must be validated against PE requirements

## Rebuild Process

### Phase 1: Analysis and Planning
1. Review existing GitHub Agent implementation
2. Identify current runtime/source workspace integration points
3. Document all dependencies and interfaces
4. Determine minimal changes needed for separation

### Phase 2: Design Implementation
1. Enhance source path selection logic to enforce runtime/separation
2. Update validation routines to check path separation
3. Modify authentication and authorization flows to support separation
4. Implement logging and monitoring for validation failures

### Phase 3: Testing and Validation
1. Test runtime/source separation enforcement
2. Verify fixed workspace binding still functions correctly
3. Confirm GitHub write operations work with separation
4. Validate that no runtime workspace is used as source path

## Configuration Requirements

### Environment Variables
| Variable | Purpose | Example |
|----------|---------|---------|
| `GITHUB_AGENT_RUNTIME_WORKTREE` | Explicit runtime workspace path | `/tmp/gh-agent-runtime-12345` |
| `GITHUB_AGENT_SOURCE_WORKTREE` | Authorized source workspace path | `/opt/elis/agent-worktrees/infra-impl-a` |
| `GITHUB_AGENT_ENFORCE_SEPARATION` | Enable runtime/worktree separation | `true` |

### Validation Checks
Each GitHub Agent operation must perform these validation steps:
1. Verify runtime worktree is different from source worktree
2. Validate both worktrees are proper fixed workspaces
3. Confirm agent identity matches expected workspace
4. Ensure no default write access to runtime workspace
5. Validate source workspace has appropriate write permissions

## Compliance Requirements

### Rule Enforcements

#### 1. NO_RUNTIME_WORKSPACE_AS_PR_SOURCE
- The GitHub Agent must never default to its runtime workspace as PR source path
- All source paths must be explicitly configured and authorized
- Any attempt to use runtime workspace as source must be rejected

#### 2. SOURCE_PATH_AUTHORIZATION
- Only explicitly authorized source paths are permitted
- Each request must validate source path against authorization rules
- Multiple source paths must cause a failure and alert

#### 3. FIXED_WORKSPACE_BINDING
- Fixed workspace identity verification required for all operations
- Path resolution from environment variables or configuration
- Commit hash checks to verify workspace authenticity

## Troubleshooting

### Common Issues

#### Issue: Runtime and Source Worktrees Identical
**Symptom**: Agent fails with "Runtime and source worktrees cannot be identical" error
**Solution**: 
1. Ensure `GITHUB_AGENT_RUNTIME_WORKTREE` and `GITHUB_AGENT_SOURCE_WORKTREE` are distinct
2. Check that runtime workspace is not set to source worktree path
3. Configure proper separation using environment variables

#### Issue: Path Verification Failure
**Symptom**: Agent rejects path ownership verification 
**Solution**:
1. Verify worktree paths are genuine fixed workspaces
2. Ensure git operations can be performed in both locations
3. Check that agent identity matches workspace

#### Issue: Missing Source Workspace
**Symptom**: Agent reports "Invalid or missing source workspace" error
**Solution**:
1. Ensure source workspace path exists and is accessible
2. Verify that agent has necessary permissions
3. Confirm that the path is a valid git repository

## Monitoring and Logging

### Audit Trail Requirements
All GitHub Agent operations should log:
- Runtime worktree path
- Source worktree path
- Operation type (PR, commit, etc.)
- Validation outcomes
- Timestamp and operator ID

### Alert Conditions
- Attempt to use runtime workspace as source path
- Failure in path verification check
- Invalid source workspace authorization
- Unauthorized source path detection

## Security Considerations

### Separation Benefits
1. **Risk Mitigation**: Prevents accidental modification of runtime environment
2. **Auditing**: Clear separation improves traceability and audit capability
3. **Isolation**: Reduces attack surface by limiting path exposure
4. **Stability**: Ensures source workspace integrity during operations

### Potential Vulnerabilities
1. Improper configuration of workspace paths 
2. Inadequate validation of path separation
3. Weak source path authorization controls
4. Insufficient logging for separation enforcement

## References
- `docs/governance/ELIS_GitHub_Agent_Operating_Model.md`
- `docs/governance/ELIS_Agent_Dispatch_Binding_and_Validation_Rules.md`
- `docs/ops/github-agent/GITHUB_AGENT_RULES.md`
- `docs/governance/ELIS_PE_Operating_Protocol.md`