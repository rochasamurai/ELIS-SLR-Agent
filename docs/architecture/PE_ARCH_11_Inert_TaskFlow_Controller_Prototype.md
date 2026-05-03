# PE-ARCH-11 — Inert TaskFlow Controller Prototype

**Document status**: Architecture and implementation specification
**PE context**: PE-ARCH-11 (`feature/pe-arch-11-inert-task-flow-controller-prototype`)
**Author**: infra-impl-b
**Date**: 2026-05-03
**Review level**: Ready for validator (infra-val-a)

---

## 1. Overview

The Inert TaskFlow Controller Prototype is a set of TypeScript source files,
unit tests, and architecture documentation that demonstrate how a managed
TaskFlow can wrap the isolated Lobster self-test. The prototype is **inert**
— it uses an in-memory stub implementation of the TaskFlow SDK and does
not touch any real OpenClaw runtime, production config, or Lobster binary.

This prototype builds on the discovery and design work from:
- **PE-ARCH-08** — TaskFlow plugin controller surface discovery
- **PE-ARCH-09** — Minimal TaskFlow controller design for Lobster self-test
- **PE-ARCH-10** — Prototype placement and API import verification

---

## 2. Prior PE Findings Incorporated

### PE-ARCH-08: TaskFlow Plugin Controller Surface

| Finding | How it is used |
|---------|----------------|
| Canonical runtime shape: `api.runtime.tasks.flow` | The bridge stub exposes `api` with `fromToolContext()` and `bindSession()` matching this shape |
| Trusted binding helpers | `bindSession()` accepts `sessionKey` and `requesterOrigin` |
| Managed lifecycle: `createManaged`, `runTask`, `setWaiting`, `resume`, `finish`, `fail` | All six methods are implemented in the inert bridge stub |
| State in `stateJson`; wait details in `waitJson` | Both are stored as `Record<string, unknown>` and passed through the lifecycle |
| Mutations are revision-checked | Every mutation returns an incremented `revision`; tests verify revision tracking |
| CLI inspection: `openclaw tasks flow list/show/cancel` | Documented as the external verification surface — not stubbed |

### PE-ARCH-09: Minimal TaskFlow Controller Design

| Design Element | Implementation |
|----------------|----------------|
| Controller boundary: only create/bind/advance/observe | `orchestrateInertPrototype()` does only TaskFlow orchestration; self-test logic is in `lobster-self-test-wrapper.ts` |
| Required state: `flowId`, `controllerId`, `peId`, `worktreePath`, `branch`, `trustedSessionKey`, `currentStep`, `status`, `revision`, `blockedSummary`, `evidence` | All present in `LobsterSelfTestFlowState` interface |
| Safe start conditions | Checked via `createManaged()` returning valid `flowId`; `runTask()` returning `created: true` |
| Safe stop conditions | Flow finishes on all-pass; fails if `runTask()` returns `created: false` |
| Monitoring/evidence | `evidence` field tracks: `agentStarted`, `correctWorktreeUsed`, `filesChanged`, `commitCreated`, `handoffExists`, `reviewExists`, `productionConfigTouched` |
| No side effects | The stub never touches disk, network, or real runtime |

### PE-ARCH-10: Prototype Placement and API Imports

| Finding | Decision |
|---------|----------|
| Plugin layout: `plugins/taskflow-controller-prototype/src/` | Used as the source directory for all TypeScript files |
| No `package.json` or `tsconfig.json` required | TypeScript source files only — compilation is verified via `npx tsc --noEmit --strict` |
| Test file: `tests/taskflow-controller-prototype.test.ts` | Created in the repo's existing `tests/` directory |
| Future implementation file list | All 7 listed files are created in this PE |

---

## 3. Architecture

### 3.1 File Layout

```
plugins/taskflow-controller-prototype/
  src/
    index.ts                     — Main entry point; orchestration function
    task-flow-bridge.ts          — Inert TaskFlow SDK bridge stub and types
    lobster-self-test-wrapper.ts — Lobster self-test wrapper and flow state
tests/
  taskflow-controller-prototype.test.ts  — Unit tests
docs/
  architecture/
    PE_ARCH_11_Inert_TaskFlow_Controller_Prototype.md  — This document
.elis/pe/PE-ARCH-11/
  PE_TASK.md                     — Task packet
HANDOFF.md                       — Implementation handoff
```

### 3.2 Module Responsibilities

#### `task-flow-bridge.ts`

Provides the inert TaskFlow SDK bridge. Contains:
- Type definitions for the managed TaskFlow API surface (`TaskFlowAPI`, `TaskFlowBinding`, `CreateManagedOptions`, etc.)
- `createInertBridge()` — factory that returns a stub `api` and a `callLog` array
- `verifyAPISurface()` — helper that checks an API instance exposes all required methods
- The stub simulates all lifecycle methods without any real runtime calls

