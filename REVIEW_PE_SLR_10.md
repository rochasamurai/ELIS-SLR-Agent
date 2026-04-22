# REVIEW — PE-SLR-10 · End-to-End Hybrid SLR Validation

**Validator:** `slr-val-a` (CODEX @ `elis-server`)
**Reviewed at:** 2026-04-22
**PR:** #361

---

### Verdict

FAIL

---

### Gate results

```bash
python -m black --check .
→ All done! ✨ 🍰 ✨
  196 files would be left unchanged.

python -m ruff check .
→ All checks passed!

python -m pytest tests/test_hybrid_slr_validation.py -v
→ ============================= test session starts =============================
  platform win32 -- Python 3.14.0, pytest-9.0.1, pluggy-1.6.0
  collected 10 items
  tests\test_hybrid_slr_validation.py ..........                           [100%]
  ======================== 10 passed, 1 warning in 0.15s ========================

python -m pytest tests/test_hybrid_slr_execution.py -v
→ ERROR: file or directory not found: tests/test_hybrid_slr_execution.py

gh pr checks 361
→ quality pass
  tests pass
  slr-quality-check pass
  validate pass
```

Note: local full-suite `pytest -q` could not be reproduced cleanly in this
sandbox because pytest temp-directory setup/cleanup hit `PermissionError`
under the worktree owner mismatch. Live PR CI is green, so this review is
blocked by contract coverage rather than by branch-health regressions.

---

### Scope

```bash
git diff --name-status origin/main..HEAD

M	HANDOFF.md
A	docs/slr/HYBRID_SLR_VALIDATION.md
A	elis/hybrid_slr_validation.py
A	tests/test_hybrid_slr_validation.py
```

4 files. Scope matches `HANDOFF.md`.

---

### Required fixes

- Update the implementation to validate the full inherited PE-SLR-10 flow from the governing plan: Harvest → Screening → support-agent → Extraction/Synthesis, including artefact placement across those surfaces.
- Restore alignment between the authoritative PE acceptance criteria and the branch artefacts: `HANDOFF.md`, the test module name, and the validator command contract must match the plan instead of redefining PE-SLR-10 locally.

---

### Evidence

The governing PE contract is inherited unchanged in the active plan lineage and
still requires the full hybrid boundary, including Harvest and the local
support-agent stage:

```text
ELIS_MultiAgent_Implementation_Plan_v1_8.md:379-393

Validate the hybrid model end to end:
- Harvest via GitHub workflow
- Screening on `elis-server`
- local support agent assistance
- Extraction/Synthesis off-host

| AC-1 | One representative review flow proves Harvest → Screening → support-agent → Extraction/Synthesis boundary works as designed |
| AC-2 | Artefacts are stored in the correct surfaces throughout |
| AC-3 | PM can report execution surface by SLR phase accurately |
| AC-4 | No unsupported local heavy workload is required for the validation run |
| AC-5 | `python -m pytest tests/test_hybrid_slr_execution.py -v` passes |
```

The new module does not compose Harvest or local support-agent code. It only
imports extraction, synthesis, and workload-placement policy helpers:

```text
elis/hybrid_slr_validation.py:14-30

from elis.extraction_offhost_contract import ...
from elis.synthesis_offhost_contract import ...
from elis.workload_placement_policy import ...
```

The runner executes screening admission plus extraction and synthesis bundles,
but never calls Harvest or local support analysis:

```text
elis/hybrid_slr_validation.py:110-154

# Phase 2 — local screening
screening_decision = enforce_local_workload_request(...)

# Phase 4a — off-host extraction
extraction_bundle = build_extraction_evidence_bundle(...)

# Phase 4b — off-host synthesis
synthesis_bundle = build_synthesis_trace_bundle(...)

# Validate invariants
assert_surface_invariants(policy=policy)
```

The declared flow inputs `screening_records` and `synthesis_findings` are not
used, which reinforces that the end-to-end boundary exercise is incomplete:

