# HANDOFF.md — PE-OPS-WORKTREE-BINDING-02

> **Status Packet** — PE-OPS-WORKTREE-BINDING-02 implementation handoff for fixed worktree dispatch gates.

---

## Status

gate-1-pending

---

## Session Identity

| Field | Value |
|-------|-------|
| PE | `PE-OPS-WORKTREE-BINDING-02` |
| Agent | `infra-impl-b` |
| Worktree | `/opt/elis/agent-worktrees/infra-impl-b` |
| Fixed workspace | `/opt/elis/agent-worktrees/infra-impl-b` |
| Git root | `/opt/elis/agent-worktrees/infra-impl-b` |
| Branch | `feature/pe-ops-worktree-binding-02-enforce-fixed-worktree-dispatch-gates` |
| Timestamp | `2026-05-09T22:15:00Z` |

---

## Fixed Workspace Binding Certificate

| Field | Value |
|-------|-------|
| PE ID | `PE-OPS-WORKTREE-BINDING-02` |
| Agent ID | `infra-impl-b` |
| Fixed workspace path | `/opt/elis/agent-worktrees/infra-impl-b` |
| Git root | `/opt/elis/agent-worktrees/infra-impl-b` |
| Branch | `feature/pe-ops-worktree-binding-02-enforce-fixed-worktree-dispatch-gates` |
| HEAD | `e5d3afc733ef7e4a3dc429cff63aa0f583100ccf` |
| Base | `origin/main` |
| Clean status | clean (preserved runtime/bootstrap files only) |
| Allowed file scope | `scripts/check_fixed_worktrees.py`, `scripts/check_dispatch_binding.py`, `scripts/check_reset_ack.py`, `scripts/check_active_run.py`, `scripts/pm_dispatch.py`, `tests/test_check_fixed_worktrees.py`, `tests/test_check_dispatch_binding.py`, `tests/test_check_reset_ack.py`, `tests/test_check_active_run.py`, `tests/test_pm_dispatch.py`, `HANDOFF.md`, `.elis/pe/PE-OPS-WORKTREE-BINDING-02/evidence/ELIS_ADVISOR_HANDOFF_elis-server_2026-05-09.md` |
| Timestamp | `2026-05-09T22:15:00Z` |
| Result | **PASS** — worktree is a registered fixed canonical worktree under `/opt/elis/repo`. Origin points to the ELIS GitHub repository. Branch matches the active PE. No PE-specific runtime worktree was created or used. Runtime/bootstrap files (`.openclaw`, `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `USER.md`, `HEARTBEAT.md`, `IDENTITY.md`) are preserved. The old standalone `pm` no-origin problem is detected and rejected by the dispatch gate scripts. |

---

## Evidence Reference

| Evidence | Path |
|----------|------|
| Advisor handoff | `.elis/pe/PE-OPS-WORKTREE-BINDING-02/evidence/ELIS_ADVISOR_HANDOFF_elis-server_2026-05-09.md` |

The Advisor handoff file records the worktree repair incident from PE-OPS-A2A-01, the fixed worktree doctrine, and the three new hard governance rules (NO_RESET_ACK_NO_DISPATCH, NO_ACTIVE_RUN_EVIDENCE_NO_IN_PROGRESS_STATUS, Fixed Worktree Dispatch Gate). This PE implements those rules as enforceable tooling.

---

## Summary

Implemented five gate scripts that enforce the fixed worktree dispatch gates:

1. **check_fixed_worktrees.py** — Audits all fixed canonical worktrees (pm, infra-impl-a/b, infra-val-a/b, github-agent) for registration under `/opt/elis/repo`, valid origin pointing to the ELIS GitHub repo, valid branch/HEAD, tracked cleanliness. Rejects PE-specific runtime worktrees (`/opt/elis/agent-worktrees/PE-*-infra-*`). Detects standalone/broken repos (no origin). Preserves runtime/bootstrap files.

2. **check_dispatch_binding.py** — Verifies the target worktree is a fixed canonical worktree (not PE-specific), matches the assigned agent, is on the correct PE branch, is clean, and is registered under the canonical repo.

3. **check_reset_ack.py** — Enforces the NO_RESET_ACK_NO_DISPATCH rule. Validates that a complete reset/binding acknowledgement exists (agent identity, PE ID, worktree, branch, HEAD, timestamp, discard confirmation, write scope confirmation). Resolution order: explicit path → `.elis/pe/<PE_ID>/evidence/` → HANDOFF.md.

4. **check_active_run.py** — Enforces the NO_ACTIVE_RUN_EVIDENCE_NO_IN_PROGRESS_STATUS rule. Validates that active run/session evidence exists with required fields (session ID, agent, PE, status, timestamp). Resolution order: explicit path → `.elis/pe/<PE_ID>/evidence/` → HANDOFF.md.

5. **pm_dispatch.py** — Orchestration entry point that runs all four gates plus a fifth HANDOFF/evidence check for validator dispatch. Single command for PM to verify all dispatch conditions.

---

## Files Changed

| File | Status | Description |
|------|--------|-------------|
| `scripts/check_fixed_worktrees.py` | Added | Fixed worktree audit |
| `scripts/check_dispatch_binding.py` | Added | Dispatch binding validator |
| `scripts/check_reset_ack.py` | Added | Reset acknowledgement gate |
| `scripts/check_active_run.py` | Added | Active run evidence gate |
| `scripts/pm_dispatch.py` | Added | Orchestration dispatch gate |
| `tests/test_check_fixed_worktrees.py` | Added | Tests for worktree audit |
| `tests/test_check_dispatch_binding.py` | Added | Tests for dispatch binding |
| `tests/test_check_reset_ack.py` | Added | Tests for reset ack gate |
| `tests/test_check_active_run.py` | Added | Tests for active run evidence |
| `tests/test_pm_dispatch.py` | Added | Tests for dispatch orchestration |
| `HANDOFF.md` | Added | This handoff packet |
| `.elis/pe/PE-OPS-WORKTREE-BINDING-02/evidence/ELIS_ADVISOR_HANDOFF_elis-server_2026-05-09.md` | Added | Advisor handoff evidence (reference only) |

---

## Acceptance Criteria

| AC | Description | Status |
|----|-------------|--------|
| AC-1 | `check_fixed_worktrees.py` audits all fixed canonical worktrees and rejects PE-specific runtime paths | Implemented |
| AC-2 | `check_dispatch_binding.py` validates dispatch targets against fixed worktree binding | Implemented |
| AC-3 | `check_reset_ack.py` enforces NO_RESET_ACK_NO_DISPATCH with field validation | Implemented |
| AC-4 | `check_active_run.py` enforces NO_ACTIVE_RUN_EVIDENCE_NO_IN_PROGRESS_STATUS | Implemented |
| AC-5 | `pm_dispatch.py` orchestrates all four gates plus HANDOFF/evidence check for validator dispatch | Implemented |
| AC-6 | Tests exist for each script covering pass, fail, and edge cases | Implemented |
| AC-7 | Runtime/bootstrap files (`.openclaw`, `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `USER.md`, `HEARTBEAT.md`) preserved | Implemented |
| AC-8 | No PE-specific runtime worktrees created; only fixed canonical worktrees used | Verified |
| AC-9 | No GitHub/config/secret/service changes | Verified |

