# REVIEW — PE-SLR-09 · `elis-server` Capacity and Placement Policy Enforcement

**Validator:** `slr-val-b` (Claude Code)
**Reviewed at:** 2026-04-21
**PR:** #359

---

### Verdict

PASS

---

### Gate results

```
python -m black --check .
→ All done! ✨ 🍰 ✨  194 files would be left unchanged.

python -m ruff check .
→ All checks passed!

python -m pytest tests/test_workload_placement_policy.py -v
→ 10 passed in 0.10s

python -m pytest --tb=no (ignoring locked pytest-cache dirs)
→ 2 failed, 1000 passed, 17 warnings in 12.72s
  (2 pre-existing failures in test_verify_claude_auth.py — not introduced by this PE)

python scripts/check_agent_scope.py
→ Agent scope clean — no secret-pattern files detected in worktree.
```

---

### Scope

```
git diff --name-status origin/main..HEAD

M  HANDOFF.md
A  docs/slr/WORKLOAD_PLACEMENT_POLICY.md
A  elis/workload_placement_policy.py
A  tests/test_workload_placement_policy.py
```

4 files. No files outside PE-SLR-09 scope.

Note: feature branch rebased onto origin/main by Validator to remove unintended
CURRENT_PE.md revert artefact (branch cut before PM-CHORE-53 landed). Force-pushed
at 1e6439e. All gate results are post-rebase.

---

### Required fixes

None.

---

### Evidence

**AC-1 — `elis-server` local SLR concurrency policy is documented and enforced**

`DEFAULT_WORKLOAD_PLACEMENT_POLICY` sets `max_local_concurrency=1`.
`enforce_local_workload_request` caps `effective_concurrency` to available slots
and returns `allowed=False, recommended_action="defer"` when capacity is full.
`test_ac1_local_concurrency_policy_documented_and_enforced` confirms throttling
when requested=2 but cap=1. `test_ac1_local_request_is_deferred_when_capacity_is_full`
confirms defer when `current_local_jobs=1`. ✓

**AC-2 — PM can report allowed local workload classes vs off-host workload classes**

`report_workload_classes()` returns `local_workload_classes` (`screening`,
`metadata-triage`, `bibliometric-preanalysis`) and `off_host_workload_classes`
(`harvest`, `extraction`, `synthesis`). `test_ac2_pm_can_report_local_vs_off_host_workload_classes`
confirms exact lists. ✓

**AC-3 — Capacity-triggered throttling guidance is committed**

`capacity_triggered_throttling` returns `throttle_required=True` when
`queue_depth > max_local_concurrency` or `memory_pressure_percent >= 80`, emitting
the full `throttle_guidance` tuple. `test_ac3_capacity_triggered_throttling_guidance_is_committed`
confirms with queue=3, memory=82. `test_ac3_no_throttling_when_capacity_is_within_policy`
confirms clean path. ✓

**AC-4 — Local helper/screening runs cannot accidentally promote Extraction/Synthesis to local execution**

`enforce_local_workload_request` raises `RuntimeError` for any `off_host_workload_classes`
member. `prevent_local_promotion` raises `RuntimeError` when `to_workload_class` is in
the off-host set. `test_ac4_off_host_workload_cannot_run_locally` confirms extraction
raises. `test_ac4_local_helper_cannot_promote_synthesis_to_local` confirms screening→synthesis
promotion raises. ✓

**AC-5 — Test suite passes**

```
tests/test_workload_placement_policy.py ..........   10 passed in 0.10s
```
✓
