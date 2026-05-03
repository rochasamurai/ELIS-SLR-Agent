/**
 * lobster-self-test-wrapper.ts — PE-ARCH-11
 *
 * Inert Lobster self-test wrapper for the TaskFlow Controller Prototype.
 *
 * This module defines the shape of a harmless Lobster self-test
 * invocation wrapped inside a managed TaskFlow. It does NOT actually
 * invoke any real Lobster CLI or OpenClaw runtime — it is an inert
 * prototype that documents the intended wiring.
 *
 * === Findings from prior PEs ===
 *
 * PE-ARCH-06 (Controlled Lobster Plugin Activation Self-Test):
 *   - Lobster extension binary lives at:
 *     /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js
 *   - Test profile at ~/.openclaw/profiles/lobster-test/openclaw.json
 *   - Registration via: "extensions": ["lobster"] in test profile config
 *
 * PE-ARCH-07 (Execute Isolated Lobster Plugin Self-Test):
 *   - Self-test commands validated: profile config ok, Lobster registered,
 *     production config untouched, extension binary reachable
 *   - Harmless self-test checks run under lobster-test profile only
 *   - Production gateway never restarted or modified
 *
 * PE-ARCH-08 (Discover TaskFlow Plugin Controller Surface):
 *   - Canonical runtime shape: api.runtime.tasks.flow
 *   - Trusted binding helpers: fromToolContext(ctx), bindSession({...})
 *   - Managed lifecycle: createManaged → runTask → setWaiting → resume → finish | fail
 *   - State persists in stateJson; wait details in waitJson
 *   - Mutations are revision-checked
 *
 * PE-ARCH-09 (Minimal TaskFlow Controller for Lobster Self-Test):
 *   - Controller boundary: only create/bind/advance/observe; no Lobster logic
 *   - Required state: flowId, controllerId, peId, worktreePath, branch,
 *     trustedSessionKey, currentStep, status, revision, blockedSummary, evidence
 *   - Safe start conditions: PE task packet exists, worktree matches PE,
 *     canonical repo clean, current PE context correct, no production config change needed
 *   - Safe stop conditions: self-test passes, verified blocker, stale session,
 *     role-boundary violation, wrong worktree/repo context
 *   - Monitoring: agent started, correct worktree, files changed/unchanged,
 *     commit created/not, HANDOFF exists, REVIEW exists, no production config touched
 *
 * PE-ARCH-10 (Verify TaskFlow Controller Prototype Placement and API Imports):
 *   - Plugin dir structure: plugins/taskflow-controller-prototype/src/
 *   - Source files: index.ts, task-flow-bridge.ts, lobster-self-test-wrapper.ts
 *   - Tests: tests/taskflow-controller-prototype.test.ts
 *   - No package.json or tsconfig.json required — TypeScript source files only
 *     for the inert prototype in the ELIS repo (OpenClaw runtime repo handles compilation)
 */

// ── Self-test step definitions ──────────────────────────────────────

export interface SelfTestStep {
  id: string;
  description: string;
  command: string;
  expectedOutput: string;
}

/**
 * The canonical sequence of harmless Lobster self-test checks.
 * These are the same commands validated in PE-ARCH-07.
 */
