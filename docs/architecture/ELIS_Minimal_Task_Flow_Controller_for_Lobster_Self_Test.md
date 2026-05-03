# ELIS Minimal Task Flow Controller for Lobster Self-Test

## Status
Draft — PE-ARCH-09

## Purpose
Define the smallest safe OpenClaw plugin/controller needed to create and manage a Task Flow around the isolated Lobster self-test.

## Design goal
Wrap the self-test in a managed TaskFlow so the execution becomes bounded, observable, and restartable without expanding production authority.

## Controller boundary
The controller should only:
- create a managed TaskFlow
- bind a trusted session key
- store minimal flow state
- advance the lifecycle through start, waiting, resume, finish, fail, or cancel
- surface compact status for monitoring

It should not:
- implement Lobster logic
- change OpenClaw production config
- enable production Lobster execution
- dispatch PE implementers or validators
- create PRs, push commits, or merge changes
- expand agent authority beyond the self-test flow

## Minimal runtime surface
Use the canonical managed TaskFlow API:
- `createManaged(...)`
- `runTask(...)`
- `setWaiting(...)`
- `resume(...)`
- `finish(...)`
- `fail(...)`
- `requestCancel(...)` / `cancel(...)` as needed

## Required state
Store only what is needed to resume safely:
- `flowId`
- `controllerId`
- `peId`
- `worktreePath`
- `branch`
- `trustedSessionKey`
- `currentStep`
- `status`
- `revision`
- `blockedSummary` or `waitJson`
- `evidence`

## Lifecycle
1. Create a managed flow for the isolated Lobster self-test.
2. Bind the trusted session and assigned worktree.
3. Start the self-test task.
4. Wait only for explicit, bounded external events.
5. Resume on a verified signal.
6. Finish on success.
7. Fail or cancel on a verified blocker.

## Safe start conditions
The controller may start only when all are true:
- PE task packet exists
- assigned worktree exists and matches the PE
- canonical repo is clean
- current PE context is correct
- no production config change is required
- the run is isolated to the Lobster self-test

## Safe stop conditions
Stop the flow when any of these are true:
- the self-test passes
- a verified blocker is detected
- the session becomes stale
- a role-boundary violation is detected
- the worktree or repo context is wrong

## Monitoring and evidence
The controller should expose compact evidence fields so a watchdog or validator can confirm:
- agent started
- correct worktree used
- files changed or not changed
- commit created or not created
- HANDOFF exists
- REVIEW exists
- no production config was touched

## No-side-effect rule
The controller must not produce production side effects. It is a design for a harmless, isolated task flow only.

## Expected next step
A later PE may implement this controller after the design is validated and separately authorised.