```text
elis/hybrid_slr_validation.py:89-100

def run_hybrid_slr_flow(
    *,
    review_id: str,
    run_id: str,
    trigger_source: str,
    screening_records: list[dict[str, Any]],
    extraction_rows: list[dict[str, Any]],
    synthesis_traces: list[SynthesisReasoningTrace],
    synthesis_findings: list[dict[str, Any]],
```

The branch artefacts redefine the PE contract instead of matching it. The
HANDOFF records a different AC list and a different pytest command:

```text
HANDOFF.md:38-51

| AC-1 | PM can report execution surface by SLR phase accurately | PASS |
| AC-2 | One representative hybrid SLR flow exercises local + off-host contracts together | PASS |
| AC-3 | Governance invariants are verifiable: extraction/synthesis off-host, screening local | PASS |
| AC-4 | Hybrid flow audit evidence is reproducible | PASS |
| AC-5 | `python -m pytest tests/test_hybrid_slr_validation.py -v` passes | PASS |
```

Running the plan's required test command fails because the expected file does
not exist on the branch:

```bash
python -m pytest tests/test_hybrid_slr_execution.py -v
→ ERROR: file or directory not found: tests/test_hybrid_slr_execution.py
```

---

**Re-validation round 2:** 2026-04-22

### Verdict

FAIL

### Gate results

```bash
python -m black --check elis/hybrid_slr_validation.py tests/test_hybrid_slr_execution.py
→ All done! ✨ 🍰 ✨
  2 files would be left unchanged.

python -m ruff check elis/hybrid_slr_validation.py tests/test_hybrid_slr_execution.py
→ All checks passed!

python -m pytest tests/test_hybrid_slr_execution.py -v
→ ============================= test session starts =============================
  platform win32 -- Python 3.14.0, pytest-9.0.1, pluggy-1.6.0
  collected 14 items
  .worktrees\pe-slr-10\tests\test_hybrid_slr_execution.py ..............   [100%]
  ======================== 14 passed, 1 warning in 0.12s ========================

gh pr checks 361
→ quality pass
  tests pass
  slr-quality-check pass
  validate pass
```

### Scope

```bash
git diff --name-status origin/main..HEAD

M	HANDOFF.md
A	REVIEW_PE_SLR_10.md
A	docs/slr/HYBRID_SLR_VALIDATION.md
A	elis/hybrid_slr_validation.py
A	tests/test_hybrid_slr_execution.py
```

### Required fixes

- Honour the local-capacity admission result for the support-agent stage. If `bibliometric-preanalysis` is denied because the screening slot is occupied, the hybrid flow must defer or serialise that work instead of running clustering anyway.
- Finish the remaining HANDOFF alignment to the renamed test artefact so validator-facing instructions and deliverables no longer point to `tests/test_hybrid_slr_validation.py`.

### Evidence

The updated branch now addresses the first-round contract mismatch: Harvest and
local support-agent code are imported and the governing plan's pytest command
exists and passes.

```text
elis/hybrid_slr_validation.py:21-38

from elis.harvest_workflow import HarvestWorkflowContract
from elis.local_support_analysis import cluster_by_title_similarity
...
from elis.workload_placement_policy import (
    DEFAULT_WORKLOAD_PLACEMENT_POLICY,
    WorkloadPlacementPolicy,
    enforce_local_workload_request,
    report_workload_classes,
)
```

```bash
python -m pytest tests/test_hybrid_slr_execution.py -v
→ 14 passed, 1 warning in 0.12s
```

However, the support-agent phase still bypasses the placement policy. The code
requests admission for `bibliometric-preanalysis` with `current_local_jobs=1`
while the policy cap is 1, stores the result in `_support_agent_admission`, and
then runs `cluster_by_title_similarity(...)` regardless of whether admission was
denied.

```text
elis/hybrid_slr_validation.py:174-184

_support_agent_admission = enforce_local_workload_request(
    "bibliometric-preanalysis",
    requested_concurrency=1,
    current_local_jobs=1,  # screening slot is occupied
    policy=policy,
)
clusters = cluster_by_title_similarity(
    screening_records, threshold=0.5, max_records=policy.max_local_concurrency * 500
)
```