#### `lobster-self-test-wrapper.ts`

Defines the Lobster self-test wrapper. Contains:
- `SelfTestStep` — type for each canonical self-test check
- `CANONICAL_SELF_TEST_STEPS` — the five self-test commands from PE-ARCH-07
- `LobsterSelfTestFlowState` — complete flow state shape with all required fields
- `runInertSelfTest()` — inert runner that simulates executing the five checks
- `CONTROLLER_ID` and `FLOW_GOAL` constants

#### `index.ts`

Main entry point. Contains:
- `orchestrateInertPrototype()` — full lifecycle orchestration function
- Steps: bind session → create managed flow → run child task → set waiting → execute self-test → resume → finish
- Error handling: if `runTask()` fails, the flow transitions to `fail` state and returns a clear error report

### 3.3 Inert Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    orchestrateInertPrototype()               │
├─────────────────────────────────────────────────────────────┤
│  1. createInertBridge()                                     │
│  2. api.bindSession({ sessionKey, requesterOrigin })        │
│  3. binding.createManaged({ controllerId, goal, ... })      │
│  4. binding.runTask({ flowId, runtime, ... })              │
│  5. binding.setWaiting({ flowId, ... })                    │
│  6. runInertSelfTest({ peId, worktreePath, ... })          │
│  7. binding.resume({ flowId, ... })                        │
│  8. binding.finish({ flowId, ... })                        │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 Canonical Self-Test Steps (from PE-ARCH-07)

| # | ID | Description | Command Expected Output |
|---|----|-------------|------------------------|
| 1 | `profile-config-exists` | Verify lobster-test profile exists | `PROFILE_CONFIG_OK` |
| 2 | `lobster-registered` | Verify Lobster registered in test profile | `LOBSTER_REGISTERED` |
| 3 | `prod-config-untouched` | Verify production config exists | `PROD_CONFIG_EXISTS` |
| 4 | `prod-no-extensions` | Verify production has no extensions | `PROD_NO_EXTENSIONS` |
| 5 | `extension-binary-reachable` | Verify Lobster binary on disk | `EXTENSION_BINARY_OK` |

---

## 4. Safety Guarantees

| Guarantee | Mechanism |
|-----------|-----------|
| No production config changes | The stub never reads or writes any files on disk |
| No Lobster enablement in production | The prototype does not modify any OpenClaw config files |
| No production PE workflow runs | `runInertSelfTest()` simulates command execution with hardcoded passing results |
| No automatic push/PR/merge | The prototype has no Git or GitHub operations |
| No real runtime calls | `createInertBridge()` returns a pure in-memory stub — no OpenClaw SDK imports |
| Type safety | All TypeScript files compile under `--strict` mode using `npx tsc --noEmit` |
| Test isolation | Unit tests create fresh bridge instances for each test case |

---

## 5. Evidence and Monitoring (from PE-ARCH-09)

The `evidence` field in `LobsterSelfTestFlowState` tracks:

| Field | Type | Meaning |
|-------|------|---------|
| `agentStarted` | boolean | The orchestration began |
| `correctWorktreeUsed` | boolean | Worktree path matches expected |
| `filesChanged` | string[] | List of files modified during the flow |
| `commitCreated` | boolean \| null | Whether an implementation commit was made |
| `handoffExists` | boolean | HANDOFF.md was created/updated |
| `reviewExists` | boolean | REVIEW file exists |
| `productionConfigTouched` | boolean | Any production config was modified (must be `false`) |

---

## 6. Compilation and Test Verification

### Type Check
```bash
npx tsc --noEmit --strict --moduleResolution node \
  plugins/taskflow-controller-prototype/src/*.ts
```

### Unit Tests
```bash
npx mocha --require ts-node/register tests/taskflow-controller-prototype.test.ts
```

### PE Registry Check
```bash
python scripts/check_current_pe.py
```

---

## 7. Rollback / Removal

If the prototype must be removed:
1. Delete `plugins/taskflow-controller-prototype/` directory
2. Delete `tests/taskflow-controller-prototype.test.ts`
3. Delete `docs/architecture/PE_ARCH_11_Inert_TaskFlow_Controller_Prototype.md`
4. Delete `.elis/pe/PE-ARCH-11/PE_TASK.md`
5. Revert `HANDOFF.md` to prior content
6. Confirm `git status` returns clean
7. Confirm production config was never touched

---

## 8. Relationship to Future PEs

This prototype is the **implementation** phase following PE-ARCH-08 (discovery),
PE-ARCH-09 (design), and PE-ARCH-10 (placement verification). A future PE
may extend the prototype to:
- Wire it to the real OpenClaw TaskFlow SDK
- Run the self-test against a real Lobster test profile
- Add validation gates and PE registry updates
- Enable the controller as a production plugin

Each of those steps requires a separate PE with its own authorisation.