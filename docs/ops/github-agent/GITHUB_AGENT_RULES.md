# GitHub Agent Rules and Source Path Enforcement

## Overview

This document outlines the rules and enforcement mechanisms for the GitHub Agent's PR source path selection process, ensuring deterministic and secure GitHub operations.

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

## PR Source Path Selection Process

1. Validate all potential PR source paths to determine exactly one authorized source
2. Fail closed if zero or multiple valid sources detected
3. Ensure source path has appropriate write access to the target GitHub repository
4. Block operations that would bypass the defined source path rules

## Action Types

### open_pr_for_validated_pe_branch

An action type that validates a PE branch and opens a pull request from the predetermined, authorized source path.

## Source Path Resolution Logic

The GitHub Agent uses these precedence rules:
1. Explicitly configured PR source path from the environment
2. PE-specific authorized source path
3. Fails if multiple or no authorized paths identified