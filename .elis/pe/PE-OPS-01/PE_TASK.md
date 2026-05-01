# PE-OPS-01 Setup Task Packet

## Purpose
Prepare PE-OPS-01 — ELIS PE Execution Pipeline Hardening under the worktree-safe execution doctrine.

## Controlling references
1. `docs/governance/ELIS_General_Guidance.md`
2. `docs/governance/ELIS_Multi_Agent_Governance_Architecture_v2.md`
3. `docs/governance/ELIS_Multi_Agent_Governance_Implementation_Plan_v2.md`

## Canonical paths
- Canonical repo: `/opt/elis/repo`
- Agent worktree root: `/opt/elis/agent-worktrees/`
- Implementer worktree: `/opt/elis/agent-worktrees/PE-OPS-01-infra-impl-a`
- Validator worktree: `/opt/elis/agent-worktrees/PE-OPS-01-infra-val-b`

## Branch
- `feature/pe-ops-01-pe-execution-pipeline-hardening`

## Governance requirements
- OpenClaw workspace must not be bound directly to `/opt/elis/repo`.
- No shared mutable working directory between active agents.
- Implementation must occur only in the assigned implementer worktree.
- Validation must occur only in the assigned validator worktree or an approved read-only verification path.
- Platform Monitor may prepare/verify worktrees only when PO-authorised, but must not dispatch agents.
- PM remains the only dispatch authority.
- Every run must verify `pwd`, `git rev-parse --show-toplevel`, branch, worktree path, and `git status`.
- No silent success: every run must emit required artefacts/evidence.
- Respect Codex/OAuth rate-limit preflight before dispatch.

## Artefact gates
- Implementation commit
- `HANDOFF.md`
- Status Packet
- tests/checks run
- changed files list
- validator `REVIEW.md` / verdict

## Deliverables
1. `docs/templates/PE_TASK.template.md`
2. ELIS PE Gatekeeper checklist
3. ELIS PE Watchdog status format
4. PM-only dispatch rule
5. Fresh-session dispatch wrapper
6. Artefact gates
7. No-silent-success rule
8. Wrong-path prevention
9. Codex/OAuth rate-limit preflight policy
10. Discord channel/thread governance

## Dispatch state
- Implementer dispatch: not yet
- Validator dispatch: not yet
- Commit: not yet
- PO approval for implementation dispatch: required
