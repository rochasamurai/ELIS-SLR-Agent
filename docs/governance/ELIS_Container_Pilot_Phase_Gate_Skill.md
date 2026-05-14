# ELIS Container Pilot Phase Gate Skill

## Overview
The ELIS Container Pilot Phase Gate Skill defines the operational framework for managing infrastructure changes through containerisation using a four-phase approach: Planning, Build-preflight, Smoke-test, and Cutover. This skill establishes governance and quality gates for containerised deployments.

## Phase Definitions

### 1. Planning Phase
**Purpose**: Establish the foundation for containerisation initiatives

**Activities**:
- Requirements gathering and analysis
- Architecture design for containerised systems
- Resource assessment and capacity planning
- Risk evaluation and mitigation strategies
- Stakeholder alignment and communication

**Gates**:
- Approval of architectural blueprint
- Resource allocation confirmation
- Risk assessment completion

### 2. Build-preflight Phase
**Purpose**: Prepare for container image creation and validation

**Activities**:
- Container image creation and tagging
- Configuration validation  
- Security scanning
- Performance baseline establishment
- Integration testing preparation

**Gates**:
- Image build successful and verified
- Security scan results approved
- Configuration compliance verified

### 3. Smoke-test Phase
**Purpose**: Basic verification of container deployment functionality

**Activities**:
- Deployment verification only (rule-based validation)
- Basic health checks
- Configuration validation
- Access rights confirmation

**Restriction**: This phase includes ONLY rule-based validation. No actual container tests or smoke-tests should be executed in this PE. The smoke-test phase is defined as a governance rule but does not perform actual container testing.

**Gates**:
- Rule-based deployment verification passed
- Health check configurations validated

### 4. Cutover Phase
**Purpose**: Migration of services to containerised environment

**Activities**:
- Service migration execution
- Production deployment
- Monitoring activation
- Rollback preparation
- Final validation

**Gates**:
- Successful production deployment
- System monitoring activated
- Data integrity verified

## Key Principles
- Phase gates mandate strict adherence to defined checkpoints
- Smoke-test phase should maintain rule-only definition without execution
- All changes must follow established governance protocols
- Documentation must be maintained throughout all phases

## Compliance Requirements
This skill supersedes previous containerisation approaches and must be fully implemented before any containerised deployments commence.

## References
- ELIS Multi-Agent Implementation Plan v2.0
- ELIS Containerised GitHub Agent Runtime Plan
- ELIS Multi-Agent Governance Architecture v2