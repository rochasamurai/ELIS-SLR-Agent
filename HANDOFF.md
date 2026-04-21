# HANDOFF — PE-SLR-08 · Synthesis Off-Host Contract

**Date:** 2026-04-21
**PE:** `PE-SLR-08`
**Branch:** `feature/pe-slr-08-synthesis-off-host-contract`
**Implementer:** `slr-impl-a` (CODEX @ `elis-server`)
**Validator:** `slr-val-b` (Claude Code)

---

## 1) Summary

Implements the synthesis off-host contract as a self-contained module:

- workflow-governed off-host synthesis envelope (`SynthesisWorkflowEnvelope`)
- cross-study evidence traceability bundle (`SynthesisReasoningTrace`,
  `build_synthesis_trace_bundle`)
- explicit human-review checkpoints for high-impact outputs
  (`HumanReviewCheckpoint`, `build_high_impact_checkpoints`)
- future local migration criteria defined but blocked from activation
  (`LocalMigrationCriteria`, `assert_local_migration_not_activated`)

---

## 2) Deliverables

| File | Change |
|------|--------|
| `elis/synthesis_offhost_contract.py` | New module with synthesis off-host envelope, reasoning trace contract, high-impact review checkpoints, migration-activation guard, and persisted audit artefacts |
| `tests/test_synthesis_contract.py` | New test suite covering AC-1 to AC-5 |
| `docs/slr/SYNTHESIS_OFF_HOST_CONTRACT.md` | New documentation for synthesis off-host contract, traceability rules, review checkpoints, and migration criteria |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | Synthesis remains workflow-governed and off-host | PASS |
| AC-2 | Cross-study reasoning outputs preserve evidence traceability | PASS |
| AC-3 | Human-review checkpoints are explicit for high-impact synthesis outputs | PASS |
| AC-4 | Future local migration criteria are documented but not activated | PASS |
| AC-5 | `python -m pytest tests/test_synthesis_contract.py -v` passes | PASS |

---

## 4) Validation Commands

```bash
C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe -m black --check elis/synthesis_offhost_contract.py tests/test_synthesis_contract.py
C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe -m ruff check elis/synthesis_offhost_contract.py tests/test_synthesis_contract.py
C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe -m pytest tests/test_synthesis_contract.py -q
```

---

## 5) Scope Gate

```bash
git diff --name-status origin/main..HEAD

M	HANDOFF.md
A	docs/slr/SYNTHESIS_OFF_HOST_CONTRACT.md
A	elis/synthesis_offhost_contract.py
A	tests/test_synthesis_contract.py
```

---

## 6) Design Notes

### Off-host synthesis governance by construction

`SynthesisWorkflowEnvelope` enforces `execution_surface="off-host-workflow"` and
`local_execution_allowed=False` in `__post_init__`. Unsupported envelopes fail at
construction time.

### Cross-study traceability as a first-class contract

`SynthesisReasoningTrace` requires claim-level links to supporting records and
evidence references. `build_synthesis_trace_bundle` emits canonical trace payload
plus SHA-256 digest (`trace_sha256`) for reproducible audit.

### High-impact outputs require human review

`build_high_impact_checkpoints` creates explicit pending checkpoints only for
`high` and `critical` findings. Each checkpoint enforces
`reviewer_required=True`.

### Migration criteria documented but not active

`LocalMigrationCriteria` stores future readiness criteria while
`assert_local_migration_not_activated` blocks activation in PE-SLR-08.

---

## 7) Notes for Validator

1. Confirm envelope rejects local/unsupported execution surfaces.
2. Confirm trace objects require claim IDs, supporting record IDs, and evidence refs.
3. Confirm high-impact findings generate pending human-review checkpoints.
4. Confirm activation attempt on local migration criteria raises.
5. Run `python -m pytest tests/test_synthesis_contract.py -v` and verify all pass.
