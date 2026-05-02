workflow: pe-recovery-check
purpose: read-only recovery classification for ambiguous or partial PE execution

rules:
  - read-only by default
  - do not dispatch agents
  - do not modify files
  - do not commit, push, merge, or create PRs
  - verify before retrying when tool output suggests partial execution

required_verification:
  - agent started
  - files changed
  - commits created
  - PRs created
  - HANDOFF.md exists
  - REVIEW.md exists
  - correct worktree used
  - canonical repo clean
  - wrong-workspace duplicates checked
  - failure class assigned before retry

failure_classes:
  - UI_DELIVERY_FAILURE
  - WRONG_WORKTREE
  - RATE_LIMIT
  - TOOL_CONTEXT_FAILURE
  - PARTIAL_EXECUTION_UNKNOWN
  - REPO_STATE_UNKNOWN
  - MISSING_HANDOFF
  - MISSING_REVIEW
  - ROLE_BOUNDARY_VIOLATION

output:
  fields:
    - PE
    - Branch
    - Current state
    - Last activity
    - Expected artefacts
    - Found artefacts
    - Missing artefacts
    - Errors
    - Failure class
    - Next owner
    - Next action
    - Evidence

recovery_rule:
  - if OpenClaw says an agent may already have executed tool actions, verify first and retry only after classification
