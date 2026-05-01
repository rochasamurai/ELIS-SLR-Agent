---
# PE-OPS-01 Infrastructure Implementation Template

## Overview
This template defines the structured approach for implementing infrastructure components within the PE-OPS-01 project.

## Repository Structure
Canonical repository: `/opt/elis/repo`
Assigned worktree: `/opt/elis/agent-worktrees/PE-OPS-01-infra-impl-a`

## Worktree Safety Practices
- No OpenClaw workspace directly bound to `/opt/elis/repo`
- No shared mutable working directory
- All artifacts committed to worktrees only

## Deliverables
- Docker configurations
- CI/CD workflows
- Shell scripts
- YAML configurations

## Acceptance Criteria
- All infrastructure changes follow ELIS standards  
- Quality gates pass (black, ruff, pytest)
- No hardcoded secrets in scripts or configs  
- Container security rule §5.4 is followed (no mounting ELIS repo inside container)

## Status
- [ ] Initial setup completed
- [ ] Configurations validated
- [ ] Scripts tested
- [ ] Documentation updated
---

## Artifact Validation
Required artifacts:
- HANDOFF.md (status packet)
- Status Packet for infra-val-b present
- REVIEW verdict