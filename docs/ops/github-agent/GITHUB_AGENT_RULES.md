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

### SELF_CONTAINED_STATE_CHANGING_DISPATCH_RULE

For the GitHub Agent specifically, this rule requires:
1. All state changes must originate from the designated and authorized PR source path
2. Runtime and source worktrees must be explicitly validated as different paths
3. Any modification must follow the complete authorization chain through PM/PO
4. All write operations must be audited and traceable to their source
5. The separation is enforced for all GitHub write operations

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

### Clarification: Runtime ≠ Source Worktree

This requirement applies specifically to GitHub Agent operations as defined in the ELIS GitHub Agent Operating Model. While other agents in the system may not need explicit runtime/source separation (as they may not operate in separate execution environments), the GitHub Agent **must always enforce** this separation to mitigate risks associated with repository manipulation.

### Error Handling

If runtime/worktree separation requirements are not met:
- The operation must fail closed with clear error messaging
- Log validation failure for audit purposes
- Trigger security alert for violation
- Prevent any further processing