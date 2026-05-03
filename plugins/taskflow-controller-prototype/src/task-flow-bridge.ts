/**
 * task-flow-bridge.ts — PE-ARCH-11
 *
 * Inert TaskFlow SDK bridge for the TaskFlow Controller Prototype.
 *
 * This module provides a thin type-safe wrapper around the OpenClaw
 * managed TaskFlow API surface. It is purpose-built for the Lobster
 * self-test flow and deliberately exposes only the subset of the
 * TaskFlow API that the prototype needs.
 *
 * === Design constraints (from PE-ARCH-08 / PE-ARCH-09 / PE-ARCH-10) ===
 *
 * - Canonical runtime shape: `api.runtime.tasks.flow` (PE-ARCH-08 §Verified surface)
 * - Legacy alias `api.runtime.taskFlow` still present but not canonical
 * - Binding: `fromToolContext(ctx)` when trusted tool context is available
 * - Managed lifecycle: createManaged → runTask → setWaiting → resume → finish | fail
 * - State persists in `stateJson`; wait details in `waitJson`
 * - All mutations are revision-checked — carry forward `flow.revision`
 * - No branching or business logic — that belongs in the Lobster caller
 *
 * === Safety guarantees (from PE-ARCH-09 §No-side-effect rule) ===
 *
 * - Does NOT enable Lobster in production
 * - Does NOT modify production OpenClaw config
 * - Does NOT run production PE workflows
 * - Does NOT implement general TaskFlow controller beyond self-test wrapper
 * - Does NOT dispatch PE implementers or validators
 * - Does NOT create PRs, push commits, or merge changes
 */

// ── Type definitions ────────────────────────────────────────────────

/** The minimal managed TaskFlow API surface for the prototype. */
export interface TaskFlowAPI {
  fromToolContext(ctx: ToolContext): TaskFlowBinding;
  bindSession(opts: SessionBindingOptions): TaskFlowBinding;
}

export interface ToolContext {
  sessionKey: string;
  requesterOrigin?: string;
}

export interface SessionBindingOptions {
  sessionKey: string;
  requesterOrigin?: string;
}

export interface CreateManagedOptions {
  controllerId: string;
  goal: string;
  currentStep: string;
  stateJson: Record<string, unknown>;
}

export interface FlowCreated {
  flowId: string;
  revision: number;
}

export interface RunTaskOptions {
  flowId: string;
  runtime: string;
  childSessionKey: string;
  runId: string;
  task: string;
  status: string;
  startedAt: number;
  lastEventAt: number;
}

export interface RunTaskResult {
  created: boolean;
  reason?: string;
}

export interface SetWaitingOptions {
  flowId: string;
  expectedRevision: number;
  currentStep: string;
  stateJson: Record<string, unknown>;
  waitJson: Record<string, unknown>;
}

export interface ResumeOptions {
  flowId: string;
  expectedRevision: number;
  currentStep: string;
  stateJson: Record<string, unknown>;
}

export interface FinishOptions {
  flowId: string;
  expectedRevision: number;
  currentStep: string;
  stateJson: Record<string, unknown>;
}

export interface FailOptions {
  flowId: string;
  expectedRevision: number;
  currentStep: string;
  stateJson: Record<string, unknown>;
  errorSummary: string;
}

export interface CancelOptions {
  flowId: string;
  expectedRevision: number;
  reason: string;
}

export interface RequestCancelOptions {
  flowId: string;
  reason: string;
}

export interface TaskFlowBinding {
  createManaged(opts: CreateManagedOptions): FlowCreated;
  runTask(opts: RunTaskOptions): RunTaskResult;
  setWaiting(opts: SetWaitingOptions): FlowCreated;
  resume(opts: ResumeOptions): FlowCreated;
  finish(opts: FinishOptions): FlowCreated;
  fail(opts: FailOptions): FlowCreated;
  requestCancel(opts: RequestCancelOptions): void;
}

// ── Inert stub implementation ───────────────────────────────────────

/**
 * createInertBridge — creates a self-contained, no-side-effect stub
 * TaskFlow bridge for the inert prototype.
 *
 * The stub simulates TaskFlow lifecycle methods without talking to
 * any real OpenClaw runtime. It returns plausible IDs and state,
 * and records every call to `callLog` for test assertions.
 */
export function createInertBridge(): { api: TaskFlowAPI; callLog: string[] } {
  const callLog: string[] = [];
  let flowCounter = 0;

  function makeBinding(_key?: string): TaskFlowBinding {
    return {
      createManaged(opts: CreateManagedOptions): FlowCreated {
        flowCounter++;
        const flowId = `inert-flow-${flowCounter}-${Date.now()}`;
        callLog.push(
          `createManaged: ${opts.controllerId} | step=${opts.currentStep} | flowId=${flowId}`
        );
        return { flowId, revision: 1 };
      },

      runTask(opts: RunTaskOptions): RunTaskResult {
        callLog.push(
          `runTask: flowId=${opts.flowId} | runId=${opts.runId} | task=${opts.task}`
        );
        return { created: true };
      },

      setWaiting(opts: SetWaitingOptions): FlowCreated {
        callLog.push(
          `setWaiting: flowId=${opts.flowId} | step=${opts.currentStep} | revision=${opts.expectedRevision}`
        );
        return { flowId: opts.flowId, revision: opts.expectedRevision + 1 };
      },

      resume(opts: ResumeOptions): FlowCreated {
        callLog.push(
          `resume: flowId=${opts.flowId} | step=${opts.currentStep} | revision=${opts.expectedRevision}`
        );
        return { flowId: opts.flowId, revision: opts.expectedRevision + 1 };
      },

      finish(opts: FinishOptions): FlowCreated {
        callLog.push(
          `finish: flowId=${opts.flowId} | step=${opts.currentStep} | revision=${opts.expectedRevision}`
        );
        return { flowId: opts.flowId, revision: opts.expectedRevision + 1 };
      },

      fail(opts: FailOptions): FlowCreated {
        callLog.push(
          `fail: flowId=${opts.flowId} | step=${opts.currentStep} | error=${opts.errorSummary} | revision=${opts.expectedRevision}`
        );
        return { flowId: opts.flowId, revision: opts.expectedRevision + 1 };
      },

      requestCancel(opts: RequestCancelOptions): void {
        callLog.push(
          `requestCancel: flowId=${opts.flowId} | reason=${opts.reason}`
        );
      },
    };
  }

  const api: TaskFlowAPI = {
    fromToolContext(ctx: ToolContext): TaskFlowBinding {
      callLog.push(`fromToolContext: sessionKey=${ctx.sessionKey}`);
      return makeBinding(ctx.sessionKey);
    },
    bindSession(opts: SessionBindingOptions): TaskFlowBinding {
      callLog.push(
        `bindSession: sessionKey=${opts.sessionKey} | origin=${opts.requesterOrigin ?? "none"}`
      );
      return makeBinding(opts.sessionKey);
    },
  };

  return { api, callLog };
}

// ── Runtime API surface verification helpers ────────────────────────

/**
 * verifyAPISurface — validates that a given TaskFlowAPI instance exposes all
 * required methods for the prototype. Returns a report of what is present
 * and what is missing, so tests can assert completeness.
 */
export function verifyAPISurface(api: TaskFlowAPI): {
  present: string[];
  missing: string[];
} {
  const required: (keyof TaskFlowAPI)[] = [
    "fromToolContext",
    "bindSession",
  ];

  const present: string[] = [];
  const missing: string[] = [];

  for (const method of required) {
    if (typeof api[method] === "function") {
      present.push(method);
    } else {
      missing.push(method);
    }
  }

  return { present, missing };
}
