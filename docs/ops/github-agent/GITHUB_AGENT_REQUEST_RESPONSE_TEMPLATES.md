# GitHub Agent Request/Response Templates

## Request Templates

### Source Path Validation Request

```
## GitHub Agent Source Path Validation Request

### Operation
{operation_type}

### Target Repository
{repo_name}

### Requested Source Path
{requested_source_path}

### Authorization Scope
{authorization_scope}

### Required Permissions
{required_permissions}
```

### Pull Request Opening Request

```
## GitHub Agent PR Opening Request

### Operation Type
open_pr_for_validated_pe_branch

### Target PE
{pe_id}

### Branch Name
{branch_name}

### Source Path
{source_path}

### Validation Status
{validation_result}

### Required Changes
{required_changes}
```

## Response Templates

### Source Path Validation Response

```
## GitHub Agent Source Path Validation Response

### Request ID
{request_id}

### Validation Status
PASS / FAIL

### Selected Source Path
{selected_source_path}

### Reasoning
{validation_reasoning}

### Required Actions
{required_actions}
```

### Pull Request Opening Response

```
## GitHub Agent PR Opening Response

### Operation ID
{operation_id}

### Status
SUCCESS / FAILURE

### PR Details
- PR Number: {pr_number}
- PR URL: {pr_url}
- Base Branch: {base_branch}

### Source Path Used
{source_path_used}

### Validation Result
{validation_result}

### Error Details (if applicable)
{error_details}
```

## Source Path Decision Process

### Explicit Source Path Decision

The GitHub Agent will explicitly decide on exactly one authoritative PR source path based on:

1. Configuration precedence
2. PE authorization rules
3. GitHub write capability validation
4. Security constraints

## Compliance Verification

All GitHub operations must pass:
- Source path validation
- Write permission verification  
- PE rule compliance check
- Risk assessment