# PE-OPS-SKILLS-01 — Harden Agent Skills and Dispatch/Validation Gates

## PE_ID
PE-OPS-SKILLS-01

## Lane
Strict / governance + infrastructure reliability

## Branch
`feature/pe-ops-skills-01-harden-agent-skills-and-dispatch-validation-gates`

## Starting HEAD
`3d505577c8f2767bfb04572200f64594c2e1969f`

## Scope
Repo-tracked governance/specification files only.
Live workspace-local `SKILLS.md` files are excluded from this PE.

## Deliverables
- `docs/governance/ELIS_Agent_Dispatch_Binding_and_Validation_Rules.md`
- `.elis/pe/PE-OPS-SKILLS-01/GOVERNANCE.md`
- `.elis/pe/PE-OPS-SKILLS-01/SKILLS_PM.md`
- `.elis/pe/PE-OPS-SKILLS-01/SKILLS_IMPLEMENTERS.md`
- `.elis/pe/PE-OPS-SKILLS-01/SKILLS_VALIDATORS.md`
- `.elis/pe/PE-OPS-SKILLS-01/SKILLS_GITHUB_GATEWAY.md` (only if needed)
- `.elis/pe/PE-OPS-SKILLS-01/HANDOFF.md`
- `.elis/pe/PE-OPS-SKILLS-01/REVIEW.md`
- deterministic scripts under `scripts/`
- tests under `tests/`

## Negative scenarios
- wrong branch
- wrong worktree
- dirty implementer state
- missing implementation commit
- validator using `/home/samurai` or another wrong filesystem scope
- stale PE artefacts

## Hard stops
- do not modify live workspace-local `SKILLS.md` files
- do not modify runtime/config/auth/container/GitHub/A2A/Dash settings
- do not delete persistent context files
- do not touch unrelated PE artefacts

## Evidence paths
- `.elis/pe/PE-OPS-SKILLS-01/HANDOFF.md`
- `.elis/pe/PE-OPS-SKILLS-01/REVIEW.md`
