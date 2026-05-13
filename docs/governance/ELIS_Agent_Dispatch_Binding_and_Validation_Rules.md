# ELIS Agent Dispatch, Binding, and Validation Rules

## Purpose
Define the canonical rules for PE dispatch, worktree binding, and validation readiness.

## Scope
This document governs:
- PM dispatch packets
- implementer binding and refusal rules
- validator evidence rules
- deterministic readiness checks
- persistent context preservation checks

## Required dispatch packet fields
Every dispatch must name:
- PE_ID
- lane
- branch
- starting HEAD
- PM worktree path / branch / HEAD / status
- implementer worktree path / branch / HEAD / status
- validator worktree path / branch / HEAD / status
- exact file scope
- explicit forbidden files
- evidence paths

## Binding rules
- The implementer must refuse work on the wrong branch.
- The implementer must refuse work on the wrong worktree.
- The implementer must refuse a dirty tracked worktree unless the PE explicitly allows and the PO approves it.
- The PM must not report "in progress" without reset/binding acknowledgement and active-run evidence.
- The validator must validate committed artefacts or a PO-approved snapshot, never a live implementer workspace.

## Validation classification
- Missing artefacts in an expected path are `WORKSPACE_MISMATCH`, not content failure.
- Wrong filesystem scope is a readiness failure, not a content failure.
- Stale PE artefacts are a validation failure when they are outside the expected scope or contradict the requested PE state.

## Persistent context preservation
The following paths are preserved across dispatch and must not be deleted or reset:
- `.openclaw/`
- `HEARTBEAT.md`
- `IDENTITY.md`
- `SOUL.md`
- `TOOLS.md`
- `USER.md`

## Deterministic checks
Required checks may include:
- dispatch binding check
- implementation readiness check
- validation readiness check
- persistent context preservation check

## Exclusions
Live workspace-local `SKILLS.md` files are excluded from this PE.
This PE only authors repo-tracked governance/specification files and PE evidence files.
