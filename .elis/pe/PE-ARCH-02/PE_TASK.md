# PE-ARCH-02 — Operationalise Lobster MVP

## Objective
Turn the PE-ARCH-01 deterministic multi-agent architecture into a working minimum viable deterministic workflow model. Produce the MVP operational workflow package with minimum necessary edits only. Do not replace the production PE process yet.

## Scope
MVP operational workflow package.

## Required deliverables
1. `docs/architecture/ELIS_Deterministic_Multi_Agent_Architecture.md` — refined only if needed
2. `docs/governance/ELIS_Agent_Roles_and_Boundaries.md` — refined only if needed
3. `workflows/pe-implement-validate-loop.lobster`
4. `workflows/pe-recovery-check.lobster`
5. `HANDOFF.md`
6. If helpful: README/usage notes or lightweight validation/preflight documentation (keep minimal)

## MVP behaviour requirements
- Exactly one implementer agent.
- Exactly one validator agent.
- Maximum 3 implement-validate iterations.
- Mandatory HANDOFF.md after implementation.
- Mandatory REVIEW.md after validation.
- Automatic loop on FAIL.
- Stop on PASS.
- No automatic push/PR.
- No automatic merge.
- Carlos approval required before push/PR/merge.
- Read-only recovery check after UI/tool delivery failure before retry.

## Agent assignments
- **Implementer**: infra-impl-b — may modify only assigned files in the assigned worktree
- **Validator**: infra-val-a — read-only by default; must not modify implementation files

## Worktree constraints
- All work within this worktree only: `/opt/elis/agent-worktrees/PE-ARCH-02-infra-impl-b`
- Do not modify `/opt/elis/repo` directly.
- Do not change runtime config.
- Do not create PRs.
- Do not merge.
- Do not dispatch other agents.

## Verification
- Run `current-pe-check` and include evidence in HANDOFF.
- Status packet must include: PE, Branch, Current state, Last activity, Expected artefacts, Found artefacts, Missing artefacts, Errors, Next owner, Next action, Evidence.

## Recovery rule
If OpenClaw reports that tool actions may already have executed (UI delivery failure), do not retry blindly. First verify:
- agent started
- files changed
- commits created
- PRs created
- HANDOFF.md exists
- REVIEW.md exists
- correct worktree used
- canonical repo clean
- wrong-workspace duplicates checked
- failure class assigned before any retry
