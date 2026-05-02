workflow: pe-implement-validate-loop
purpose: bounded implement/validate loop for one PE

defaults:
  max_iterations: 3
  auto_push_pr: false
  auto_merge: false
  human_approval_required: true

inputs:
  pe_id: string
  branch: string
  implementer: string
  validator: string

rules:
  - exactly one implementer
  - exactly one validator
  - implementer and validator must be distinct
  - implementer may modify only assigned files
  - validator is read-only by default
  - HANDOFF.md is mandatory after implementation
  - REVIEW.md is mandatory after validation
  - fail_results_loop_back: true
  - pass_results_stop: true

loop:
  - step: preflight
    checks:
      - current PE context
      - assigned worktree
      - canonical repo cleanliness
      - branch / HEAD
      - expected artefacts
  - step: implement
    exit_on: handoff_written
  - step: validate
    exit_on: review_written
  - step: decide
    on_fail: repeat_until_max_iterations
    on_pass: stop

status_packet:
  required_fields:
    - PE
    - Branch
    - Current state
    - Last activity
    - Expected artefacts
    - Found artefacts
    - Missing artefacts
    - Errors
    - Next owner
    - Next action
    - Evidence

controls:
  - no automatic push
  - no automatic PR
  - no merge without Carlos
  - no worktree changes outside the assigned path
