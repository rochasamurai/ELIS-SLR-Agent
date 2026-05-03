# ELIS TaskFlow Plugin/Controller Surface

**PE**: PE-ARCH-08
**Type**: Discovery-only
**Scope**: minimal safe OpenClaw plugin/controller surface for wrapping the isolated Lobster self-test

## Summary
The minimal safe surface is a **managed TaskFlow controller wrapper** inside the OpenClaw plugin/runtime layer that can:

- bind trusted tool/session context
- create and own a managed TaskFlow
- launch a child task for the isolated Lobster self-test
- persist wait/resume state
- finish the flow cleanly
- inspect state via the existing CLI

This is enough for discovery and orchestration. It is **not** a production controller implementation.

## Verified surface
From the documented TaskFlow skill/runtime guidance:

- canonical runtime shape: `api.runtime.tasks.flow`
- alias still present: `api.runtime.taskFlow`
- trusted binding helpers:
  - `fromToolContext(ctx)`
  - `bindSession({ sessionKey, requesterOrigin })`
- managed lifecycle methods:
  - `createManaged(...)`
  - `runTask(...)`
  - `setWaiting(...)`
  - `resume(...)`
  - `finish(...)`
  - `fail(...)`
  - `requestCancel(...)` / `cancel(...)`
- `runTask(...)` is the linkage point for child work
- state is persisted in `stateJson`; wait details belong in `waitJson`
- mutations are revision-checked

CLI inspection surface already available:

- `openclaw tasks flow list`
- `openclaw tasks flow show`
- `openclaw tasks flow cancel`

## Minimal safe controller shape
A safe plugin/controller for the isolated Lobster self-test should expose only:

1. **Session binding**
   - accept a trusted `sessionKey`
   - derive requester/origin from the tool context

2. **Flow creation**
   - create a managed flow with a controller id and goal
   - store only the minimum state needed to resume

3. **Child task launch**
   - start the isolated Lobster self-test as a child task via `runTask(...)`

4. **Wait/resume**
   - use `setWaiting(...)` for human or external gates
   - use `resume(...)` when the child work can continue

5. **Completion**
   - call `finish(...)` once the self-test and report are complete

## Safe boundaries
This surface must **not**:

- enable Lobster in production
- modify production OpenClaw config
- run production PE workflows
- implement a general TaskFlow controller beyond the isolated self-test wrapper
- treat CLI inspection as a replacement for runtime ownership

## Recommended placement
The controller belongs in the OpenClaw plugin/runtime layer, not in ELIS governance docs alone. ELIS should only define:

- the allowed controller goal
- the required isolation boundary
- the flow state contract
- the discovery/report output

## Conclusion
For PE-ARCH-08, the safe discovery result is a **managed TaskFlow wrapper surface** with trusted session binding, managed flow lifecycle, child-task linkage, and CLI inspection. That is sufficient to describe how ELIS would wrap the isolated Lobster self-test without creating a production controller.
