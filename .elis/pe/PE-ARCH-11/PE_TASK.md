# PE-ARCH-11 — Implement Inert Task Flow Controller Prototype

## Objective
Implement an inert TaskFlow controller prototype in the ELIS repo that wraps the isolated Lobster self-test inside a managed TaskFlow lifecycle, producing typed source files, unit tests, and architecture documentation. The prototype must stay inert — no production OpenClaw config changes, no production Lobster enablement, no automatic push/PR/merge.

## Scope
Implementation of an inert (self-contained, no-side-effect) TaskFlow controller prototype as a set of TypeScript source files, unit tests, and architecture documentation. The prototype uses an in-memory stub to simulate the managed TaskFlow API surface without touching any real OpenClaw runtime.

### Required deliverables
1. `plugins/taskflow-controller-prototype/src/index.ts` — Main entry point; orchestrates the inert flow lifecycle
2. `plugins/taskflow-controller-prototype/src/task-flow-bridge.ts` — Inert TaskFlow SDK bridge with type definitions and stub implementation
3. `plugins/taskflow-controller-prototype/src/lobster-self-test-wrapper.ts` — Inert Lobster self-test wrapper with flow state shape
4. `tests/taskflow-controller-prototype.test.ts` — Unit tests for the inert prototype
5. `docs/architecture/PE_ARCH_11_Inert_TaskFlow_Controller_Prototype.md` — Architecture document capturing the prototype design
6. `.elis/pe/PE-ARCH-11/PE_TASK.md` — This file
7. `HANDOFF.md` — Implementation handoff with complete status packet

### Findings from prior PEs to incorporate
- **PE-ARCH-08**: Discovered the canonical TaskFlow API surface (`api.runtime.tasks.flow`), trusted binding helpers (`fromToolContext`, `bindSession`), managed lifecycle methods (`createManaged`, `runTask`, `setWaiting`, `resume`, `finish`, `fail`), and CLI inspection surface
- **PE-ARCH-09**: Designed the minimal controller boundary, required flow state fields, safe start/stop conditions, monitoring/evidence expectations, and the no-side-effect rule
- **PE-ARCH-10**: Verified repository placement (`plugins/taskflow-controller-prototype/src/`), recorded the exact file list for implementation, confirmed test placement conventions, and documented the API import surface

## Constraints
- Inert prototype only — no real OpenClaw runtime calls
- No production OpenClaw config changes
- No production Lobster enablement
- No production PE workflow runs
- No automatic push/PR/merge behaviour
- PE-AGT-01 remains held
- PE-OPS-01 Increment 3 remains paused

## Roles
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`

## Acceptance criteria
- [ ] All 7 required files exist with meaningful content
- [ ] TypeScript source files compile without errors (type-checked via `npx tsc --noEmit —strict`)
- [ ] Unit tests pass
- [ ] PE-ARCH-08/09/10 findings are incorporated in the prototype docs/tests
- [ ] Production OpenClaw config not modified
- [ ] No Lobster plugin enabled in production
- [ ] Implementation commit present
- [ ] Worktree is clean after commit
- [ ] `python scripts/check_current_pe.py` passes

## Verification
- `python scripts/check_current_pe.py`
- `npx tsc --noEmit --strict plugins/taskflow-controller-prototype/src/*.ts` (type check)
- `npx mocha --require ts-node/register tests/taskflow-controller-prototype.test.ts` or equivalent test runner
- `git status` confirms clean worktree
- `git log --oneline -1` confirms implementation commit
- Confirm no production config files modified