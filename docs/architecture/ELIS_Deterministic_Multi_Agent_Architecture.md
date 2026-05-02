# ELIS Deterministic Multi-Agent Architecture

## Status
Draft — PE-ARCH-01

## Purpose
Define a deterministic multi-agent operating model for ELIS before further OpenClaw dispatch changes.

## Core authority model
- **GitHub** is the canonical repository and governance record.
- **OpenClaw/Lobster** is the execution and orchestration layer.
- **Hermes** supervises and advises through Platform Monitor and PO Advisor roles.
- **Carlos** is the final approval authority.
- External agent output is not authoritative until reflected in GitHub with commits, artefacts, validation evidence, CI status, and required governance files.

## Operating principles
1. Deterministic PE execution over free-form ad hoc dispatch.
2. One implementer and one validator per PE.
3. Role boundaries are strict and inspectable.
4. GitHub records the source of truth; OpenClaw executes.
5. Recovery must be read-only first when tool output is ambiguous.
6. No automatic push, PR, or merge.
7. Human approval is required for release-moving actions.

## Architecture layers
### 1. GitHub record layer
Stores:
- PE task packets
- handoffs
- reviews
- validation evidence
- merged history

### 2. OpenClaw execution layer
Runs:
- PE worktrees
- implementer sessions
- validator sessions
- bounded recovery workflows

### 3. Hermes supervision layer
Provides:
- platform monitoring
- recovery classification
- PO advisory drafting
- operational risk detection

### 4. Carlos approval layer
Approves:
- push
- PR
- merge
- release
- major governance changes

## Deterministic PE lifecycle
1. PM publishes the PE task packet.
2. Implementer works in the assigned worktree.
3. Implementer records HANDOFF.md.
4. Validator checks artefacts and evidence.
5. Validator writes REVIEW.md.
6. PASS stops the loop.
7. FAIL loops back, bounded by the workflow limit.
8. Recovery checks are read-only until the failure class is known.

## Recovery rule
If OpenClaw reports that tool actions may already have executed, do not retry blindly. First verify:
- agent start
- changed files
- commits
- PRs
- HANDOFF.md
- REVIEW.md
- correct worktree
- canonical repo cleanliness
- wrong-workspace duplicates
- failure class

## Workflow requirements
- maximum 3 implement/validate iterations
- explicit evidence fields in status packets
- no dispatch from recovery workflows
- no production runtime changes from documentation tasks

## Governance outputs
PE-ARCH-01 produces the architecture and boundary documents needed to make later PE workflows deterministic, auditable, and safe.
