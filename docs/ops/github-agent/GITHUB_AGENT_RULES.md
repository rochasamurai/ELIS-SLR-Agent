# GitHub Agent Rules and Source Path Enforcement

## Overview

This document outlines the rules and enforcement mechanisms for the GitHub Agent's PR source path selection process, ensuring deterministic and secure GitHub operations with explicit runtime/worktree separation.

## Rules

### RULE_DEFINED_PR_SOURCE_PATH

The GitHub Agent must select exactly one defined PR source path that is explicitly authorized for the operation, or fail closed if multiple or no valid paths exist.

### GITHUB_AGENT_READS_SOURCE_WRITES_REMOTE

The GitHub Agent reads from the specified PR source path and writes all changes to the remote GitHub repository.

### NO_RUNTIME_WORKSPACE_AS_PR_SOURCE

The GitHub Agent must not default to its runtime workspace as the PR source path. This prevents accidental modifications to the runtime workspace.

### NO_SINGLE_AUTHORISED_PR_SOURCE_PATH_NO_GITHUB_WRITE

The GitHub Agent must not allow operations through a single authorized PR source path that would not enable GitHub writes.

### NO_PREPARED_GITHUB_AGENT_RUNTIME_NO_GITHUB_WRITE

The GitHub Agent must always ensure that any prepared runtime workspace has proper GitHub write capabilities enabled.

### RUNTIME_WORKTREE_SEPARATION_REQUIREMENT

The GitHub Agent must enforce explicit separation between the runtime execution environment and the PR source worktree. The runtime workspace must be different from the source workspace to maintain security boundaries.

### SOURCE_PATH_AUTHORIZATION_AND_VALIDATION

All source paths must be explicitly authorized and validated against the fixed workspace binding model. The agent must verify that:
1. The source workspace is a legitimate fixed workspace path
2. The runtime workspace is distinct from the source workspace
3. Both workspaces are valid git repositories
4. Agent identity matches expected workspace

## PR Source Path Selection Process

1. Validate all potential PR source paths to determine exactly one authorized source
2. Fail closed if zero or multiple valid sources detected
3. Ensure source path has appropriate write access to the target GitHub repository
4. Block operations that would bypass the defined source path rules
5. Enforce runtime/worktree separation as part of validation process

## Action Types

### open_pr_for_validated_pe_branch

An action type that validates a PE branch and opens a pull request from the predetermined, authorized source path.

## Source Path Resolution Logic

The GitHub Agent uses these precedence rules:
1. Explicitly configured PR source path from the environment
2. PE-specific authorized source path
3. Fails if multiple or no authorized paths identified

## Runtime/Worktree Separation Requirements

### Separation Enforcement

To maintain security boundaries and operational clarity, the GitHub Agent must:

1. **Runtime Isolation**: Verify that the execution environment (runtime) differs from the source worktree
2. **Workspace Verification**: Confirm both environment and source are proper fixed workspaces
3. **Identity Binding**: Ensure agent activation matches workspace identity
4. **Access Controls**: Restrict source workspace from being runtime workspace

### Validation Sequence

For each GitHub operation, the agent must perform the following validation sequence:

1. Determine the runtime worktree location
2. Determine the source worktree location  
3. Verify runtime and source worktrees are distinct paths
4. Validate both worktrees are fixed workspaces
5. Confirm valid git repository state in both workspaces
6. Authenticate agent identity against expected workspace

### Error Handling

If runtime/worktree separation requirements are not met:
- The operation must fail closed with clear error messaging
- Log validation failure for audit purposes
- Trigger security alert for violation
- Prevent any further processing

## Implementation Guidance

### Environment-based Configuration

Agents should support configuration options to explicitly define:
- `GITHUB_AGENT_RUNTIME_WORKTREE`: The execution environment path
- `GITHUB_AGENT_SOURCE_WORKTREE`: The authorized source path  
- `GITHUB_AGENT_ENFORCE_SEPARATION`: Toggle for separation enforcement

### Validation Checks

Implement comprehensive path validation:
```bash
# Example validation logic
if [ "$RUNTIME_WORKTREE" = "$SOURCE_WORKTREE" ]; then
    echo "ERROR: Runtime and source worktrees cannot be identical"
    exit 1
fi

if [[ ! -d "$RUNTIME_WORKTREE" ]] || [[ ! -d "$SOURCE_WORKTREE" ]]; then
    echo "ERROR: One or both worktrees are invalid"
    exit 1
fi

if ! git -C "$RUNTIME_WORKTREE" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: Runtime worktree is not a valid git repository"
    exit 1
fi

if ! git -C "$SOURCE_WORKTREE" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: Source worktree is not a valid git repository"
    exit 1
fi
```