export const CANONICAL_SELF_TEST_STEPS: SelfTestStep[] = [
  {
    id: "profile-config-exists",
    description: "Verify lobster-test profile config file exists",
    command:
      'ls ~/.openclaw/profiles/lobster-test/openclaw.json && echo "PROFILE_CONFIG_OK"',
    expectedOutput: "PROFILE_CONFIG_OK",
  },
  {
    id: "lobster-registered",
    description: "Verify Lobster extension is registered in test profile",
    command:
      'grep -q \'"extensions".*"lobster"\' ~/.openclaw/profiles/lobster-test/openclaw.json && echo "LOBSTER_REGISTERED"',
    expectedOutput: "LOBSTER_REGISTERED",
  },
  {
    id: "prod-config-untouched",
    description: "Verify production config file still exists",
    command:
      'ls ~/.openclaw/openclaw.json && echo "PROD_CONFIG_EXISTS"',
    expectedOutput: "PROD_CONFIG_EXISTS",
  },
  {
    id: "prod-no-extensions",
    description: "Verify production config has no extensions section",
    command:
      'grep -c \'"extensions"\' ~/.openclaw/openclaw.json || echo "PROD_NO_EXTENSIONS"',
    expectedOutput: "PROD_NO_EXTENSIONS",
  },
  {
    id: "extension-binary-reachable",
    description: "Verify Lobster extension binary is on disk",
    command:
      "test -f /opt/openclaw/lib/node_modules/openclaw/dist/extensions/lobster/index.js && echo \"EXTENSION_BINARY_OK\"",
    expectedOutput: "EXTENSION_BINARY_OK",
  },
];

// ── Flow state shape ────────────────────────────────────────────────

export interface LobsterSelfTestFlowState {
  peId: string;
  worktreePath: string;
  branch: string;
  trustedSessionKey: string;
  currentStep: string;
  stepIndex: number;
  totalSteps: number;
  status: "created" | "running" | "waiting" | "completed" | "failed" | "cancelled";
  revision: number;
  blockedSummary: string | null;
  evidence: {
    agentStarted: boolean;
    correctWorktreeUsed: boolean;
    filesChanged: string[];
    commitCreated: boolean | null;
    handoffExists: boolean;
    reviewExists: boolean;
    productionConfigTouched: boolean;
  };
  stepResults: Array<{
    stepId: string;
    passed: boolean;
    output: string;
  }>;
  errorSummary: string | null;
}

// ── Flow configuration ──────────────────────────────────────────────

export const CONTROLLER_ID = "elis/taskflow-controller-prototype";
export const FLOW_GOAL =
  "Wrap isolated Lobster self-test in a managed TaskFlow — inert prototype only";
export const CHILD_RUNTIME = "subprocess";
export const CHILD_TASK_ID = "lobster-self-test-run";

// ── Inert self-test runner ──────────────────────────────────────────

export interface InertSelfTestResult {
  passed: boolean;
  flowState: LobsterSelfTestFlowState;
}

/**
 * runInertSelfTest — simulates a Lobster self-test inside a managed TaskFlow.
 *
 * This is the inert prototype runner. It walks through the canonical
 * self-test steps, accumulating results without touching any real
 * runtime. This lets tests and architecture docs reference the
 * exact flow lifecycle without production side effects.
 */
export function runInertSelfTest(
  initialState: Partial<LobsterSelfTestFlowState> & {
    peId: string;
    worktreePath: string;
    branch: string;
    trustedSessionKey: string;
  }
): InertSelfTestResult {
  const stepResults: LobsterSelfTestFlowState["stepResults"] = [];

  for (const step of CANONICAL_SELF_TEST_STEPS) {
    // In inert mode, simulate successful checks
    stepResults.push({
      stepId: step.id,
      passed: true,
      output: step.expectedOutput,
    });
  }

  const allPassed = stepResults.every((sr) => sr.passed);

  const flowState: LobsterSelfTestFlowState = {
    peId: initialState.peId,
    worktreePath: initialState.worktreePath,
    branch: initialState.branch,
    trustedSessionKey: initialState.trustedSessionKey,
    currentStep: allPassed ? "completed" : "failed",
    stepIndex: CANONICAL_SELF_TEST_STEPS.length,
    totalSteps: CANONICAL_SELF_TEST_STEPS.length,
    status: allPassed ? "completed" : "failed",
    revision: 1,
    blockedSummary: allPassed ? null : "One or more self-test steps failed",
    evidence: {
      agentStarted: true,
      correctWorktreeUsed: true,
      filesChanged: [],
      commitCreated: null,
      handoffExists: false,
      reviewExists: false,
      productionConfigTouched: false,
    },
    stepResults,
    errorSummary: allPassed ? null : "Self-test failed — see stepResults for details",
  };

  return { passed: allPassed, flowState };
}