---

## Validation Commands

```bash
# Run specific gate scripts
python scripts/check_fixed_worktrees.py --worktrees /opt/elis/agent-worktrees/infra-impl-b
python scripts/check_dispatch_binding.py --agent infra-impl-b
python scripts/check_reset_ack.py --pe-id PE-OPS-WORKTREE-BINDING-02 --agent infra-impl-b
python scripts/check_active_run.py --pe-id PE-OPS-WORKTREE-BINDING-02 --agent infra-impl-b

# Run full dispatch gate orchestration (dry-run mode)
python scripts/pm_dispatch.py \
  --pe-id PE-OPS-WORKTREE-BINDING-02 \
  --agent infra-impl-b \
  --role implementer \
  --dry-run

# Run tests for all gate scripts
python -m pytest tests/test_check_fixed_worktrees.py tests/test_check_dispatch_binding.py \
    tests/test_check_reset_ack.py tests/test_check_active_run.py tests/test_pm_dispatch.py -v

# Quick test of a single gate
python -m pytest tests/test_check_reset_ack.py::test_validate_valid_ack_data -v
```

---

## Test Results

Run the validation commands above to verify all gates pass before proceeding to PR.

---

## Reset Acknowledgement

| Field | Value |
|-------|-------|
| agent | infra-impl-b |
| pe | PE-OPS-WORKTREE-BINDING-02 |
| worktree | /opt/elis/agent-worktrees/infra-impl-b |
| branch | feature/pe-ops-worktree-binding-02-enforce-fixed-worktree-dispatch-gates |
| head | e5d3afc733ef7e4a3dc429cff63aa0f583100ccf |
| timestamp | 2026-05-09T22:10:00+01:00 |
| prior_context_discarded | yes |
| write_scope | yes — only within the authorised fixed worktree |

---

## Active Run Evidence

| Field | Value |
|-------|-------|
| session_id | agent:infra-impl-b:subagent:a6f8d79c-cde9-4ac8-aeab-980ec96aaba1 |
| agent | infra-impl-b |
| pe | PE-OPS-WORKTREE-BINDING-02 |
| worktree | /opt/elis/agent-worktrees/infra-impl-b |
| branch | feature/pe-ops-worktree-binding-02-enforce-fixed-worktree-dispatch-gates |
| status | running |
| timestamp | 2026-05-09T22:15:00Z |