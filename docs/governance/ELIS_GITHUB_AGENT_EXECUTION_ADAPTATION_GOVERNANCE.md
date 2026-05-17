# ELIS GitHub Agent Execution Adaptation Governance

## Overview
This document provides the governance framework for adapting GitHub Agent execution to support explicit runtime/worktree separation. It establishes the principles, processes, and controls needed to maintain operational integrity while implementing the separation model.

## Purpose
To establish a governance framework that allows the GitHub Agent to operate effectively with explicit runtime/worktree separation while:
- Maintaining strict adherence to fixed workspace principles
- Enforcing security boundaries between execution and source contexts  
- Supporting all existing GitHub operation capabilities
- Preserving the auditability and traceability required for compliance

## Scope
This governance framework applies to:
- All GitHub Agent execution environments
- Runtime/worktree separation implementation
- Source path selection and validation processes
- Integration with existing ELIS protocols and policies
- Monitoring and compliance requirements

## Governance Principles

### 1. Security by Design
Runtime/worktree separation is implemented as a fundamental security control, not as an afterthought.

### 2. Operational Integrity
All GitHub Agent operations maintain complete functional equivalence to prior implementation while adding security boundaries.

### 3. Compliance First
All adaptations must align with existing governance documents and compliance requirements.

### 4. Transparency
All separation mechanisms must be well-documented and easily auditable.

## Execution Model Adaptations

### Runtime Environment Characteristics
The adapted GitHub Agent execution model defines:

#### Execution Context
- Runtime environment: Separate from source worktree
- Process isolation: Clean execution boundary
- Resource containment: Limited access to runtime resources

#### Source Context 
- Worktree isolation: Authenticated fixed workspace
- Change sources: Verified from designated worktree
- Access controls: Explicit access permissions

### Implementation Requirements

#### 1. Path Resolution Logic
The agent must resolve paths in a standardized fashion:
```
# Standard path resolution approach
RUNTIME_WORKTREE=$(get_runtime_worktree_path)
SOURCE_WORKTREE=$(get_source_worktree_path)

# Validate separation
validate_separation "$RUNTIME_WORKTREE" "$SOURCE_WORKTREE"
```

#### 2. Authorization Workflow
All GitHub operations must follow this workflow:
1. Validate runtime/worktree separation
2. Verify fixed workspace binding
3. Confirm PE and branch context
4. Obtain PM/PO authorization for write operations
5. Execute operation with full audit trail

#### 3. State Management
Maintain clear state transitions for:
- Workspace binding
- Operation validation 
- Authorization checks
- Execution context setup
- Result reporting

### Clarification: Runtime ≠ Source Requirement

The requirement that "runtime ≠ source worktree paths" is a **GitHub Agent-specific** enforcement mechanism. This is because not all agents in the ELIS system necessarily execute in separate contexts, but the GitHub Agent requires explicit separation to maintain security boundaries for repository operations. While other agents in the system may not need this enforcement, the GitHub Agent MUST maintain explicit separation between its execution environment and source workspace to:

- Prevent unintentional repository modifications in the runtime environment
- Maintain auditability of changes originated from specific workspaces  
- Enforce authorization boundaries for write operations
- Preserve the integrity of fixed workspace assignments for different agent roles

## Risk Mitigation Strategies

### Separation Risks
- *Risk*: Runtime workspace accidentally used as source
- *Mitigation*: Mandatory separation validation at startup and operation entry

- *Risk*: Path confusion due to similar naming 
- *Mitigation*: Clear distinction in documentation and automated validation

- *Risk*: Performance impacts from additional validation
- *Mitigation*: Optimized validation routines with caching where appropriate

### Operational Risks
- *Risk*: Agent startup failures due to binding issues
- *Mitigation*: Comprehensive error handling and graceful degradation

- *Risk*: Unauthorized operations despite validation
- *Mitigation*: Multi-layered validation and audit trails

- *Risk*: Misconfiguration in workspace definitions
- *Mitigation*: Parameter validation and documentation standards

## Compliance Requirements

### Regulatory Alignment
The adaptation must comply with:
- Internal security policies
- Fixed workspace compliance requirements  
- GitHub write boundary governance
- Audit and logging mandates

### Audit Trail Requirements  
Each GitHub Agent execution must produce:
- Runtime worktree path at startup
- Source worktree path for each operation
- Authorization status for write operations
- Validation results for binding and separation
- Timestamps and session identifiers

### Monitoring Parameters
Monitor these key metrics:
- Agent activation success rates
- Path separation validation results
- Authorization compliance rates  
- Operation throughput
- Error frequency and types

## Implementation Controls

### 1. Configuration Management
- Required environment variables for workspace separation:
  - `GITHUB_AGENT_RUNTIME_WORKTREE`
  - `GITHUB_AGENT_SOURCE_WORKTREE`  
  - `GITHUB_AGENT_ENFORCE_SEPARATION`

### 2. Validation Controls
- Startup binding validation
- Per-operation path verification
- Identity consistency checks
- Repository integrity validation

### 3. Failure Handling
- Graceful error messaging for separation violations
- Immediate termination on critical binding failures
- Complete logging of failure conditions
- Support for manual recovery procedures

## Process Integration

### With Existing Workflows
The adaptation integrates with:
- PE Operating Protocol 
- GitHub Agent Operating Model
- Agent Dispatch Binding Rules
- Fixed Worktree Preflight Checklist

### With Supervisor Role
The Supervisor role monitors:
- Agent binding compliance
- Separation enforcement adherence
- Audit trail completeness
- Operational anomaly detection

## Quality Assurance

### Testing Framework
The governance requires:
- Unit tests for separation validation
- Integration tests for end-to-end operations
- Regression tests for existing functionality
- Security penetration testing for separation controls

### Performance Benchmarking
Measure:
- Validation overhead on operation timing
- Memory usage efficiency
- Resource utilization patterns
- Scalability characteristics

## Version Control and Updates

### Release Management
Each update to the execution model must:
- Follow standard release procedures
- Include backward compatibility considerations
- Provide clear migration paths
- Document breaking changes

### Change Control
Changes to this governance framework follow:
- Formal change request process
- Stakeholder review and approval
- Documentation update requirements
- Rollback capability maintenance

## Governance Structure

### Owners and Responsibilities
- **Product Owner**: Final authority on adaptation direction
- **PM Team**: Oversight of implementation timeline and execution  
- **Security Team**: Review of risk mitigations and controls
- **Infrastructure Team**: Implementation and deployment responsibility
- **Supervisor Role**: Ongoing compliance monitoring

### Review Cadence
- Quarterly governance reviews
- Post-incident analysis of separation violations
- Annual comprehensive assessment of effectiveness
- As-needed updates for significant changes

## References and Appendices

### Related Documents
- `docs/governance/ELIS_PE_Operating_Protocol.md`
- `docs/governance/ELIS_GitHub_Agent_Operating_Model.md`
- `docs/governance/ELIS_Agent_Dispatch_Binding_and_Validation_Rules.md`
- `docs/ops/github-agent/GITHUB_AGENT_RULES.md`
- `docs/governance/ELIS_Worktree_Preflight_Checklist.md`

### Appendices
Appendix A: Sample Implementation Code
Appendix B: Audit Log Schema
Appendix C: Compliance Checklist
Appendix D: Incident Response Procedures