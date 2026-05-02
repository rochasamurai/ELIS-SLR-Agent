# PE-ARCH-02 — Operationalise Lobster MVP

## Purpose
Minimum viable deterministic workflow model for ELIS. Turns the PE-ARCH-01 architecture into operational workflow artefacts.

## Quick reference

### Agent identities
- **Implementer**: `infra-impl-b` — works in this worktree only
- **Validator**: `infra-val-a` — read-only validation, writes REVIEW.md

### MVP loop behaviour
```
Step 1: Preflight       → verify worktree, branch, artefacts
Step 2: Implement       → modify assigned files → write HANDOFF.md → exit
Step 3: Validate        → review artefacts → write REVIEW.md → exit
Step 4: Decide          → PASS → stop | FAIL → loop (max 3 iterations)
```

### Key rules
- Max 3 implement-validate iterations
- HANDOFF.md mandatory after implementation
- REVIEW.md mandatory after validation
- No automatic push, PR, or merge
- Carlos approval required before push/PR/merge
- Read-only recovery check after UI/tool delivery failure

### Recovery failure classes
UI_DELIVERY_FAILURE | WRONG_WORKTREE | RATE_LIMIT | TOOL_CONTEXT_FAILURE | PARTIAL_EXECUTION_UNKNOWN | REPO_STATE_UNKNOWN | MISSING_HANDOFF | MISSING_REVIEW | ROLE_BOUNDARY_VIOLATION

### Validation criteria
Validator must confirm:
- [ ] GitHub authority maintained
- [ ] OpenClaw/Lobster execution role preserved
- [ ] Implementer/validator separation
- [ ] Bounded loop behaviour
- [ ] Mandatory artefact gates (HANDOFF.md, REVIEW.md)
- [ ] No automatic push/PR/merge
- [ ] Carlos approval required for release
- [ ] Read-only recovery rule present
- [ ] Explicit evidence fields in status packets

### Run sequence
```bash
# From within this worktree:
cd /opt/elis/agent-worktrees/PE-ARCH-02-infra-impl-b

# 1. Confirm context
git branch                     # should show feature/pe-arch-02-operationalise-lobster-mvp
git rev-parse --show-toplevel  # should show this worktree
cat CURRENT_PE.md              # confirms PE-ARCH-02 is active

# 2. Run preflight checks
# (manual or via pe-implement-validate-loop.lobster)

# 3. Implement → commit → HANDOFF.md
# 4. Validate → REVIEW.md
# 5. Repeat on FAIL up to 3 iterations
# 6. Carlos approval → push → PR → merge
```
