/**
 * index.ts — PE-ARCH-11
 *
 * Inert TaskFlow Controller Prototype — Main Entry Point.
 *
 * This module is the public entry point for the inert TaskFlow controller
 * prototype. It orchestrates the LifecycleManager by combining the TaskFlow
 * bridge with the Lobster self-test wrapper, exposing a single, safe
 * orchestration function.
 *
 * === Scope ===
 * Inert prototype only. Does NOT:
 *   - Enable Lobster in production
 *   - Modify production OpenClaw config
 *   - Run production PE workflows
 *   - Create automatic push/PR/merge behaviour
 *   - Implement a general-purpose TaskFlow controller
 *
 * === Usage ===
 * ```ts
 * import { orchestrateInertPrototype } from "./index";
 *
 * const result = orchestrateInertPrototype({
 *   peId: "PE-ARCH-11",
 *   worktreePath: "/opt/elis/agent-worktrees/PE-ARCH-11-infra-impl-b",
 *   branch: "feature/pe-arch-11-inert-task-flow-controller-prototype",
 *   trustedSessionKey: "inert-prototype-key",
 * });
 * ```
 */

import {
  createInertBridge,
  type TaskFlowBinding,
} from "./task-flow-bridge";
import {
  runInertSelfTest,
  CONTROLLER_ID,
  FLOW_GOAL,
  CHILD_RUNTIME,
  CHILD_TASK_ID,
  type LobsterSelfTestFlowState,
} from "./lobster-self-test-wrapper";

// ── Orchestration input ─────────────────────────────────────────────

export interface OrchestrationInput {
  peId: string;
  worktreePath: string;
  branch: string;
  trustedSessionKey: string;
}

// ── Orchestration result ────────────────────────────────────────────

export interface OrchestrationResult {
  passed: boolean;
  callLog: string[];
  flowState: LobsterSelfTestFlowState;
  flowId: string | null;
}

// ── Orchestration (inert) ───────────────────────────────────────────

/**
 * orchestrateInertPrototype — run the full inert TaskFlow lifecycle
 * over the Lobster self-test.
 *
 * Steps:
 * 1. Create an inert TaskFlow bridge
 * 2. Bind session
 * 3. Create managed flow
 * 4. Run child task (the self-test)
 * 5. Execute self-test steps
 * 6. Wait (simulate external gate)
 * 7. Resume
 * 8. Finish
 *
 * Every step is logged into `callLog` for test assertion.
 */
export function orchestrateInertPrototype(
  input: OrchestrationInput
): OrchestrationResult {
  const { api, callLog } = createInertBridge();

  // Step 1: Bind session
  const binding: TaskFlowBinding = api.bindSession({
    sessionKey: input.trustedSessionKey,
    requesterOrigin: `pe-worktree:${input.peId}`,
  });

  // Step 2: Create managed flow
  const created = binding.createManaged({
    controllerId: CONTROLLER_ID,
    goal: FLOW_GOAL,
    currentStep: "init",
    stateJson: {
      peId: input.peId,
      worktreePath: input.worktreePath,
      branch: input.branch,
      status: "created",
      stepResults: [],
    },
  });
  const flowId = created.flowId;
  let revision = created.revision;

  // Step 3: Run child task (the self-test)
  const taskResult = binding.runTask({
    flowId,
    runtime: CHILD_RUNTIME,
    childSessionKey: input.trustedSessionKey,
    runId: CHILD_TASK_ID,
    task: "Lobster self-test under inert TaskFlow prototype",
    status: "running",
    startedAt: Date.now(),
    lastEventAt: Date.now(),
  });

  if (!taskResult.created) {
    // If the task can't be created, fail the flow
    const failResult = binding.fail({
      flowId,
      expectedRevision: revision,
      currentStep: "init",
      stateJson: { error: taskResult.reason ?? "Unknown runTask failure" },
      errorSummary: `runTask failed: ${taskResult.reason ?? "unknown"}`,
    });

    return {
      passed: false,
      callLog,
      flowState: {
        peId: input.peId,
        worktreePath: input.worktreePath,
        branch: input.branch,
        trustedSessionKey: input.trustedSessionKey,
        currentStep: "failed",
        stepIndex: 0,
        totalSteps: 0,
        status: "failed",
        revision: failResult.revision,
        blockedSummary: taskResult.reason ?? "runTask returned created=false",
        evidence: {
          agentStarted: true,
          correctWorktreeUsed: true,
          filesChanged: [],
          commitCreated: null,
          handoffExists: false,
          reviewExists: false,
          productionConfigTouched: false,
        },
        stepResults: [],
        errorSummary: taskResult.reason ?? "runTask failed",
      },
      flowId,
    };
  }

  // Step 4: Advance to self-test
  revision++;
  const waiting = binding.setWaiting({
    flowId,
    expectedRevision: revision,
    currentStep: "await_self_test_gate",
    stateJson: {
      status: "waiting",
      stepIndex: 0,
      totalSteps: 5,
    },
    waitJson: {
      kind: "exec",
      description: "Await Lobster self-test execution",
    },
  });
  revision = waiting.revision;

  // Step 5: Execute the self-test (inert simulation)
  const selfTestResult = runInertSelfTest({
    peId: input.peId,
    worktreePath: input.worktreePath,
    branch: input.branch,
    trustedSessionKey: input.trustedSessionKey,
  });

  // Step 6: Resume after self-test
  revision++;
  const resumed = binding.resume({
    flowId,
    expectedRevision: revision,
    currentStep: "evaluate_results",
    stateJson: {
      status: "evaluating",
      stepResults: selfTestResult.flowState.stepResults,
    },
  });
  revision = resumed.revision;

  // Step 7: Finish the flow
  revision++;
  const finished = binding.finish({
    flowId,
    expectedRevision: revision,
    currentStep: selfTestResult.passed ? "completed" : "failed",
    stateJson: {
      status: selfTestResult.passed ? "completed" : "failed",
      finalResults: selfTestResult.flowState.stepResults,
      evidence: selfTestResult.flowState.evidence,
    },
  });

  return {
    passed: selfTestResult.passed,
    callLog,
    flowState: {
      ...selfTestResult.flowState,
      revision: finished.revision,
    },
    flowId,
  };
}
