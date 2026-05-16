# ELIS PM Workspace Skills

## Purpose
Model-agnostic operating skills for the PM workspace. Read `AGENTS.md` first for constitutional rules, then this file for workflow skills and failure-class taxonomy.

## Mandatory rules
- Treat `CURRENT_PE.md` as the source for active PE state and `PLAN_CURRENT.md` as the source for plan details.
- Before any dispatch, require PE ID, branch, HEAD, worktree path, and status.
- Require explicit reset/binding acknowledgement before declaring work active.
- PM coordinates only: do not edit implementation files, do not implement, do not validate, and do not author REVIEW.md / REVIEW_PE*.md.
- PM should maintain broad read-only visibility, with narrow or no write authority.
- Future containerisation must enforce the read-broadly/write-narrowly boundary with filesystem permissions and mount design.
- Refuse dispatch if the implementer worktree is dirty, detached, or on the wrong branch.
- Validate file scope before announcing a PE in progress.
- Keep live context changes append-only and backed up first.
- If the workspace scope is wrong or files are missing, stop and report a mismatch.
- Do not introduce provider-specific, runtime, auth, container, GitHub, A2A, or Dash changes as part of this workflow.

## PE opening context workflow

1. Confirm authoritative baseline (`origin/main`).
2. Reconcile `CURRENT_PE.md` state (use `git show origin/main:CURRENT_PE.md`).
3. Verify implementer worktree binding and cleanliness.
4. Verify validator worktree preparation.
5. Run `scripts/check_pe_opening_context.py` with correct arguments.
6. Report all checks before requesting PO approval.
7. Only dispatch after PO approves the opening packet.

## Dispatch binding workflow

1. Confirm PE ID, branch, and HEAD from the opening packet.
2. Run:
   ```bash
   python scripts/check_dispatch_binding.py \
     --pe-id <PE-ID> \
     --branch <BRANCH> \
     --head <HEAD> \
     --worktree <AGENT_WORKTREE_PATH> \
     --mode implementer
   ```
3. If exit code is non-zero, classify the failure and report to PO.
4. Do not dispatch until binding passes.

## Failure-class taxonomy

Use these failure classes when dispatch is blocked:

| Failure class | When to use |
|---|---|
| `DISPATCH_BLOCKED` | General blocking; no specific classification |
| `WRONG_BRANCH` | Worktree on wrong branch |
| `WRONG_HEAD` | HEAD mismatch |
| `DIRTY_WORKTREE` | Tracked files are dirty |
| `MISSING_ORIGIN_REMOTE` | No origin remote in checkout |
| `STALE_FETCH` | `origin/main` not reachable |
| `DETACHED_HEAD` | Implementer is detached |
| `MISSING_PE_TASK` | PE_TASK.md missing |
| `IMPLEMENTER_EXECUTION_BLOCKED` | Runner failed before clean commit |
| `MISSING_RESET_ACK` | Reset/binding acknowledgement missing |
| `SELF_FIX_ROUTING` | Agent routed work to itself |
| `UNCOMMITTED_MISREPORTED` | Uncommitted work claimed as complete |

Classify every blocking scenario with `scripts/check_dispatch_binding.py --classify <CODE>`.

## PM no-write verification

After each PE, verify that PM authored no implementation or validation files:

```bash
python scripts/check_pm_no_write.py --pe-id <PE-ID> --pe-range origin/main..HEAD
```

## Implementation readiness check

Before dispatching an implementer runner, verify:

```bash
python scripts/check_implementation_readiness.py \
  --repo /opt/elis/repo \
  --worktree <AGENT_WORKTREE_PATH> \
  --branch <BRANCH> \
  --head <HEAD> \
  --pe-id <PE-ID>
```

This checks branch binding, HEAD match, worktree cleanliness, PE task packet existence, and optional persistent context files.

## Governed closeout readiness gates (PE-OPS-PE-CLOSEOUT-01)

Before closing out a PE, verify these governed readiness gates:

### Workspace binding gate
- [ ] Agent runtime workspace is correctly bound (e.g. `infra-impl-b` → `/home/samurai/openclaw/workspace-infra-impl-b`)
- [ ] Authorised Git worktree is correctly bound (e.g. `infra-impl-b` → `/opt/elis/agent-worktrees/infra-impl-b`)
- [ ] Runtime workspace and Git worktree are distinct paths
- [ ] No persistent runtime files (`.openclaw/`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, `USER.md`) exist inside the Git worktree

### Dispatch packet gate
- [ ] Fixed Workspace Binding Certificate includes: agent identity, role, runtime workspace, authorised Git worktree, git root, branch, HEAD, worktree status, write scope
- [ ] Validator readiness uses the same feature branch (not detached HEAD)
- [ ] Write scope is limited to the authorised Git worktree only

### Pre-close verification
Run before declaring a PE complete:
```bash
python scripts/check_fixed_worktrees.py
python scripts/check_dispatch_binding.py \
  --pe-id <PE-ID> \
  --branch <BRANCH> \
  --head <HEAD> \
  --worktree <AGENT_WORKTREE_PATH> \
  --mode implementer
python scripts/check_implementation_readiness.py \
  --repo /opt/elis/repo \
  --worktree <AGENT_WORKTREE_PATH> \
  --branch <BRANCH> \
  --head <HEAD> \
  --pe-id <PE-ID>
```

### Version history note
- PE-OPS-PE-CLOSEOUT-01 (2026-05-16): Added governed closeout readiness gates for workspace binding, dispatch packets, and pre-close verification.

## Evidence
- Record exact file paths, before/after hashes, backups, and readback evidence for live context updates.

## ELIS_CONTAINER_PILOT_PHASE_GATE_SKILL

Containerisation work must use strict phase gates.

### Mandatory phases

1. Planning
2. Build/preflight
3. Smoke-test
4. Cutover

Each phase requires explicit PO approval before execution and validator PASS before moving to the next phase.

### Hard stops

- Do not combine build/preflight with runtime launch.
- Do not run `docker compose up -d` without explicit PO approval.
- Do not start or enable services without explicit PO approval.
- Do not create duplicate Discord/Hermes gateway sessions.
- Do not copy `.env` into images, commits, logs, evidence, or messages.
- Do not mount the Docker socket.
- Do not use broad `/home` or `/opt` mounts.
- Do not expose secrets.
- Do not restart services or perform cutover without explicit PO approval.

### Smoke-test rules

- Use `--network none` where possible.
- Override entrypoint for smoke-tests.
- Do not use `.env` in smoke-tests unless explicitly approved.
- Confirm the gateway cannot start during smoke-test.

### Rollback and evidence

- Rollback commands must exist before runtime changes.
- Runtime changes require backup paths and restore commands.
- Evidence must not include secret values.

### Authorship separation

- Implementer writes implementation evidence and `HANDOFF.md`.
- Validator writes `REVIEW.md` and validation verdicts.
- No implementer, PM, or GitHub/Gateway agent may author `REVIEW.md`.

### Failure classes

Use these failure classes when applicable:

- CONTAINER_PHASE_GATE_VIOLATION
- DUPLICATE_GATEWAY_SESSION_RISK
- SECRET_EXPOSURE_RISK
- RUNTIME_CHANGE_NOT_APPROVED
- MISSING_ROLLBACK_PLAN
- VALIDATOR_REVIEW_REQUIRED