The policy function returns a defer decision in exactly that situation:

```bash
python -c "from elis.workload_placement_policy import enforce_local_workload_request; print(enforce_local_workload_request('bibliometric-preanalysis', requested_concurrency=1, current_local_jobs=1))"
→ {'allowed': False, 'workload_class': 'bibliometric-preanalysis', 'effective_concurrency': 0, 'throttled': True, 'reason': 'local capacity reached', 'recommended_action': 'defer'}
```

That means the representative flow still runs a local support step even when
the active capacity policy says it should defer, so the bounded local-governance
behaviour is not yet proved end to end.

There is also remaining HANDOFF drift after the rename. The deliverables table
and validator note still reference the old test filename:

```text
HANDOFF.md:30-32
| `elis/hybrid_slr_validation.py` | New module implementing hybrid flow runner, surface registry, invariant checks, reproducibility validation, and PM reporting |
| `tests/test_hybrid_slr_validation.py` | New test suite with 10 tests covering AC-1 to AC-5 |
| `docs/slr/HYBRID_SLR_VALIDATION.md` | New documentation for hybrid flow, surface registry, and invariants |

HANDOFF.md:105
6. Run `python -m pytest tests/test_hybrid_slr_validation.py -v` and verify all pass.
```

---

**Re-validation round 3:** 2026-04-22

### Verdict

PASS

### Gate results

```bash
python -m black --check elis/hybrid_slr_validation.py tests/test_hybrid_slr_execution.py
→ All done! ✨ 🍰 ✨
  2 files would be left unchanged.

python -m ruff check elis/hybrid_slr_validation.py tests/test_hybrid_slr_execution.py
→ All checks passed!

python -m pytest tests/test_hybrid_slr_execution.py -v
→ ============================= test session starts =============================
  platform win32 -- Python 3.14.0, pytest-9.0.1, pluggy-1.6.0
  collected 14 items
  .worktrees\pe-slr-10\tests\test_hybrid_slr_execution.py ..............   [100%]
  ======================== 14 passed, 1 warning in 0.36s ========================

gh pr checks 361
→ quality pass
  tests pass
  slr-quality-check pass
  validate pass
```

### Scope

```bash
git diff --name-status origin/main..HEAD

M	HANDOFF.md
A	REVIEW_PE_SLR_10.md
A	docs/slr/HYBRID_SLR_VALIDATION.md
A	elis/hybrid_slr_validation.py
A	tests/test_hybrid_slr_execution.py
```

### Required fixes

None.

### Evidence

The round-2 blocker is resolved in code. The support-agent stage now uses a
sequential model (`current_local_jobs=0`) and only runs clustering when the
admission result is allowed:

```text
elis/hybrid_slr_validation.py:174-188

support_agent_admission = enforce_local_workload_request(
    "bibliometric-preanalysis",
    requested_concurrency=1,
    current_local_jobs=0,
    policy=policy,
)
if support_agent_admission["allowed"]:
    clusters = cluster_by_title_similarity(
        screening_records,
        threshold=0.5,
        max_records=policy.max_local_concurrency * 500,
    )
else:
    clusters = []
```

The stale HANDOFF references are also aligned to the renamed PE test artefact:

```text
HANDOFF.md:28-32
| `elis/hybrid_slr_validation.py` | New module implementing hybrid flow runner, surface registry, invariant checks, reproducibility validation, and PM reporting |
| `tests/test_hybrid_slr_execution.py` | New test suite with 14 tests covering AC-1 to AC-5 |
| `docs/slr/HYBRID_SLR_VALIDATION.md` | New documentation for hybrid flow, surface registry, and invariants |

HANDOFF.md:104
6. Run `python -m pytest tests/test_hybrid_slr_execution.py -v` and verify all pass.
```

Fresh validator execution confirms the governing PE command now passes and CI is
green:

```bash
python -m pytest tests/test_hybrid_slr_execution.py -v
→ 14 passed, 1 warning in 0.36s

gh pr checks 361
→ quality pass
  tests pass
  slr-quality-check pass
  validate pass
```

No new blocking findings were discovered in this round.
