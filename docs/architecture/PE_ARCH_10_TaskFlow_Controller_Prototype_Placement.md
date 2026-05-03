# PE-ARCH-10 — Task Flow Controller Prototype Placement and API Imports

## Status
Draft — PE-ARCH-10

## Purpose
Verify the correct repository placement, package conventions, TypeScript build/test pattern, and TaskFlow SDK import/API surface before any inert controller prototype is created.

## Evidence gathered so far
- The ELIS repo currently has no verified `plugins/` tree.
- The ELIS repo is documentation-first here: docs, tests, workflows, and governance files are present, but no confirmed plugin package layout for a TypeScript controller prototype.
- Existing discovery work documents the canonical managed TaskFlow surface as `api.runtime.tasks.flow`, with the alias `api.runtime.taskFlow` still present.
- Trusted binding helpers and managed lifecycle methods are already documented in prior PE-ARCH discovery notes.

## Placement conclusion
A future TaskFlow controller prototype should live in the **OpenClaw runtime/plugin layer**, not as ELIS production logic.

For the ELIS repo itself:
- do **not** add controller source code here
- do **not** add production config changes here
- do **not** add tests for non-existent controller code here

The earlier placeholder path `plugins/taskflow-controller-prototype` is **not confirmed as correct inside this repo**. It may only be used later if the OpenClaw runtime repository confirms that plugin/package convention.

## API import conclusion
Documented discovery currently supports:
- canonical runtime shape: `api.runtime.tasks.flow`
- alias: `api.runtime.taskFlow`

The exact import path must be confirmed in the OpenClaw runtime source before any prototype implementation is written. Until then, the safe statement is: the prototype should bind only trusted tool/session context and call the managed TaskFlow surface documented by the runtime.

## Test/package convention conclusion
This ELIS repo does not currently show a TypeScript plugin/package test convention. Therefore:
- do not invent a new TypeScript package here
- do not add a controller test file here
- confirm the OpenClaw runtime repo’s package layout first

## Production safety
This discovery remains safe because it only records placement and API assumptions. It does not:
- enable Lobster in production
- modify production OpenClaw config
- run production PE workflows
- create PRs, push, or merge changes

## Rollback / removal path
If a future prototype is later created in the OpenClaw runtime repo, rollback should be:
1. remove the prototype package directory
2. remove the task packet / handoff references
3. leave production config unchanged
4. confirm the canonical repo returns clean

## Future PE-ARCH-11 implementation file list
Provisional, pending OpenClaw repo convention confirmation:
- `plugins/taskflow-controller-prototype/src/index.ts`
- `plugins/taskflow-controller-prototype/src/task-flow-bridge.ts`
- `plugins/taskflow-controller-prototype/src/lobster-self-test-wrapper.ts`
- `plugins/taskflow-controller-prototype/package.json` (or equivalent package manifest in the runtime repo)
- `tests/taskflow-controller-prototype.test.ts` (only if the runtime repo uses that convention)
- `HANDOFF.md`

## Validation criteria
A validator should confirm:
- ELIS repo stays docs-only for this PE
- the placement decision is evidence-based
- the TaskFlow alias/import surface is documented
- future prototype files are scoped to the runtime repo, not ELIS governance files
- no production config change is required
