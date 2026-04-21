# HANDOFF — PE-SLR-09 · `elis-server` Capacity and Placement Policy Enforcement

**Date:** 2026-04-21
**PE:** `PE-SLR-09`
**Branch:** `feature/pe-slr-09-capacity-and-placement-policy`
**Implementer:** `infra-impl-codex` (CODEX @ `elis-server`)
**Validator:** `infra-val-claude` (Claude Code)

---

## 1) Summary

Implements bounded local placement policy controls for `elis-server`:

- documented canonical local/off-host workload class policy
- runtime local-capacity enforcement with deterministic throttle/defer outcomes
- PM-facing policy reporting for local vs off-host workload classes
- explicit capacity-triggered throttling guidance contract
- hard guard preventing local helper/screening pathways from promoting
  Extraction/Synthesis to local execution

---

## 2) Deliverables

| File | Change |
|------|--------|
| `elis/workload_placement_policy.py` | New module implementing workload placement policy, capacity checks, PM reporting, throttling guidance, and promotion guard |
| `tests/test_workload_placement_policy.py` | New test suite covering AC-1 to AC-5 |
| `docs/slr/WORKLOAD_PLACEMENT_POLICY.md` | New operator documentation for local/off-host classes, throttling, and reporting |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | `elis-server` local SLR concurrency policy is documented and enforced | PASS |
| AC-2 | PM can report allowed local workload classes vs off-host workload classes | PASS |
| AC-3 | Capacity-triggered throttling guidance is committed | PASS |
| AC-4 | Local helper/screening runs cannot accidentally promote Extraction/Synthesis to local execution | PASS |
| AC-5 | `python -m pytest tests/test_workload_placement_policy.py -v` passes | PASS |

---

## 4) Validation Commands

```bash
python -m black --check elis/workload_placement_policy.py tests/test_workload_placement_policy.py
python -m ruff check elis/workload_placement_policy.py tests/test_workload_placement_policy.py
python -m pytest tests/test_workload_placement_policy.py -v
```

---

## 5) Scope Gate

```bash
git diff --name-status origin/main..HEAD
```

---

## 6) Design Notes

### Policy as code, not guidance text only

`WorkloadPlacementPolicy` defines local/off-host class sets and rejects overlap so
misclassification fails at construction time.

### Deterministic local capacity enforcement

`enforce_local_workload_request()` returns explicit scheduling decisions:

- local run admitted with bounded effective concurrency, or
- local run deferred when local capacity is full.

### Throttling guidance is machine-readable

`capacity_triggered_throttling()` emits deterministic guidance payloads that PM
can surface in operational updates.

### Off-host safeguards are runtime-enforced

Local execution requests for `extraction` and `synthesis` raise immediately, and
`prevent_local_promotion()` blocks helper/screening promotion to off-host classes.

---

## 7) Notes for Validator

1. Confirm AC-1 by checking enforced concurrency cap and defer behaviour.
2. Confirm AC-2 by verifying PM report output contains local/off-host class lists.
3. Confirm AC-3 by verifying throttling guidance triggers when queue/memory thresholds are crossed.
4. Confirm AC-4 by verifying extraction/synthesis local requests and promotions fail at runtime.
5. Run `python -m pytest tests/test_workload_placement_policy.py -v` and verify all tests pass.

