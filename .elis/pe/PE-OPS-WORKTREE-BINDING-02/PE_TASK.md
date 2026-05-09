# PE-OPS-WORKTREE-BINDING-02 — Enforce Fixed Worktree Dispatch Gates

## PE_ID
PE-OPS-WORKTREE-BINDING-02

## Objective
Enforce fixed canonical worktree binding for PM dispatch so an agent can only be claimed as working when its fixed worktree is reset, bound, and evidenced correctly.

## Background
Previous PE dispatches showed that reporting and validation can drift when the runtime context is confused with the canonical fixed worktree. This PE hardens dispatch gates so PM cannot claim an agent is implementing or validating without a reset acknowledgement and active-run evidence from the fixed worktree.

## Opening file scope
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-WORKTREE-BINDING-02/PE_TASK.md`

## Implementation file scope to be proposed/pinned before dispatch
- `scripts/check_fixed_worktrees.py`
- `scripts/check_dispatch_binding.py`
- `scripts/check_reset_ack.py`
- `scripts/check_active_run.py`
- `scripts/pm_dispatch.py`

## Fixed worktree requirements
- Use only fixed worktrees.
- Do not create PE-specific runtime worktrees.
- Use the canonical fixed worktrees attached to `/opt/elis/repo`.
- Reset/bind acknowledgement is required before dispatch.
- Active-run evidence is required before PM may claim "in progress".
- HANDOFF/evidence is required before validator dispatch.

## Scope
The tools must:
- audit `pm`, `infra-impl-a/b`, `infra-val-a/b`, `prog-impl-a/b`, `prog-val-a/b`, `github-agent`
- verify each fixed worktree is registered under `/opt/elis/repo`
- verify origin points to the ELIS GitHub repo
- verify branch, HEAD, and tracked cleanliness
- reject PE-specific runtime worktrees such as `/opt/elis/agent-worktrees/PE-*-infra-*`
- preserve runtime/bootstrap files; do not blindly delete `.openclaw`, `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `USER.md`, or `HEARTBEAT.md`
- detect standalone/broken repos such as the old PM no-origin problem
- enforce reset acknowledgement before dispatch
- enforce active-run evidence before PM reports implementing/validating
- require HANDOFF/evidence before validator dispatch

## Acceptance criteria
- bad worktrees are detected
- fixed worktrees are accepted
- missing or wrong reset acknowledgement blocks dispatch
- missing active run blocks "in progress"
- checks pass in CI
- dispatch helper refuses unsafe or unbound targets

## Out of scope
- PE-specific runtime worktrees
- implementation of product features outside dispatch gating
- GitHub writes
- service restarts
- config edits
- secret/token changes
- PR creation or merges
- PO approvals

## Handoff requirements
- Opening packet recorded in `CURRENT_PE.md`
- Task file created at the approved path
- Implementer dispatch deferred until reset/binding acknowledgement is complete
- Validator dispatch deferred until HANDOFF/evidence exists
